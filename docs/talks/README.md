# Talks Directory

Presentation materials for DASH_GUI — SHACL Brick + Schema Editor

## Directory Structure

```
talks/
├── README.md                 # This file
├── basic_intro/              # Non-technical audience (30-45 min)
│   └── README.md            # Full slide guide + demo script
├── technical_deep_dive/      # Technical audience (45-60 min)
│   └── README.md            # Architecture, enrichment layers, implementation
└── hands_on_workshop/        # Developer workshop (2-3 hours)
    └── README.md            # Step-by-step exercises
```

## Choosing the Right Talk

| Talk Type | Audience | Duration | Goal |
|-----------|----------|----------|------|
| **Basic Intro** | Policy makers, industry, students | 30-45 min | Understand the brick→schema→form approach |
| **Technical Deep Dive** | Developers, architects, data engineers | 45-60 min | Architecture, enrichment engine, SHACL export |
| **Hands-on Workshop** | Developers, technical staff | 2-3 hours | Build bricks and schemas themselves |

## Key Metaphors (Use Across All Talks)

- **Lego bricks** → Reusable SHACL components
- **Grammar rules** → SHACL validation
- **Autocomplete** → Enrichment engine
- **Blueprints** → Schemas that assemble bricks

## Common Demo Materials

All talks use the same demo setup:
- **Pre-loaded bricks**: Mass, Temperature, BatteryCapacity, Manufacturer
- **Example schema**: "Demo EV Battery" (empty shell)
- **Live apps**: brick_app (port 5001), schema_app (port 5000)

**Critical demo moment**: The unit dropdown appearing automatically when a qudt:Mass brick is used. Pause there.

## Creating a New Talk

1. Create subdirectory: `mkdir talks/your_talk_name`
2. Copy template from existing talk
3. Adjust for your audience depth
4. Test demo flow end-to-end
5. Add to this README

## Presentation Tips (All Talks)

1. **Speak slowly** during the unit dropdown reveal—this is the magic moment
2. **Use your cursor** as a pointer—circle the icons, dropdowns, tree structure
3. **Have backup screenshots** in case live demo fails
4. **Pause after key points**—let the audience absorb
5. **End 5 minutes early** for questions

## External Resources

- [SHACL W3C Spec](https://www.w3.org/TR/shacl/) (for technical talks)
- [DASH Ontology](https://datashapes.org/) (widget system)
- [QUDT Ontology](http://www.qudt.org/) (units and quantities)
- EU Digital Product Passport documentation (regulatory context)

## Contact

For questions about talks or to request a new talk outline, see the main project README.
