---
name: add-or-update-i18n-ptbr-support
description: Workflow command scaffold for add-or-update-i18n-ptbr-support in orbe.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-i18n-ptbr-support

Use this workflow when working on **add-or-update-i18n-ptbr-support** in `orbe`.

## Goal

Adds or updates Brazilian Portuguese (pt-BR) internationalization support for locales, plugins, agent profiles, or skills, with corresponding tests.

## Common Files

- `console/src/locales/pt-BR.json`
- `plugins/bundle/*/plugin.json`
- `plugins/bundle/*/agents/*/pt/PROFILE.md`
- `plugins/bundle/*/agents/*/pt/SOUL.md`
- `src/qwenpaw/agents/skills/*-pt/SKILL.md`
- `tests/frontend/test_ptbr_locale.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or update pt-BR translation files (console/src/locales/pt-BR.json, plugin.json, PROFILE.md, SOUL.md, SKILL.md, etc.)
- Add or update tests to verify pt-BR content (tests/frontend/test_ptbr_locale.py, tests/plugins/test_plugin_ptbr.py, tests/plugins/test_agent_pt_profiles.py, tests/skill_system/test_pt_skills_part1.py, test_pt_skills_part2.py, test_registry_pt.py)
- Optionally add or update scripts/check_ptbr.py and its tests for automated verification

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.