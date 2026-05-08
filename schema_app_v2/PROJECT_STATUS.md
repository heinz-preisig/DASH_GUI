# Schema App v2 - Project Status Documentation

**Last Updated:** May 8, 2026  
**Purpose:** Session hand-off reference — current state, architecture, and next steps.

---

## Project Overview

**Schema App v2** is a SHACL schema editor with brick-based composition. Users create, edit, and export SHACL schemas built from reusable brick components. The application supports a PyQt6 desktop interface backed by a multi-tenant session architecture, and can generate DASH-compatible HTML web forms directly from schemas.

### Key Features
- **SHACL Schema Creation**: Build schemas from reusable NodeShape / PropertyShape bricks
- **Schema References**: Embed saved schemas into a parent schema via `sh:node` (`schema_refs`)
- **Multi-Tenant Backend**: Session isolation for concurrent users (Qt, Web, API)
- **UI Metadata System**: Sequences, groups, and parent-child relationships on components
- **Tree View**: Hierarchical QTreeWidget showing root brick → groups → components → schema refs
- **List View**: Flat ordered list with context-menu reordering and metadata editing
- **DASH Form Generation**: `core/dash_integration.py` produces HTML forms from hierarchical schemas
- **SHACL Export**: Turtle export saved alongside each schema JSON; user-triggered file export
- **Flow Engine**: Multi-step data entry workflows (linear, branching, conditional)
- **Event System**: Real-time updates across multiple clients

---

## Architecture

### Directory Structure
```
schema_app_v2/
├── core/
│   ├── schema_core.py             # Schema + UIMetadata data structures; all tree queries
│   ├── brick_integration.py       # Brick library access and NodeShape/PropertyShape types
│   ├── shacl_export.py            # Turtle export (flat + hierarchical)
│   ├── dash_integration.py        # DASHFormGenerator → HTML forms from schemas
│   ├── flow_engine.py             # Flow configuration engine
│   ├── schema_helper.py           # User-friendly helper wrappers
│   ├── abstract_events.py         # Abstract event types for multi-client support
│   ├── session_manager.py         # Session lifecycle management
│   └── multi_tenant_backend.py    # Backend coordinator (Qt / Web / API sessions)
├── interfaces/
│   ├── qt/
│   │   ├── schema_gui.py          # SchemaGUI — wiring only; all logic in mixins
│   │   ├── mixins/                # Logic split by concern (see Mixin Architecture below)
│   │   │   ├── __init__.py
│   │   │   ├── schema_management.py   # CRUD, export, validate, extend, daisy-chain, library
│   │   │   ├── component_list.py      # Flat list: add/remove, schema refs, context menu
│   │   │   ├── component_tree.py      # Tree: rendering, groups, parent-child, context menu
│   │   │   ├── brick_panel.py         # Brick library panel, search, details
│   │   │   └── flow_management.py     # Flow type, edit flow dialog, flow steps list
│   │   ├── add_component_dialog.py
│   │   ├── flow_editor_dialog.py
│   │   ├── daisy_chain_editor_dialog.py
│   │   ├── help_dialog.py
│   │   ├── ui_metadata_panel_dialog.py
│   │   ├── ui_state_manager.py    # UIStateManager + SchemaState automaton
│   │   ├── ui_components.py       # UiLoader / ComponentManager utilities
│   │   └── ui/                    # Qt Designer .ui files
│   │       ├── main_window.ui
│   │       ├── add_component_dialog.ui
│   │       ├── flow_editor.ui
│   │       └── main_window_help.ui
│   └── web/                       # Flask interface (secondary, may lag behind Qt)
├── shared_libraries/              # Brick + schema JSON/TTL files on disk
├── main.py                        # Application entry point
├── test_tree_structure.py         # Tree structure + DASH integration tests
├── test_shacl_export.py
├── test_ui_metadata.py
├── test_flask_api.py
└── test_ui_metadata_api.py
```

### Mixin Architecture (Qt Interface)

`SchemaGUI` inherits from `QMainWindow` plus five mixins. `schema_gui.py` contains only `__init__`, `setup_ui`, and signal wiring.

| Mixin | File | Responsibility |
|---|---|---|
| `SchemaManagementMixin` | `mixins/schema_management.py` | New/open/save/delete/export SHACL/generate web form/validate/extend/daisy-chain/library management/preview |
| `ComponentListMixin` | `mixins/component_list.py` | Flat list refresh, add brick, remove brick, add schema reference, context menu (move up/down/remove/UI metadata) |
| `ComponentTreeMixin` | `mixins/component_tree.py` | Tree refresh, group nodes, parent-child nesting, schema-ref expansion, context menu (set parent/move to group/remove) |
| `BrickPanelMixin` | `mixins/brick_panel.py` | Brick library combo, search filter, brick details panel |
| `FlowManagementMixin` | `mixins/flow_management.py` | Flow type combo, flow editor dialog, flow steps list |

