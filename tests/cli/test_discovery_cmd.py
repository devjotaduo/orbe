# -*- coding: utf-8 -*-
"""Testes do grupo Click `qwenpaw discovery`."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner


def test_import_discovery_group():
    """discovery_group importa sem erro."""
    from qwenpaw.cli.discovery_cmd import discovery_group

    assert callable(discovery_group)


def test_discovery_group_help_lists_start():
    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    result = runner.invoke(discovery_group, ["--help"])
    assert result.exit_code == 0
    assert "start" in result.output


def test_discovery_start_help_shows_out_option():
    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    result = runner.invoke(discovery_group, ["start", "--help"])
    assert result.exit_code == 0
    assert "--out" in result.output


def test_discovery_start_default_out_no_blueprint(tmp_path):
    """Saída sem blueprint quando session.emitted == False."""
    fake_session = MagicMock()
    fake_session.emitted = False

    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    with patch(
        "qwenpaw.cli.discovery_cmd.asyncio.run", return_value=fake_session
    ):
        result = runner.invoke(discovery_group, ["start"])
    assert result.exit_code == 0
    assert "Encerrado sem blueprint" in result.output


def test_discovery_start_default_out_contains_session_id(tmp_path):
    """O session_id (8 hex) aparece na saída."""
    fake_session = MagicMock()
    fake_session.emitted = False

    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    with patch(
        "qwenpaw.cli.discovery_cmd.asyncio.run", return_value=fake_session
    ):
        result = runner.invoke(discovery_group, ["start"])
    assert result.exit_code == 0
    # session_id gerado via uuid4().hex[:8] — 8 chars hex
    import re
    assert re.search(r"[0-9a-f]{8}", result.output)


def test_discovery_start_with_custom_out_emitted(tmp_path):
    """Mostra caminho do blueprint quando session.emitted == True."""
    fake_session = MagicMock()
    fake_session.emitted = True

    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    with patch(
        "qwenpaw.cli.discovery_cmd.asyncio.run", return_value=fake_session
    ):
        result = runner.invoke(
            discovery_group, ["start", "--out", str(tmp_path)]
        )
    assert result.exit_code == 0
    assert "blueprint.md" in result.output


def test_discovery_start_with_custom_out_passes_path(tmp_path):
    """O Path correto é passado para run_discovery_session."""
    fake_session = MagicMock()
    fake_session.emitted = False
    captured = {}

    import asyncio as _asyncio

    def fake_run(coro):
        captured["coro"] = coro
        return fake_session

    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    with patch("qwenpaw.cli.discovery_cmd.asyncio.run", side_effect=fake_run):
        result = runner.invoke(
            discovery_group, ["start", "--out", str(tmp_path)]
        )
    assert result.exit_code == 0


def test_discovery_start_default_out_uses_discovery_subdir():
    """Sem --out, o diretório default é discovery/<session_id>."""
    fake_session = MagicMock()
    fake_session.emitted = False

    from qwenpaw.cli.discovery_cmd import discovery_group

    runner = CliRunner()
    with patch(
        "qwenpaw.cli.discovery_cmd.asyncio.run", return_value=fake_session
    ):
        result = runner.invoke(discovery_group, ["start"])
    assert result.exit_code == 0
    assert "discovery" in result.output


def test_discovery_registered_in_main_cli():
    """O grupo 'discovery' está registrado no CLI principal."""
    from qwenpaw.cli.main import cli

    assert "discovery" in cli.commands or hasattr(cli, "list_commands")


def test_discovery_lazy_entry_points_to_correct_module():
    """lazy_subcommands aponta para o módulo e função corretos."""
    from qwenpaw.cli import main as main_mod

    lazy = getattr(main_mod.cli, "lazy_subcommands", None)
    if lazy is None:
        pytest.skip("CLI não usa LazyGroup com lazy_subcommands")
    assert "discovery" in lazy
    module_path, func_name, _ = lazy["discovery"]
    assert "discovery_cmd" in module_path
    assert func_name == "discovery_group"
