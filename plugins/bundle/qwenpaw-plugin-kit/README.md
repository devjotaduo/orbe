# QwenPaw Plugin Kit

Plugin basico em portugues para servir como ponto de partida para novos
plugins QwenPaw.

Ele demonstra os principais elementos que um plugin pode usar:

- `plugin.json`: manifesto com id, versao, entradas, dependencias e `meta`.
- `plugin.py`: entrada backend que exporta `plugin`.
- `register_http_router`: API propria em `/api/plugin-kit`.
- `register_startup_hook` e `register_shutdown_hook`: hooks de ciclo de vida.
- `register_tool`: ferramenta simples para agentes.
- `entry.frontend`: bundle JavaScript carregado pelo Console.
- `window.QwenPaw.menu`, `route` e `slot`: extensoes de UI.
- `description_i18n.pt-BR`: texto localizado em portugues.

## Estrutura

```text
qwenpaw-plugin-kit/
├── plugin.json
├── plugin.py
├── tools.py
├── requirements.txt
├── dist/index.js
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/index.tsx
└── README.md
```

## Instalar

Com o QwenPaw parado:

```bash
qwenpaw plugin install plugins/bundle/qwenpaw-plugin-kit --force
qwenpaw app
```

Depois de instalar, recarregue o Console.

## Endpoints

O router backend fica sob `/api/plugin-kit`:

```text
GET /api/plugin-kit/status
GET /api/plugin-kit/elements
```

## Tool

O plugin registra a ferramenta:

```text
plugin_kit_describe_elements
```

Ela retorna uma descricao curta dos elementos que um plugin QwenPaw pode usar.

## Frontend

O bundle `dist/index.js` registra:

- menu lateral: `Plugin Kit`
- rota: `/plugin/qwenpaw-plugin-kit`
- slot: `content.statusBar`

O codigo-fonte editavel fica em `frontend/src/index.tsx`. Para reconstruir:

```bash
cd plugins/bundle/qwenpaw-plugin-kit/frontend
npm install
npm run build
```
