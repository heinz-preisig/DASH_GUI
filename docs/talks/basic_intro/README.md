# DASH_GUI Talk Guide
## "From Bricks to Forms: Building Digital Product Passports with SHACL"

**Audience**: Non-technical (policy makers, industry, students)  
**Duration**: 30-45 minutes  
**Goal**: Understand the brick→schema→form approach without coding knowledge

---

## Slide Structure

### Slide 1: Title
**Title**: From Bricks to Forms: Building Digital Product Passports  
**Subtitle**: A visual approach to structured data using SHACL  

**Notes**: Thank organizers, set expectations: "No coding required to understand this"

---

### Slide 2: The Problem
**Title**: Digital Product Passports Are Hard

**Visual**: 
- Left: Messy stack of PDFs, Excel files, paper forms
- Right: Sad face emoji

**Talking Points**:
- "Every company describes the same product differently"
- "One says 'weight: 5kg', another says 'mass: 5000g', another just '5'"
- "Computers can't understand this—it's just text"
- "Result: Manual data entry, errors, compliance headaches"

---

### Slide 3: The Vision
**Title**: What If Data Had Grammar?

**Visual**:
```
❌ "The product weighs about 5kg usually"  (ambiguous)

✓ Product.weight = 5 kg                    (precise)
  - Must be a number
  - Must have a unit
  - Unit can be kg, g, lb, oz
```

**Talking Points**:
- "Like grammar rules in language, data needs rules too"
- "SHACL is a standard for writing these rules"
- "It's readable by humans AND checkable by computers"

---

### Slide 4: The Lego Metaphor
**Title**: Legos for Data Schemas

**Visual**: 
- Photo of actual Lego bricks
- Arrow →
- Diagram of "Mass" brick, "Temperature" brick, "Company" brick

**Talking Points**:
- "Instead of building from scratch every time..."
- "Create reusable 'bricks' once, snap them together"
- "Mass brick knows: number + unit (kg, g, lb, oz)"
- "Temperature brick knows: number + degrees (C, F, K)"

---

### Slide 5: The Brick Editor
**Title**: Creating Reusable Bricks

**Visual**: Screenshot of brick_app (or mockup)
- Highlight: Creating a "BatteryCapacity" brick
- Datatype: xsd:decimal
- Class: qudt:ElectricCharge (triggers unit dropdown)

**Talking Points**:
- "Here we define what a 'Battery Capacity' field looks like"
- "It knows it's a number with units (Ah, mAh, Coulombs)"
- "Do this once, use in every battery schema forever"

---

### Slide 6: From Bricks to Schemas
**Title**: Assembling Bricks into Product Schemas

**Visual**: 
```
EV Battery Schema:
├── Battery Identification (NodeShape)
│   ├── Model Number (string)
│   ├── Serial Number (string)
│   └── Manufacturer (link to Company)
├── Physical Properties (NodeShape)
│   ├── Mass → [Mass brick] → unit dropdown
│   ├── Dimensions → [Dimensions brick]
│   └── Capacity → [BatteryCapacity brick]
└── Environmental (NodeShape)
    ├── Carbon Footprint → [CO2 brick]
    └── Recyclability → [Percent brick]
```

**Talking Points**:
- "This is a schema editor—like a visual blueprint"
- "Each box is a brick we defined earlier"
- "The tree shows hierarchy: Battery contains Physical Properties"
- "Arrow shows: Mass brick gives us a unit dropdown automatically"

---

### Slide 7: The Magic—One Source, Many Forms
**Title**: One Schema → Multiple Representations

**Visual**: Three columns:
```
[Brick Definition]      [SHACL Rules]         [User Form]
Mass brick            sh:property [         [5] [▼kg]
- number              sh:path :mass;          [10] [▼g]
- unit                sh:datatype xsd:dec;  [0.005] [▼t]
- units: kg,g,lb      sh:class qudt:Mass;    
                      sh:in (unit:KG unit:G  
                             unit:LB...)
```

**Talking Points**:
- "Same Mass brick produces three things"
- "Middle column: validation rules (SHACL)"
- "Right column: what the user sees—dropdown with 6 units"
- "Change the brick once, every form updates"

---

### Slide 8: Enrichment—The Secret Sauce
**Title**: Smart Widgets from Context

**Visual**:
```
User selects: qudt:Mass
                ↓
System queries: QUDT ontology
                ↓
Auto-finds: 6 applicable units (kg, g, lb, oz, mg, t)
                ↓
Creates: Unit dropdown widget
```

**Talking Points**:
- "This is the enrichment engine—like autocomplete for meaning"
- "When you say 'this is a Mass', it looks up what units exist"
- "No manual configuration needed"
- "Works for temperature, pressure, energy—any physical quantity"

---

### Slide 9: Architecture (High Level)
**Title**: How It All Connects

**Visual**: Simple flow diagram
```
[Shared Ontologies] ← QUDT, Schema.org, FOAF, SKOS
         ↓
[Brick Library] ← Reusable building blocks
         ↓
[Schema Composer] ← Assemble bricks into products
         ↓
[SHACL Exporter] ← Validation rules
         ↓
[Form Generator] ← HTML interface
         ↓
[Validated Data] ← Ready for passports
```

**Talking Points**:
- "Shared ontologies: public dictionaries everyone uses"
- "Brick library: your organization's reusable parts"
- "Schema composer: product-specific blueprints"
- "Form generator: what the data entry clerk sees"

