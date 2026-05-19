# Session Status
Last updated: 2026-05-19

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

## Next Steps (Priority Order)

1. **Docker smoke test**
   ```bash
   ./dev-start-schema-docker.sh
   # verify http://localhost:5000 loads
   ./dev-start-brick-docker.sh
   # verify http://localhost:5001 loads
   ```

2. **Fix `docs/TROUBLESHOOTING.md`** — still has `run_tasks.py` references

3. **Add smoke test script** — create `tests/test_smoke.py` that instantiates:
   - `BrickCore`, `BrickService`, `OntologyManager` from `brick_app_v2`
   - `SchemaBackend` / equivalent from `schema_app_v2`

4. **"Import SHACL" UI button** in brick app Qt GUI
   - API endpoint already exists: `POST /api/import/shacl` in `brick_app_v2/api/web_api.py`
   - Just needs a button + file dialog in `brick_editor.py`

5. **Docker Hub publish**
   ```bash
   ./dev-docker-publish-hub.sh
   ```
   Only after Docker smoke test passes.

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
```

## Known Issues
- `docs/TROUBLESHOOTING.md` still has stale `run_tasks.py` references (non-critical)
- `common/` module is outside both sub-packages — fine for local/Docker use, breaks `pip install`
- No automated test suite yet
