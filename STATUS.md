# Session Status
Last updated: 2026-06-12

## What Was Done (2026-06-12)

### Directory Rename
- `brick_app_v2/` → `brick_app/`, `schema_app_v2/` → `schema_app/`
- All imports, `pyproject.toml` names and `uv` workspace members updated
- `uv sync` confirmed clean after rename

### Test Infrastructure
- Archived old script-style tests from `schema_app/` to `schema_app/archive/`
- Created `tests/test_schema_app.py` — proper pytest covering Schema CRUD,
  sequences, grouping, nesting, serialisation, SHACL export
- `pyproject.toml` `testpaths = ["tests"]` — all 60 tests passing

### EnrichmentEngine — moved to `common/`
- `common/enrichment_engine.py` + `common/widget_rules.ttl` are now the
  **single source of truth** (previously only in `brick_app/core/`)
- `brick_app/core/enrichment_engine.py` is a thin re-export from `common`
- Both `brick_app` and `schema_app` import from `common`

### Enrichment Engine layers — all verified
| Layer | Trigger | Widget type |
|-------|---------|-------------|
| 0 | `sh:datatype` (e.g. `xsd:boolean`) | `boolean_toggle`, `date_picker`, `decimal_input`, etc. |
| 1 | ProMo dimensional signature | `unit_dropdown` |
| 2 | QUDT/ontology predicate query | `unit_dropdown` |
| 3 | IRI namespace prefix | `property_suggestions` |

### Enrichment wired into SHACL exporter (the core goal)
- `schema_app/core/shacl_export.py` `_get_dash_editor()` / `_get_dash_viewer()`
  now call `EnrichmentEngine` instead of using a hardcoded datatype map
- Resolution order: `sh:class` (Layers 1–3) → `sh:datatype` (Layer 0) → fallback
- Exported Turtle now contains **semantically-correct** `dash:editor` /
  `dash:viewer` annotations — these drive the Darmstadt `shacl-form`
  end-user widget rendering

### Bug fixes
- `GET /api/session/<id>/ontologies` was returning HTTP 500 because the
  response dict contained a live `rdflib.Graph` (not JSON-serialisable).
  Fixed by stripping the `"graph"` key before `jsonify`.
- Web frontend: added Layer 0 datatype `useEffect` — green widget hint badge
  now appears below the datatype dropdown in Add Property dialog
- Qt frontend: `_run_datatype_enrichment()` wired to
  `datatype_combo.currentTextChanged` — same green hint label in Qt dialog

### Verified end-to-end (both Web and Qt)
| Test | Web | Qt |
|------|-----|----|
| Ontology browser loads | ✅ | ✅ |
| `xsd:boolean` → `boolean_toggle` hint | ✅ | ✅ |
| `xsd:decimal` → `decimal_input` hint | ✅ | ✅ |
| `qudt:Mass` → unit dropdown (58 units) | ✅ | ✅ |
| `foaf:Person` → property suggestions | ✅ | ✅ |
| Exported SHACL has correct `dash:editor` | ✅ | n/a |

---

## What Was Done (2026-06-11)

### Semantic Awareness Feature (3 Phases)

**Phase 1 — sh:class Foundation**
- Added `sh_class` to `LeafProperty` dataclass
- Web UI + Qt GUI: sh:class field with ontology browser

**Phase 2 — EnrichmentEngine Backend**
- `EnrichmentEngine` with layered resolution (dimensional, predicate, namespace)
- QUDT unit lookup, Schema.org / FOAF / Brick property suggestions
- `GET /api/enrichment?class_iri=...` and `GET /api/enrichment/datatype?datatype=...`

**Phase 3 — Frontend Enrichment Widgets**
- Web: React `useEffect` hooks, unit dropdown, suggested properties chips
- Qt: `_run_enrichment()`, `_show_unit_dropdown()`, `_show_property_suggestions()`

### Earlier work (2026-05-20 and prior)
- Docker smoke tests, Import SHACL UI, Schema App Qt features (validate, extend,
  add_schema_reference, generate_web_form), constraint editor, property editor
  parity between Qt and web

---

## How to Launch

```bash
# Desktop Qt
uv run python run_brick_app_qt.py
uv run python run_schema_app_qt.py

# Web
uv run python run_brick_app_web.py    # → http://localhost:5001
uv run python run_schema_app_web.py   # → http://localhost:5000

# Tests
uv run python -m pytest tests/ -v     # 60 tests, all passing
```

## Quick API Tests (with server running on :5001)

```bash
# Layer 0 — datatype
curl "http://localhost:5001/api/enrichment/datatype?datatype=xsd:boolean"

# Layer 2 — QUDT predicate
curl "http://localhost:5001/api/enrichment?class_iri=http://qudt.org/vocab/quantitykind/Mass"

# Layer 3 — namespace
curl "http://localhost:5001/api/enrichment?class_iri=foaf:Person"

# Ontology browser
curl "http://localhost:5001/api/session/<session_id>/ontologies"
```

## Key Files

| File | Role |
|------|------|
| `common/enrichment_engine.py` | EnrichmentEngine — single source of truth |
| `common/widget_rules.ttl` | Declarative widget rules (datatype, sig, predicate, namespace) |
| `brick_app/core/enrichment_engine.py` | Re-export from common |
| `brick_app/api/web_api.py` | Flask REST API incl. `/api/enrichment` endpoints |
| `brick_app/api/templates/index.html` | Web frontend (React/JSX inline) |
| `brick_app/gui_components.py` | Qt PropertyEditorDialog with enrichment wiring |
| `schema_app/core/shacl_export.py` | SHACL/Turtle exporter — uses EnrichmentEngine for dash:editor/viewer |

## Pending / Next Steps

- **`skos_selector` widget** — stubs in `widget_rules.ttl`, needs a SKOS vocabulary loaded
- **`entity_lookup` widget** — stubs in `widget_rules.ttl`, needs named-entity class hierarchy
- **`unit_dropdown` in exported SHACL** — currently maps to `dash:DecimalFieldEditor`;
  may need a custom DASH extension for a real unit-aware widget
- `extend_schema` not exposed in web API
- `common/` outside sub-packages — fine for local/Docker, breaks standalone `pip install`

## Troubleshooting

```bash
# Clear Python cache
find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +

# Hard-refresh browser after template changes
Ctrl+Shift+R
```