---

### Slide 10: Live Demo Setup
**Title**: Let's See It Work

**Visual**: Screenshot of starting state
- Brick app open with pre-loaded bricks
- Schema app ready

**Demo Script** (see below)

---

### Slide 11: Real-World Impact
**Title**: Why This Matters

**Visual**: Before/After comparison
```
BEFORE:                          AFTER:
- 3 months to define passport    - 1 week (assemble existing bricks)
- Manual unit conversions        - Automatic dropdowns
- 50 validation errors           - 2 errors (caught early)
- Inconsistent across products   - Standardized
```

**Talking Points**:
- "This isn't theoretical—it's built for the EU Digital Product Passport"
- "Reduces schema development from months to days"
- "Ensures consistency across thousands of products"
- "Non-technical users can build schemas via point-and-click"

---

### Slide 12: Summary
**Title**: Key Takeaways

**Visual**: Three icons with text
1. 🧱 **Bricks** = Reusable, semantic data components
2. 🔗 **SHACL** = Standardized validation rules
3. 🎨 **Forms** = Automatic user interfaces

**Talking Points**:
- "Bricks capture meaning (Mass knows its units)"
- "SHACL ensures data quality (can't skip required fields)"
- "Forms make it usable (dropdowns, not text boxes)"
- "All from a single source of truth"

---

### Slide 13: Q&A
**Title**: Questions?

**Visual**: Your contact info, GitHub repo, demo links

---

## Live Demo Script (10 minutes)

### Setup (Do before talk)
- Have brick_app running on localhost:5001
- Have schema_app running on localhost:5000
- Pre-load with example bricks: Mass, Temperature, BatteryCapacity
- Create example schema: "Demo EV Battery" (empty, ready to build)

### Demo Flow

**Step 1: Show Existing Bricks (2 min)**
1. Open brick_app web UI
2. Show brick list: "These are our reusable building blocks"
3. Click on "Mass" brick
4. Point out:
   - Path: ex:mass
   - Datatype: xsd:decimal
   - Class: qudt:Mass (this triggers the magic)
   - No units listed here—they come from the ontology!
5. "This brick knows what it is, not just what it's called"

**Step 2: Create Simple Schema (3 min)**
1. Open schema_app web UI
2. "Create New Schema" → name: "Demo EV Battery"
3. Add component: Select "Mass" brick
4. Show tree view:
   - ⬡ Demo EV Battery (root)
   - ⬡ Mass (child)
5. "Notice the icons: hexagon = NodeShape, rectangle would be PropertyShape"
6. "Click the ▶ to expand/collapse—handles deep nesting"

**Step 3: Export and Show Form (3 min)**
1. Click "Export DASH Form"
2. Opens HTML form in new tab
3. **Key moment**: Scroll to Mass field
4. "Look—automatic unit dropdown! kg, g, lb, oz, mg, tonne"
5. "This came from the QUDT ontology, not manual configuration"
6. Enter a value: 500
7. Change unit to kg
8. Click "Review & Submit"
9. Show generated Turtle data
10. "This is valid SHACL—can be validated, queried, stored"

**Step 4: The Payoff (2 min)**
1. Back in schema_app
2. "What if we need 100 different battery schemas?"
3. "Same Mass brick, same automatic units"
4. "Change the brick once → 100 forms update"
5. "That's the power of reusable, semantic components"

---

## Backup Slides (if questions arise)

### Backup 1: SHACL Basics
Show simple Turtle (only if asked):
```turtle
ex:Battery a sh:NodeShape ;
    sh:property [
        sh:path ex:mass ;
        sh:datatype xsd:decimal ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] .
```
Say: "This is what the computer sees—rules that can be checked automatically"

### Backup 2: Enrichment Layers
Show the 4-layer table (from STATUS.md) if technical audience asks how it works.

### Backup 3: Architecture Deep Dive
Show the file structure diagram if someone asks about implementation.

---

## Tips for Delivery

1. **Speak slowly** when showing the demo—let people absorb the unit dropdown appearing
2. **Pause after key points**: "Notice it just... knew... the units"
3. **Use the mouse cursor** as a pointer—circle the dropdown, the icons
4. **Have a backup screenshot** in case live demo fails
5. **End 5 minutes early** for questions—people always ask about "can it do X?"

## Common Questions & Answers

**Q: Can non-programmers use this?**  
A: Yes—brick_app and schema_app are point-and-click web interfaces.

**Q: Does it work with our existing databases?**  
A: Exported SHACL validates data—can export to JSON, XML, or RDF for any system.

**Q: What about proprietary/vocabulary we invented?**  
A: Can load custom ontologies—enrichment works with any RDF vocabulary.

**Q: Is this production-ready?**  
A: Core is stable—used in EU DPP pilots. UI polish ongoing.

**Q: How does this compare to JSON Schema?**  
A: SHACL is more expressive (semantic units, linked data)—but can convert between them.

---

## Checklist Before Talk

- [ ] Both apps running and tested
- [ ] Pre-loaded bricks visible (Mass, Temperature, etc.)
- [ ] Demo schema created (empty "Demo EV Battery")
- [ ] Screen resolution set (1024x768 minimum, 1920x1080 ideal)
- [ ] Backup screenshots saved (in case live demo fails)
- [ ] Water nearby (talking is thirsty work!)

---

Good luck! The system sells itself once people see the unit dropdown appear automatically.
