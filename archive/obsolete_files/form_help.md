# SHACL Form Help

## Overview
This form helps you create RDF data using SHACL shapes. The form is dynamically generated from SHACL constraints.

## How to Use

### 1. Generate Form
- Click **"Generate Form"** to create input fields
- The form is built from SHACL shapes defined in the system

### 2. Fill in Data
- **Required fields** are marked with an asterisk (*)
- **Date fields** use date picker for proper formatting
- **Text fields** accept any string input

### 3. Save RDF Data
- Click **"Save RDF Data"** to convert form input to RDF triples
- The RDF output appears in the **RDF Output** panel

## Field Types

### Text Fields
- Accept any string input
- Used for names, descriptions, etc.

### Date Fields  
- Use date picker for selection
- Automatically formatted as ISO dates
- Example: `2026-04-14`

### Email Fields
- Basic email format validation
- Example: `user@example.org`

## RDF Output

The generated RDF follows this structure:
```turtle
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:instance1 a ex:Person ;
    ex:fullName "John Doe" ;
    ex:email "john@example.org" ;
    ex:birthDate "1951-02-06"^^xsd:date .
```

## Tips

- **Save frequently** - RDF data is only generated when you click "Save RDF Data"
- **Check output** - Review the RDF panel to ensure correct data
- **Required fields** - Must be filled for valid RDF generation

## Troubleshooting

### Form Not Generating
- Ensure SHACL shapes are properly loaded
- Check browser console for errors

### RDF Not Saving
- Verify all required fields are filled
- Check field formats (dates, emails)

### Invalid RDF Output
- Review input data for special characters
- Ensure proper field formatting

## Advanced Features

### Custom SHACL Shapes
- Use the SHACL Editor to create custom shapes
- Export shapes and reload the form

### Multiple Instances
- Each save creates a new instance with unique ID
- Previous instances are preserved in the output

## Support

For issues or questions:
1. Check the browser console for JavaScript errors
2. Verify SHACL syntax in the preview panel
3. Consult the project documentation in `project_memory.md`
