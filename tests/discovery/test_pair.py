# -*- coding: utf-8 -*-
"""Testes do pareamento WhatsApp por PIN do discovery (sem rede/WhatsApp).

neonize e completamente mockado (NewAClient, PairPhone, ConnectedEv) e
``load_agent_config`` e substituido. O pareamento real (interativo) NAO e
testado por design.
"""

from __future__ import annotations

import asyncio
import json
import sys
import types
from pathlib import Path

import pytest
from click.testing import CliRunner

from qwenpaw.app.channels.whatsapp import pairing as wa_pairing
from qwenpaw.app.channels.whatsapp.pairing import (
    PairingDependencyError,
    PairingError,
    pair_by_code,
)
from qwenpaw.discovery.deploy import DeployError
from qwenpaw.discovery.pairing import (
    PairError,
    PairResult,
    _resolve_auth_dir,
    pair_discovery_whatsapp,
    resolve_session_dir,
)
from qwenpaw.discovery.state import (
    AgentSpec,
    CompanyProfile,
    OnboardingInfo,
    TeamBlueprint,
)

# --- Helpers de sessao -----------------------------------------------------


def _write_session(
    tmp_path: Path,
    *,
    team: list[AgentSpec],
    deployed: dict[str, str],
    whatsapp_number: str | None = "11 98765-4321",
) -> Path:
    """Cria uma sessao com blueprint.json + deployed.json."""
    session_dir = tmp_path / "sess"
    session_dir.mkdir(parents=True, exist_ok=True)

    onboarding = (
        OnboardingInfo(
            whatsapp_number=whatsapp_number,
            responsible_name="Joao",
        )
        if whatsapp_number is not None
        else None
    )
    blueprint = TeamBlueprint(
        company_profile=CompanyProfile(segment="varejo"),
        proposed_team=team,
        onboarding=onboarding,
    )
    (session_dir / "blueprint.json").write_text(
        blueprint.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (session_dir / "deployed.json").write_text(
        json.dumps({"version": 1, "agents": deployed}, ensure_ascii=False),
        encoding="utf-8",
    )
    return session_dir


def _spec(name: str, role: str) -> AgentSpec:
    return AgentSpec(name=name, role=role, objective=f"objetivo {name}")


class _FakeAgentCfg:
    """Config de agente minima com .channels e .workspace_dir."""

    def __init__(self, workspace_dir: str, auth_dir: str = "") -> None:
        self.workspace_dir = workspace_dir
        wa = types.SimpleNamespace(auth_dir=auth_dir)
        self.channels = types.SimpleNamespace(whatsapp=wa)


@pytest.fixture
def patch_agent_cfg(monkeypatch, tmp_path):
    """Substitui load_agent_config por um stub com workspace temporario."""

    def _fake_load_agent_config(agent_id: str):
        return _FakeAgentCfg(str(tmp_path / "ws" / agent_id))

    monkeypatch.setattr(
        "qwenpaw.config.config.load_agent_config",
        _fake_load_agent_config,
    )
    return _fake_load_agent_config


# --- Resolucao da sessao ---------------------------------------------------


def test_resolve_session_dir_positional(tmp_path):
    assert resolve_session_dir(str(tmp_path), None) == tmp_path


def test_resolve_session_dir_by_id():
    out = resolve_session_dir(None, "abc123")
    assert out == (Path("discovery") / "abc123")


def test_resolve_session_dir_both_raises():
    with pytest.raises(PairError, match="nao ambos"):
        resolve_session_dir("x", "y")


def test_resolve_session_dir_none_raises():
    with pytest.raises(PairError, match="Informe o diretorio"):
        resolve_session_dir(None, None)


# --- Escolha do agente -----------------------------------------------------


def _patch_pair_by_code(monkeypatch, *, connected=True, sink=None):
    """Substitui pair_by_code; invoca on_pin e retorna ``connected``."""

    async def _fake(auth_dir, phone, on_pin, timeout):
        on_pin("PINCODE1")
        if sink is not None:
            sink.update(
                auth_dir=auth_dir,
                phone=phone,
                timeout=timeout,
            )
        return connected

    # pair_discovery_whatsapp importa pair_by_code de dentro da funcao
    # (from ..app.channels.whatsapp.pairing import pair_by_code), entao
    # basta substituir no modulo de origem.
    monkeypatch.setattr(wa_pairing, "pair_by_code", _fake)


def test_default_client_facing_agent(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
    capsys,
):
    team = [
        _spec("Financeiro", "controle financeiro"),
        _spec("Atendente", "atendimento ao cliente"),
    ]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Financeiro": "financeiro", "Atendente": "atendente"},
    )
    _patch_pair_by_code(monkeypatch, connected=True)

    result = asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))

    assert result.agent_id == "atendente"
    assert result.agent_name == "Atendente"
    assert result.connected is True
    out = capsys.readouterr().out
    assert "PINCODE1" in out


