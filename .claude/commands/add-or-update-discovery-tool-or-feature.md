---
name: add-or-update-discovery-tool-or-feature
description: Workflow command scaffold for add-or-update-discovery-tool-or-feature in orbe.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-discovery-tool-or-feature

Use this workflow when working on **add-or-update-discovery-tool-or-feature** in `orbe`.

## Goal

Adds or updates a Discovery tool, session, or agent feature, and ensures it is covered by tests.

## Common Files

- `src/qwenpaw/discovery/tools.py`
- `src/qwenpaw/discovery/agent.py`
- `src/qwenpaw/discovery/runner.py`
- `src/qwenpaw/discovery/prompts.py`
- `src/qwenpaw/discovery/segments/taxonomy.py`
- `src/qwenpaw/discovery/segments/data/cnae_seed.json`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Implement or update feature in src/qwenpaw/discovery/*.py (tools.py, agent.py, runner.py, prompts.py, taxonomy.py, etc.)
- Update or add supporting data files if needed (e.g., segments/data/cnae_seed.json)
- Add or update tests in tests/discovery/ (test_tools.py, test_runner.py, test_taxonomy.py, etc.)

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.