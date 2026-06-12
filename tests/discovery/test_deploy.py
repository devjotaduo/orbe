# -*- coding: utf-8 -*-
"""Testes do importador de deploy do discovery (sem LLM, sem rede)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from qwenpaw.cli.discovery_cmd import discovery_deploy
from qwenpaw.config.config import (
    AgentProfileConfig,
    AgentProfileRef,
    AgentsConfig,
)
from qwenpaw.discovery import deploy as deploy_mod
from qwenpaw.discovery.deploy import DeployError, deploy_session
from qwenpaw.discovery.state import (
    AgentSpec,
    CompanyProfile,
    ConnectorRef,
    OnboardingInfo,
    TeamBlueprint,
)


class FakeRootConfig:
    """Config raiz minima com .agents (profiles + agent_order)."""

    def __init__(self) -> None:
        self.agents = AgentsConfig()
        # AgentsConfig pode trazer profiles default; zera para o teste.
        self.agents.profiles = {}
        self.agents.agent_order = []
        self.agents.language = "pt"


@pytest.fixture
def fake_env(tmp_path, monkeypatch):
    """Aponta o caminho oficial de criacao para um workspace temporario.

    Mantem uma config raiz em memoria e grava agent.json reais em disco,
    sem tocar a config global do usuario nem chamar LLM/rede.
    """
    config = FakeRootConfig()
    saved_agent_configs: dict[str, AgentProfileConfig] = {}
    workspaces_root = tmp_path / "workspaces"

    def fake_load_config():
        return config

    def fake_save_config(_cfg):
        return None

    def fake_save_agent_config(agent_id, agent_config):
        if agent_id not in config.agents.profiles:
            raise AssertionError(
                f"save_agent_config para id nao registrado: {agent_id}",
            )
        saved_agent_configs[agent_id] = agent_config
        ref = config.agents.profiles[agent_id]
        ws = Path(ref.workspace_dir)
        ws.mkdir(parents=True, exist_ok=True)
        (ws / "agent.json").write_text(
            agent_config.model_dump_json(exclude_none=True, indent=2),
            encoding="utf-8",
        )

    def fake_default_workspace_dir(agent_id):
        return workspaces_root / agent_id

    def fake_initialize_workspace(workspace_dir, *, language):
        # Simula o helper oficial: cria PROFILE.md como o template faria.
        Path(workspace_dir).mkdir(parents=True, exist_ok=True)
        profile = Path(workspace_dir) / "PROFILE.md"
        if not profile.exists():
            profile.write_text("# template\n", encoding="utf-8")

    monkeypatch.setattr(deploy_mod, "load_config", fake_load_config)
    monkeypatch.setattr(deploy_mod, "save_config", fake_save_config)
    monkeypatch.setattr(
        deploy_mod,
        "save_agent_config",
        fake_save_agent_config,
    )
    monkeypatch.setattr(
        deploy_mod,
        "_default_workspace_dir",
        fake_default_workspace_dir,
    )
    monkeypatch.setattr(
        deploy_mod,
        "_initialize_workspace",
        fake_initialize_workspace,
    )

    return {
        "config": config,
        "saved": saved_agent_configs,
        "workspaces_root": workspaces_root,
    }


def _write_blueprint(session_dir: Path, blueprint: TeamBlueprint) -> None:
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "blueprint.json").write_text(
        blueprint.model_dump_json(indent=2),
        encoding="utf-8",
    )


def _sample_blueprint() -> TeamBlueprint:
    return TeamBlueprint(
        company_profile=CompanyProfile(
            segment="ecommerce de roupas",
            cnae="4781-4",
            size="pequena",
            business_model="venda online",
            pains=["atendimento manual lento"],
        ),
        proposed_team=[
            AgentSpec(
                name="Atendente Virtual",
                role="Atendimento ao cliente",
                objective="Responder clientes no WhatsApp",
                tasks=["Responder duvidas", "Registrar pedidos"],
                tools_integrations=["builtin:read_file", "crm:rdstation"],
                talks_to=["Analista de Estoque"],
            ),
            AgentSpec(
                name="Analista de Estoque",
                role="Backoffice de estoque",
                objective="Controlar o estoque",
                tasks=["Atualizar niveis de estoque"],
                tools_integrations=[],
                talks_to=["Fantasma Inexistente"],
            ),
        ],
        recommended_connectors=[
            ConnectorRef(
                integration_kind="crm",
                name="RD Station",
                origin="rdstation",
                slug_or_url="rdstation",
                status="recomendado",
            ),
        ],
        onboarding=OnboardingInfo(
            whatsapp_number="+5511999999999",
            responsible_name="Maria",
            is_owner=True,
        ),
    )


# --- blueprint ausente / invalido ------------------------------------------


def test_missing_blueprint_raises(tmp_path, fake_env):
    with pytest.raises(DeployError, match="blueprint.json nao encontrado"):
        deploy_session(tmp_path / "sessao_inexistente")


def test_invalid_blueprint_raises(tmp_path, fake_env):
    session = tmp_path / "sessao"
    session.mkdir()
    (session / "blueprint.json").write_text("{not valid", encoding="utf-8")
    with pytest.raises(DeployError, match="invalido"):
        deploy_session(session)


def test_schema_invalid_blueprint_raises(tmp_path, fake_env):
    session = tmp_path / "sessao"
    session.mkdir()
    # JSON valido mas faltando company_profile (campo obrigatorio).
    (session / "blueprint.json").write_text(
        json.dumps({"proposed_team": []}),
        encoding="utf-8",
    )
    with pytest.raises(DeployError, match="invalido"):
        deploy_session(session)


# --- criacao de N agentes --------------------------------------------------


def test_creates_n_agents(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    result = deploy_session(session)

    assert len(result.created) == 2
    config = fake_env["config"]
    assert len(config.agents.profiles) == 2
    # Cada agente tem um AgentProfileRef e um agent.json salvo.
    for ag in result.created:
        assert isinstance(config.agents.profiles[ag.agent_id], AgentProfileRef)
        assert ag.agent_id in fake_env["saved"]
        ws = Path(ag.workspace_dir)
        assert (ws / "agent.json").exists()


def test_profile_md_written_in_ptbr(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    result = deploy_session(session)
    atendente = next(
        ag for ag in result.created if ag.name == "Atendente Virtual"
    )
    profile = (Path(atendente.workspace_dir) / "PROFILE.md").read_text(
        encoding="utf-8",
    )
    assert "# Atendente Virtual" in profile
    assert "Atendimento ao cliente" in profile
    assert "ecommerce de roupas" in profile
    assert "portugues do Brasil" in profile
    # PROFILE.md foi sobrescrito (nao ficou o stub do template).
    assert "# template" not in profile


# --- WhatsApp --------------------------------------------------------------


def test_whatsapp_enabled_on_client_facing(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    deploy_session(session)
    saved = fake_env["saved"]

    atendente = next(
        c for c in saved.values() if c.name == "Atendente Virtual"
    )
    estoque = next(
        c for c in saved.values() if c.name == "Analista de Estoque"
    )
    assert atendente.channels.whatsapp.enabled is True
    # Agente de backoffice nao tem WhatsApp habilitado.
    assert estoque.channels.whatsapp.enabled is False


# --- pendencias ------------------------------------------------------------


def test_pendencies_reported(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    result = deploy_session(session)

    # 'crm:rdstation' tem conector recomendado mas sem mapeamento MCP auto.
    assert any("rdstation" in p for p in result.pending_tools)
    # talks_to para agente inexistente vira pendencia, sem quebrar.
    assert any("Fantasma Inexistente" in p for p in result.pending_talks_to)


def test_a2a_peers_wired_for_known_peer(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    result = deploy_session(session)

    atendente = next(
        ag for ag in result.created if ag.name == "Atendente Virtual"
    )
    estoque = next(
        ag for ag in result.created if ag.name == "Analista de Estoque"
    )
    # 'Analista de Estoque' consta no blueprint -> par real do atendente.
    assert atendente.peers == ["Analista de Estoque"]
    # 'Fantasma Inexistente' nao consta -> nenhum par real, vira pendencia.
    assert estoque.peers == []
    assert any("Fantasma Inexistente" in p for p in result.pending_talks_to)
    # Os builtins a2a continuam habilitados (default) no agente com par.
    saved = fake_env["saved"]
    cfg = next(c for c in saved.values() if c.name == "Atendente Virtual")
    assert cfg.tools.builtin_tools["chat_with_agent"].enabled is True
    assert cfg.tools.builtin_tools["list_agents"].enabled is True


# --- idempotencia ----------------------------------------------------------


def test_idempotent_second_run(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    first = deploy_session(session)
    assert len(first.created) == 2

    config = fake_env["config"]
    ids_after_first = set(config.agents.profiles.keys())

    second = deploy_session(session)
    assert len(second.created) == 0
    assert len(second.skipped) == 2
    # Nenhum agente novo foi criado.
    assert set(config.agents.profiles.keys()) == ids_after_first

    # Sidecar deployed.json existe e mapeia os nomes.
    sidecar = json.loads(
        (session / "deployed.json").read_text(encoding="utf-8"),
    )
    assert set(sidecar["agents"].keys()) == {
        "Atendente Virtual",
        "Analista de Estoque",
    }


# --- colisao de agent_id ---------------------------------------------------


def test_colliding_names_get_unique_ids(tmp_path, fake_env):
    # Dois nomes que slugificam para o mesmo id ("agente-de-vendas").
    blueprint = TeamBlueprint(
        company_profile=CompanyProfile(segment="varejo"),
        proposed_team=[
            AgentSpec(
                name="Agente de Vendas",
                role="Vendas",
                objective="Vender",
                tasks=["Atender clientes"],
            ),
            AgentSpec(
                name="Agente: de Vendas!",
                role="Vendas premium",
                objective="Vender mais",
                tasks=["Atender clientes vip"],
            ),
        ],
    )
    session = tmp_path / "sessao"
    _write_blueprint(session, blueprint)

    result = deploy_session(session)

    assert len(result.created) == 2
    ids = [ag.agent_id for ag in result.created]
    # Mesmo slug base -> o segundo recebe um sufixo unico.
    assert ids[0] == "agente-de-vendas"
    assert ids[1] == "agente-de-vendas-2"
    assert len(set(ids)) == 2

    config = fake_env["config"]
    # Dois profiles distintos: nenhum sobrescreveu o outro.
    assert len(config.agents.profiles) == 2
    assert set(config.agents.profiles.keys()) == set(ids)
    # Workspaces distintos -> nenhum agent.json foi sobrescrito.
    ws_dirs = {ag.workspace_dir for ag in result.created}
    assert len(ws_dirs) == 2


# --- falha parcial + idempotencia ------------------------------------------


def test_partial_failure_no_duplicate_on_rerun(
    tmp_path,
    fake_env,
    monkeypatch,
):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    real_save = deploy_mod.save_agent_config
    state = {"calls": 0}

    def flaky_save(agent_id, agent_config):
        state["calls"] += 1
        # Falha ao salvar o 2o agente do primeiro run.
        if state["calls"] == 2:
            raise RuntimeError("disco cheio (simulado)")
        return real_save(agent_id, agent_config)

    monkeypatch.setattr(deploy_mod, "save_agent_config", flaky_save)

    config = fake_env["config"]

    # 1o run: o 2o agente falha no save -> deploy propaga o erro.
    with pytest.raises(RuntimeError, match="disco cheio"):
        deploy_session(session)

    # Apenas o 1o agente ficou persistido no sidecar.
    sidecar = json.loads(
        (session / "deployed.json").read_text(encoding="utf-8"),
    )
    assert set(sidecar["agents"].keys()) == {"Atendente Virtual"}

    ids_after_first = set(config.agents.profiles.keys())

    # Restaura o save saudavel e roda de novo.
    monkeypatch.setattr(deploy_mod, "save_agent_config", real_save)
    second = deploy_session(session)

    # O 1o agente nao e recriado (pulado); somente o que faltou e criado.
    created_names = {ag.name for ag in second.created}
    skipped_names = {ag.name for ag in second.skipped}
    assert "Analista de Estoque" in created_names
    assert "Atendente Virtual" in skipped_names

    # Nenhuma duplicata: o 1o agente tem exatamente 1 profile/workspace.
    final_ids = list(config.agents.profiles.keys())
    assert len(final_ids) == len(set(final_ids))
    # O profile do 1o agente sobreviveu intacto entre os runs.
    assert ids_after_first.issubset(set(final_ids))
    # Total final = 2 agentes distintos, sem duplicar "Atendente Virtual".
    all_deployed = json.loads(
        (session / "deployed.json").read_text(encoding="utf-8"),
    )
    assert set(all_deployed["agents"].keys()) == {
        "Atendente Virtual",
        "Analista de Estoque",
    }


# --- PROFILE.md: secao "Trabalha com" (talks_to) ---------------------------


def test_profile_md_lists_peers_for_a2a(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    result = deploy_session(session)
    atendente = next(
        ag for ag in result.created if ag.name == "Atendente Virtual"
    )
    profile = (Path(atendente.workspace_dir) / "PROFILE.md").read_text(
        encoding="utf-8",
    )
    assert "## Trabalha com" in profile
    assert "Analista de Estoque" in profile
    assert "chat_with_agent" in profile
    assert "list_agents" in profile


# --- CLI: qwenpaw discovery deploy -----------------------------------------


def test_cli_deploy_with_session_dir(tmp_path, fake_env):
    session = tmp_path / "sessao"
    _write_blueprint(session, _sample_blueprint())

    runner = CliRunner()
    res = runner.invoke(discovery_deploy, [str(session)])

    assert res.exit_code == 0, res.output
    assert "Agentes criados (2)" in res.output
    assert "Atendente Virtual" in res.output
    # Bloco de passos manuais do WhatsApp aparece (ha agente client-facing).
    assert "Proximos passos manuais (WhatsApp)" in res.output
    assert "+5511999999999" in res.output


def test_cli_deploy_with_session_id_option(tmp_path, fake_env, monkeypatch):
    # --session <id> resolve para ./discovery/<id> a partir do cwd.
    monkeypatch.chdir(tmp_path)
    session = tmp_path / "discovery" / "abc123"
    _write_blueprint(session, _sample_blueprint())

    runner = CliRunner()
    res = runner.invoke(discovery_deploy, ["--session", "abc123"])

    assert res.exit_code == 0, res.output
    assert "Agentes criados (2)" in res.output


def test_cli_deploy_mutual_exclusion(tmp_path, fake_env):
    runner = CliRunner()
    res = runner.invoke(
        discovery_deploy,
        ["alguma/sessao", "--session", "abc123"],
    )
    assert res.exit_code != 0
    assert "nao ambos" in res.output


def test_cli_deploy_missing_arg(fake_env):
    runner = CliRunner()
    res = runner.invoke(discovery_deploy, [])
    assert res.exit_code != 0
    assert "SESSION_DIR" in res.output


def test_cli_deploy_missing_blueprint_clickexception(tmp_path, fake_env):
    runner = CliRunner()
    res = runner.invoke(discovery_deploy, [str(tmp_path / "vazia")])
    assert res.exit_code != 0
    assert "blueprint.json nao encontrado" in res.output


def test_cli_deploy_no_whatsapp_block_when_no_client_agent(tmp_path, fake_env):
    blueprint = TeamBlueprint(
        company_profile=CompanyProfile(segment="industria"),
        proposed_team=[
            AgentSpec(
                name="Analista Financeiro",
                role="Financeiro",
                objective="Conciliar contas",
                tasks=["Fechar caixa"],
            ),
        ],
    )
    session = tmp_path / "sessao"
    _write_blueprint(session, blueprint)

    runner = CliRunner()
    res = runner.invoke(discovery_deploy, [str(session)])

    assert res.exit_code == 0, res.output
    assert "Agentes criados (1)" in res.output
    # Nenhum agente atende cliente -> sem bloco de WhatsApp.
    assert "Proximos passos manuais (WhatsApp)" not in res.output