### Multi-Tenant Backend

- **`MultiTenantBackend`**: Coordinates sessions; each session gets isolated `SchemaCore`, `FlowEngine`, `BrickIntegration`
- **Session types**: `qt_session`, `web_session`, `api_session`
- **Event types**: `SCHEMA_CREATED/UPDATED/LOADED/SAVED/DELETED`, `COMPONENT_ADDED/REMOVED`, `ROOT_BRICK_SET`, `FLOW_UPDATED`, `LIBRARY_CHANGED`, `ERROR_OCCURRED`, `DIALOG_REQUESTED`, `STATUS_MESSAGE`
- **Event handlers**: `QtEventHandler` (Qt signals), `WebEventHandler` (WebSocket), `APIEventHandler` (HTTP callbacks)

### State Management

`UIStateManager` enforces a `SchemaState` automaton:
- States: `INITIAL`, `SCHEMA_SELECTED`, `SCHEMA_MODIFIED`, `SCHEMA_SAVING`, `COMPONENT_ADDING`, `FLOW_EDITING`
- Controls widget enable/visibility; validates transitions before execution

---

## Completed Work

### Core
✅ **Schema Management** (`schema_core.py`)
- Full CRUD; library management; schema extension/inheritance; daisy-chain

✅ **UI Metadata & Tree Queries** (`schema_core.py`)
- `UIMetadata` dataclass (sequence, group_id, parent_id, label, help_text, …)
- `schema_refs` list — embed other schemas via `sh:node` with `attach_to_brick_id` + `property_path`
- Tree queries: `get_ui_root_components`, `get_ui_children`, `get_hierarchical_tree`, `get_components_by_sequence`, `get_groups_by_sequence`, `get_schema_refs_for_brick`, `validate_tree_structure`

✅ **Brick Integration** (`brick_integration.py`)
- NodeShape / PropertyShape brick types; CRUD; SHACL per brick; shared_libraries integration

✅ **SHACL Export** (`shacl_export.py`)
- Flat Turtle export (`export_schema`); hierarchical export (`export_schema_hierarchical`)
- Auto-saved as `.ttl` alongside schema JSON on every save

✅ **DASH Form Generation** (`dash_integration.py`)
- `DASHFormGenerator.generate_dash_form()` → structured config dict
- `DASHFormGenerator.generate_dash_html_form()` → standalone HTML with DASH markup
- Accessible via "Generate Web Form" button in Qt UI

✅ **Flow Engine** (`flow_engine.py`)
- Linear, branching, conditional flows; step conditions; navigation rules; daisy-chain

✅ **Multi-Tenant Backend** (`multi_tenant_backend.py`)
- Session isolation; event-driven architecture; Qt/Web/API client support

### Qt UI
✅ **Mixin Refactor** (May 2026)
- `schema_gui.py` reduced from ~1000 lines to ~250 lines (wiring only)
- Logic split into five focused mixin classes
- All dialogs backed by `.ui` files

✅ **Component Tree View**
- Tree toggle (list ↔ tree) via `componentViewStack`
- Root brick as bold ◆ header node
- Groups as collapsible ▼ branches
- Parent-child nesting rendered recursively
- Schema references expanded inline (read-only, greyed, circular-reference guard)
- Context menu: set parent, move to group, remove from parent/group, move up/down, remove

✅ **Schema References**
- `add_schema_reference()`: pick schema → pick attach brick → enter `sh:node` property path
- Shown in both list view (⬡ prefix, blue colour) and tree view (⬡ prefix, italic grey)
- Removal via context menu or Remove button

✅ **SHACL Auto-Export**
- Every Save writes a `.ttl` alongside the JSON in `shared_libraries/schemas/{lib}/`

✅ **PyQt6 Migration**
- All Qt imports use `PyQt6`; `ItemDataRole.UserRole`, `DialogCode.Accepted`, etc.

### Testing
✅ `test_tree_structure.py` — tree validation, navigation, hierarchical SHACL export, DASH form generation

---

## Remaining Work / Next Steps

### High Priority

1. **Drag-Drop in Tree View**
   - Drag components onto group nodes or other bricks to set parent/group without the context menu
   - Use `QTreeWidget` internal drag-drop with `dropEvent` override

