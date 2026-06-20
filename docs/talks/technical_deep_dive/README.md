# Technical Deep Dive: DASH_GUI Architecture
## "SHACL, Enrichment, and the Brick Approach"

**Audience**: Developers, architects, data engineers, semantic web practitioners  
**Duration**: 45-60 minutes  
**Goal**: Understand the full architecture, enrichment layers, and implementation details

---

## Slide Structure

### Slide 1: Title
**Title**: DASH_GUI: A Technical Deep Dive  
**Subtitle**: Architecture, Enrichment, and SHACL Generation

---

### Slide 2: Agenda
**Title**: What We'll Cover

1. The Brick Approach — Semantic Component Reuse
2. Architecture Overview — Multi-Tenant Design
3. The Enrichment Engine — Layered Resolution
4. SHACL Export — From Bricks to Validation Rules
5. Web vs. Qt — Shared Core, Different Frontends
6. Live Demo — Under the Hood

---

### Slide 3: The Problem Space
**Title**: Why Traditional SHACL Authoring Fails

**Visual**: Comparison table
```
Traditional              |  Brick Approach
-------------------------|------------------------
Write raw Turtle         |  Compose visual bricks
Manual unit lists        |  Ontology-driven widgets
Copy-paste repetition    |  Reuse across schemas
Validation errors late   |  Enrichment hints early
```

**Talking Points**:
- SHACL is powerful but verbose
- Domain experts can't write Turtle
- Reuse is copy-paste, not semantic
- We need: visual + semantic + reusable

---

### Slide 4: The Brick Metaphor (Detailed)
**Title**: What Is a Brick?

**Visual**: Brick anatomy diagram
```
┌─────────────────────────────────────┐
│  Brick: "Mass"                      │
├─────────────────────────────────────┤
│  Path: ex:mass                       │
│  Datatype: xsd:decimal               │
│  Class: qudt:Mass  ←── triggers     │
│                      enrichment     │
├─────────────────────────────────────┤
│  Constraints:                        │
│  - minCount: 1                       │
│  - maxCount: 1                       │
│  - pattern: [0-9]+                   │
└─────────────────────────────────────┘
```

**Talking Points**:
- Brick = NodeShape + PropertyShapes
- Class field is key — triggers enrichment
- Stored as JSON, exported as SHACL

---

### Slide 5: Architecture Overview
**Title**: System Architecture

**Visual**: Component diagram
```
┌─────────────────────────────────────────────────────┐
│  Frontend Layer                                     │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │  Web (React)│  │  Qt (PyQt)  │                   │
│  │  Port 5001  │  │  Desktop    │                   │
│  └──────┬──────┘  └──────┬──────┘                   │
└─────────┼────────────────┼──────────────────────────┘
          │                │
          └────────┬───────┘
                   │ REST API
┌──────────────────┴──────────────────────────────────┐
│  Backend Layer (Multi-Tenant)                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  MultiTenantBackend                         │    │
│  │  ├── SessionManager                         │    │
│  │  ├── BrickCore (shared_libraries)          │    │
│  │  └── EventManager (cross-client sync)      │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
          │
┌─────────┴───────────────────────────────────────────┐
│  Core Services                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │ OntologyMgr │  │ Enrichment  │  │ SHACL Export │   │
│  │ (17 ontos)  │  │ Engine      │  │ (dash:editor)│   │
│  └─────────────┘  └─────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────┘
```

**Key Point**: Both web and Qt use the same BrickCore via MultiTenantBackend

---

### Slide 6: Shared Libraries
**Title**: The Shared Library System

**Visual**: Directory tree
```
shared_libraries/
├── bricks/
│   └── default/
│       └── bricks/
│           ├── mass_*.json
│           ├── temperature_*.json
│           └── ...
├── schemas/
│   └── default/
│       └── schemas/
│           ├── ev_battery_*.json
│           └── ...
└── ontologies/
    └── cache/
        ├── qudt-units.ttl (2906 units)
        ├── qudt_quantitykind.ttl (1217)
        ├── skos.rdf
        └── ...
```

**Talking Points**:
- Filesystem-based library discovery
- JSON storage for bricks/schemas
- TTL cache for ontologies
- Single source of truth across apps

---

### Slide 7: The Enrichment Engine (Layer 0)
**Title**: Layer 0: Datatype → Widget

**Visual**: Simple mapping
```
xsd:boolean    →  boolean_toggle  (checkbox)
xsd:date       →  date_picker     (calendar)
xsd:decimal    →  decimal_input   (number field)
xsd:anyURI     →  uri_input       (validated URL)
rdf:langString →  language_text   (multilingual input)
```