def test_explicit_agent_override(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente", "Financeiro": "financeiro"},
    )
    _patch_pair_by_code(monkeypatch)

    result = asyncio.run(
        pair_discovery_whatsapp(
            session_dir=str(session),
            agent_id="financeiro",
        ),
    )
    assert result.agent_id == "financeiro"


def test_explicit_agent_not_deployed_raises(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="nao foi deployado"):
        asyncio.run(
            pair_discovery_whatsapp(
                session_dir=str(session),
                agent_id="inexistente",
            ),
        )


def test_no_client_facing_agent_raises(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Financeiro", "controle financeiro")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Financeiro": "financeiro"},
    )
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="client-facing"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))


def test_nothing_deployed_raises(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(tmp_path, team=team, deployed={})
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="Nenhum agente deployado"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))


def test_session_not_found_raises(tmp_path, monkeypatch, patch_agent_cfg):
    _patch_pair_by_code(monkeypatch)
    missing = tmp_path / "nope"
    with pytest.raises(PairError, match="Sessao nao encontrada"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(missing)))


# --- Resolucao do numero ---------------------------------------------------


def test_phone_normalized_from_onboarding(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
        whatsapp_number="11 98765-4321",
    )
    sink: dict = {}
    _patch_pair_by_code(monkeypatch, sink=sink)

    result = asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))
    assert result.phone == "+5511987654321"
    assert sink["phone"] == "+5511987654321"


def test_phone_override(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    _patch_pair_by_code(monkeypatch)
    result = asyncio.run(
        pair_discovery_whatsapp(
            session_dir=str(session),
            phone="+5521988887777",
        ),
    )
    assert result.phone == "+5521988887777"


def test_phone_override_invalid_raises(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="invalido"):
        asyncio.run(
            pair_discovery_whatsapp(
                session_dir=str(session),
                phone="123",
            ),
        )


def test_missing_onboarding_number_raises(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
        whatsapp_number=None,
    )
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="--phone"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))


# --- auth_dir --------------------------------------------------------------


def test_auth_dir_from_workspace(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    sink: dict = {}
    _patch_pair_by_code(monkeypatch, sink=sink)
    asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))
    expected = (
        tmp_path / "ws" / "atendente" / "credentials" / "whatsapp" / "default"
    )
    assert Path(sink["auth_dir"]) == expected


def test_auth_dir_explicit_override(tmp_path, monkeypatch):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    explicit = str(tmp_path / "custom-auth")

    def _fake_load(agent_id):
        return _FakeAgentCfg(str(tmp_path / "ws" / agent_id), explicit)

    monkeypatch.setattr(
        "qwenpaw.config.config.load_agent_config",
        _fake_load,
    )
    sink: dict = {}
    _patch_pair_by_code(monkeypatch, sink=sink)
    asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))
    assert Path(sink["auth_dir"]) == Path(explicit)


# --- Timeout (orquestracao) ------------------------------------------------


def test_timeout_returns_not_connected(tmp_path, monkeypatch, patch_agent_cfg):
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )
    _patch_pair_by_code(monkeypatch, connected=False)
    result = asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))
    assert result.connected is False


# --- Helper neonize (pair_by_code) -----------------------------------------


class _FakeAClient:
    """Cliente neonize falso: ConnectedEv simulado + PairPhone fixo."""

    instances: list["_FakeAClient"] = []

    def __init__(self, name: str) -> None:
        self.name = name
        self._handlers: dict = {}
        self.disconnected = False
        _FakeAClient.instances.append(self)

    def event(self, ev_type):
        def _decorator(fn):
            self._handlers[ev_type] = fn
            return fn

        return _decorator

    async def connect(self):
        async def _runner():
            await asyncio.sleep(3600)

        return asyncio.ensure_future(_runner())

    async def PairPhone(self, phone, show):  # noqa: N802 - API neonize
        # Dispara o ConnectedEv logo apos devolver o PIN.
        handler = self._handlers.get(_FAKE_CONNECTED_EV)
        if handler is not None:
            asyncio.get_running_loop().call_soon(
                lambda: asyncio.ensure_future(handler(self, object())),
            )
        return "ABCD1234"

    async def disconnect(self):
        self.disconnected = True


_FAKE_CONNECTED_EV = type("ConnectedEv", (), {})


