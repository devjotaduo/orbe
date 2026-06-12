# Conectores Conhecidos (connector_lookup) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Gate do projeto:** mexe em `src/qwenpaw/` → a implementação DEVE passar pelo `/agentscope-guardian` antes de editar (executar via `/dev-team`, que aplica o gate). Nunca abrir PR para o upstream.

**Goal:** O discovery agent recomenda conectores concretos (origem/slug/status/notas) a partir de uma whitelist curada, via nova tool `connector_lookup`, e o blueprint ganha a seção estruturada `recommended_connectors`.

**Architecture:** Catálogo `connectors_seed.json` indexado por `integration_kind` canônico (Abordagem A do spec `docs/superpowers/specs/2026-06-11-known-connectors-design.md`); `taxonomy.py` carrega/valida e faz lookup com filtro por segmento; `tools.py` expõe a 4ª tool e renderiza a seção no markdown; `state.py` adiciona `ConnectorRef` ao `TeamBlueprint` (retrocompatível).

**Tech Stack:** Python ≥3.11, Pydantic v2, pytest + pytest-asyncio (padrões existentes em `tests/discovery/`).

**Comando de teste (na raiz do repo):** `python -m pytest tests/discovery -v`

---

### Task 1: Vocabulário canônico + normalização do `cnae_seed.json`

**Files:**
- Modify: `src/qwenpaw/discovery/segments/taxonomy.py`
- Modify: `src/qwenpaw/discovery/segments/data/cnae_seed.json`
- Test: `tests/discovery/test_taxonomy.py`

- [ ] **Step 1: Write the failing test** — adicionar ao FINAL de `tests/discovery/test_taxonomy.py`:

```python
# ---------------------------------------------------------------------------
# Vocabulário canônico de integration_kind (spec known-connectors)
# ---------------------------------------------------------------------------


def test_common_integrations_are_canonical():
    """Todo valor de common_integrations deve estar no vocabulário canônico."""
    from qwenpaw.discovery.segments.taxonomy import (
        CANONICAL_INTEGRATION_KINDS,
    )

    for seg in load_segments():
        for kind in seg.common_integrations:
            assert kind in CANONICAL_INTEGRATION_KINDS, (
                f"Segmento '{seg.key}' usa kind não-canônico: '{kind}'"
            )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/discovery/test_taxonomy.py::test_common_integrations_are_canonical -v`
Expected: FAIL com `ImportError: cannot import name 'CANONICAL_INTEGRATION_KINDS'`

- [ ] **Step 3: Adicionar a constante em `taxonomy.py`** — logo após `_DATA = ...`:

```python
CANONICAL_INTEGRATION_KINDS: frozenset[str] = frozenset({
    "whatsapp", "crm", "planilha", "agenda", "erp", "pagamento",
    "fiscal", "ecommerce", "helpdesk", "email", "delivery", "voz",
    "juridico", "lms", "pdv", "prontuario", "chat-interno", "analytics",
})
```

- [ ] **Step 4: Normalizar `cnae_seed.json`** — substituir APENAS os arrays `common_integrations` (manter o resto intocado, incluindo `keywords` e acentos):

| Segmento | `common_integrations` novo |
|---|---|
| ecommerce | `["whatsapp", "ecommerce", "planilha", "erp", "pagamento"]` |
| varejo | `["whatsapp", "pdv", "planilha"]` |
| servicos | `["whatsapp", "crm", "agenda"]` |
| alimentacao | `["whatsapp", "delivery", "planilha"]` |
| saude | `["whatsapp", "agenda", "prontuario", "erp"]` |
| educacao | `["whatsapp", "crm", "lms"]` |
| beleza | `["whatsapp", "agenda"]` |
| tecnologia | `["crm", "helpdesk", "chat-interno", "pagamento", "analytics"]` |
| construcao | `["whatsapp", "planilha", "erp", "agenda"]` |
| servicos_b2b | `["crm", "whatsapp", "email", "erp", "agenda"]` |

- [ ] **Step 5: Run full taxonomy tests**

Run: `python -m pytest tests/discovery/test_taxonomy.py -v`
Expected: ALL PASS (o novo teste e os existentes — `test_new_segments_have_complete_rails` continua válido)

- [ ] **Step 6: Commit**

```bash
git add src/qwenpaw/discovery/segments/taxonomy.py src/qwenpaw/discovery/segments/data/cnae_seed.json tests/discovery/test_taxonomy.py
git commit -m "feat(discovery): vocabulario canonico de integration_kind + cnae_seed normalizado"
```

