# Session Status
Last updated: 2026-06-15

## What Was Done (2026-06-15, afternoon)

### Ontology Browser — Generic Label-Driven Entity Extraction
- Replaced hardcoded type-based class extraction (`owl:Class`, `qudt:QuantityKind`, etc.)
  with a **general label-driven approach**: any `URIRef` subject carrying `rdfs:label` or
  `skos:prefLabel` is indexed as a browsable entity. Covers OWL, QUDT, SKOS, BRICK, and
  any future vocabulary without special-casing.
- Result: `qudt_quantitykind` now shows **1217 entities**, `qudt-units` 2906, etc.

### Ontology Browser — "All Ontologies" Default
- Added `_all` virtual ontology to API: merges classes (or properties) across all loaded
  ontologies in a single response.
- Browser now **opens pre-selected on "— All ontologies —"** so all items load immediately
  on open. User can still narrow to a single ontology via the dropdown.
- Eliminates the need to know which sub-ontology (e.g. `qudt-datatype` vs `qudt-units`)
  contains the predicate you want.

### SHACL Exporter — Generic Prefix Resolution
- Replaced the hardcoded `@prefix` block with a fully **ontology-graph-driven** approach:
  1. Build a prefix→namespace map by harvesting namespace bindings from every loaded
     ontology graph (`g.namespaces()` across all ontologies in `OntologyManager`).
  2. Generate Turtle body first, then scan it for used `prefix:localname` tokens.
  3. Emit only the `@prefix` declarations actually needed.
- Only 4 built-ins not found in any ontology graph are declared explicitly: `sh:`, `dash:`,
  `ex:`, `schema:`.
- Fixes `Undefined prefix "ex:"` error on schema reference edges.
- Any new ontology loaded automatically makes its prefixes available — no code changes needed.

### Add Property UX Improvements
- **Double labels** on the two most confusing fields:
  - "Field Identifier" with `sh:path` in small grey monospace below
  - "Concept Type" with `sh:class` in small grey monospace below
  - "Allowed Values" with `sh:in`, "Fixed Value" with `sh:hasValue`
- **`?` help tooltips** on every field with plain-English one-sentence explanations.
- **Auto-set datatype from `sh:class`**: when Concept Type is set and enrichment resolves
  to `unit_dropdown`, datatype auto-sets to `xsd:decimal`; `boolean_toggle` → `xsd:boolean`;
  `date_picker` → `xsd:date`; etc. Generic rule, no vocabulary special-casing.
- **Auto-set datatype from `rdfs:range`**: when a property is selected from the browser,
  its `rdfs:range` (if declared) auto-fills the datatype field.

### Semantic Unit Dropdown — End-to-End Working
- **`SHACLExporter` now loads `OntologyManager`** at construction time. Uses
  `get_enrichment_engine()` singleton so ontologies are only loaded once.
- **`sh:in` list emitted for quantity-kind properties**: `qudt:Mass`, `qudt:Temperature`,
  etc. resolve to `unit_dropdown` and emit the full QUDT unit list as `sh:in`.
- **`dash:editor dash:InstancesSelectEditor`** emitted for unit fields.
- All 60 tests still pass.

### Next Steps
- End-to-end test: create Mass brick → assemble schema → export → verify unit dropdown
  renders in the browser form.
- ~~Fix: deleted component not removed from component list~~ **FIXED** (2026-06-16): `removeComp` now computes `filteredIds` first, passes them to `loadComponents(filteredIds)` before `onSaved` propagates.

---

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
| `brick_app/gui_components.py` | Qt PropertyEditorDialog, ConstraintEditorDialog, SimpleOntologyBrowser |
| `brick_app/ui/property_editor.ui` | Qt Designer UI for property editor with all constraint fields |
| `brick_app/ui/constraint_editor.ui` | Qt Designer UI for enhanced constraint editor |
| `brick_app/brick_editor.py` | Main PyQt window (BrickEditor) with constraint management |
| `schema_app/core/shacl_export.py` | SHACL/Turtle exporter — uses EnrichmentEngine for dash:editor/viewer |

## What Was Done (2026-06-14)

### PyQt Frontend Feature Parity Complete
- **Property Editor UI**: Updated `brick_app/ui/property_editor.ui` with all constraint fields matching web frontend:
  - Cardinality: Min Count / Max Count (always shown)
  - String Constraints group (min/max length, pattern) — shown for xsd:string, xsd:anyURI, rdf:HTML, rdf:langString
  - Language Constraints group (language_in, unique_lang) — shown for rdf:langString only
  - Value Bounds group (min/max inclusive/exclusive) — shown for numeric & date types
  - sh:in and sh:hasValue fields (always shown)
  - Added xsd:decimal, rdf:langString, rdf:HTML to datatype combo

- **PropertyEditorDialog Rewrite**: Complete rewrite in `gui_components.py` using `loadUi("property_editor.ui")`:
  - `_update_group_visibility()` drives show/hide of group boxes by datatype
  - `_populate_fields()` restores all fields when editing existing property
  - `get_property_data()` returns full LeafProperty-compatible dict
  - Defined `DEFAULT_NAMESPACE`, `_STRING_TYPES`, `_LANG_TYPES`, `_BOUNDS_TYPES` module-level constants

- **Brick Editor Integration**: Updated `brick_editor.py`:
  - `add_property()` stores into `leaf_properties` list (modern format)
  - `on_property_double_clicked()` writes back full updated dict
  - `_create_property_list_item()` appends inline constraint chips

### Complete Constraint Editor System
- **Enhanced Constraint Editor UI**: Professional Qt Designer layout (`constraint_editor.ui`) with type-specific input fields
- **State Controller**: `ConstraintEditorStateController` manages widget visibility and dynamic labels
- **Full CRUD Operations**: Complete constraint viewing, adding, editing, and deletion with double-click interface
- **Data Persistence**: All constraint changes properly integrated with brick core and JSON storage

### Ontology Browser Fixed
- **Complete GUI Resolution**: Fixed missing `populate_ontology_list()` method call and corrected cache directory path
- **Real Data**: Now using cached ontologies (Schema.org, FOAF, BRICK) instead of fallback hardcoded data
- **End-to-End Functionality**: Class selection and property clipboard work exactly as in TopBraid

## Pending / Next Steps

- **`skos_selector` widget** — stubs in `widget_rules.ttl`, needs a SKOS vocabulary loaded
- **`entity_lookup` widget** — stubs in `widget_rules.ttl`, needs named-entity class hierarchy
- **`unit_dropdown` in exported SHACL** — currently maps to `dash:DecimalFieldEditor`;
  may need a custom DASH extension for a real unit-aware widget
- `extend_schema` not exposed in web API
- `common/` outside sub-packages — fine for local/Docker, breaks standalone `pip install`
- **Frontend refactor (future)** — both `brick_app` and `schema_app` UIs are single-file
  inline-JSX/Babel templates (~1400 and ~1250 lines). Migrate to a proper **Vite + React**
  build (separate `.jsx` component files, hot reload, TypeScript optional). Flask serves
  the compiled `static/bundle.js`. No functional change needed — pure DX improvement.

## Troubleshooting

```bash
# Clear Python cache
find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +

# Hard-refresh browser after template changes
Ctrl+Shift+R
```
