# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MD_FILES_DIR = REPO_ROOT / "src" / "qwenpaw" / "agents" / "md_files"
PT_FILES = [
    MD_FILES_DIR / "pt" / "PROFILE.md",
    MD_FILES_DIR / "pt" / "SOUL.md",
    MD_FILES_DIR / "local" / "pt" / "SOUL.md",
    MD_FILES_DIR / "qa" / "pt" / "PROFILE.md",
    MD_FILES_DIR / "qa" / "pt" / "SOUL.md",
]

PARITY_DIRS = [
    (MD_FILES_DIR / "en", MD_FILES_DIR / "pt"),
    (MD_FILES_DIR / "qa" / "en", MD_FILES_DIR / "qa" / "pt"),
    (MD_FILES_DIR / "local" / "en", MD_FILES_DIR / "local" / "pt"),
]


def _md_names(directory: Path) -> set[str]:
    return {p.name for p in directory.glob("*.md")}


def test_pt_md_files_exist():
    for p in PT_FILES:
        assert p.exists(), f"Faltando: {p}"


def test_pt_md_files_not_empty():
    for p in PT_FILES:
        content = p.read_text(encoding="utf-8")
        assert len(content) > 100, f"{p} parece vazio"


@pytest.mark.parametrize(
    "en_dir, pt_dir",
    PARITY_DIRS,
    ids=lambda d: str(d.relative_to(MD_FILES_DIR)),
)
def test_pt_md_files_match_en_structure(en_dir: Path, pt_dir: Path):
    """pt/ deve ter exatamente os mesmos arquivos *.md que en/."""
    en_names = _md_names(en_dir)
    pt_names = _md_names(pt_dir)
    assert en_names, f"Nenhum *.md em {en_dir} (caminho errado?)"
    missing = en_names - pt_names
    extra = pt_names - en_names
    assert not missing, f"Faltando em {pt_dir}: {sorted(missing)}"
    assert not extra, f"Sobrando em {pt_dir} (sem original en): {sorted(extra)}"


@pytest.mark.parametrize(
    "en_dir, pt_dir",
    PARITY_DIRS,
    ids=lambda d: str(d.relative_to(MD_FILES_DIR)),
)
def test_pt_md_files_parity_not_empty(en_dir: Path, pt_dir: Path):
    """Todos os *.md de pt/ devem ter conteúdo real, não placeholder."""
    for name in _md_names(en_dir):
        pt_file = pt_dir / name
        if pt_file.exists():
            content = pt_file.read_text(encoding="utf-8")
            assert len(content) > 100, f"{pt_file} parece vazio"
