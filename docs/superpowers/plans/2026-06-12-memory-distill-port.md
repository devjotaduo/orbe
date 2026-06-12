# Memory-Distill Port — Implementation Plan

> **For agentic workers:** Este plano é a entrada do fluxo `/dev-team` (plan → code → review → test). Backend que importa AgentScope → passa pelo gate **agentscope-guardian**. Steps usam checkbox (`- [ ]`).

**Goal:** Portar o tool plugin `memory-distill` (PR upstream agentscope-ai/QwenPaw#4171) para o fork, como drop-in conflito-free, adaptado ao nosso layout/config.

**Architecture:** Tool plugin em `plugins/tool/memory-distill/` (3 tools opt-in: `distill_memory`, `consolidate_memory`, `inspect_memory`) que faz title-diffing entre `MEMORY.md` e daily notes `memory/YYYY-MM-DD.md`, sem LLM. Sem alterar `plugins/api.py` (já compatível) nem o core de memória.

**Tech Stack:** Python, `agentscope.tool.ToolResponse`/`TextBlock`, `qwenpaw.plugins.api.PluginApi`, pytest (`pytest-asyncio`).

**Fonte canônica:** PR #4171 — buscar o conteúdo verbatim com:
`gh pr diff 4171 --repo agentscope-ai/QwenPaw`
Arquivos do PR: `plugins/tool/memory-distill/{plugin.json,memory_distill_plugin.py,memory_distill_tool.py,README.md}`, `src/qwenpaw/agents/skills/memory-distill-{en,zh}/SKILL.md`, `tests/unit/plugins/test_memory_distill_tool.py`. **NÃO** portar o hunk de `src/qwenpaw/plugins/api.py` (já presente no fork).

---

## File Structure

| Arquivo | Responsabilidade | Ação |
|---|---|---|
| `plugins/tool/memory-distill/plugin.json` | Manifest (tools, config_fields, i18n) | Criar |
| `plugins/tool/memory-distill/memory_distill_plugin.py` | Registro via `api.register_tool` | Criar |
| `plugins/tool/memory-distill/memory_distill_tool.py` | Engine title-diffing (3 tools + helpers) | Criar (port + 1 adaptação) |
| `plugins/tool/memory-distill/README.md` | Doc do plugin | Criar (port) |
| `src/qwenpaw/agents/skills/memory-distill-en/SKILL.md` | Skill EN | Criar (port) |
| `src/qwenpaw/agents/skills/memory-distill-zh/SKILL.md` | Skill ZH | Criar (port) |
| `src/qwenpaw/agents/skills/memory-distill-pt/SKILL.md` | Skill pt-BR | Criar (tradução) |
| `tests/unit/plugins/test_memory_distill_tool.py` | Testes unitários | Criar (port) |

**Intocados:** `src/qwenpaw/plugins/api.py`, `agents/memory/*` (dream/ReMe/ADB-PG).

---

## Task 1: Scaffold do plugin (manifest + registro + README)

**Files:**
- Create: `plugins/tool/memory-distill/plugin.json`
- Create: `plugins/tool/memory-distill/memory_distill_plugin.py`
- Create: `plugins/tool/memory-distill/README.md`

- [ ] **Step 1: Criar `plugin.json`** — base do PR #4171, adicionando i18n pt-BR (padrão dos plugins existentes do fork, ex. `plugins/tool/qwen-image/plugin.json`):

```json
{
  "id": "memory-distill-tool",
  "name": "Memory Distillation Tool",
  "version": "1.0.0",
  "description": "Advanced memory consolidation for agent daily notes. Features title-diffing distillation (~92% noise reduction), incremental MEMORY.md updates, and three-tier memory classification.",
  "description_i18n": {
    "zh-CN": "智能记忆蒸馏工具：基于标题差分检测每日笔记中的新信息（约 92% 降噪），增量更新 MEMORY.md。",
    "en-US": "Smart memory distillation: title-diffing to detect new info in daily notes (~92% noise reduction), incremental MEMORY.md updates.",
    "pt-BR": "Destilação inteligente de memória: title-diffing para detectar informação nova nas daily notes (~92% menos ruído), atualização incremental do MEMORY.md."
  },
  "author": "QwenPaw Community",
  "entry": { "backend": "memory_distill_plugin.py" },
  "dependencies": [],
  "min_version": "1.1.6",
  "meta": {
    "tools": [
      { "name": "distill_memory", "description": "Distill daily notes into MEMORY.md using title-diffing to find genuinely new information.", "icon": "🧠" },
      { "name": "consolidate_memory", "description": "Run the full memory consolidation pipeline: distill, archive, clean, and audit.", "icon": "🧠" },
      { "name": "inspect_memory", "description": "Inspect MEMORY.md and daily notes health, size, and recent activity.", "icon": "🔍" }
    ],
    "requires_config": false,
    "config_fields": [
      { "name": "working_dir", "label": "Working Directory", "type": "text", "required": false, "placeholder": "agent working directory", "help": "Override agent working directory (leave empty to use default)" },
      { "name": "default_days", "label": "Default Lookback Days", "type": "number", "required": false, "placeholder": "15", "min": 1, "max": 90, "help": "Default number of days to scan for consolidation (default: 15)" }
    ]
  }
}
```

- [ ] **Step 2: Criar `memory_distill_plugin.py`** (verbatim do PR — usa `api.register_tool`, que já existe no fork; tools `enabled=False`):

```python
# -*- coding: utf-8 -*-
"""Memory Distillation Tool Plugin Entry Point."""

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)


class MemoryDistillToolPlugin:
    """Memory Distillation Tool Plugin."""

    def register(self, api: PluginApi):
        """Register memory distillation tools via PluginApi."""
        logger.info("Registering Memory Distillation tools...")

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        tool_path = os.path.join(plugin_dir, "memory_distill_tool.py")
        spec = importlib.util.spec_from_file_location(
            "memory_distill_tool", tool_path,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                f"Failed to load memory distill tool module from {tool_path}",
            )
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)

        api.register_tool(
            "distill_memory", tool_module.distill_memory,
            description="Distill daily notes into MEMORY.md using title-diffing to find genuinely new information.",
            icon="🧠", enabled=False,
        )
        api.register_tool(
            "consolidate_memory", tool_module.consolidate_memory,
            description="Run the full memory consolidation pipeline: distill, archive, clean, and audit.",
            icon="🧠", enabled=False,
        )
        api.register_tool(
            "inspect_memory", tool_module.inspect_memory,
            description="Inspect MEMORY.md and daily notes health, size, and recent activity.",
            icon="🔍", enabled=False,
        )
        logger.info("✓ Memory Distillation tool plugin registered")
```

- [ ] **Step 3: Criar `README.md`** — portar verbatim de `gh pr diff 4171` (arquivo `plugins/tool/memory-distill/README.md`). Sem adaptação.

- [ ] **Step 4: Commit**

```bash
git add plugins/tool/memory-distill/plugin.json plugins/tool/memory-distill/memory_distill_plugin.py plugins/tool/memory-distill/README.md
git commit -m "feat(memory-distill): scaffold do tool plugin (manifest+registro+readme) — porte #4171"
```

---

## Task 2: Engine `memory_distill_tool.py` (port + adaptação do diretório de daily notes)

**Files:**
- Create: `plugins/tool/memory-distill/memory_distill_tool.py`

Portar verbatim do PR (557 linhas: constantes `_KNOWN_TEMPLATE_TITLES`, `_SAFE_DIRS`; helpers `_resolve_working_dir`, `_read_file`, `_known_topics_in_memory`, `_daily_note_titles`, `_classify_and_format`; tools `distill_memory`, `consolidate_memory`, `inspect_memory`). Imports usam `from agentscope.tool import ToolResponse` e `from agentscope.message import TextBlock` (confirmar nomes exatos no diff).

**Única adaptação funcional:** o PR hardcoda o subdiretório de daily notes como `wd / "memory"` em 3 lugares (`_resolve_working_dir`, `distill_memory`, `consolidate_memory`/`inspect_memory`). Substituir por um diretório resolvido do config do agente, com fallback `"memory"` (mantém os testes verdes, pois o default é `"memory"`).

- [ ] **Step 1: Portar o arquivo verbatim** de `gh pr diff 4171` (`plugins/tool/memory-distill/memory_distill_tool.py`), removendo o prefixo `+` do diff.

- [ ] **Step 2: Adicionar helper de resolução do daily dir** (logo após `_resolve_working_dir`):

```python
def _resolve_daily_dir_name() -> str:
    """Resolve the daily-notes subdir name from the current agent config.

    Falls back to ``"memory"`` (the upstream default and the value used by
    ``AgentMdManager``) when no agent context/config is available.
    """
    try:
        from qwenpaw.app.agent_context import get_current_agent_id
        from qwenpaw.config.config import load_agent_config

        agent_id = get_current_agent_id()
        if agent_id:
            cfg = load_agent_config(agent_id)
            name = getattr(cfg.running, "daily_memory_dir", None)
            if name:
                return str(name)
    except Exception:  # pragma: no cover - best-effort, never block the tool
        pass
    return "memory"
```

- [ ] **Step 3: Trocar os usos hardcoded** `wd / "memory"` por `wd / _resolve_daily_dir_name()` em `_resolve_working_dir` (checagem de existência do workspace), `distill_memory` (`memory_dir = wd / ...`) e `consolidate_memory`/`inspect_memory` (onde varrem daily notes). Manter `_SAFE_DIRS` contendo `"memory"` E o nome resolvido (adicionar dinamicamente ao set de proteção contra exclusão).

- [ ] **Step 4: Validar import/sintaxe**

Run: `python -c "import importlib.util,pathlib; p=pathlib.Path('plugins/tool/memory-distill/memory_distill_tool.py'); s=importlib.util.spec_from_file_location('m',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(sorted(f for f in dir(m) if not f.startswith('__')))"`
Expected: lista contendo `distill_memory`, `consolidate_memory`, `inspect_memory`, `_resolve_daily_dir_name`.

- [ ] **Step 5: Commit**

```bash
git add plugins/tool/memory-distill/memory_distill_tool.py
git commit -m "feat(memory-distill): engine title-diffing + respeito a daily_memory_dir do config"
```

---

## Task 3: Testes unitários (port + caso da adaptação)

**Files:**
- Create: `tests/unit/plugins/test_memory_distill_tool.py`

- [ ] **Step 1: Portar o teste verbatim do PR** (3 casos: rejeita dir não-workspace; detecta títulos novos ignorando conhecidos; consolidate não apaga `.png` do workspace):

```python
# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "plugins" / "tool" / "memory-distill" / "memory_distill_tool.py"
)
SPEC = importlib.util.spec_from_file_location("memory_distill_tool", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
memory_distill_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory_distill_tool)


@pytest.mark.asyncio
async def test_distill_memory_rejects_non_workspace_dir(tmp_path):
    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path), days=7, dry_run=True,
    )
    block = result.content[0]
    text = block["text"] if isinstance(block, dict) else block.text
    assert "agent workspace" in text


@pytest.mark.asyncio
async def test_distill_memory_detects_new_titles_when_known_topics_exist(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "MEMORY.md").write_text(
        "# MEMORY\n\n- **Known Topic**: existing note\n", encoding="utf-8",
    )
    (tmp_path / "memory" / "2026-06-03.md").write_text(
        "# Daily\n\n## New Discovery\nFresh content here.\n\n"
        "## Known Topic\nShould be skipped.\n", encoding="utf-8",
    )
    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path), days=30, dry_run=True,
    )
    block = result.content[0]
    text = block["text"] if isinstance(block, dict) else block.text
    assert "New Discovery" in text
    assert "Known Topic" not in text


@pytest.mark.asyncio
async def test_consolidate_memory_does_not_delete_workspace_png(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "MEMORY.md").write_text("# MEMORY\n", encoding="utf-8")
    (tmp_path / "tool_results").mkdir()
    png = tmp_path / "keep.png"
    png.write_bytes(b"png")
    await memory_distill_tool.consolidate_memory(
        working_dir=str(tmp_path), days=30, dry_run=False,
    )
    assert png.exists()
```

- [ ] **Step 2: Adicionar teste do dry_run não-escrita** (cobre critério de aceite):

```python
@pytest.mark.asyncio
async def test_distill_memory_dry_run_does_not_write(tmp_path):
    (tmp_path / "memory").mkdir()
    mem = tmp_path / "MEMORY.md"
    mem.write_text("# MEMORY\n", encoding="utf-8")
    (tmp_path / "memory" / "2026-06-03.md").write_text(
        "# Daily\n\n## Brand New Thing\nstuff\n", encoding="utf-8",
    )
    before = mem.read_text(encoding="utf-8")
    await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path), days=30, dry_run=True,
    )
    assert mem.read_text(encoding="utf-8") == before
```

- [ ] **Step 3: Rodar os testes**

Run (atenção ao PYTHONPATH em worktree — venv aponta para o src principal; usar o src deste worktree):
`PYTHONPATH=src python -m pytest tests/unit/plugins/test_memory_distill_tool.py -v`
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/plugins/test_memory_distill_tool.py
git commit -m "test(memory-distill): porte dos testes do #4171 + caso dry_run não escreve"
```

---

## Task 4: Skills (en/zh portadas + pt-BR nova)

**Files:**
- Create: `src/qwenpaw/agents/skills/memory-distill-en/SKILL.md`
- Create: `src/qwenpaw/agents/skills/memory-distill-zh/SKILL.md`
- Create: `src/qwenpaw/agents/skills/memory-distill-pt/SKILL.md`

- [ ] **Step 1: Portar SKILL.md en e zh verbatim** de `gh pr diff 4171`.

- [ ] **Step 2: Criar SKILL.md pt-BR** (tradução fiel do en, mesmo front-matter `name: memory-distill`, `emoji: 🧠`):

```markdown
---
name: memory-distill
description: Ferramenta de destilação inteligente de memória. Usa title-diffing para detectar informação genuinamente nova nas daily notes (~92% menos ruído) e anexa incrementalmente ao MEMORY.md. Ideal para consolidação periódica de memória.
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "🧠"
---

# Destilação de Memória

## Quando usar
- O agente detecta informação duplicada entre MEMORY.md e daily notes
- O usuário pede "consolidar memória" ou "destilar notas"
- Manutenção periódica (a cada 7–15 dias)
- Checagem rápida de saúde da memória

## Quando NÃO usar
- Só buscar memória existente → use `memory_search`
- Só registrar uma informação → atualize MEMORY.md/daily note direto

## Ferramentas
| Função | Para quê | Args comuns |
|:---|:---|---:|
| `distill_memory()` | Title-diffing: varre daily notes, acha o que é novo | `days=7`, `dry_run=True` |
| `consolidate_memory()` | Pipeline completo: distill → arquivar → limpar → auditar | `days=15`, `dry_run=True` |
| `inspect_memory()` | Health check rápido | — |

## Fluxo
1. `await inspect_memory()`
2. `await distill_memory(days=7, dry_run=True)` (sempre preview primeiro)
3. `await distill_memory(days=7, dry_run=False)`
4. `await consolidate_memory(days=15, dry_run=False)` (a cada 15 dias)

## Algoritmo
1. Title-diffing: extrai `**palavras em negrito**` e headers `###` do MEMORY.md como "tópicos conhecidos", compara com os títulos `##` das daily notes
2. Filtra 15+ títulos de template comuns
3. Anexa descobertas novas a uma seção `🔄 Auto Discovery`, sem reescrever o MEMORY.md
4. ~92% menos redundância que abordagens puramente via LLM

## Notas
- Sempre comece com `dry_run=True`
- Daily notes nunca são apagadas (só anexa seletivamente ao MEMORY.md)
- `consolidate_memory` arquiva logs antigos em `archive/`
```

- [ ] **Step 3: Commit**

```bash
git add src/qwenpaw/agents/skills/memory-distill-en src/qwenpaw/agents/skills/memory-distill-zh src/qwenpaw/agents/skills/memory-distill-pt
git commit -m "feat(memory-distill): skills en/zh (porte) + pt-BR"
```

---

## Task 5: Verificação de integração + gate do guardião

- [ ] **Step 1: Confirmar que `api.py` ficou intocado**

Run: `git diff --name-only origin/main...HEAD -- src/qwenpaw/plugins/api.py`
Expected: saída vazia (nenhuma mudança em api.py).

- [ ] **Step 2: Rodar a suíte de testes de plugins**

Run: `PYTHONPATH=src python -m pytest tests/unit/plugins/ -v`
Expected: todos passam (incl. os 4 novos).

- [ ] **Step 3: Lint/pre-commit nos arquivos novos** (pylint/mypy conforme config do projeto)

Run: `pre-commit run --files plugins/tool/memory-distill/*.py tests/unit/plugins/test_memory_distill_tool.py`
Expected: passa (atenção a falso-positivo pylint E1102 conhecido — ver memória de gotchas pre-commit).

- [ ] **Step 4: Revisão do agentscope-guardian** — confirmar que o uso de `ToolResponse`/`TextBlock`/`PluginApi` segue a API correta (KB `docs/agentscope-v2/`). Sem violação → aprovado.

---

## Critérios de aceite (do spec)
- [ ] As 3 tools registram e aparecem no toolkit (disabled por padrão).
- [ ] `distill_memory(dry_run=True)` retorna preview sem escrever (teste Task 3 Step 2).
- [ ] `distill_memory(dry_run=False)` anexa só descobertas novas, sem reescrever (teste Task 3).
- [ ] Respeita `daily_memory_dir` do config (helper Task 2).
- [ ] Testes unitários passam (Task 3/5).
- [ ] `plugins/api.py` e core de memória intocados (Task 5 Step 1).
- [ ] Guardião aprova (Task 5 Step 4).
