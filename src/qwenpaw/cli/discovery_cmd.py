# -*- coding: utf-8 -*-
"""CLI do discovery agent — ``qwenpaw discovery start``."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

import click


@click.group("discovery")
def discovery_group() -> None:
    """Entrevista o empresário e gera o blueprint de um time de agentes."""


@discovery_group.command("start")
@click.option(
    "--out",
    "out_dir",
    default=None,
    help="Diretório de saída (default: ./discovery/<session_id>).",
)
def discovery_start(out_dir: str | None) -> None:
    """Inicia uma entrevista de discovery no terminal."""
    from ..discovery import run_discovery_cli, run_discovery_session

    if out_dir:
        # Override explícito: grava direto no diretório informado.
        session_id = uuid4().hex[:8]
        target = Path(out_dir)
        click.echo(f"Sessão de discovery: {session_id} -> {target}")
        session = asyncio.run(
            run_discovery_session(session_id=session_id, out_dir=target),
        )
    else:
        # Caminho padrão: delega ao wrapper, que monta
        # ./discovery/<session_id>.
        click.echo("Sessão de discovery -> ./discovery/<id>")
        session = asyncio.run(run_discovery_cli())

    if session.emitted:
        click.echo(
            f"\nBlueprint em {session.out_dir / 'blueprint.md'}",
        )
    else:
        click.echo("\nEncerrado sem blueprint (estado salvo).")
