```markdown
# orbe Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill guides contributors through the development patterns, coding conventions, and key workflows of the **orbe** repository. The codebase is primarily JavaScript, with no major framework detected, and features a modular structure with a focus on maintainability, internationalization, and robust UI theming. Development follows conventional commit standards and emphasizes test coverage for all features and bugfixes.

---

## Coding Conventions

### File Naming

- Use **camelCase** for file names.
  - Example: `mainLayout.tsx`, `sidebarMenu.js`

### Import Style

- Use **alias imports** for modules.
  - Example:
    ```js
    import { Sidebar } from '@/layouts/Sidebar';
    ```

### Export Style

- Use **named exports**.
  - Example:
    ```js
    export function HomePage() { /* ... */ }
    export const SIDEBAR_WIDTH = 240;
    ```

### Commit Messages

- Use **conventional commit** prefixes: `feat`, `fix`, `docs`, `test`.
- Keep commit messages concise (average ~69 characters).
  - Example: `feat: add drag-resize to sidebar component`

---

## Workflows

### add-or-update-discovery-tool-or-feature

**Trigger:** When adding or updating a Discovery tool, session logic, or agent capability  
**Command:** `/new-discovery-tool`

1. Implement or update the feature in `src/qwenpaw/discovery/*.py` (e.g., `tools.py`, `agent.py`, `runner.py`, `prompts.py`, `taxonomy.py`).
2. Update or add supporting data files if needed (e.g., `segments/data/cnae_seed.json`).
3. Add or update tests in `tests/discovery/` (e.g., `test_tools.py`, `test_runner.py`, `test_taxonomy.py`).

**Example:**
```python
# src/qwenpaw/discovery/tools.py
def new_tool(...):
    pass

# tests/discovery/test_tools.py
def test_new_tool():
    assert new_tool(...) == ...
```

---

### add-or-update-i18n-ptbr-support

**Trigger:** When improving or adding Brazilian Portuguese (pt-BR) translations or content  
**Command:** `/add-ptbr-i18n`

1. Add or update pt-BR translation files (e.g., `console/src/locales/pt-BR.json`, `plugin.json`, `PROFILE.md`, `SOUL.md`, `SKILL.md`).
2. Add or update tests to verify pt-BR content (e.g., `tests/frontend/test_ptbr_locale.py`, `tests/plugins/test_plugin_ptbr.py`).
3. Optionally, add or update `scripts/check_ptbr.py` and its tests for automated verification.

**Example:**
```json
// console/src/locales/pt-BR.json
{
  "home.title": "Página Inicial",
  "sidebar.collapse": "Recolher"
}
```

---

### ui-theme-refactor-and-homepage

**Trigger:** When improving UI theming, migrating to design tokens, or updating the Home page  
**Command:** `/ui-theme-refactor`

1. Add or update CSS/LESS tokens (e.g., `aionui-tokens.less`, `aionui-tokens.css`, `layout.css`).
2. Refactor layout and component styles to use tokens instead of hardcoded colors.
3. Add or update Home page files (`console/src/pages/Home/index.tsx`, `index.module.less`).
4. Register Home route (`console/src/layouts/registry/builtinRoutes.tsx`).
5. Add or update i18n keys in all locale files.
6. Add or update tests for Home page or layout.

**Example:**
```less
// console/src/styles/aionui-tokens.less
@primary-color: #1a73e8;

// console/src/pages/Home/index.tsx
export function Home() {
  return <div className="home">Welcome!</div>;
}
```

---

### sidebar-and-layout-enhancement

**Trigger:** When enhancing sidebar or layout interactivity, appearance, or usability  
**Command:** `/enhance-sidebar`

1. Update `Sidebar.tsx` and `MainLayout/index.tsx` to add or improve features (collapse, drag-resize, search, overlays, etc.).
2. Update `index.module.less` and `aionui-tokens.less` for styling and tokens.
3. Update or add supporting CSS variables or classes.
4. Add or update tests if needed.

**Example:**
```js
// console/src/layouts/Sidebar.tsx
export function Sidebar({ collapsed }) {
  return <aside className={collapsed ? 'sidebar-collapsed' : 'sidebar'} />;
}
```

---

### bugfix-with-targeted-test

**Trigger:** When fixing a bug and ensuring it is covered by a test  
**Command:** `/bugfix-with-test`

1. Fix the bug in the relevant source file(s).
2. Add or update a test in the corresponding `tests/` directory to cover the fixed scenario.

**Example:**
```js
// src/qwenpaw/discovery/runner.py
def run_discovery(...):
    # fixed logic here

// tests/discovery/test_runner.py
def test_run_discovery_handles_edge_case():
    assert run_discovery(...) == expected
```

---

## Testing Patterns

- **Framework:** [vitest](https://vitest.dev/)
- **Test file pattern:** `*.test.tsx`
- **Location:** Tests are placed alongside or within a `tests/` directory corresponding to the module.
- **Test Example:**
  ```tsx
  // console/src/pages/Home/index.test.tsx
  import { render } from '@testing-library/react';
  import { Home } from './index';

  test('renders Home page', () => {
    const { getByText } = render(<Home />);
    expect(getByText('Welcome!')).toBeInTheDocument();
  });
  ```

---

## Commands

| Command              | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| /new-discovery-tool  | Add or update a Discovery tool, session, or agent feature with tests     |
| /add-ptbr-i18n       | Add or update Brazilian Portuguese (pt-BR) i18n support and tests        |
| /ui-theme-refactor   | Refactor UI theme tokens, layout, or Home page with i18n and dark mode   |
| /enhance-sidebar     | Enhance sidebar and layout features (collapse, drag, search, etc.)       |
| /bugfix-with-test    | Fix a bug and add or update a targeted test for regression coverage      |
```
