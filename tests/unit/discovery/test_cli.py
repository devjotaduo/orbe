# -*- coding: utf-8 -*-
"""CLI ``qwenpaw discovery start`` (Task 7) com o runner mockado.

Verifica que o comando está registrado no grupo principal e que ``start``
delega corretamente: com ``--out`` chama ``run_discovery_session`` no
diretório informado; sem ``--out`` chama ``run_discovery_cli``. O loop real
(LLM/terminal) é substituído por stubs — nenhum LLM nem ``input`` é tocado.
"""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from qwenpaw.cli import discovery_cmd


class _FakeSession:
    def __init__(self, emitted: bool, out_dir: Path) -> None:
        self.emitted = emitted
        self.out_dir = out_dir


def test_discovery_registered_in_main_cli():
    from qwenpaw.cli.main import cli

    # O grupo principal expõe o subcomando ``discovery``.
    assert "discovery" in cli.list_commands(ctx=None)
    cmd = cli.get_command(None, "discovery")
    assert cmd is not None
    assert "start" in cmd.commands


def test_discovery_start_with_out_calls_run_session(tmp_path):
    target = tmp_path / "bp"
    fake = _FakeSession(emitted=True, out_dir=target)
    seen = {}

    async def _fake_run_session(session_id, out_dir):
        seen["out_dir"] = Path(out_dir)
        return fake

    async def _should_not_run():
        raise AssertionError("run_discovery_cli não deveria ser usado")

    # ``run_discovery_session`` é importado de forma tardia (dentro do
    # comando) a partir de ``qwenpaw.discovery``; é lá que se faz o patch.
    runner = CliRunner()
    with patch(
        "qwenpaw.discovery.run_discovery_session",
        _fake_run_session,
    ):
        with patch("qwenpaw.discovery.run_discovery_cli", _should_not_run):
            result = runner.invoke(
                discovery_cmd.discovery_group,
                ["start", "--out", str(target)],
            )

    assert result.exit_code == 0, result.output
    assert seen["out_dir"] == target
    assert "blueprint.md" in result.output


def test_discovery_start_without_out_calls_run_cli(tmp_path):
    out_dir = tmp_path / "discovery" / "abcd1234"
    fake = _FakeSession(emitted=True, out_dir=out_dir)

    async def _fake_run_cli():
        return fake

    async def _should_not_run(session_id, out_dir):
        raise AssertionError("run_discovery_session não deveria ser usado")

    runner = CliRunner()
    with patch("qwenpaw.discovery.run_discovery_cli", _fake_run_cli):
        with patch(
            "qwenpaw.discovery.run_discovery_session",
            _should_not_run,
        ):
            result = runner.invoke(
                discovery_cmd.discovery_group,
                ["start"],
            )

    assert result.exit_code == 0, result.output
    assert "blueprint.md" in result.output


def test_discovery_start_without_blueprint_reports_no_blueprint(tmp_path):
    out_dir = tmp_path / "discovery" / "deadbeef"
    fake = _FakeSession(emitted=False, out_dir=out_dir)

    async def _fake_run_cli():
        return fake

    runner = CliRunner()
    with patch("qwenpaw.discovery.run_discovery_cli", _fake_run_cli):
        result = runner.invoke(discovery_cmd.discovery_group, ["start"])

    assert result.exit_code == 0, result.output
    assert "sem blueprint" in result.output.lower()