def _install_fake_neonize(monkeypatch, *, connecting=True):
    """Injeta modulos neonize falsos em sys.modules."""
    client_mod = types.ModuleType("neonize.aioze.client")
    client_mod.NewAClient = _FakeAClient
    events_mod = types.ModuleType("neonize.events")
    events_mod.ConnectedEv = _FAKE_CONNECTED_EV

    aioze_pkg = types.ModuleType("neonize.aioze")
    neonize_pkg = types.ModuleType("neonize")

    monkeypatch.setitem(sys.modules, "neonize", neonize_pkg)
    monkeypatch.setitem(sys.modules, "neonize.aioze", aioze_pkg)
    monkeypatch.setitem(sys.modules, "neonize.aioze.client", client_mod)
    monkeypatch.setitem(sys.modules, "neonize.events", events_mod)


def test_pair_by_code_success(tmp_path, monkeypatch):
    _FakeAClient.instances.clear()
    _install_fake_neonize(monkeypatch)
    # Sem espera real entre connect e PairPhone.
    monkeypatch.setattr(wa_pairing, "_CONNECT_SETTLE_SECONDS", 0.0)

    pins: list[str] = []
    ok = asyncio.run(
        pair_by_code(
            auth_dir=str(tmp_path / "auth"),
            phone="+5511987654321",
            on_pin=pins.append,
            timeout=5.0,
        ),
    )
    assert ok is True
    assert pins == ["ABCD1234"]
    # neonize.db dir criado e cliente desconectado no finally.
    assert (tmp_path / "auth").is_dir()
    assert _FakeAClient.instances[-1].disconnected is True


def test_pair_by_code_timeout(tmp_path, monkeypatch):
    _FakeAClient.instances.clear()

    class _NoConnectClient(_FakeAClient):
        async def PairPhone(self, phone, show):  # noqa: N802
            return "ABCD1234"  # nunca dispara ConnectedEv

    _install_fake_neonize(monkeypatch)
    monkeypatch.setitem(
        sys.modules["neonize.aioze.client"].__dict__,
        "NewAClient",
        _NoConnectClient,
    )
    monkeypatch.setattr(wa_pairing, "_CONNECT_SETTLE_SECONDS", 0.0)

    ok = asyncio.run(
        pair_by_code(
            auth_dir=str(tmp_path / "auth"),
            phone="+5511987654321",
            on_pin=lambda c: None,
            timeout=0.1,
        ),
    )
    assert ok is False


def test_pair_by_code_neonize_missing(tmp_path, monkeypatch):
    # Forca o ImportError no import interno.
    monkeypatch.setitem(sys.modules, "neonize.aioze.client", None)
    with pytest.raises(PairingDependencyError, match="qwenpaw\\[whatsapp\\]"):
        asyncio.run(
            pair_by_code(
                auth_dir=str(tmp_path / "auth"),
                phone="+5511987654321",
                on_pin=lambda c: None,
                timeout=1.0,
            ),
        )


# --- _resolve_auth_dir: load_agent_config falha ----------------------------


def test_resolve_auth_dir_load_config_error_raises_pair_error(monkeypatch):
    """load_agent_config explodindo vira PairError amigavel (nao vaza)."""

    def _boom(agent_id):
        raise RuntimeError("disco cheio")

    monkeypatch.setattr(
        "qwenpaw.config.config.load_agent_config",
        _boom,
    )
    with pytest.raises(PairError, match="Nao consegui carregar a config"):
        _resolve_auth_dir("atendente")


def test_resolve_auth_dir_load_config_error_through_orchestrator(
    tmp_path,
    monkeypatch,
):
    """O erro de config tambem vira PairError via pair_discovery_whatsapp."""
    team = [_spec("Atendente", "atendimento ao cliente")]
    session = _write_session(
        tmp_path,
        team=team,
        deployed={"Atendente": "atendente"},
    )

    def _boom(agent_id):
        raise RuntimeError("config corrompida")

    monkeypatch.setattr(
        "qwenpaw.config.config.load_agent_config",
        _boom,
    )
    _patch_pair_by_code(monkeypatch)
    with pytest.raises(PairError, match="Nao consegui carregar a config"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))


# --- Blueprint ausente / DeployError (leak flagged by review) --------------


def test_missing_blueprint_surfaces_friendly_error(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
):
    """deployed.json existe mas blueprint.json some.

    O default (sem --agent) precisa do blueprint para achar o
    client-facing, entao load_blueprint dispara DeployError. Esse erro
    NAO pode vazar cru: a CLI so trata PairError/PairingError, entao o
    orquestrador deve traduzi-lo para PairError (mensagem amigavel).
    """
    session = tmp_path / "sess"
    session.mkdir(parents=True, exist_ok=True)
    (session / "deployed.json").write_text(
        json.dumps({"version": 1, "agents": {"Atendente": "atendente"}}),
        encoding="utf-8",
    )
    # Sem blueprint.json de proposito.
    _patch_pair_by_code(monkeypatch)

    with pytest.raises(PairError, match="blueprint"):
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))


