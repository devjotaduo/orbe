# Spec — Porte do memory-distill (#4171) para o fork QwenPaw

**Data:** 2026-06-12 · **Origem:** PR upstream [agentscope-ai/QwenPaw#4171](https://github.com/agentscope-ai/QwenPaw/pull/4171) (OPEN) · **Status:** aprovado para planejamento

## 1. Objetivo

Adicionar **destilação incremental de memória por title-diffing**: comparar os tópicos já conhecidos no `MEMORY.md` com os títulos das daily notes (`memory/YYYY-MM-DD.md`) e anexar **apenas o que é genuinamente novo**, sem re-summarização por LLM.

Complementa — não substitui — o `dream()`/ReMeLight existente. Ganhos: ~92% de redução de ruído (claim do PR) e **custo zero de tokens** (é diffing de texto, não chamada de modelo).

## 2. Contexto / por que encaixa sem atrito

- **Layout de memória idêntico ao alvo do PR:** o fork já usa `MEMORY.md` (raiz do workspace) + `memory/YYYY-MM-DD.md` (daily notes). Confirmado em `src/qwenpaw/agents/memory/prompts.py` e `adbpg_memory_manager.py` (`memory_search` já varre `MEMORY.md` e `memory/*.md`).
- **API de plugin já compatível:** `src/qwenpaw/plugins/api.py` (848 linhas) já expõe `register_tool`, `register_http_router`, `register_startup_hook`, `set_tool_config`, `get_tool_config`. As 185 linhas que o PR adicionava ao `api.py` upstream **já existem** (ou superset) no fork → **não tocar em `api.py`**.
- **Padrão de tool plugin já estabelecido:** `plugins/tool/` hospeda `gpt-image2`, `qwen-image`, `wan27`, cada um com `plugin.json` (com i18n incl. `pt-BR`) + backend `.py` + tool `.py` + `README.md` + `requirements.txt`.

## 3. Arquitetura — drop-in como tool plugin (espelha o upstream)

```
plugins/tool/memory-distill/
  plugin.json               # manifest no schema do fork, i18n zh/en/pt-BR, tools disabled por padrão
  memory_distill_plugin.py  # registro via api.register_tool(...)
  memory_distill_tool.py    # engine title-diffing (3 tools)
  README.md
src/qwenpaw/agents/skills/memory-distill-zh/SKILL.md
src/qwenpaw/agents/skills/memory-distill-en/SKILL.md
src/qwenpaw/agents/skills/memory-distill-pt/SKILL.md
tests/unit/plugins/test_memory_distill_tool.py
```

### Fluxo de dados (distill_memory)
1. Ler `MEMORY.md` da raiz do workspace → extrair tópicos conhecidos: marcadores `**bold**` + headers `###`.
2. Varrer daily notes dos últimos `days` dias em `<daily_memory_dir>/YYYY-MM-DD.md` → coletar títulos de seção `##`.
3. Filtrar ~15 títulos de template comuns (lista hardcoded do PR).
4. Diff: manter só títulos/descobertas **não** presentes nos tópicos conhecidos.
5. `dry_run=True` → retorna preview (não escreve). `dry_run=False` → anexa numa seção "Auto Discovery" do `MEMORY.md` (append incremental, sem reescrever o arquivo).

## 4. Componentes (3 tools, opt-in / `enabled=False` por padrão)

| Tool | Assinatura | Função |
|---|---|---|
| `distill_memory` | `(days=7, dry_run=True)` | Title-diffing; anexa só descobertas novas à seção "Auto Discovery". |
| `consolidate_memory` | `(days=15, dry_run=False)` | Pipeline: distill → arquivar logs antigos → limpar temporários → auditar saúde do MEMORY.md. |
| `inspect_memory` | `()` | Health check: tamanho do MEMORY.md, nº de tópicos, atividade recente. |

Cada tool retorna `agentscope.tool.ToolResponse`.

## 5. Decisões de design (usuário delegou)

1. **Drop-in puro** — não modificar `plugins/api.py`, `dream()`, ReMeLight nem ADB-PG. Mantém o porte conflito-free com merges futuros do upstream.
2. **Respeitar `daily_memory_dir` do config** (default `"memory"`) em vez de hardcodar `memory/`, casando com `AgentMdManager` (`agent_config.running.daily_memory_dir`).
3. **Skills em zh + en + pt-BR** — o upstream traz só zh/en; adiciona-se pt-BR por o fork ser pt-BR.
4. **Portar os testes unitários** do PR (`tests/unit/plugins/test_memory_distill_tool.py`) adaptando caminhos/fixtures ao fork.
5. **Path-safety**: reusar o padrão de sanitização já presente em `AgentMdManager` (`_sanitize_md_name`, `_assert_within_dir`) ao resolver caminhos de arquivos de memória.

## 6. Escopo / não-escopo

**Em escopo**
- Pasta `plugins/tool/memory-distill/` (plugin.json + plugin + tool + README) adaptada ao layout/config do fork.
- 3 skills (zh/en/pt) em `src/qwenpaw/agents/skills/`.
- Testes unitários portados.

**Fora de escopo**
- Qualquer alteração em `plugins/api.py`.
- Alterações em `dream()`, ReMeLight, ADB-PG ou no core de memória.
- UI nova no console (a tool aparece no toolkit do agente quando habilitada).
- Endpoint REST (`register_http_router`) — não necessário para esta feature.

## 7. Tratamento de erros

- `MEMORY.md` ausente → criar vazio / retornar preview vazio sem falhar.
- Diretório de daily notes ausente ou vazio → retornar "nada a destilar" (sucesso, lista vazia).
- `MEMORY.md` corrompido/encoding → usar `read_text_file_with_encoding_fallback` (já existe em `agents/utils/file_handling`).
- Escrita: `dry_run=False` só escreve após diff não-vazio; append atômico (escrever em temp + replace) para não corromper em caso de crash no meio.

## 8. Estratégia de testes

- Reusar/adaptar `tests/unit/plugins/test_memory_distill_tool.py` do PR.
- Cobrir: extração de tópicos (`**bold**` + `###`), filtragem de títulos de template, diff (só novos passam), `dry_run` não escreve, append incremental preserva conteúdo existente, casos de borda (arquivos ausentes/vazios), respeito ao `daily_memory_dir` do config.
- Rodar via pytest (atenção ao `PYTHONPATH` em worktree — venv aponta para o src principal).

## 9. Gate

Backend que importa AgentScope (`ToolResponse`) e adiciona arquivos em `src/qwenpaw/**` (skills) → **revisão obrigatória do agentscope-guardian** (KB em `docs/agentscope-v2/`) dentro do fluxo `/dev-team` (plan → code → review → test).

## 10. Critérios de aceite

- [ ] As 3 tools registram e aparecem no toolkit (disabled por padrão).
- [ ] `distill_memory(dry_run=True)` retorna preview correto sem escrever.
- [ ] `distill_memory(dry_run=False)` anexa só descobertas novas, sem reescrever o MEMORY.md existente.
- [ ] Respeita `daily_memory_dir` do config.
- [ ] Testes unitários passam no pytest.
- [ ] `plugins/api.py` e o core de memória ficam intocados.
- [ ] Guardião aprova (sem violação de API AgentScope).
