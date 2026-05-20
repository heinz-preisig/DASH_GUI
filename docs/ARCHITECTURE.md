# DASH GUI — Architecture Reference

> Last updated: 2026-05-20

---

## Overview

The system builds hierarchical SHACL schemas that drive DASH browser-based data-entry forms.
It has two independent Qt applications that share a common data layer:

```
run_brick_app_qt.py    →  brick_app_v2/   (create & edit SHACL bricks)
run_schema_app_qt.py   →  schema_app_v2/  (assemble bricks into schemas, export TTL + HTML)
```

Both apps also expose a Flask REST API (`run_brick_app_web.py` / `run_schema_app_web.py`) and
share brick/schema data via an external library directory (`ShaclForm_library/` sibling to `DASH_GUI/`).

### Form Rendering

Schemas are exported as self-contained HTML files that load the
[`@ulb-darmstadt/shacl-form`](https://www.npmjs.com/package/@ulb-darmstadt/shacl-form)
JavaScript web component from CDN. The Python side generates the SHACL Turtle;
the Darmstadt component renders the interactive form in the browser.

---

## Core Data Model

### 1. `SHACLBrick`  *(brick_app_v2/core/brick_core_simple.py)*

A brick is **always** a `sh:NodeShape` with `sh:targetClass`.
It contains a flat list of leaf `sh:property` entries — **no nesting inside a brick**.

```python
@dataclass
class SHACLBrick:
    brick_id:         str
    name:             str
    description:      str
    template_type:    str          # BrickTemplateType value
    namespace:        str          # IRI prefix, e.g. "turbine"
    target_class:     str          # sh:targetClass IRI
    leaf_properties:  List[Dict]   # List of LeafProperty.to_dict()
    xone_alternatives: List[List[Dict]]  # only for xone_choice
```

### 2. `LeafProperty`  *(brick_app_v2/core/brick_core_simple.py)*

One `sh:property [...]` entry inside a `NodeShape`.

```python
@dataclass
class LeafProperty:
    path:          str            # sh:path IRI
    label:         str            # rdfs:label
    datatype:      Optional[str]  # xsd:string, xsd:decimal, …
    node_kind:     Optional[str]  # sh:IRI for dropdowns
    in_values:     List[str]      # sh:in (IRIs or literals)
    has_value:     Optional[str]  # sh:hasValue for static labels
    min_count:     int
    max_count:     Optional[int]  # None = unbounded
    description:   str
    min_inclusive: Optional[float]
    max_inclusive: Optional[float]
    single_line:   Optional[bool] # dash:singleLine
```

### 3. `BrickTemplateType`  *(brick_app_v2/core/brick_core_simple.py)*

Each template type maps to a specific SHACL leaf pattern and drives
a specialised editor form in the GUI.

| Template type       | SHACL pattern                                      | GUI fields shown            |
|---------------------|----------------------------------------------------|-----------------------------|
| `free_text`         | `sh:datatype xsd:string`                           | datatype, singleLine        |
| `decimal_with_unit` | `sh:datatype xsd:decimal` + `sh:in` unit selector | datatype, range, sh:in      |
| `dropdown_iri`      | `sh:nodeKind sh:IRI` + `sh:in`                     | sh:in list                  |
| `date_field`        | `sh:datatype xsd:date`                             | datatype (locked)           |
| `static_label`      | `sh:hasValue`                                      | has_value                   |
| `file_upload`       | custom `sh:datatype` (e.g. `digipass:stl`)         | datatype (free entry)       |
| `xone_choice`       | `sh:xone ( [...] [...] )`                          | alternatives list           |
| `custom`            | all fields editable                                | all                         |

---

## TTL Serialisation

### Brick standalone TTL  *(brick_app_v2/core/brick_ttl_serialiser.py)*

Written alongside `.json` on every save.

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix ex:   <http://example.org/turbine/> .

ex:TurbineShape a sh:NodeShape ;
    sh:targetClass ex:Turbine ;
    sh:property [
        sh:path ex:serialNumber ;
        rdfs:label "Serial Number" ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] .
```

### Schema hierarchical TTL  *(schema_app_v2/core/shacl_export.py)*

`SHACLExporter.export_schema()` does a **BFS edge-walk** over `Schema.edges`.
Parents always precede children in the output.
Each `NodeShape` block contains:
1. Its own leaf `sh:property` entries (from `SHACLBrick.leaf_properties`)
2. One `sh:property [sh:path … ; sh:node <ChildShape>]` block per outgoing `SchemaEdge`

```turtle
ex:TurbineShape a sh:NodeShape ;
    sh:targetClass ex:Turbine ;
    sh:property [ sh:path ex:serialNumber ; ... ] ;   ← leaf (from brick)
    sh:property [
        sh:path ex:hasAddress ;
        sh:node ex:AddressShape ;                      ← child edge
        rdfs:label "Address" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:order 0 ;
    ] .

ex:AddressShape a sh:NodeShape ;
    sh:targetClass ex:Address ;
    sh:property [ sh:path ex:street ; ... ] .
```

---

## Schema Data Model

### 4. `SchemaEdge`  *(schema_app_v2/core/schema_core.py)*

Explicit directed edge in the schema tree: **parent brick → child brick**.
Carries the SHACL `path_iri` used in the `sh:property [sh:path … ; sh:node …]` block,
plus UI metadata (`label`, `sequence`, `min_count`, `max_count`, `collapsible`, `description`).

```python
@dataclass
class SchemaEdge:
    child_brick_id:  str
    path_iri:        str            # sh:path IRI for this edge
    label:           str = ""       # rdfs:label on the sh:property block
    parent_brick_id: Optional[str]  # None = root-level edge
    min_count:       int = 1
    max_count:       Optional[int] = 1
    collapsible:     bool = True
    description:     str = ""
    sequence:        int = 0        # sh:order
```

### 5. `Schema`  *(schema_app_v2/core/schema_core.py)*

Holds all bricks referenced in a schema and the tree of `SchemaEdge` objects.
`UIMetadata` is retained for per-component display metadata (label, help text,
visibility) but is **not** used for parent-child relationships — that is
exclusively handled by `SchemaEdge`.

Key API:

```python
schema.add_edge(edge)                     # add SchemaEdge
schema.get_root_components()              # brick_ids with no parent edge
schema.get_children(parent_brick_id)      # direct child brick_ids
schema.get_parent(child_brick_id)         # parent brick_id or None
schema.get_edges_from(parent_brick_id)    # outgoing SchemaEdge objects
schema.get_hierarchical_tree()            # nested dict for UI tree widget
```

---

## Application Layers

### Brick App (`brick_app_v2/`)

```
main.py                        entry point (--gui / --web)
refactored_gui.py              QMainWindow — brick editor
gui_components.py              dialogs: LeafPropertyEditorDialog,
                               SimpleOntologyBrowser, ConstraintEditorDialog
state/app_state.py             AppStateManager — single source of truth
business/brick_operations.py   BrickBusinessLogic — no Qt imports
core/brick_core_simple.py      SHACLBrick, LeafProperty, BrickCore
core/brick_ttl_serialiser.py   TTL serialisation helpers
core/ontology_manager.py       loads cached ontology JSON files
ui/                            UIManager, formatters, constraint_manager
```

### Schema App (`schema_app_v2/`)

```
interfaces/qt/schema_gui.py              SchemaGUI — Qt main window (no mixins)
interfaces/qt/ui_metadata_panel_dialog.py UIMetadataPanelDialog — sequence/group/nesting editor
interfaces/qt/ui_components.py           UiLoader, ComponentManager utilities
interfaces/web/flask_app.py              Flask REST API (port 5000)
core/schema_core.py                      Schema, SchemaEdge, UIMetadata, SchemaCore
core/shacl_export.py                     SHACLExporter — BFS TTL + HTML form export
core/brick_integration.py                bridges schema_app to brick library
core/multi_tenant_backend.py             session isolation for web API
```

### Shared

```
common/library_manager.py      SharedLibraryManager — resolves ShaclForm_library/ path
ontologies/cache/              pre-loaded ontology JSON caches
```

### External Data

```
../ShaclForm_library/          sibling directory (outside the code repo)
  default/bricks/              brick JSON + TTL files
  default/schemas/             schema JSON files
```

---

## Key Design Decisions

1. **All bricks are NodeShapes.** There are no standalone PropertyShape bricks.
   Hierarchy is expressed via `SchemaEdge.path_iri` + `sh:node`, not via
   embedded PropertyShapes.

2. **Leaf properties live on the brick, not on the schema.**
   A brick carries its own `sh:property` entries. The schema only adds the
   *inter-brick* `sh:property [sh:path … ; sh:node …]` blocks via edges.

3. **`SchemaEdge` is the single source of parent-child truth.**
   `UIMetadata.parent_id` is gone. All tree traversal (`get_children`,
   `get_parent`, `get_root_components`) delegates to `schema.edges`.

4. **Template type drives both UI and TTL.**
   The `template_type` field on a brick selects which editor fields appear
   in `LeafPropertyEditorDialog` and which SHACL pattern
   `brick_ttl_serialiser` emits.

5. **JSON + TTL written on every save.**
   `BrickCore.save_brick()` always writes `<name>_<uuid>.json` and
   `<name>_<uuid>.ttl` side by side so the library is always inspectable
   as plain Turtle.

---

## Known Limitations

- `common/` module is outside both sub-packages — fine for local/Docker use, breaks `pip install`.
- `extend_schema` is only available in the Qt GUI, not exposed in the web API.
- `xone_choice` multi-alternative editor in the brick GUI is not yet implemented.