---

### Task 2: `connectors_seed.json` + `ConnectorInfo` + `load_connectors()`

**Files:**
- Create: `src/qwenpaw/discovery/segments/data/connectors_seed.json`
- Modify: `src/qwenpaw/discovery/segments/taxonomy.py`
- Test: `tests/discovery/test_connectors.py` (novo)

- [ ] **Step 1: Write the failing tests** — criar `tests/discovery/test_connectors.py`:

```python
# -*- coding: utf-8 -*-
from qwenpaw.discovery.segments.taxonomy import (
    CANONICAL_INTEGRATION_KINDS,
    load_connectors,
)


def test_connectors_seed_loads_and_is_nonempty():
    conns = load_connectors()
    assert len(conns) >= 25


def test_connector_ids_are_unique():
    conns = load_connectors()
    ids = [c.id for c in conns]
    assert len(ids) == len(set(ids))


def test_connector_kinds_are_canonical():
    for c in load_connectors():
        assert c.integration_kind in CANONICAL_INTEGRATION_KINDS, c.id


def test_build_entries_have_empty_slug_and_build_origin():
    builds = [c for c in load_connectors() if c.status == "build"]
    assert builds, "seed deve conter entradas status=build (lacunas BR)"
    for c in builds:
        assert c.slug_or_url == "", c.id
        assert c.origin == "build", c.id


def test_seed_covers_whatsapp_and_juridico():
    kinds = {c.integration_kind for c in load_connectors()}
    assert "whatsapp" in kinds
    assert "juridico" in kinds
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/discovery/test_connectors.py -v`
Expected: FAIL com `ImportError: cannot import name 'load_connectors'`

- [ ] **Step 3: Criar `connectors_seed.json`** com o conteúdo COMPLETO (32 entradas, da tabela do spec):

