# -*- coding: utf-8 -*-
"""Pareamento do WhatsApp do agente de atendimento direto no terminal.

Orquestra ``qwenpaw discovery pair``: resolve a sessao de discovery,
escolhe o agente de atendimento (client-facing) ja deployado, normaliza o
numero do empresario para E.164 e dispara o fluxo de pareamento por PIN
(helper puro em :mod:`qwenpaw.app.channels.whatsapp.pairing`).

Nenhuma API ``agentscope.*`` e usada aqui: tudo passa pela camada de
config/workspace do qwenpaw (``load_agent_config``) e pelo helper neonize.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .deploy import _is_client_facing, _load_deployed, load_blueprint

# E.164: '+' seguido de 5 a 15 digitos (primeiro nao-zero).
_E164_RE = re.compile(r"^\+[1-9]\d{4,14}$")
# Regiao default usada para normalizar numeros sem codigo de pais.
_DEFAULT_REGION = "BR"
# Timeout (s) aguardando a confirmacao do PIN no celular.
_PAIR_TIMEOUT_SECONDS = 120.0


class PairError(Exception):
    """Erro claro para o usuario (sessao/agente/numero invalidos)."""


@dataclass
class PairResult:
    """Resumo do pareamento para a CLI renderizar."""

    agent_name: str
    agent_id: str
    phone: str
    auth_dir: str
    connected: bool


# --- Resolucao da sessao ---------------------------------------------------


def resolve_session_dir(
    session_dir: Optional[str],
    session_id: Optional[str],
) -> Path:
    """Resolve o diretorio da sessao (SESSION_DIR XOR --session).

    Raises:
        PairError: se ambos ou nenhum forem informados.
    """
    if session_dir and session_id:
        raise PairError("Informe SESSION_DIR ou --session, nao ambos.")
    if session_dir:
        return Path(session_dir).expanduser()
    if session_id:
        return (Path("discovery") / session_id).expanduser()
    raise PairError(
        "Informe o diretorio da sessao (SESSION_DIR) ou --session <id>.",
    )


# --- Escolha do agente -----------------------------------------------------


def _choose_agent(
    session_dir: Path,
    agent_id: Optional[str],
) -> tuple[str, str]:
    """Escolhe o agente alvo do pareamento.

    Prioridade:
      1. ``--agent <id>`` (deve constar no deployed.json da sessao).
      2. Primeiro AgentSpec client-facing do blueprint que ja foi
         deployado (consta no deployed.json).

    Returns:
        (agent_name, agent_id).

    Raises:
        PairError: se nao houver agente pareavel.
    """
    deployed = _load_deployed(session_dir)
    if not deployed:
        raise PairError(
            "Nenhum agente deployado nesta sessao. "
            "Rode 'qwenpaw discovery deploy' primeiro.",
        )

    # name -> agent_id; precisamos do inverso para resolver --agent.
    by_id = {aid: name for name, aid in deployed.items()}

    if agent_id:
        if agent_id not in by_id:
            raise PairError(
                f"Agente '{agent_id}' nao foi deployado nesta sessao. "
                f"Deployados: {', '.join(sorted(by_id)) or '(nenhum)'}.",
            )
        return by_id[agent_id], agent_id

    blueprint = load_blueprint(session_dir)
    for spec in blueprint.proposed_team:
        if _is_client_facing(spec) and spec.name in deployed:
            return spec.name, deployed[spec.name]

    raise PairError(
        "Nenhum agente de atendimento (client-facing) deployado foi "
        "encontrado. Use --agent <id> para escolher um agente "
        "manualmente.",
    )


# --- Resolucao do numero ---------------------------------------------------


def _resolve_phone(
    session_dir: Path,
    phone: Optional[str],
) -> str:
    """Resolve o numero E.164 (--phone ou onboarding do blueprint).

    Raises:
        PairError: se o numero for invalido / nao puder ser normalizado.
    """
    if phone:
        candidate = phone.strip()
        if not _E164_RE.match(candidate):
            raise PairError(
                f"Numero '{phone}' invalido. Use o formato E.164, "
                "ex.: +5511987654321.",
            )
        return candidate

    blueprint = load_blueprint(session_dir)
    raw = (
        blueprint.onboarding.whatsapp_number if blueprint.onboarding else None
    )
    if not raw:
        raise PairError(
            "O blueprint nao tem um numero de WhatsApp de onboarding. "
            "Passe o numero com --phone +5511987654321.",
        )

    try:
        import phonenumbers

        parsed = phonenumbers.parse(raw, _DEFAULT_REGION)
        normalized = phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164,
        )
    except Exception:  # noqa: BLE001 - qualquer erro -> mensagem amigavel
        raise PairError(
            f"Nao consegui entender o numero '{raw}' do blueprint. "
            "Passe o numero com --phone +5511987654321.",
        )

    if not _E164_RE.match(normalized):
        raise PairError(
            f"O numero '{raw}' do blueprint nao virou um E.164 valido. "
            "Passe o numero com --phone +5511987654321.",
        )
    return normalized


# --- Resolucao do auth_dir -------------------------------------------------


def _resolve_auth_dir(agent_id: str) -> str:
    """Resolve o auth_dir do agente (mesma ordem de ``_get_wa_auth_dir``).

    Prioridade:
      1. ``channels.whatsapp.auth_dir`` explicito no agent config.
      2. ``<workspace_dir>/credentials/whatsapp/default`` (por agente).
      3. ``WORKING_DIR/credentials/whatsapp/default`` (fallback global).

    Raises:
        PairError: se o agente nao existir no config.
    """
    from ..config.config import load_agent_config
    from ..constant import WORKING_DIR

    try:
        cfg = load_agent_config(agent_id)
    except Exception as exc:  # noqa: BLE001 - superficie amigavel
        raise PairError(
            f"Nao consegui carregar a config do agente '{agent_id}': {exc}",
        ) from exc

    wa_cfg = getattr(cfg.channels, "whatsapp", None) if cfg.channels else None
    explicit = (getattr(wa_cfg, "auth_dir", "") if wa_cfg else "") or ""
    if explicit:
        return str(Path(explicit).expanduser())

    workspace = (cfg.workspace_dir or "").strip()
    if workspace:
        base = Path(workspace).expanduser()
        return str(base / "credentials" / "whatsapp" / "default")
    return str(WORKING_DIR / "credentials" / "whatsapp" / "default")


# --- Orquestracao ----------------------------------------------------------


def _print_pin(agent_name: str, phone: str, code: str) -> None:
    """Imprime o PIN em destaque + instrucoes em pt-BR no terminal."""
    print()
    print("=" * 52)
    print(f"  CODIGO DE PAREAMENTO: {code}")
    print("=" * 52)
    print()
    print(f"No celular do numero {phone}, abra o WhatsApp e:")
    print("  1. Toque em Configuracoes (ou os 3 pontinhos).")
    print("  2. Aparelhos conectados.")
    print("  3. Conectar um aparelho.")
    print("  4. Conectar com numero de telefone.")
    print(f"  5. Digite o codigo acima ({code}).")
    print()
    print(f"Aguardando a confirmacao no celular do agente {agent_name}...")
    print()


async def pair_discovery_whatsapp(
    session_dir: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    phone: Optional[str] = None,
    timeout: float = _PAIR_TIMEOUT_SECONDS,
) -> PairResult:
    """Pareia o WhatsApp do agente de atendimento da sessao via PIN.

    Args:
        session_dir: Diretorio da sessao (posicional). XOR com session_id.
        session_id: ID da sessao -> ./discovery/<id>. XOR com session_dir.
        agent_id: Agente alvo; default = 1o client-facing deployado.
        phone: Numero E.164; default = onboarding do blueprint (BR).
        timeout: Tempo maximo (s) aguardando a confirmacao no celular.

    Returns:
        PairResult com agente, numero e se conectou.

    Raises:
        PairError: sessao/agente/numero invalidos.
        PairingDependencyError: neonize nao instalado.
        PairingError: falha no fluxo neonize.
    """
    from ..app.channels.whatsapp.pairing import pair_by_code

    target = resolve_session_dir(session_dir, session_id)
    if not target.exists():
        raise PairError(f"Sessao nao encontrada em {target}.")

    agent_name, resolved_agent_id = _choose_agent(target, agent_id)
    resolved_phone = _resolve_phone(target, phone)
    auth_dir = _resolve_auth_dir(resolved_agent_id)

    def _on_pin(code: str) -> None:
        _print_pin(agent_name, resolved_phone, code)

    connected = await pair_by_code(
        auth_dir=auth_dir,
        phone=resolved_phone,
        on_pin=_on_pin,
        timeout=timeout,
    )
    return PairResult(
        agent_name=agent_name,
        agent_id=resolved_agent_id,
        phone=resolved_phone,
        auth_dir=auth_dir,
        connected=connected,
    )
