# -*- coding: utf-8 -*-
"""Importador do discovery: blueprint -> agentes qwenpaw reais.

Transforma o ``blueprint.json`` de uma sessao de discovery em agentes
qwenpaw concretos, usando o caminho OFICIAL de criacao de agente do
projeto (o mesmo que ``qwenpaw agents create`` executa). Nenhuma API do
AgentScope e usada aqui: tudo passa pela camada de config/workspace do
qwenpaw.

Fluxo (ver :func:`deploy_session`):

1. Carrega e valida o blueprint.
2. Para cada ``AgentSpec`` cria um agente real (template ``default``).
3. Deriva um ``PROFILE.md`` em pt-BR a partir de role/objetivo/tarefas +
   perfil da empresa.
4. Configura (nao pareia) o canal WhatsApp nos agentes de atendimento.
5. Mapeia ferramentas/conectores conhecidos; o resto vira pendencia.
6. Habilita comunicacao agente-a-agente (``talks_to``) via os builtins
   ``list_agents`` / ``chat_with_agent``.
7. E idempotente via um sidecar ``deployed.json`` na sessao.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..agents.templates import DEFAULT_AGENT_TEMPLATE, build_agent_template
from ..config import load_config, save_config
from ..config.config import (
    AgentProfileRef,
    ChannelConfig,
    ToolsConfig,
    WhatsAppConfig,
    save_agent_config,
)
from .state import AgentSpec, CompanyProfile, TeamBlueprint

# Builtins de comunicacao agente-a-agente (existem no qwenpaw v2).
A2A_BUILTIN_TOOLS = ("list_agents", "chat_with_agent")

# Palavras que indicam um agente voltado ao cliente (atendimento).
_CLIENT_FACING_HINTS = (
    "atend",
    "client",
    "cliente",
    "vend",
    "venda",
    "comercial",
    "suporte",
    "whatsapp",
    "sac",
    "relacionamento",
)


class DeployError(Exception):
    """Erro de deploy claro para o usuario (blueprint ausente/invalido)."""


@dataclass
class DeployedAgent:
    """Um agente criado (ou reutilizado) pelo deploy."""

    name: str
    agent_id: str
    workspace_dir: str
    whatsapp_enabled: bool = False
    # Pares de talks_to encontrados entre os agentes do blueprint.
    peers: list[str] = field(default_factory=list)


@dataclass
class DeployResult:
    """Resumo estruturado do deploy para a CLI renderizar."""

    session_dir: str
    created: list[DeployedAgent] = field(default_factory=list)
    skipped: list[DeployedAgent] = field(default_factory=list)
    # Pendencias: ferramentas sem conector conhecido.
    pending_tools: list[str] = field(default_factory=list)
    # Pendencias: pares de talks_to nao encontrados entre os agentes.
    pending_talks_to: list[str] = field(default_factory=list)
    whatsapp_number: str | None = None


# --- Carga do blueprint ----------------------------------------------------


def load_blueprint(session_dir: Path) -> TeamBlueprint:
    """Le e valida ``<session_dir>/blueprint.json``.

    Raises:
        DeployError: se o arquivo nao existir ou for invalido.
    """
    bp_path = session_dir / "blueprint.json"
    if not bp_path.exists():
        raise DeployError(
            f"blueprint.json nao encontrado em {session_dir}. "
            "Rode 'qwenpaw discovery start' primeiro.",
        )
    try:
        raw = bp_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - IO raro
        raise DeployError(f"Falha ao ler {bp_path}: {exc}") from exc

    try:
        return TeamBlueprint.model_validate_json(raw)
    except ValueError as exc:
        raise DeployError(
            f"blueprint.json invalido em {bp_path}: {exc}",
        ) from exc


# --- Helpers ---------------------------------------------------------------


def _slugify_agent_id(name: str) -> str:
    """Deriva um agent_id deterministico a partir do nome do AgentSpec.

    Mantem letras/digitos, troca o resto por '-' e respeita as regras de
    ``validate_agent_id`` (sem inicio/fim em '-' ou '_', minimo 2 chars).
    """
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    slug = slug.strip("-_")
    if len(slug) < 2:
        slug = f"ag-{slug}" if slug else "agente"
    return slug[:64].strip("-_") or "agente"


def _is_client_facing(spec: AgentSpec) -> bool:
    """Heuristica: o agente atende cliente (role/tarefas/objetivo)?"""
    haystack = " ".join(
        [spec.role, spec.objective, *spec.tasks],
    ).lower()
    return any(hint in haystack for hint in _CLIENT_FACING_HINTS)


def _build_profile_md(
    spec: AgentSpec,
    company: CompanyProfile,
    whatsapp_number: str | None,
    *,
    whatsapp_enabled: bool,
    peers: list[str],
) -> str:
    """Gera o conteudo de PROFILE.md (identidade do agente) em pt-BR."""
    lines: list[str] = [f"# {spec.name}", ""]
    lines.append(f"**Papel:** {spec.role}")
    lines.append("")
    lines.append(f"**Objetivo:** {spec.objective}")
    lines.append("")

    if spec.tasks:
        lines.append("## Responsabilidades")
        for task in spec.tasks:
            lines.append(f"- {task}")
        lines.append("")

    ctx: list[str] = []
    if company.segment:
        ctx.append(f"- Segmento: {company.segment}")
    if company.cnae:
        ctx.append(f"- CNAE: {company.cnae}")
    if company.size:
        ctx.append(f"- Porte: {company.size}")
    if company.business_model:
        ctx.append(f"- Modelo de negocio: {company.business_model}")
    if company.pains:
        ctx.append("- Dores do negocio:")
        ctx.extend(f"  - {pain}" for pain in company.pains)
    if ctx:
        lines.append("## Contexto da empresa")
        lines.extend(ctx)
        lines.append("")

    if peers:
        lines.append("## Trabalha com")
        for peer in peers:
            lines.append(f"- {peer}")
        lines.append(
            "\nUse as ferramentas `list_agents` e `chat_with_agent` "
            "para coordenar com esses colegas.",
        )
        lines.append("")

    if whatsapp_enabled:
        lines.append("## Canal WhatsApp")
        num = whatsapp_number or "(numero a definir)"
        lines.append(
            f"Atende clientes pelo WhatsApp ({num}). O pareamento "
            "(QR/codigo) deve ser feito manualmente no Console.",
        )
        lines.append("")

    lines.append("## Tom")
    lines.append(
        "Responda sempre em portugues do Brasil, de forma clara, "
        "objetiva e cordial.",
    )
    lines.append("")
    return "\n".join(lines)


# Mapeamento minimo de tools_integrations -> builtin tool do qwenpaw.
# 'origin:slug' ou texto livre; so o que houver correspondencia direta.
_BUILTIN_TOOL_MAP = {
    "read_file": "read_file",
    "write_file": "write_file",
    "edit_file": "edit_file",
    "list_agents": "list_agents",
    "chat_with_agent": "chat_with_agent",
}


def _enable_builtin_tools(tools: ToolsConfig, names: list[str]) -> list[str]:
    """Habilita os builtins indicados; retorna os que existiam mesmo."""
    enabled: list[str] = []
    for name in names:
        tc = tools.builtin_tools.get(name)
        if tc is not None:
            tc.enabled = True
            enabled.append(name)
    return enabled


def _map_tools(
    spec: AgentSpec,
    blueprint: TeamBlueprint,
    tools: ToolsConfig,
) -> list[str]:
    """Mapeia tools_integrations para builtins; retorna as pendencias.

    Nao quebra: o que nao tiver correspondencia conhecida vira pendencia.
    """
    pending: list[str] = []
    known_slugs = {
        c.slug_or_url
        for c in blueprint.recommended_connectors
        if c.slug_or_url
    }
    for entry in spec.tools_integrations:
        slug = entry.split(":", 1)[-1].strip().lower()
        builtin = _BUILTIN_TOOL_MAP.get(slug)
        if builtin is not None and _enable_builtin_tools(tools, [builtin]):
            continue
        # Conector recomendado existe mas nao ha mapeamento MCP automatico.
        if entry.split(":", 1)[-1].strip() in known_slugs or slug in {
            s.lower() for s in known_slugs
        }:
            pending.append(f"{spec.name}: conector '{entry}' (configurar MCP)")
        else:
            pending.append(f"{spec.name}: ferramenta '{entry}' sem conector")
    return pending


# --- Idempotencia ----------------------------------------------------------


def _load_deployed(session_dir: Path) -> dict[str, str]:
    """Le o sidecar deployed.json (name -> agent_id)."""
    path = session_dir / "deployed.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    agents = data.get("agents", {})
    if not isinstance(agents, dict):
        return {}
    return {str(k): str(v) for k, v in agents.items()}


def _save_deployed(session_dir: Path, mapping: dict[str, str]) -> None:
    """Persiste o sidecar deployed.json (name -> agent_id)."""
    path = session_dir / "deployed.json"
    path.write_text(
        json.dumps(
            {"version": 1, "agents": mapping},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _unique_agent_id(base_id: str, existing: set[str]) -> str:
    """Garante unicidade do agent_id contra os ids ja registrados."""
    if base_id not in existing:
        return base_id
    for i in range(2, 100):
        candidate = f"{base_id}-{i}"[:64].strip("-_")
        if candidate not in existing:
            return candidate
    raise DeployError(
        f"Nao foi possivel gerar um agent_id unico a partir de '{base_id}'.",
    )


# --- Deploy principal ------------------------------------------------------


def deploy_session(session_dir: Path) -> DeployResult:
    """Cria agentes qwenpaw reais a partir do blueprint da sessao.

    Args:
        session_dir: Diretorio da sessao de discovery (contem blueprint.json).

    Returns:
        DeployResult com agentes criados/pulados e pendencias.

    Raises:
        DeployError: se o blueprint estiver ausente ou invalido.
    """
    session_dir = Path(session_dir).expanduser()
    blueprint = load_blueprint(session_dir)

    company = blueprint.company_profile
    whatsapp_number = (
        blueprint.onboarding.whatsapp_number if blueprint.onboarding else None
    )
    spec_names = {s.name for s in blueprint.proposed_team}

    result = DeployResult(
        session_dir=str(session_dir),
        whatsapp_number=whatsapp_number,
    )

    deployed = _load_deployed(session_dir)
    config = load_config()

    try:
        _deploy_agents(
            session_dir,
            blueprint,
            company,
            whatsapp_number,
            spec_names,
            config,
            deployed,
            result,
        )
    finally:
        # Persiste o mapeamento mesmo em falha parcial (idempotencia).
        _save_deployed(session_dir, deployed)
    return result


def _deploy_agents(
    session_dir: Path,
    blueprint: TeamBlueprint,
    company: CompanyProfile,
    whatsapp_number: str | None,
    spec_names: set[str],
    config,
    deployed: dict[str, str],
    result: DeployResult,
) -> None:
    """Cria cada agente do blueprint, persistindo o sidecar a cada um."""
    for spec in blueprint.proposed_team:
        existing_ids = set(config.agents.profiles.keys())

        # Idempotencia: ja deployado e ainda presente -> pula.
        mapped = deployed.get(spec.name)
        if mapped and mapped in config.agents.profiles:
            ref = config.agents.profiles[mapped]
            wa = _is_client_facing(spec)
            result.skipped.append(
                DeployedAgent(
                    name=spec.name,
                    agent_id=mapped,
                    workspace_dir=ref.workspace_dir,
                    whatsapp_enabled=wa,
                ),
            )
            # Registra pendencias mesmo ao pular (relatorio consistente).
            _collect_pendencies(spec, blueprint, spec_names, result)
            continue

        agent_id = _unique_agent_id(
            _slugify_agent_id(spec.name),
            existing_ids,
        )
        workspace_dir = _default_workspace_dir(agent_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        template_result = build_agent_template(
            DEFAULT_AGENT_TEMPLATE,
            agent_id=agent_id,
            workspace_dir=workspace_dir,
            fallback_language=getattr(config.agents, "language", None) or "pt",
            name=spec.name,
            description=spec.objective,
            language="pt",
        )
        agent_config = template_result.agent_config
        if agent_config.tools is None:
            agent_config.tools = ToolsConfig()
        if agent_config.channels is None:
            agent_config.channels = ChannelConfig()

        # Mapeia ferramentas conhecidas; resto vira pendencia.
        result.pending_tools.extend(
            _map_tools(spec, blueprint, agent_config.tools),
        )

        # talks_to: liga via builtins a2a; pares ausentes viram pendencia.
        peers = [p for p in spec.talks_to if p in spec_names]
        missing = [p for p in spec.talks_to if p not in spec_names]
        for peer in missing:
            result.pending_talks_to.append(
                f"{spec.name} -> '{peer}' (agente nao consta no blueprint)",
            )
        if peers:
            _enable_builtin_tools(
                agent_config.tools,
                list(A2A_BUILTIN_TOOLS),
            )

        # WhatsApp: configura (NAO pareia) nos agentes de atendimento.
        wa_enabled = _is_client_facing(spec)
        if wa_enabled:
            agent_config.channels.whatsapp = WhatsAppConfig(enabled=True)

        # Inicializa o workspace pelo caminho oficial.
        _initialize_workspace(workspace_dir, language="pt")

        # PROFILE.md: identidade do agente (sobrescreve o template).
        profile_md = _build_profile_md(
            spec,
            company,
            whatsapp_number,
            whatsapp_enabled=wa_enabled,
            peers=peers,
        )
        (workspace_dir / "PROFILE.md").write_text(profile_md, encoding="utf-8")

        # Registra no config raiz e salva (caminho oficial).
        config.agents.profiles[agent_id] = AgentProfileRef(
            id=agent_id,
            workspace_dir=str(workspace_dir),
            enabled=True,
        )
        config.agents.agent_order = _normalized_agent_order(config)
        save_config(config)
        save_agent_config(agent_id, agent_config)

        deployed[spec.name] = agent_id
        # Persiste o sidecar a cada agente concluido (idempotencia
        # robusta mesmo se um agente seguinte falhar).
        _save_deployed(session_dir, deployed)
        result.created.append(
            DeployedAgent(
                name=spec.name,
                agent_id=agent_id,
                workspace_dir=str(workspace_dir),
                whatsapp_enabled=wa_enabled,
                peers=peers,
            ),
        )


def _collect_pendencies(
    spec: AgentSpec,
    blueprint: TeamBlueprint,
    spec_names: set[str],
    result: DeployResult,
) -> None:
    """Coleta pendencias de tools/talks_to sem criar agente (caso pulado)."""
    throwaway = ToolsConfig()
    result.pending_tools.extend(_map_tools(spec, blueprint, throwaway))
    for peer in spec.talks_to:
        if peer not in spec_names:
            result.pending_talks_to.append(
                f"{spec.name} -> '{peer}' (agente nao consta no blueprint)",
            )


def _default_workspace_dir(agent_id: str) -> Path:
    """Resolve WORKING_DIR/workspaces/<id> (mesmo padrao do agents_cmd)."""
    from ..constant import WORKING_DIR

    return (WORKING_DIR / "workspaces" / agent_id).expanduser()


def _initialize_workspace(workspace_dir: Path, *, language: str) -> None:
    """Inicializa o workspace pelo helper oficial do servidor."""
    from ..app.routers.agents import _initialize_agent_workspace

    _initialize_agent_workspace(
        workspace_dir,
        skill_names=[],
        md_template_id=None,
        language=language,
    )


def _normalized_agent_order(config) -> list[str]:
    """Ordem de agentes deduplicada (mesma logica do agents_cmd)."""
    profile_ids = list(config.agents.profiles.keys())
    ordered_ids: list[str] = []
    for agent_id in config.agents.agent_order:
        if agent_id in config.agents.profiles and agent_id not in ordered_ids:
            ordered_ids.append(agent_id)
    for agent_id in profile_ids:
        if agent_id not in ordered_ids:
            ordered_ids.append(agent_id)
    return ordered_ids