```json
[
  {"id": "evolution-api-clawhub", "integration_kind": "whatsapp", "name": "Evolution API v2", "origin": "clawhub", "slug_or_url": "evolution-api", "status": "recomendado", "notes": "WhatsApp não-oficial (risco de ban); integra Chatwoot. Para produção considerar whatsapp-cloud-api oficial.", "segments": []},
  {"id": "whatsapp-cloud-api-lobehub", "integration_kind": "whatsapp", "name": "WhatsApp Cloud API (oficial Meta)", "origin": "lobehub", "slug_or_url": "techwavedev-agi-agent-kit-whatsapp-cloud-api", "status": "recomendado", "notes": "API oficial Meta; rota compliance-safe para produção.", "segments": []},
  {"id": "mcp-evolution-whatsapp", "integration_kind": "whatsapp", "name": "MCP Evolution API", "origin": "github", "slug_or_url": "aiteks-ltda/mcp-evolution-whatsapp-api", "status": "recomendado", "notes": "MCP citado no design do discovery; mesmo risco de ban do Evolution.", "segments": []},
  {"id": "hubspot-clawhub", "integration_kind": "crm", "name": "HubSpot", "origin": "clawhub", "slug_or_url": "hubspot", "status": "recomendado", "notes": "26 installs reais no ClawHub (publisher kwall1).", "segments": []},
  {"id": "mcp-hubspot", "integration_kind": "crm", "name": "mcp-hubspot (baryhuang)", "origin": "github", "slug_or_url": "baryhuang/mcp-hubspot", "status": "recomendado", "notes": "Vector storage embutido para contornar limites da API HubSpot.", "segments": []},
  {"id": "rd-station-clawhub", "integration_kind": "crm", "name": "RD Station", "origin": "clawhub", "slug_or_url": "rd-station", "status": "validar", "notes": "Skill gerada em massa (gora050); testar funcionalidade real antes de adotar.", "segments": []},
  {"id": "rd-station-build", "integration_kind": "crm", "name": "Conector RD Station próprio", "origin": "build", "slug_or_url": "", "status": "build", "notes": "API REST simples; diferencial BR previsto no design do discovery.", "segments": []},
  {"id": "pipedrive-clawhub", "integration_kind": "crm", "name": "Pipedrive", "origin": "clawhub", "slug_or_url": "pipedrive-api", "status": "validar", "notes": "OAuth gerenciado (byungkyu); sem installs comprovados.", "segments": []},
  {"id": "google-sheets-clawhub", "integration_kind": "planilha", "name": "Google Sheets", "origin": "clawhub", "slug_or_url": "google-sheets", "status": "recomendado", "notes": "15k downloads / 50 installs; skill mais usada do recorte.", "segments": []},
  {"id": "mcp-google-sheets", "integration_kind": "planilha", "name": "mcp-google-sheets (xing5)", "origin": "github", "slug_or_url": "xing5/mcp-google-sheets", "status": "recomendado", "notes": "Já citado no design do discovery; Service Account recomendado.", "segments": []},
  {"id": "excel-mcp-server", "integration_kind": "planilha", "name": "Excel MCP (xlsx local)", "origin": "github", "slug_or_url": "haris-musa/excel-mcp-server", "status": "recomendado", "notes": "Cria/edita .xlsx sem Excel instalado; PME que vive de planilha local.", "segments": []},
  {"id": "google-workspace-mcp", "integration_kind": "agenda", "name": "Google Workspace MCP", "origin": "github", "slug_or_url": "taylorwilsdon/google_workspace_mcp", "status": "recomendado", "notes": "MIT; cobre agenda + email + planilha num só MCP (12 serviços).", "segments": []},
  {"id": "calendar-scheduling-clawhub", "integration_kind": "agenda", "name": "calendar-scheduling", "origin": "clawhub", "slug_or_url": "calendar-scheduling", "status": "recomendado", "notes": "Google/Outlook/CalDAV + sub-skills de datetime.", "segments": []},
  {"id": "keeper-sh", "integration_kind": "agenda", "name": "keeper.sh", "origin": "github", "slug_or_url": "ridafkih/keeper.sh", "status": "validar", "notes": "AGPL; tier grátis sincroniza a cada 30min.", "segments": []},
  {"id": "mcp-odoo", "integration_kind": "erp", "name": "mcp-odoo (tuanle96)", "origin": "github", "slug_or_url": "tuanle96/mcp-odoo", "status": "recomendado", "notes": "36 tools, ferramentas contábeis, audit trail; Odoo 16-19.", "segments": []},
  {"id": "odoo-clawhub", "integration_kind": "erp", "name": "Odoo", "origin": "clawhub", "slug_or_url": "odoo", "status": "validar", "notes": "Read-before-write (ivangdavila); engenharia acima da média do hub.", "segments": []},
  {"id": "frappe-assistant-core", "integration_kind": "erp", "name": "ERPNext (Frappe Assistant)", "origin": "github", "slug_or_url": "buildswithpaul/Frappe_Assistant_Core", "status": "validar", "notes": "AGPL-3.0 — atenção em uso multi-tenant comercial.", "segments": []},
  {"id": "mercado-pago-mcp", "integration_kind": "pagamento", "name": "Mercado Pago MCP", "origin": "lobehub", "slug_or_url": "hdbookie-mercado-pago-mcp", "status": "validar", "notes": "Pix com QR, fraude, export contábil; baixa tração.", "segments": []},
  {"id": "pix-mcp", "integration_kind": "pagamento", "name": "Pix MCP", "origin": "lobehub", "slug_or_url": "regenerating-world-pix-mcp", "status": "validar", "notes": "Cobranças Pix standalone; baixa tração.", "segments": []},
  {"id": "stripe-agent-toolkit", "integration_kind": "pagamento", "name": "Stripe Agent Toolkit (oficial)", "origin": "github", "slug_or_url": "stripe/agent-toolkit", "status": "recomendado", "notes": "Oficial Stripe; sem Pix — indicado para SaaS/recorrência.", "segments": []},
  {"id": "nfe-build", "integration_kind": "fiscal", "name": "Conector NF-e/NFS-e próprio", "origin": "build", "slug_or_url": "", "status": "build", "notes": "Lacuna em todos os marketplaces pesquisados.", "segments": []},
  {"id": "shopify-mcp", "integration_kind": "ecommerce", "name": "shopify-mcp (GeLi2001)", "origin": "github", "slug_or_url": "GeLi2001/shopify-mcp", "status": "recomendado", "notes": "31 tools GraphQL Admin API.", "segments": []},
  {"id": "vtex-mcp", "integration_kind": "ecommerce", "name": "mcp-vtex", "origin": "lobehub", "slug_or_url": "leosepulveda-mcp-vtex", "status": "validar", "notes": "Único conector VTEX encontrado; maturidade incerta.", "segments": []},
  {"id": "mercadolivre-mcp", "integration_kind": "ecommerce", "name": "Mercado Livre MCP (oficial)", "origin": "github", "slug_or_url": "mercadolibre/mercadolibre-mcp-server", "status": "validar", "notes": "Oficial porém recém-criado.", "segments": []},
  {"id": "nuvemshop-build", "integration_kind": "ecommerce", "name": "Conector Nuvemshop próprio", "origin": "build", "slug_or_url": "", "status": "build", "notes": "Alternativa BridgeAPI no LobeHub é embrionária (3 stars).", "segments": []},
  {"id": "chatwoot-fazer-ai", "integration_kind": "helpdesk", "name": "Chatwoot skills (fazer.ai)", "origin": "github", "slug_or_url": "fazer-ai/chatwoot-skills", "status": "validar", "notes": "Empresa brasileira; par natural do Evolution API.", "segments": []},
  {"id": "zendesk-mcp", "integration_kind": "helpdesk", "name": "zendesk-mcp-server", "origin": "github", "slug_or_url": "reminia/zendesk-mcp-server", "status": "recomendado", "notes": "Tickets + Help Center como base de conhecimento.", "segments": []},
  {"id": "ifood-clawhub", "integration_kind": "delivery", "name": "iFood", "origin": "clawhub", "slug_or_url": "ifood", "status": "validar", "notes": "Skill gerada em massa; único iFood encontrado nos marketplaces.", "segments": ["alimentacao"]},
  {"id": "ifood-build", "integration_kind": "delivery", "name": "Conector iFood próprio", "origin": "build", "slug_or_url": "", "status": "build", "notes": "Lacuna real do segmento alimentação/delivery.", "segments": ["alimentacao"]},
  {"id": "qwen3-asr", "integration_kind": "voz", "name": "Qwen3-ASR", "origin": "modelscope", "slug_or_url": "Qwen/Qwen3-ASR-1.7B", "status": "recomendado", "notes": "52 idiomas incluindo português; ecossistema Qwen (irmão do qwenpaw).", "segments": []},
  {"id": "audio-ptbr-clawhub", "integration_kind": "voz", "name": "audio-ptbr-autoreply", "origin": "clawhub", "slug_or_url": "audio-ptbr-autoreply", "status": "validar", "notes": "Única skill pt-BR do ClawHub (wav2vec2 local).", "segments": []},
  {"id": "brlaw-mcp", "integration_kind": "juridico", "name": "Brazilian Law Research MCP", "origin": "github", "slug_or_url": "pdmtt/brlaw_mcp_server", "status": "recomendado", "notes": "Jurisprudência STF/STJ/TST em fontes oficiais; tools em português.", "segments": ["servicos_b2b"]}
]
```