**Code snippet**:
```python
# enrichment_engine.py — driven by widget_rules.ttl, not hardcoded
rules_by_datatype = {
    "xsd:boolean": {"widget": "boolean_toggle"},
    "xsd:date":    {"widget": "date_picker"},
    # ... extensible: add new datatype rules in TTL, zero Python changes
}
```

**Key Point**: No ontology lookup needed—fast, always available. Pure datatype-to-widget mapping.

---

### Slide 8: The Enrichment Engine (Layers 1-2)
**Title**: Layers 1-2: Semantic Resolution (quantity example + SKOS example)

**Visual**: Two side-by-side flow diagrams
```
── Physical quantities (QUDT) ──────────────────
sh:class = qudt:Mass
    ↓ Layer 1: dimensional signature (1,0,0,0,0,0,0)
    ↓ Layer 2: query applicableUnit in QUDT graph
Widget: unit_dropdown  [kg, g, lb, oz, mg, t]

── Controlled vocabularies (SKOS) ──────────────
sh:class = skos:Concept  +  skos:inScheme <myVocab>
    ↓ Layer 2: extract concepts from scheme
Widget: skos_selector  [Option A, Option B, ...]
```

**Talking Points**:
- QUDT is one example — any ontology with the right structure works
- Layer 1 (dimensional signatures) is QUDT-specific; Layer 2 is generic predicate lookup
- SKOS controlled vocabularies trigger skos_selector with no code changes
- Rules declared in widget_rules.ttl — extend by adding TTL triples

---

### Slide 9: The Enrichment Engine (Layers 3-4)
**Title**: Layers 3-4: Namespace & Inheritance Fallbacks

**Visual**: Table of layer triggers
```
Layer | Trigger                 | What happens                      | Example
------|------------------------|-----------------------------------|---------------------------
  3   | Namespace prefix        | Suggest known properties          | foaf:Person → name, mbox…
  3   | Predicate match in onto | Suggest known properties          | schema:Thing → identifier…
  4   | rdfs:subClassOf chain   | Entity lookup (search-as-you-type)| foaf:Person ⊑ foaf:Agent
```

**Key Point**: Graceful degradation — unknown class? Try namespace. Still nothing? Fall back to plain text field.

**Talking Points**:
- Layers 3-4 work with *any* OWL/RDFS ontology loaded into the manager
- Load your proprietary ontology → its classes and subclass chains are immediately available
- No hardcoding of vocabulary names anywhere in Python — purely data-driven

---

### Slide 10: Widget Rules (Declarative)
**Title**: widget_rules.ttl — Declarative Configuration

**Visual**: Turtle excerpt
```turtle
dashgui:MassRule a dashgui:WidgetRule ;
    dashgui:widget "unit_dropdown" ;
    dashgui:dimensionalSignature "1 0 0 0 0 0 0" ;
    dashgui:siUnit <http://qudt.org/vocab/unit/KiloGM> ;
    dashgui:alternativeUnits (
        <http://qudt.org/vocab/unit/KiloGM>
        <http://qudt.org/vocab/unit/GM>
        <http://qudt.org/vocab/unit/LB>
    ) .

dashgui:SkosConceptSchemeRule a dashgui:WidgetRule ;
    dashgui:widget "skos_selector" ;
    dashgui:triggerPredicate <http://www.w3.org/2004/02/skos/core#inScheme> .
```

**Talking Points**:
- No hardcoded ontology names in Python
- Rules in TTL—extensible without code changes
- 12 dimensional signatures, 4 predicate rules, 3 subclassof rules

---

### Slide 11: SHACL Export Pipeline
**Title**: From Bricks to SHACL Turtle

**Visual**: Export flow
```
Brick (JSON)                              SHACL (Turtle)
────────────                              ──────────────
{
  "name": "Mass",
  "object_type": "NodeShape",
  "target_class": "ex:Mass",
  "leaf_properties": [{
    "path": "ex:value",
    "datatype": "xsd:decimal",
    "sh_class": "qudt:Mass"
  }]
}
                ↓  export_schema()
                ↓
schema:Mass a sh:NodeShape ;
    sh:targetClass ex:Mass ;
    sh:property [
        sh:path ex:value ;
        sh:datatype xsd:decimal ;
        sh:class qudt:Mass ;
        dash:editor dash:InstancesSelectEditor ;
        sh:in (unit:KG unit:G unit:LB ...) ;
    ] .
```

**Key Points**:
- Enrichment runs at export time
- `dash:editor` resolved from `sh:class` or `sh:datatype`
- `sh:in` populated from QUDT lookup