2. **Schema References — Inline Editing**
   - Currently schema refs are read-only in the tree; allow editing `property_path` after creation

3. **DASH Form — Dynamic Repeated Elements**
   - Support `sh:maxCount > 1` with JavaScript add/remove row
   - Handle nested schema ref sections as collapsible sub-forms

4. **Web Interface Parity**
   - `interfaces/web/` lags behind Qt interface; update Flask API to expose schema refs and tree structure

### Medium Priority

5. **Unit Tests**
   - Pytest suite for `schema_core.py` tree/ref methods
   - Mixin methods tested via a headless Qt fixture

6. **Error Handling**
   - Graceful recovery when a referenced schema is missing from the library
   - Better validation feedback in `validate_schema()` (check component brick IDs exist, etc.)

7. **Performance**
   - Caching brick lookups in `BrickIntegration` (currently re-reads disk on every `get_available_bricks()`)
   - Lazy tree expansion for schemas with > 50 components

### Low Priority

8. **Features**
   - Schema templates (pre-filled root + components)
   - Import from JSON Schema / XML Schema
   - Version history for schemas
   - Collaboration / multi-user editing

---

## How to Run

### Prerequisites
```
Python 3.10+
PyQt6
Flask
rdflib
```
```bash
pip install PyQt6 Flask rdflib
```

### Qt Interface
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2
python main.py
```

### Web Interface
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2/interfaces/web
python app.py
```

### Tests
```bash
cd /home/heinz/1_Gits/DASH_GUI/schema_app_v2
python test_tree_structure.py    # tree + DASH integration
python test_shacl_export.py
python test_ui_metadata.py
python test_flask_api.py
python test_ui_metadata_api.py
```

---

## Key Files Reference

### Core Logic
| File | Purpose |
|---|---|
| `core/schema_core.py` | Schema + UIMetadata + schema_refs + all tree queries |
| `core/brick_integration.py` | Brick library: read, write, search |
| `core/shacl_export.py` | Flat + hierarchical Turtle export |
| `core/dash_integration.py` | DASH HTML form generator |
| `core/flow_engine.py` | Flow configuration (linear/branching/conditional) |
| `core/multi_tenant_backend.py` | Session management + event routing |

### Qt UI
| File | Purpose |
|---|---|
| `interfaces/qt/schema_gui.py` | Main window — wiring only |
| `interfaces/qt/mixins/schema_management.py` | All schema CRUD + export actions |
| `interfaces/qt/mixins/component_list.py` | Flat list view logic |
| `interfaces/qt/mixins/component_tree.py` | Tree view logic |
| `interfaces/qt/mixins/brick_panel.py` | Brick library panel |
| `interfaces/qt/mixins/flow_management.py` | Flow editor integration |
| `interfaces/qt/ui_state_manager.py` | SchemaState automaton |
| `interfaces/qt/ui_metadata_panel_dialog.py` | UIMetadata editor dialog |

### UI Designer Files
- `interfaces/qt/ui/main_window.ui`
- `interfaces/qt/ui/add_component_dialog.ui`
- `interfaces/qt/ui/flow_editor.ui`
- `interfaces/qt/ui/main_window_help.ui`

---

## Important Notes

### Shared Libraries
- Brick JSONs: `shared_libraries/bricks/{lib_name}/`
- Schema JSONs + TTLs: `shared_libraries/schemas/{lib_name}/`
- `shared_libraries/library_manager.py` manages library metadata

### Data Persistence
- Schema JSON embeds all `ui_metadata`, `groups`, `schema_refs`
- SHACL `.ttl` is auto-generated on save (not the source of truth)

### Session Isolation
- Each client session has isolated `SchemaCore`, `FlowEngine`, `BrickIntegration`
- Shared data via `shared_libraries`; events routed by `EventRouter`

### Qt Version
- **PyQt6** is used throughout (not PyQt5). Use `Qt.ItemDataRole`, `QDialog.DialogCode`, etc.

---

## Project Context

Part of the larger **DASH_GUI** system. Goal: author SHACL schemas visually, then render them as browser-based DASH data-entry forms.

**Related Projects:**
- `brick_app_v2/` — brick library editor (sibling directory)
- `ontologies/` — cached ontologies used in property suggestions

**Key Design Decisions Made:**
1. Schema hierarchy represented via `schema_refs` (embedded schemas via `sh:node`) rather than flat inheritance
2. Groupings stored in schema metadata (`schema.groups`), not in SHACL
3. Qt GUI split into mixin classes for maintainability; `schema_gui.py` is wiring only

---

**End of Documentation**