- [ ] **Step 4: Adicionar model + loader em `taxonomy.py`** — após a classe `SegmentInfo`:

```python
from typing import Literal  # mover para o bloco de imports no topo

_CONNECTORS_DATA = Path(__file__).parent / "data" / "connectors_seed.json"

_STATUS_ORDER = {"recomendado": 0, "validar": 1, "build": 2}


class ConnectorInfo(BaseModel):
    id: str
    integration_kind: str
    name: str
    origin: Literal[
        "clawhub", "lobehub", "modelscope",
        "skills-sh", "skillsmp", "github", "build",
    ]
    slug_or_url: str = ""
    status: Literal["recomendado", "validar", "build"]
    notes: str = ""
    segments: list[str] = []

    @field_validator("integration_kind")
    @classmethod
    def _kind_is_canonical(cls, v: str) -> str:
        if v not in CANONICAL_INTEGRATION_KINDS:
            raise ValueError(
                f"integration_kind '{v}' fora do vocabulário canônico"
            )
        return v

    @model_validator(mode="after")
    def _build_entries_consistent(self) -> "ConnectorInfo":
        if self.status == "build" and (
            self.origin != "build" or self.slug_or_url
        ):
            raise ValueError(
                f"conector build '{self.id}' deve ter origin='build' "
                f"e slug_or_url vazio"
            )
        return self


@lru_cache(maxsize=1)
def load_connectors() -> tuple[ConnectorInfo, ...]:
    raw = json.loads(_CONNECTORS_DATA.read_text(encoding="utf-8"))
    conns = tuple(ConnectorInfo.model_validate(item) for item in raw)
    ids = [c.id for c in conns]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise ValueError(f"connectors_seed.json: ids duplicados: {dupes}")
    return conns
```

