# SHACL Knowledge Graph Authoring System - Project Memory

## Project Status
**Current State**: Working SHACL form generator completed
**Last Updated**: 2026-04-12

## Working Files
- `/home/heinz/1_Gits/DASH_GUI/working_shacl_form.html` - Fully functional SHACL form generator
- `/home/heinz/1_Gits/DASH_GUI/shacl_builder.py` - Python SHACL component library
- `/home/heinz/1_Gits/DASH_GUI/shacl_frontend.py` - SHACL editor frontend (PyQt6)
- `/home/heinz/1_Gits/DASH_GUI/shacl_backend.py` - SHACL editor backend logic
- `/home/heinz/1_Gits/DASH_GUI/rdflib_test.html` - RDFLib functionality test
- `/home/heinz/1_Gits/DASH_GUI/minimal_pyscript_test.html` - Basic PyScript test

## Achievements
1. ✅ Fixed PyScript syntax issues (URL parsing problems)
2. ✅ Created working SHACL-to-browser form generator
3. ✅ Demonstrated complete workflow: SHACL generation -> Form building -> RDF data capture
4. ✅ Successfully tested with Person shape (fullName, email, birthDate)
5. ✅ Built SHACL editor with frontend/backend separation
6. ✅ Integrated public ontology support (FOAF, Schema.org, DCTERMS)
7. ✅ Implemented brick-based SHACL construction system

## Architecture Overview

### Two-Step Workflow
1. **SHACL Editor Phase**: Visual brick creation from public ontologies
2. **Form Generation Phase**: Browser-based forms from SHACL shapes

### Frontend/Backend Separation
- **Backend** (`shacl_backend.py`): Pure SHACL logic, brick generation, event processing
- **Frontend** (`shacl_frontend.py`): PyQt6 UI, ontology browser, brick tree, SHACL preview

### Brick System
- **NodeShape Bricks**: For ontology classes with targetClass
- **PropertyShape Bricks**: For properties with constraints (datatype, minCount, maxCount)
- **Primitive Bricks**: For reusable data types (string, integer, date, etc.)

## Technical Solutions
- **Programmatic SHACL graph creation** - Avoids HTML parsing issues
- **PyScript with RDFLib in browser** - Dynamic form generation
- **Event-driven architecture** - Clean frontend/backend communication
- **Public ontology integration** - FOAF, Schema.org, DCTERMS support
- **Real-time SHACL and RDF output display**

## Key Insights
- PyScript interprets URLs in strings as HTML tags - need programmatic approach
- RDFLib works correctly in PyScript environment
- User wants visual SHACL editor (not pre-programmed shapes)
- Two-tier ontology/term system for domain-specific terminology
- Frontend/backend separation essential for maintainability

## PyQt6 Compatibility Issues Resolved
- `Qt.UserRole` → `Qt.ItemDataRole.UserRole`
- `QApplication.exec_()` → `QApplication.exec()`
- `Dialog.exec_()` → `Dialog.exec()`

## Next Development Steps
1. **Enhance Ontology Support**: Add more public ontologies
2. **Improve Brick System**: Add more SHACL constraint types
3. **Form Integration**: Better integration between editor and form generator
4. **Validation**: Real-time SHACL validation in editor
5. **Export Options**: Multiple export formats (JSON, RDF/XML, etc.)

## Usage Instructions

### SHACL Editor
```bash
cd /home/heinz/1_Gits/DASH_GUI
python3 shacl_frontend.py
```

### Browser Form Generator
```bash
cd /home/heinz/1_Gits/DASH_GUI
python3 -m http.server 8000
# Then visit: http://localhost:8000/working_shacl_form.html
```

## Integration with PeriConto
The SHACL editor follows the same architectural patterns as the PeriConto ontology builder:
- Event-driven backend processing
- Visual brick/tree construction
- Component reuse system
- Clean frontend/backend separation

## File Structure
```
DASH_GUI/
├── shacl_frontend.py          # PyQt6 frontend UI
├── shacl_backend.py          # Backend logic and brick system
├── working_shacl_form.html    # Browser form generator
├── shacl_builder.py          # Original SHACL component library
└── project_memory.md         # This memory file
```

## Git Integration
This file should be committed to git to track project progress and enable quick context restoration for future development sessions.

## Memory Reload Instructions
When returning to the project after a break:

### Quick Context Restoration
1. **Read the memory file**:
   ```bash
   cat /home/heinz/1_Gits/DASH_GUI/project_memory.md
   ```

2. **Review current status** - Check "Project Status" and "Achievements" sections

3. **Understand architecture** - Review "Architecture Overview" and "Technical Solutions"

4. **Check usage instructions** - Review "Usage Instructions" for both editor and form generator

5. **Continue development** - Use "Next Development Steps" as guidance

### For AI Assistant Context
When working with an AI assistant on this project:
1. **Share this memory file** to provide complete project context
2. **Reference specific sections** for quick understanding
3. **Update the file** after major changes or achievements

### Manual Memory Updates
After significant development sessions, update this file with:
- New achievements completed
- Architecture changes made
- Issues encountered and resolved
- New files created or modified
- Updated next development steps

This ensures continuity across development sessions and team collaboration.
