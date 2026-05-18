# Pattern Presets Documentation

## Overview

Pattern presets provide a user-friendly way to add regular expression (regex) validation to SHACL property constraints without requiring knowledge of regex syntax. These presets use **international standards** by default, making them suitable for global applications.

## Available Pattern Presets

### International Standard Patterns

| Preset | Description | Pattern | Example |
|--------|-------------|---------|---------|
| **Email Address** | Standard email format validation | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` | `user@example.com` |
| **Phone (E.164)** | International phone number format | `^\+[1-9]\d{1,14}$` | `+12345678901` |
| **URL/Website** | HTTP/HTTPS URL format | `^https?://.+\..+` | `https://example.com` |
| **Postal Code (Generic)** | Flexible postal code for most countries | `^[A-Z0-9\s-]{3,10}$` | `12345`, `NW1 6XE`, `10115` |
| **Date (ISO 8601)** | Standard date format YYYY-MM-DD | `^\d{4}-\d{2}-\d{2}$` | `2026-05-18` |
| **UUID** | Universally Unique Identifier | `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$` | `550e8400-e29b-41d4-a716-446655440000` |
| **IP Address (IPv4)** | IPv4 address format | `^(?:(?:25[0-5]\|2[0-4][0-9]\|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]\|2[0-4][0-9]\|[01]?[0-9][0-9]?)$` | `192.168.1.1` |

### Custom Pattern

Users can also enter their own custom regex patterns for specialized validation needs.

## Using Pattern Presets

### In PyQt GUI

1. Open the **Constraint Editor** dialog for a property
2. Select **"sh:pattern"** as the constraint type
3. Choose a **Pattern Preset** from the dropdown
4. The regex pattern is automatically filled in
5. (Optional) Modify the pattern or enter a custom one
6. Save the constraint

### In Web Interface

1. Open the **Constraint Editor** modal for a property
2. Select **"sh:pattern"** as the constraint type
3. Choose a **Pattern Preset** from the dropdown
4. The regex pattern is automatically filled in with example shown
5. Use the **Test Pattern** feature to validate against sample data
6. Save the constraint

## Pattern Testing

The web interface includes a **pattern testing feature** that allows users to:

1. Enter a test value
2. Click **"Test"** button
3. See immediate feedback:
   - **Green** ✓ Pattern matches
   - **Red** ✗ Pattern does not match
   - **Yellow** Invalid regex syntax

This helps users verify their patterns work correctly before saving.

## Extending Pattern Presets

Pattern presets are stored in `shared_libraries/pattern_presets.json` and can be extended for specific domains or countries.

### Configuration File Structure

```json
{
  "version": "1.0",
  "description": "SHACL Pattern Presets for Common Validation Patterns",
  "presets": {
    "international": {
      "name": "International Standards",
      "patterns": [...]
    },
    "custom": {
      "name": "User Custom Patterns",
      "patterns": []
    }
  },
  "extensibility": {
    "planned_extensions": [
      "country_specific_postal",
      "industry_specific",
      "organization_patterns"
    ]
  }
}
```

### Adding Custom Presets

To add domain-specific patterns:

1. Edit `shared_libraries/pattern_presets.json`
2. Add a new preset object:

```json
{
  "id": "my_custom_pattern",
  "name": "My Custom Pattern",
  "description": "Description of what this pattern validates",
  "pattern": "^your-regex-pattern-here$",
  "example": "example@value.com"
}
```

3. Restart the application to load new presets

## Why International Standards?

### Smart Defaults Strategy

The pattern presets follow a **smart defaults** approach:

- **Works globally now** - International standards cover 90% of use cases
- **Extensible later** - Easy to add country-specific patterns when needed
- **No premature optimization** - Don't build complex country logic until user domain is known
- **User-friendly** - Defaults work without configuration

### International vs. Country-Specific

| Approach | Pros | Cons |
|----------|------|------|
| **International (Current)** | Works everywhere, simple, maintainable | May not validate country-specific formats strictly |
| **Country-Specific** | Strict validation per country | Complex, requires country selection, more maintenance |

The international approach accepts valid inputs from any country while remaining simple and maintainable.

## Future Extensions

Planned extensions for when specific domains are identified:

1. **Country-Specific Postal Codes**
   - US ZIP (+4 optional)
   - UK Postcodes
   - German PLZ
   - Canadian Postal Codes
   - etc.

2. **Industry-Specific Patterns**
   - Healthcare: Medical record numbers, ICD codes
   - Finance: IBAN, SWIFT, credit card formats
   - Legal: Case numbers, docket formats
   - Education: Student IDs, course codes

3. **Organization-Specific Patterns**
   - Company-specific ID formats
   - Department codes
   - Project identifiers

## Best Practices

### When to Use Pattern Presets

✅ **Use for:**
- Email validation
- Phone numbers (when E.164 format is acceptable)
- URL validation
- Generic postal codes
- UUIDs
- IP addresses

⚠️ **Consider custom patterns for:**
- Strict country-specific formats
- Organization-specific ID formats
- Industry-standard codes with specific rules

### Pattern Testing Tips

1. **Test valid inputs** - Ensure the pattern accepts valid data
2. **Test invalid inputs** - Ensure the pattern rejects invalid data
3. **Test edge cases** - Empty strings, special characters, boundaries
4. **Consider international data** - Test with data from different countries

## Technical Details

### SHACL Pattern Constraint

Pattern presets generate `sh:pattern` constraints in SHACL:

```turtle
ex:EmailProperty a sh:PropertyShape ;
    sh:path schema:email ;
    sh:datatype xsd:string ;
    sh:pattern "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" ;
    sh:name "Email Address" .
```

### Regex Syntax

Patterns use JavaScript/Python compatible regex syntax:
- `^` - Start of string
- `$` - End of string
- `\d` - Digit
- `\s` - Whitespace
- `[A-Z0-9]` - Character class
- `{3,10}` - Quantifier (3 to 10 occurrences)
- `+` - One or more
- `*` - Zero or more
- `?` - Zero or one

## Related Documentation

- [Brick Building Guide](BRICK_BUILDING_GUIDE.md) - Comprehensive guide to building SHACL bricks
- [User Guide](USER_GUIDE.md) - General application usage
- [Architecture](ARCHITECTURE.md) - System architecture overview

---

**Last Updated:** 2026-05-18  
**Version:** 1.0
