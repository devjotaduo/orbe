# -*- coding: utf-8 -*-
"""CLI do discovery agent — ``qwenpaw discovery start``."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

import click


@click.group("discovery")
def discovery_group():
    """Entrevista o empresario e gera o blueprint de um time de agentes."""


@discovery_group.command("start")
@click.option(
    "--out",
    "out_dir",
    default=None,
    help="Diretorio de saida (default: ./discovery/<session_id>).",
)
def discovery_start(out_dir: str | None) -> None:
    """Inicia uma entrevista de discovery no terminal."""
    from ..discovery import run_discovery_session

    session_id = uuid4().hex[:8]
    target = Path(out_dir) if out_dir else Path("discovery") / session_id
    click.echo(f"Sessao de discovery: {session_id} -> {target}")
    session = asyncio.run(
        run_discovery_session(session_id=session_id, out_dir=target)
    )
    if session.emitted:
        click.echo(f"\nBlueprint em {target / 'blueprint.md'}")
    else:
        click.echo("\nEncerrado sem blueprint (estado salvo).")


@discovery_group.command("deploy")
@click.argument("session_dir", required=False, default=None)
@click.option(
    "--session",
    "session_id",
    default=None,
    help="ID da sessao (resolve para ./discovery/<id>).",
)
def discovery_deploy(session_dir: str | None, session_id: str | None) -> None:
    """Cria agentes qwenpaw reais a partir do blueprint da sessao."""
    from ..discovery import DeployError, deploy_session

    if session_dir and session_id:
        raise click.UsageError(
            "Informe SESSION_DIR ou --session, nao ambos.",
        )
    if session_dir:
        target = Path(session_dir)
    elif session_id:
        target = Path("discovery") / session_id
    else:
        raise click.UsageError(
            "Informe o diretorio da sessao (SESSION_DIR) ou --session <id>.",
        )

    try:
        result = deploy_session(target)
    except DeployError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Deploy da sessao: {result.session_dir}")
    if result.created:
        click.echo(f"\nAgentes criados ({len(result.created)}):")
        for ag in result.created:
            wa = " [WhatsApp]" if ag.whatsapp_enabled else ""
            click.echo(f"  - {ag.name} -> {ag.agent_id}{wa}")
            click.echo(f"      workspace: {ag.workspace_dir}")
    if result.skipped:
        click.echo(f"\nJa existentes (pulados) ({len(result.skipped)}):")
        for ag in result.skipped:
            click.echo(f"  - {ag.name} -> {ag.agent_id}")

    if result.pending_tools:
        click.echo("\nPendencias de ferramentas/conectores:")
        for item in result.pending_tools:
            click.echo(f"  - {item}")
    if result.pending_talks_to:
        click.echo("\nPendencias de comunicacao entre agentes:")
        for item in result.pending_talks_to:
            click.echo(f"  - {item}")

    has_whatsapp = any(ag.whatsapp_enabled for ag in result.created)
    if has_whatsapp:
        num = result.whatsapp_number or "(numero oficial da empresa)"
        click.echo("\nProximos passos manuais (WhatsApp):")
        click.echo(
            "  1. Abra o Console e selecione o agente de atendimento.\n"
            "  2. Va em Canais > WhatsApp e inicie o pareamento "
            "(QR/codigo).\n"
            f"  3. Use o numero {num} no aparelho que vai parear.",
        )
