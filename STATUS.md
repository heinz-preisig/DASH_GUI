# Session Status
Last updated: 2026-05-20

## What Was Done This Session

### Fixes Applied
- `common` module import path fixed in all 4 files that needed it:
  - `brick_app_v2/core/brick_core_simple.py`
  - `brick_app_v2/core/multi_tenant_backend.py`
  - `brick_app_v2/core/brick_backend.py`
  - `brick_app_v2/api/web_api.py`
  - Each now adds `DASH_GUI/` root to `sys.path` via `Path(__file__)` — no longer fragile
- `brick_app_v2/pyproject.toml` — `packages.find` now includes `business*`, `api*`, `ui*`
- `brick_app_v2/core/ontology_manager.py.backup` moved to `brick_app_v2/archive/`
- Empty dirs removed: `interfaces/`, `gui/`, `schema/core/`, `schema/gui/`
- `ontology_manager._parse_rdf_file` — malformed `schema.rdf` now silenced (was printing error on every startup)
- `progress.txt` added to `.gitignore`
- All docs updated — no more references to `run_tasks.py` (removed) or `start-schema-app.sh` (renamed):
  - `README.md`
  - `docs/QUICK_START.md`
  - `docs/USER_GUIDE.md`
  - `docs/README_V2_STATUS.md`
  - `docs/TASK_MANAGER.md` — deprecation notice added at top

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

## Known Issues
- `common/` module is outside both sub-packages — fine for local/Docker use, breaks `pip install`
- `extend_schema` not exposed in web API (authoring-only feature)