Ajustar o import do Pydantic no topo do arquivo para:

```python
from pydantic import BaseModel, field_validator, model_validator
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/discovery/test_connectors.py -v`
Expected: 5 PASS

- [ ] **Step 6: Commit**

```bash
git add src/qwenpaw/discovery/segments/data/connectors_seed.json src/qwenpaw/discovery/segments/taxonomy.py tests/discovery/test_connectors.py
git commit -m "feat(discovery): seed curada de conectores + ConnectorInfo/load_connectors"
```

---

### Task 3: `lookup_connectors(kind, segment=None)`

**Files:**
- Modify: `src/qwenpaw/discovery/segments/taxonomy.py`
- Test: `tests/discovery/test_connectors.py`

- [ ] **Step 1: Write the failing tests** — adicionar ao final de `tests/discovery/test_connectors.py`:

```python
import pytest

from qwenpaw.discovery.segments.taxonomy import lookup_connectors


def test_lookup_orders_by_status():
    conns = lookup_connectors("crm")
    statuses = [c.status for c in conns]
    assert statuses == sorted(
        statuses, key=lambda s: {"recomendado": 0, "validar": 1, "build": 2}[s]
    )
    assert conns[0].status == "recomendado"


def test_lookup_filters_by_segment():
    # brlaw-mcp é restrito a servicos_b2b
    juridico_b2b = lookup_connectors("juridico", segment="servicos_b2b")
    assert any(c.id == "brlaw-mcp" for c in juridico_b2b)
    juridico_eco = lookup_connectors("juridico", segment="ecommerce")
    assert not any(c.id == "brlaw-mcp" for c in juridico_eco)


def test_lookup_without_segment_includes_segmented():
    todos = lookup_connectors("delivery", segment=None)
    assert any(c.id == "ifood-clawhub" for c in todos)


def test_lookup_unknown_kind_raises():
    with pytest.raises(ValueError) as exc:
        lookup_connectors("blockchain")
    assert "whatsapp" in str(exc.value)  # lista os kinds válidos


def test_lookup_canonical_kind_without_connectors_returns_empty():
    assert lookup_connectors("pdv") == ()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/discovery/test_connectors.py -v`
Expected: os 5 novos FAIL com `ImportError: cannot import name 'lookup_connectors'`

- [ ] **Step 3: Implementar em `taxonomy.py`** — após `load_connectors`:

```python
def lookup_connectors(
    kind: str,
    segment: str | None = None,
) -> tuple[ConnectorInfo, ...]:
    """Conectores curados de um tipo de integração, ordenados por status.

    Levanta ValueError quando `kind` não é canônico. Quando `segment` é
    informado, exclui conectores restritos a outros segmentos; quando é
    None/vazio, retorna todos do kind (inclusive os segmentados).
    """
    if kind not in CANONICAL_INTEGRATION_KINDS:
        raise ValueError(
            f"integration_kind desconhecido: '{kind}'. "
            f"Válidos: {', '.join(sorted(CANONICAL_INTEGRATION_KINDS))}"
        )
    result = [
        c for c in load_connectors()
        if c.integration_kind == kind
        and (not segment or not c.segments or segment in c.segments)
    ]
    result.sort(key=lambda c: _STATUS_ORDER[c.status])
    return tuple(result)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/discovery/test_connectors.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/discovery/segments/taxonomy.py tests/discovery/test_connectors.py
git commit -m "feat(discovery): lookup_connectors com ordenacao por status e filtro de segmento"
```

---

### Task 4: `ConnectorRef` + `TeamBlueprint.recommended_connectors`

**Files:**
- Modify: `src/qwenpaw/discovery/state.py`
- Test: `tests/discovery/test_state.py`

- [ ] **Step 1: Write the failing tests** — adicionar ao final de `tests/discovery/test_state.py`:

```python
def test_blueprint_validates_without_recommended_connectors():
    """Retrocompat: blueprints antigos (sem o campo) continuam válidos."""
    from qwenpaw.discovery.state import CompanyProfile, TeamBlueprint

    bp = TeamBlueprint(company_profile=CompanyProfile(segment="ecommerce"))
    assert bp.recommended_connectors == []


def test_blueprint_validates_with_recommended_connectors():
    from qwenpaw.discovery.state import (
        CompanyProfile,
        ConnectorRef,
        TeamBlueprint,
    )

    bp = TeamBlueprint(
        company_profile=CompanyProfile(segment="ecommerce"),
        recommended_connectors=[
            ConnectorRef(
                integration_kind="whatsapp",
                name="Evolution API v2",
                origin="clawhub",
                slug_or_url="evolution-api",
                status="recomendado",
                notes="não-oficial; risco de ban",
            )
        ],
    )
    assert bp.recommended_connectors[0].origin == "clawhub"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/discovery/test_state.py -v`
