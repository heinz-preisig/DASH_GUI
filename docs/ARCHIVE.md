# Archive Directory

This directory contains legacy and experimental components that are not part of the main v2 implementation but may be useful for reference or future development.

## Archived Components

### Refactored Components (May 2026)
Architecture changed from global state to local state. These components were archived:

#### State Management (Replaced by Local State)
- `brick_app/state/` - Global `app_state_manager` module
  - `app_state.py` - Centralized state management (now local in GUI classes)

#### Business Logic (Replaced by brick_service.py)
- `brick_app/business/brick_operations.py` - Old business logic with global state dependencies

#### UI Abstractions (Removed)
- `brick_app/ui/ui_abstraction.py` - Unused UI abstraction layer
- `brick_app/ui/constraint_manager.py` - Constraint manager (depends on old state)
- `brick_app/ui/__init__.py` - Import file for removed modules

#### GUI Files (Renamed)
- `brick_app/refactored_gui.py` → `brick_editor.py` (renamed after refactoring complete)

### Legacy Applications
- `shacl_brick_app/` - Original SHACL brick generator application
- `guided_brick_gui/` - Guided brick creation GUI
- `guided_brick_gui.py` - Standalone guided brick GUI

### Legacy Launchers
- `launch_brick_generator.py` - Original brick generator launcher
- `run_brick_app.py` - Legacy brick app launcher
- `run_schema_app.py` - Legacy schema app launcher
- `run_schema_app_final.py` - Previous version of v2 launcher

### Test Files
- `test_imports.py` - Import testing utilities
- `test_schema_app.py` - Schema app v2 tests
- `test_simple_gui.py` - Simple GUI tests
- `test_schemas/` - Test schema files

### Legacy Repositories
- `brick_repositories_v2/` - Empty v2 brick repository structure
- `brick_repositories_v2_test/` - Test brick repository
- `default_brick_repository/` - Default brick repository template
- `topbraid_repositories/` - TopBraid integration repositories

Note: All repositories remaining in the root directory (`brick_repositories/`, `schema_repositories/`, `ontologies/`) are actively used by the v2 applications and are not archived.

### Documentation
- `BRICK_APP_STATUS.md` - Legacy brick app status (May 2026, pre-Docker)
- `GUI_LAUNCH_GUIDE.md` - Legacy GUI launch guide
- `IMPLEMENTATION_STATUS.md` - Previous implementation status
- `LIBRARY_MANAGEMENT.md` - Library management documentation
- `MULTI_TENANT_ARCHITECTURE.md` - Multi-tenant architecture docs
- `ontology_browser_fix_history.md` - Ontology browser fix history
- `project_memory.md` - Project memory documentation

### Other Files
- `working_shacl_form_with_help.html` - Working SHACL form with help

## Current Active Implementation

The main implementation now focuses on:
- `brick_app/` - Core brick management system
- `schema_app/` - Schema construction system
- `brick_repositories/` - Active brick repository
- `schema_repositories/` - Schema repository
- `run_schema_app.py` - Main launcher

## Restoration

If needed, items can be restored from this archive by moving them back to the root directory.