---

### Slide 12: DASH Widget Mappings
**Title**: Widget Types to DASH Editors

**Visual**: Mapping table
```
Widget Type        →  DASH Editor              →  Viewer
─────────────────────────────────────────────────────────
text               →  dash:TextFieldEditor     →  dash:LabelViewer
boolean_toggle     →  dash:BooleanSelectEditor →  dash:BooleanViewer
date_picker        →  dash:DatePickerEditor    →  dash:LabelViewer
unit_dropdown      →  dash:InstancesSelectEditor →  dash:LabelViewer
skos_selector      →  dash:InstancesSelectEditor →  dash:LabelViewer
entity_lookup      →  dash:AutoCompleteEditor  →  dash:LabelViewer
```

**Talking Point**: DASH (Data Shapes) provides the form widgets—SHACL provides the validation

---

### Slide 13: Web Architecture Detail
**Title**: Web Frontend: React + Babel

**Visual**: Simplified component tree
```
index.html (single file)
├── App
│   ├── SessionManager
│   ├── BrickList (sidebar)
│   ├── BrickEditor (main)
│   │   ├── BasicFields
│   │   ├── LeafPropertiesList
│   │   └── PropertyEditorModal
│   │       ├── DatatypeSelector
│   │       ├── OntologyBrowser (class selection)
│   │       └── EnrichmentDisplay (unit dropdown preview)
│   └── ConstraintEditorModal
```

**Technical Details**:
- Single-file React (Babel standalone, no build step)
- REST API calls to Flask backend
- Event-driven updates (WebSocket-ready architecture)

---

### Slide 14: Qt Architecture Detail
**Title**: Qt Frontend: PyQt6 + UI Files

**Visual**: Component structure
```
brick_editor.py (main window)
├── loadUi("property_editor.ui")  ← Qt Designer
│   ├── Constraint groups (dynamic show/hide)
│   ├── Datatype combo
│   └── Class browser button
├── gui_components.py
│   ├── PropertyEditorDialog
│   ├── ConstraintEditorDialog
│   └── SimpleOntologyBrowser
└── brick_core_simple.py (shared with web)
```

**Key Point**: Same BrickCore, different UI technology

---

### Slide 15: Multi-Tenancy Design
**Title**: Session Isolation & Event Broadcasting

**Visual**: Session diagram
```
┌─────────────────────────────────────────┐
│         MultiTenantBackend              │
├─────────────────────────────────────────┤
│  Session A (Web)  │  Session B (Qt)     │
│  ───────────────  │  ───────────────    │
│  BrickCore (view) │  BrickCore (view)   │
│  working on:      │  working on:        │
│  "EV Battery"     │  "Solar Panel"      │
│                   │                     │
│  Events ──────────┼────────────────→    │
│  brick_saved      │  brick_saved        │
│  (broadcast)      │  (received)         │
└─────────────────────────────────────────┘
```

**Talking Points**:
- Per-session BrickCore instances
- Shared library manager (filesystem)
- Cross-client event broadcasting
- Ready for collaborative editing

---

### Slide 16: Live Demo — Technical Deep Dive
**Title**: Under the Hood

**Demo Flow** (15 minutes):

1. **Show Enrichment API** (3 min)
   ```bash
   curl "http://localhost:5001/api/enrichment?class_iri=qudt:Mass"
   ```
   - Show JSON response with units
   - Explain: no hardcoding, ontology-driven

2. **Create Brick with Constraints** (4 min)
   - Open brick_app
   - Create "Certification" brick
   - Add properties: name (string, pattern), validDate (date)
   - Show constraint fields in UI

3. **Export and Inspect SHACL** (4 min)
   - Export brick to Turtle
   - Open in text editor
   - Point out: sh:pattern, sh:datatype, dash:editor

4. **Schema Assembly** (4 min)
   - Open schema_app
   - Create schema using Certification brick
   - Show tree view with expand/collapse
   - Export full schema
   - Validate with shacl-js or similar

---

### Slide 17: Extension Points
**Title**: How to Extend the System

**Visual**: Extension diagram
```
Current:                    Your Extension:
────────                    ───────────────
widget_rules.ttl    ────→   widget_rules.ttl
                             + your:CustomRule

OntologyManager     ────→   OntologyManager
(17 ontologies)              + your_ontology.ttl

BrickCore           ────→   BrickCore
(JSON storage)               + custom validators

SHACLExporter     ────→   SHACLExporter
(standard DASH)              + custom templates
```

**Talking Points**:
- Add custom widget rules to TTL
- Load proprietary ontologies
- Hook into export pipeline
- Everything is pluggable