Expected: os 2 novos FAIL (`AttributeError`/`ImportError` de `ConnectorRef`)

- [ ] **Step 3: Implementar em `state.py`** — antes da classe `TeamBlueprint`:

```python
class ConnectorRef(BaseModel):
    """Conector recomendado no blueprint (whitelist curada).

    Campos string lenientes de propósito: o JSON vem do LLM; a validação
    estrita de vocabulário vive em ConnectorInfo (taxonomy.py).
    """
    integration_kind: str
    name: str
    origin: str
    slug_or_url: str = ""
    status: str
    notes: str = ""
```

E em `TeamBlueprint`, adicionar o campo após `open_questions`:

```python
    recommended_connectors: list[ConnectorRef] = Field(default_factory=list)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/discovery/test_state.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/discovery/state.py tests/discovery/test_state.py
git commit -m "feat(discovery): ConnectorRef + recommended_connectors no TeamBlueprint"
```

---

### Task 5: Tool `connector_lookup` no `DiscoverySession`

**Files:**
- Modify: `src/qwenpaw/discovery/tools.py`
- Test: `tests/discovery/test_tools.py`

- [ ] **Step 1: Write the failing tests** — adicionar ao final de `tests/discovery/test_tools.py`:

```python
@pytest.mark.asyncio
async def test_connector_lookup_known_kind(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("whatsapp")
    text = _text(chunk)
    assert "evolution-api" in text
    assert "recomendado" in text


@pytest.mark.asyncio
async def test_connector_lookup_unknown_kind_errors_with_valid_list(tmp_path):
    from agentscope.message import ToolResultState

    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("blockchain")
    assert chunk.state == ToolResultState.ERROR
    assert "whatsapp" in _text(chunk)  # lista os kinds válidos


@pytest.mark.asyncio
async def test_connector_lookup_kind_without_connectors_guides_build(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("pdv")
    text = _text(chunk).lower()
    assert "build" in text
    assert "open_question" in text


@pytest.mark.asyncio
async def test_connector_lookup_filters_by_state_segment(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    s.state.company.segment = "ecommerce"
    chunk = await s.connector_lookup("juridico")
    # brlaw-mcp é restrito a servicos_b2b: para ecommerce não aparece
    assert "brlaw" not in _text(chunk)

    s.state.company.segment = "servicos_b2b"
    chunk = await s.connector_lookup("juridico")
    assert "brlaw" in _text(chunk)


def test_toolkit_has_four_tools(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    tk = s.build_toolkit()
    # Toolkit deve registrar segment_lookup, reflect, emit_blueprint,
    # connector_lookup. A API exata de listagem pode variar; usar o
    # atributo público disponível (ex.: len(tk.tools) == 4) conforme a
    # versão do agentscope no repo.
    assert len(tk.tools) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/discovery/test_tools.py -v`
Expected: novos FAIL com `AttributeError: 'DiscoverySession' object has no attribute 'connector_lookup'`

- [ ] **Step 3: Implementar a tool em `tools.py`** — import no topo:

```python
from .segments.taxonomy import lookup_connectors, lookup_segment
```

Novo método no `DiscoverySession`, após `segment_lookup`:

