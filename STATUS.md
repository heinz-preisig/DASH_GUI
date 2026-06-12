# Session Status
Last updated: 2026-06-11

## What Was Done This Session (2026-06-11)

### Semantic Awareness Feature (3 Phases Complete)

**Phase 1: sh:class Foundation (Web + Qt)**
- Added `sh_class` field to `LeafProperty` dataclass in `brick_core_simple.py`
- **Web UI**: Added semantic class input to PropertyEditorModal with ontology browser
- **Qt GUI**: Added sh:class field to `property_editor.ui` with browse/clear buttons
- Updated `PropertyEditorDialog` in `gui_components.py` to handle sh_class
- Updated SHACL export to include `sh:class` predicate

**Phase 2: Enrichment Engine Backend**
- Created `brick_app/core/enrichment_engine.py` with:
  - `EnrichmentEngine` class for ontology-aware enrichment
  - QUDT unit lookup (Mass → kg/g/lb/oz, Temperature → K/°C/°F, etc.)
  - Schema.org property suggestions (Person → givenName/familyName/email)
  - FOAF property suggestions (Person → name/mbox/homepage)
  - Brick schema suggestions (Temperature_Sensor → measures/hasLocation)
- Added `GET /api/enrichment?class_iri=...` endpoint to Flask API

**Phase 3: Frontend Enrichment Widgets**
- Added React state for enrichment data and loading state
- Added `useEffect` hook to auto-fetch enrichment when sh_class changes
- Added QUDT unit dropdown widget (appears when class is a quantity kind)
- Added suggested properties widget (appears for Schema.org/FOAF/Brick classes)
- Clicking a suggested property auto-fills the property path

### Bug Fixes (Schema Preview)
- Fixed library path to use `ShaclForm-library` (hyphen) consistently across:
  - `common/library_manager.py`
  - `Dockerfile`
  - `docker-compose.yml`
  - `docs/ARCHITECTURE.md`
  - `docs/USER_GUIDE.md`
- Fixed Turtle generation bugs in `shacl_export.py`:
  - Schema references now use prefixed names instead of angle brackets
  - Brick names with spaces are sanitized (spaces → underscores)
  - Prefix collector now scans edge-referenced bricks (fixes missing foaf: prefix)

## Completed (2026-05-20)

1. ✅ Docker smoke test — schema:200, brick:200
2. ✅ Fix `docs/TROUBLESHOOTING.md` — stale references replaced
3. ✅ Smoke test script — `test_smoke.py`, 11/11 passing
4. ✅ "Import SHACL" UI button — brick app Qt GUI
5. ✅ Docker Hub publish — via GitHub CI
6. ✅ Schema App Qt — `open_ui_metadata_editor` wired to `UIMetadataPanelDialog`
7. ✅ Schema App Qt — `create_daisy_chain` removed (out of scope for this tool)
8. ✅ Schema App Qt — `validate_schema` implemented (tree structure check)
9. ✅ Schema App Qt — `add_schema_reference` implemented (sh:node cross-schema ref)
10. ✅ Schema App Qt — `extend_schema` implemented (inheritance-based schema copy)
11. ✅ Schema App Qt — `generate_web_form` now opens browser preview automatically
12. ✅ `UiLoader.load_dialog()` method added
13. ✅ Absolute imports → relative imports in `schema_gui.py`
14. ✅ Tree items now store `brick_id` as UserRole data

## How to Launch

```bash
# Desktop
uv run python run_brick_app_qt.py
uv run python run_schema_app_qt.py

# Web
uv run python run_brick_app_web.py    # → http://localhost:5001
uv run python run_schema_app_web.py   # → http://localhost:5000

# Docker
./dev-start-schema-docker.sh          # → http://localhost:5000
./dev-start-brick-docker.sh           # → http://localhost:5001

# Tests
uv run python -m pytest test_smoke.py -v
```

## Testing Semantic Awareness (Pending)

To test the new semantic awareness feature:

```bash
cd /home/heinz/1_Gits/ShaclForms/DASH_GUI
uv run python run_brick_app_web.py
# Open http://localhost:5001
```

### Test Cases:

1. **QUDT Units**
   - Create brick → Add Property
   - Set Semantic Class to `qudt:Mass` (or browse QUDT ontology)
   - **Expected**: Unit dropdown appears with [kg, g, lb, oz]
   - Select a unit, save property

2. **Schema.org Suggestions**
   - Set Semantic Class to `schema:Person`
   - **Expected**: Suggested properties appear: [givenName, familyName, email, ...]
   - Click a suggestion → property path auto-fills

3. **FOAF Suggestions**
   - Set Semantic Class to `foaf:Person`
   - **Expected**: Suggested properties: [name, mbox, homepage, depiction, ...]

4. **SHACL Export**
   - Save brick with semantic class
   - Export to TTL
   - **Expected**: `sh:class foaf:Person ;` appears in property block

### API Test:
```bash
curl "http://localhost:5001/api/enrichment?class_iri=qudt:Mass"
```

## Files Modified Today

| File | Change |
|------|--------|
| `brick_app/core/brick_core_simple.py` | Added `sh_class` to `LeafProperty` |
| `brick_app/core/enrichment_engine.py` | **NEW** - EnrichmentEngine class |
| `brick_app/api/web_api.py` | Added `/api/enrichment` endpoint |
| `brick_app/api/templates/index.html` | Added enrichment widgets (web) |
| `brick_app/ui/property_editor.ui` | Added sh:class field (Qt) |
| `brick_app/gui_components.py` | Added sh_class handling (Qt) |
| `schema_app/core/shacl_export.py` | Export `sh:class` predicate |
| `common/library_manager.py` | Fixed library path (hyphen) |
| `Dockerfile` | Fixed library path |
| `docker-compose.yml` | Fixed library path |
| `docs/ARCHITECTURE.md` | Updated library path references |
| `docs/USER_GUIDE.md` | Updated library path references |

## Quick Start for Tomorrow

```bash
cd /home/heinz/1_Gits/ShaclForms/DASH_GUI
uv run python run_brick_app_web.py
# Test at http://localhost:5001
```

**What's Ready:**
- All 3 phases of semantic awareness implemented
- Backend enrichment API working
- Frontend widgets added (unit dropdown, suggested properties)
- Test cases documented above

**If Something Breaks:**
- Clear Python cache:
  ```bash
  find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +
  ```
- Clear browser cache and hard refresh (Ctrl+F5)

## Known Issues
- `common/` module is outside both sub-packages — fine for local/Docker use, breaks `pip install`
- `extend_schema` not exposed in web API (authoring-only feature)
- **Qt GUI**: Basic sh:class field added, but enrichment widgets (unit dropdown, suggestions) not yet implemented (web has full enrichment)
