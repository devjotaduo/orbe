---
name: memory-distill
description: Use esta skill para destilação incremental e consolidação de memória. Use quando o usuário pedir "destilar memória", "consolidar notas", "limpar o MEMORY.md", "encontrar descobertas novas nas daily notes" ou para manutenção periódica de memória. Usa title-diffing (custo zero de tokens) para detectar informação genuinamente nova nas daily notes e anexá-la ao MEMORY.md. NÃO use para busca simples de memória (use memory_search) nem para escrever uma nota diretamente.
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "🧠"
---

# Destilação de Memória

## Quando usar

- O usuário pede para "destilar", "consolidar" ou "limpar" a memória
- O agente detecta informação duplicada entre MEMORY.md e daily notes
- Manutenção periódica (a cada 7–15 dias)
- Verificação rápida do estado da memória

## Quando NÃO usar

- Apenas buscar memória existente → use `memory_search`
- Registrar uma nota diretamente → atualize MEMORY.md ou a daily note diretamente
- Re-sumarização completa via LLM → esta tool faz diffing de texto, não sumarização

## Ferramentas

| Função | Para quê | Args comuns |
|:---|:---|---:|
| `distill_memory()` | Title-diffing: varre daily notes, acha o que é novo | `days=7`, `dry_run=True` |
| `consolidate_memory()` | Pipeline completo: distill → arquivar → limpar → auditar | `days=15`, `dry_run=True` |
| `inspect_memory()` | Health check rápido | — |

## Fluxo

1. `await inspect_memory()` — checar estado atual
2. `await distill_memory(days=7, dry_run=True)` — sempre preview primeiro
3. `await distill_memory(days=7, dry_run=False)` — aplicar se o preview estiver correto
4. `await consolidate_memory(days=15, dry_run=False)` — pipeline completo a cada ~15 dias

## Algoritmo

1. Extrair **tópicos conhecidos** do MEMORY.md: marcadores `**negrito**` e headers `###`
2. Varrer títulos `##` das daily notes (`memory/YYYY-MM-DD.md`)
3. Filtrar 15+ títulos de template comuns ("Daily", "Tasks", "Todo" etc.)
4. Anexar apenas descobertas novas numa seção `🔄 Auto Discovery`
5. Escrita atômica (arquivo temp + replace) — não corrompe MEMORY.md em caso de crash

## Notas

- Sempre comece com `dry_run=True`
- Daily notes nunca são apagadas (apenas arquivadas pelo `consolidate_memory`)
- Custo zero de tokens — diffing puro de texto/títulos
- ~92% menos redundância em relação a re-sumarização completa via LLM