```python
    async def connector_lookup(self, integration_kind: str) -> ToolChunk:
        """Consulta a whitelist curada de conectores de um tipo de integração.

        Chame na hora de MONTAR O BLUEPRINT, uma vez para cada integração
        detectada ou proposta (ex.: 'whatsapp', 'crm', 'planilha'). Retorna
        conectores concretos com origem, slug, status e notas de risco.
        Prefira status 'recomendado'; inclua 'validar' citando a nota de
        risco; trate 'build' como item de roadmap (conector próprio).

        Args:
            integration_kind: Tipo canônico da integração (whatsapp, crm,
                planilha, agenda, erp, pagamento, fiscal, ecommerce,
                helpdesk, email, delivery, voz, juridico, lms, pdv,
                prontuario, chat-interno, analytics).

        Returns:
            `ToolChunk`: conectores curados do tipo, ou orientação de build.
        """
        try:
            conns = lookup_connectors(
                integration_kind,
                segment=self.state.company.segment,
            )
        except ValueError as exc:
            return _err(f"{exc} Reenvie com um kind válido.")
        if not conns:
            return _ok(
                f"Nenhum conector curado para '{integration_kind}'. "
                "Registre no blueprint um ConnectorRef com origin='build' e "
                "status='build', e adicione uma open_question sobre essa "
                "integração."
            )
        payload = [
            {
                "integration_kind": c.integration_kind,
                "name": c.name,
                "origin": c.origin,
                "slug_or_url": c.slug_or_url,
                "status": c.status,
                "notes": c.notes,
            }
            for c in conns
        ]
        return _ok(
            "Conectores curados (use em recommended_connectors; referência "
            "curta em tools_integrations = '<origin>:<slug>'):\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )
```

E registrar no `build_toolkit`:

```python
    def build_toolkit(self) -> Toolkit:
        return Toolkit(
            tools=[
                FunctionTool(self.segment_lookup, is_read_only=False),
                FunctionTool(self.reflect, is_read_only=False),
                FunctionTool(self.emit_blueprint, is_read_only=False),
                FunctionTool(self.connector_lookup, is_read_only=True),
            ]
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/discovery/test_tools.py -v`
Expected: ALL PASS (se `test_toolkit_has_four_tools` falhar por API do Toolkit, ajustar o acesso à lista de tools conforme a versão do agentscope — verificar `docs/agentscope-v2/` — mantendo a asserção de 4 tools)

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/discovery/tools.py tests/discovery/test_tools.py
git commit -m "feat(discovery): tool connector_lookup com filtro por segmento do estado"
```

---

### Task 6: Seção no `blueprint.md` + instruções no prompt

**Files:**
- Modify: `src/qwenpaw/discovery/tools.py` (`_blueprint_to_markdown`)
- Modify: `src/qwenpaw/discovery/prompts.py`
- Test: `tests/discovery/test_tools.py`

- [ ] **Step 1: Write the failing tests** — adicionar ao final de `tests/discovery/test_tools.py`:

```python
def test_blueprint_markdown_renders_connectors_section():
    from qwenpaw.discovery.state import (
        CompanyProfile,
        ConnectorRef,
        TeamBlueprint,
    )
    from qwenpaw.discovery.tools import _blueprint_to_markdown

    bp = TeamBlueprint(
        company_profile=CompanyProfile(segment="ecommerce"),
        recommended_connectors=[
            ConnectorRef(
                integration_kind="whatsapp",
                name="Evolution API v2",
                origin="clawhub",
                slug_or_url="evolution-api",
                status="recomendado",
                notes="não-oficial; risco de ban",
            )
        ],
    )
    md = _blueprint_to_markdown(bp)
    assert "## Conectores recomendados" in md
    assert "clawhub:evolution-api" in md
    assert "risco de ban" in md


def test_blueprint_markdown_omits_empty_connectors_section():
    from qwenpaw.discovery.state import CompanyProfile, TeamBlueprint
    from qwenpaw.discovery.tools import _blueprint_to_markdown

    bp = TeamBlueprint(company_profile=CompanyProfile(segment="ecommerce"))
    assert "Conectores recomendados" not in _blueprint_to_markdown(bp)


def test_system_prompt_mentions_connector_lookup():
    from qwenpaw.discovery.prompts import build_discovery_system_prompt

    assert "connector_lookup" in build_discovery_system_prompt()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/discovery/test_tools.py -v`
Expected: os 3 novos FAIL

- [ ] **Step 3: Renderizar a seção em `_blueprint_to_markdown`** — inserir após o bloco do roadmap e ANTES do bloco de `open_questions`:

```python
    if bp.recommended_connectors:
        lines.append("\n## Conectores recomendados")
        for c in bp.recommended_connectors:
            ref = f"{c.origin}:{c.slug_or_url}" if c.slug_or_url else c.origin
            entry = (
                f"- **{c.name}** ({c.integration_kind}) — `{ref}`"
                f" — status: {c.status}"
            )
            if c.notes:
                entry += f" — {c.notes}"
            lines.append(entry)