def test_missing_blueprint_does_not_leak_deploy_error(
    tmp_path,
    monkeypatch,
    patch_agent_cfg,
):
    """Mesmo cenario: garante que DeployError nao escapa cru.

    Se DeployError vazar, a CLI nao o captura e o usuario ve traceback.
    """
    session = tmp_path / "sess"
    session.mkdir(parents=True, exist_ok=True)
    (session / "deployed.json").write_text(
        json.dumps({"version": 1, "agents": {"Atendente": "atendente"}}),
        encoding="utf-8",
    )
    _patch_pair_by_code(monkeypatch)

    try:
        asyncio.run(pair_discovery_whatsapp(session_dir=str(session)))
        raise AssertionError("esperava um erro de blueprint ausente")
    except PairError:
        pass  # comportamento desejado
    except DeployError as exc:  # pragma: no cover - documenta o leak
        raise AssertionError(
            "DeployError vazou de pair_discovery_whatsapp; a CLI nao o "
            f"captura e o usuario veria um traceback cru: {exc}",
        )


# --- CLI (CliRunner): wrapper fino + mapeamento de erros -------------------


def _patch_discovery_pair(monkeypatch, *, result=None, exc=None):
    """Substitui pair_discovery_whatsapp visto pela CLI.

    A CLI faz ``from ..discovery import pair_discovery_whatsapp`` dentro
    da funcao, entao patchamos o atributo no pacote ``qwenpaw.discovery``.
    """

    async def _fake(**kwargs):
        if exc is not None:
            raise exc
        return result

    import qwenpaw.discovery as discovery_pkg

    monkeypatch.setattr(
        discovery_pkg,
        "pair_discovery_whatsapp",
        _fake,
    )


def _import_cmd():
    from qwenpaw.cli.discovery_cmd import discovery_pair

    return discovery_pair


def test_cli_mutual_exclusion_usage_error():
    runner = CliRunner()
    result = runner.invoke(
        _import_cmd(),
        ["somedir", "--session", "abc"],
    )
    assert result.exit_code != 0
    assert "nao ambos" in result.output


def test_cli_no_session_usage_error():
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), [])
    assert result.exit_code != 0
    assert "Informe o diretorio" in result.output


def test_cli_dependency_error_maps_to_install_hint(monkeypatch):
    # A CLI repassa str(exc); a propria PairingDependencyError ja carrega
    # a dica de instalacao (ver app/channels/whatsapp/pairing.py).
    _patch_discovery_pair(
        monkeypatch,
        exc=PairingDependencyError(
            "neonize-qwenpaw nao instalado. "
            "Instale com: pip install qwenpaw[whatsapp]",
        ),
    )
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), ["somedir"])
    assert result.exit_code != 0
    assert "pip install qwenpaw[whatsapp]" in result.output


def test_cli_pair_error_maps_to_click_exception(monkeypatch):
    _patch_discovery_pair(
        monkeypatch,
        exc=PairError("numero invalido use --phone"),
    )
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), ["somedir"])
    assert result.exit_code != 0
    assert "numero invalido use --phone" in result.output


def test_cli_pairing_error_maps_to_click_exception(monkeypatch):
    _patch_discovery_pair(
        monkeypatch,
        exc=PairingError("falha no PairPhone"),
    )
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), ["somedir"])
    assert result.exit_code != 0
    assert "falha no PairPhone" in result.output


def test_cli_success_message(monkeypatch):
    _patch_discovery_pair(
        monkeypatch,
        result=PairResult(
            agent_name="Atendente",
            agent_id="atendente",
            phone="+5511987654321",
            auth_dir="/tmp/auth",
            connected=True,
        ),
    )
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), ["somedir"])
    assert result.exit_code == 0
    assert "Atendente conectado" in result.output


def test_cli_timeout_message(monkeypatch):
    _patch_discovery_pair(
        monkeypatch,
        result=PairResult(
            agent_name="Atendente",
            agent_id="atendente",
            phone="+5511987654321",
            auth_dir="/tmp/auth",
            connected=False,
        ),
    )
    runner = CliRunner()
    result = runner.invoke(_import_cmd(), ["somedir"])
    assert result.exit_code == 0
    assert "Tempo esgotado" in result.output
    assert "+5511987654321" in result.output
