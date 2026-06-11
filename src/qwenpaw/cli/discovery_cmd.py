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