```

- [ ] **Step 4: Atualizar `prompts.py`** — (a) no bloco "FLUXO DE RACIOCÍNIO", inserir um passo entre os atuais 4 e 5 (renumerando o atual 5 para 6):

```text
5. ANTES de chamar `emit_blueprint`: para CADA integração detectada ou
   proposta no time, chame `connector_lookup` com o tipo canônico
   (whatsapp, crm, planilha, agenda, erp, pagamento, ecommerce, ...).
   Preencha `recommended_connectors` com os conectores retornados —
   prefira status 'recomendado'; inclua 'validar' citando a nota de
   risco; trate 'build' como item de roadmap. Em `tools_integrations`
   de cada agente use a referência curta '<origin>:<slug>'.
```

(b) no `_EXAMPLE`, trocar `"tools_integrations": ["whatsapp", "cardápio digital"]` do Atendente WhatsApp por `"tools_integrations": ["clawhub:evolution-api", "cardápio digital"]` e adicionar a chave ao dict (após `"open_questions"`):

```python
    "recommended_connectors": [
        {
            "integration_kind": "whatsapp",
            "name": "Evolution API v2",
            "origin": "clawhub",
            "slug_or_url": "evolution-api",
            "status": "recomendado",
            "notes": "não-oficial (risco de ban); p/ produção considerar WhatsApp Cloud API",
        },
    ],
```

Atenção: `_SYSTEM` passa por `.format()` — o texto novo não pode conter `{` ou `}` literais (o passo 5 acima não contém).

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/discovery/test_tools.py tests/discovery/test_state.py -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/qwenpaw/discovery/tools.py src/qwenpaw/discovery/prompts.py tests/discovery/test_tools.py
git commit -m "feat(discovery): secao de conectores no blueprint.md + fluxo no prompt"
```

---

### Task 7: Integração — entrevista roteirizada emite conectores

**Files:**
- Modify: `tests/discovery/test_runner.py`

- [ ] **Step 1: Estender o `FakeAgent`** — no turno 2 de `FakeAgent.reply` (em `tests/discovery/test_runner.py`), ANTES de montar `bp`, adicionar a chamada da nova tool:

```python
            await s.connector_lookup("whatsapp")
```

E no dict `bp`, adicionar após `"open_questions"`:

```python
                "recommended_connectors": [
                    {"integration_kind": "whatsapp",
                     "name": "Evolution API v2",
                     "origin": "clawhub",
                     "slug_or_url": "evolution-api",
                     "status": "recomendado",
                     "notes": "não-oficial; risco de ban"}],
```

E trocar, no mesmo `bp`, `"tools_integrations": ["mcp:evolution-whatsapp"]` por `"tools_integrations": ["clawhub:evolution-api"]`.

- [ ] **Step 2: Estender as asserções** — em `test_runner_scripted_interview`, após `assert bp["proposed_team"][0]["name"] == "Atendente WhatsApp"`:

```python
    assert bp["recommended_connectors"], "blueprint deve recomendar conectores"
    rc = bp["recommended_connectors"][0]
    assert rc["origin"] == "clawhub" and rc["slug_or_url"] == "evolution-api"
    md = (tmp_path / "blueprint.md").read_text(encoding="utf-8")
    assert "## Conectores recomendados" in md
```

- [ ] **Step 3: Run the full discovery suite**

Run: `python -m pytest tests/discovery -v`
Expected: ALL PASS

- [ ] **Step 4: Rodar também os testes de CLI/eval que tocam discovery** (regressão)

Run: `python -m pytest tests/cli/test_discovery_cmd.py tests/scripts/test_eval_discovery.py -v`
Expected: ALL PASS (nenhum toca o schema novo, mas valida que nada quebrou)

- [ ] **Step 5: Commit**

```bash
git add tests/discovery/test_runner.py
git commit -m "test(discovery): entrevista roteirizada cobre connector_lookup + recommended_connectors"
```

---

## Verificação final (critérios de aceite do spec)

- [ ] `connector_lookup` disponível como 4ª tool, filtrando por segmento — Tasks 3, 5
- [ ] `cnae_seed.json` 100% canônico com teste de regressão — Task 1
- [ ] Blueprint com `recommended_connectors` + seção no `.md` com notas de risco — Tasks 4, 6, 7
- [ ] Blueprints antigos continuam validando — Task 4 (teste de retrocompat)
- [ ] Suíte completa verde: `python -m pytest tests/discovery tests/cli/test_discovery_cmd.py -v`
- [ ] `/agentscope-guardian` aprovou as edições em `src/qwenpaw/` (aplicado pelo `/dev-team` antes de cada edição)