---

### Slide 18: Performance & Scalability
**Title**: Numbers

**Visual**: Metrics table
```
Metric                      Value
─────────────────────────────────────────
Ontologies cached           17 (45MB TTL)
QUDT units                  2,906
Quantity kinds              1,217
Enrichment cache hit rate   ~95%
SHACL export time           <100ms per brick
Concurrent sessions tested  50+
Session memory footprint    ~10MB
```

**Key Points**:
- Caching at multiple levels (ontology, enrichment, brick)
- Lazy loading of ontology graphs
- JSON persistence is fast enough

---

### Slide 19: Related Work & Standards
**Title**: Where This Fits

**Visual**: Positioning diagram
```
                    SHACL (validation)
                         ↑
DASH (forms) ←── DASH_GUI ──→ TopBraid Composer
                         ↓
              Your SHACL toolchain
                         ↓
              RDF/JSON/JSON-LD data
```

**Talking Points**:
- Not a replacement for TopBraid—complementary
- Standard SHACL output—works with any validator
- DASH widgets are de facto standard

---

### Slide 20: Summary & Q&A
**Title**: Key Takeaways

1. **Bricks** = Semantic, reusable SHACL components
2. **Enrichment** = Ontology-driven widget selection (4 layers)
3. **Multi-tenant** = Web + Qt + API, shared core
4. **Extensible** = Add ontologies, rules, templates
5. **Standards-based** = SHACL + DASH, no vendor lock-in

**Resources**:
- GitHub: [your-repo]
- Demo: http://localhost:5001 (live)
- Docs: /docs in repository

---

## Demo Checklist

Before presenting:

- [ ] `uv run python run_brick_app_web.py` running on :5001
- [ ] `uv run python run_schema_app_web.py` running on :5000
- [ ] curl test enrichment endpoint works
- [ ] Pre-loaded bricks visible in UI
- [ ] Pre-created empty schema ready
- [ ] Text editor available to show exported TTL
- [ ] Browser DevTools closed (clean look)

---

## Technical Q&A Preparation

**Q: Why not use JSON Schema instead of SHACL?**
A: JSON Schema validates structure; SHACL validates semantics (linked data, units, ontologies). Can convert between them if needed.

**Q: How do you handle ontology versioning?**
A: Ontologies cached as files; version control via filenames. QUDT updates → reload cache.

**Q: Can this work with property graphs (Neo4j, etc.)?**
A: SHACL is RDF-native; but can export to JSON and map to property graphs. Validation happens before storage.

**Q: How is this different from TopBraid?**
A: TopBraid is full IDE for ontologists; this is streamlined for DPP authors. Complementary—can round-trip.

**Q: Why single-file React instead of proper build?**
A: Rapid prototyping, no build step for deployment. Production would use Vite/Webpack.

**Q: How does the enrichment cache work?**
A: EnrichmentEngine keeps in-memory cache per session; keys are class IRIs. Cleared on session end.

**Q: Why don't you use SPARQL to query the ontology graphs instead of Python graph traversal?**
A: SPARQL is already supported by rdflib (the underlying library) and is used in spirit — but the enrichment engine uses direct Python/rdflib graph traversal rather than SPARQL string queries. The reasons:
- **Performance**: direct triple iteration avoids SPARQL query parsing overhead; enrichment runs on every UI interaction.
- **Simplicity**: Python stack traces are easier to debug than SPARQL string construction errors.
- **Sufficiency**: the enrichment rules are straightforward pattern matches (dimensional signature, predicate lookup, namespace prefix, subClassOf chain) — SPARQL's expressive power is not needed.

SPARQL *would* add value if enrichment rules grew into complex cross-graph joins, or if you wanted external tools to interrogate the widget rule graph directly. For the current use case it would be over-engineering.

---

## Additional Materials

### Code Walkthrough (Optional 15 min)

If audience wants deeper dive:

1. **enrichment_engine.py** (5 min)
   - WidgetRules parsing
   - _try_dimensional() method
   - _build_unit_enrichment()

2. **shacl_export.py** (5 min)
   - _get_dash_editor() enrichment call
   - _get_unit_in_list() QUDT query
   - Turtle generation

3. **brick_core_simple.py** (5 min)
   - SHACLBrick dataclass
   - save_brick() JSON serialization
   - load_brick() deserialization

---

## After the Talk

Share with audience:
- GitHub repository link
- This talk guide (for their own presentations)
- Docker compose file for easy local setup
- Link to EU DPP documentation for context

---

Good luck with the deep dive! The architecture sells itself to technical audiences—emphasize the clean separation and standards compliance.
