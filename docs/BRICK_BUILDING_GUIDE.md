# Brick Building Guide: Target Classes and Properties

## Overview

This guide explains what target classes are and what properties you can add when building SHACL bricks for your schema constructor.

## Target Classes

### **What is a Target Class?**

A **target class** defines what type of entity your brick represents. It's the main subject of your SHACL shape and determines what the brick applies to.

### **Common Target Classes**

#### **Person-Related Classes**
```turtle
# Basic person
schema:Person          # General person
foaf:Person           # Friend of a Friend person
vcard:Individual      # vCard individual

# Specific person types
schema:Student        # Student
schema:Teacher        # Teacher
schema:Employee       # Employee
schema:Customer       # Customer
schema:Patient        # Patient
```

#### **Organization Classes**
```turtle
# Organizations
schema:Organization    # General organization
schema:Corporation     # Company/corporation
schema:EducationalOrganization  # School/university
schema:GovernmentOrganization   # Government entity
schema:Nonprofit      # Non-profit organization
```

#### **Location Classes**
```turtle
# Addresses and places
schema:PostalAddress  # Mailing address
schema:Place          # General place
schema:City           # City/town
schema:Country        # Country
schema:Address       # General address
```

#### **Product Classes**
```turtle
# Products and services
schema:Product        # General product
schema:Service        # Service offering
schema:Book           # Book
schema:Vehicle        # Vehicle
schema:Food           # Food item
```

#### **Event Classes**
```turtle
# Events and activities
schema:Event          # General event
schema:Meeting        # Meeting
schema:Conference     # Conference
schema:Wedding        # Wedding
schema:ConcertEvent   # Concert
```

#### **Content Classes**
```turtle
# Digital content
schema:CreativeWork   # Creative work
schema:Article        # Article
schema:BlogPosting    # Blog post
schema:VideoObject    # Video
schema:ImageObject    # Image
```

### **Custom Target Classes**

You can also create your own target classes:

```turtle
# Custom classes (use your own prefix)
ex:StudentRecord      # Student record
ex:ProjectProposal   # Project proposal
ex:InventoryItem     # Inventory item
ex:ServiceTicket     # Support ticket
```

## Property Types

### **Basic Data Properties**

#### **Text/String Properties**
```turtle
# Names and identifiers
schema:name           # Full name
schema:firstName      # First name
schema:lastName       # Last name
schema:middleName     # Middle name
schema:alternateName  # Alternative name
schema:description    # Description
schema:text           # Text content

# Contact information
schema:email          # Email address
schema:telephone      # Phone number
schema:faxNumber      # Fax number

# Identifiers
schema:identifier     # General identifier
schema:serialNumber   # Serial number
schema:isbn           # ISBN for books
schema:sku            # SKU for products
```

#### **Numeric Properties**
```turtle
# Numbers and quantities
schema:number         # General number
schema:integer        # Integer value
schema:float          # Floating point
schema:price          # Price/amount
schema:weight         # Weight
schema:height         # Height
schema:width          # Width
schema:depth          # Depth
schema:age            # Age
schema:year           # Year
schema:month          # Month
schema:day            # Day
```

#### **Date/Time Properties**
```turtle
# Dates and times
schema:date           # Date
schema:dateTime       # Date and time
schema:time           # Time only
schema:birthDate      # Birth date
schema:deathDate      # Death date
schema:foundingDate   # Founding date
schema:startDate      # Start date
schema:endDate        # End date
schema:modified       # Last modified
schema:created        # Creation date
```

#### **Boolean Properties**
```turtle
# True/false values
schema:Boolean        # General boolean
schema:isAccessibleForFree  # Free access
schema:isFamilyFriendly     # Family friendly
schema:isActive            # Active status
schema:isValid             # Valid status
schema:isRequired          # Required field
```

#### **URL/URI Properties**
```turtle
# Links and references
schema:url            # URL
schema:website        # Website
schema:image          # Image URL
schema:video          # Video URL
schema:sameAs         # Same as reference
schema:about          # About page
schema:mainEntity     # Main entity
```

### **Object Properties (Relationships)**

#### **Person Relationships**
```turtle
# Family relationships
schema:spouse         # Spouse
schema:parent         # Parent
schema:child          # Child
schema:sibling        # Sibling
schema:ancestor       # Ancestor
schema:knows          # Knows someone
schema:colleague      # Colleague
schema:friend         # Friend

# Professional relationships
schema:employer       # Employer
schema:employee       # Employee
schema:worksFor       # Works for
schema:alumniOf       # Alumni of
schema:memberOf       # Member of
schema:author         # Author of
schema:contributor    # Contributor to
```

#### **Location Properties**
```turtle
# Address components
schema:streetAddress  # Street address
schema:addressLocality # City/town
schema:addressRegion  # State/region
schema:postalCode     # Postal code
schema:addressCountry # Country
schema:postOfficeBoxNumber # PO Box

# Geographic relationships
schema:containedIn    # Contained in
schema:containsPlace  # Contains place
schema:geo            # Geo coordinates
schema:latitude       # Latitude
schema:longitude      # Longitude
```

#### **Organization Properties**
```turtle
# Organization details
schema:legalName      # Legal name
schema:alternateName  # Alternate name
schema:description     # Description
schema:foundingDate   # Founding date
schema:dissolutionDate # Dissolution date
schema:taxID          # Tax ID
schema:vatID          # VAT ID

# Organization relationships
schema:subOrganization # Sub-organization
schema:parentOrganization # Parent org
schema:member         # Member
schema:employee       # Employee
```

#### **Product Properties**
```turtle
# Product details
schema:brand          # Brand
schema:manufacturer   # Manufacturer
schema:model          # Model
schema:color          # Color
schema:size           # Size
schema:weight         # Weight
schema:height         # Height
schema:material       # Material
schema:productionDate # Production date
schema:releaseDate    # Release date
schema:expiryDate     # Expiry date

# Product relationships
schema:offers         # Offers/pricing
schema:review         # Reviews
schema:aggregateRating # Aggregate rating
```

### **Structured Properties**

#### **Address Structure**
```turtle
# Complete address object
schema:address        # Address object
  -> schema:PostalAddress
     -> schema:streetAddress
     -> schema:addressLocality
     -> schema:addressRegion
     -> schema:postalCode
     -> schema:addressCountry
```

#### **Contact Structure**
```turtle
# Contact information
schema:contactPoint   # Contact point
  -> schema:ContactPoint
     -> schema:telephone
     -> schema:email
     -> schema:contactType
     -> schema:areaServed
```

#### **Geo Structure**
```turtle
# Geographic coordinates
schema:geo            # Geo coordinates
  -> schema:GeoCoordinates
     -> schema:latitude
     -> schema:longitude
     -> schema:elevation
```

## Property Constraints

### **Data Type Constraints**
```turtle
# String constraints
sh:datatype xsd:string     # Text string
sh:datatype xsd:integer    # Whole number
sh:datatype xsd:decimal    # Decimal number
sh:datatype xsd:boolean    # True/false
sh:datatype xsd:date       # Date (YYYY-MM-DD)
sh:datatype xsd:dateTime   # Date and time
sh:datatype xsd:anyURI     # URL/URI
sh:datatype xsd:email      # Email address
```

### **Cardinality Constraints**
```turtle
# Required/optional
sh:minCount 1             # Required (at least 1)
sh:maxCount 1             # Maximum 1 (single value)
sh:minCount 2             # At least 2
sh:maxCount 5             # Maximum 5
```

### **String Constraints**
```turtle
# Length limits
sh:minLength 3            # Minimum 3 characters
sh:maxLength 50           # Maximum 50 characters

# Pattern matching
sh:pattern "^[A-Z][a-z]*$" # First letter capital
sh:pattern "^\\d{3}-\\d{2}-\\d{4}$" # SSN format
sh:pattern "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" # Email
sh:pattern "^\\d{5}(-\\d{4})?$" # ZIP code
```

### **Numeric Constraints**
```turtle
# Range constraints
sh:minInclusive 0         # Minimum value (inclusive)
sh:maxInclusive 100       # Maximum value (inclusive)
sh:minExclusive 0         # Minimum value (exclusive)
sh:maxExclusive 100       # Maximum value (exclusive)
```

### **Date Constraints**
```turtle
# Date ranges
sh:minInclusive "1990-01-01"^^xsd:date  # Earliest date
sh:maxInclusive "2025-12-31"^^xsd:date  # Latest date
```

## Example Brick Configurations

### **Person Brick**
```turtle
# Target Class: schema:Person
# Properties:
- schema:firstName (xsd:string, required, pattern: ^[A-Z][a-z]*$)
- schema:lastName (xsd:string, required, pattern: ^[A-Z][a-z]*$)
- schema:birthDate (xsd:date, optional, range: 1900-2025)
- schema:email (xsd:email, optional, email pattern)
- schema:telephone (xsd:string, optional, phone pattern)
```

### **Address Brick**
```turtle
# Target Class: schema:PostalAddress
# Properties:
- schema:streetAddress (xsd:string, required, max 200 chars)
- schema:addressLocality (xsd:string, required, max 100 chars)
- schema:addressRegion (xsd:string, optional, max 50 chars)
- schema:postalCode (xsd:string, required, ZIP pattern)
- schema:addressCountry (xsd:string, required, 2-letter country)
```

### **Product Brick**
```turtle
# Target Class: schema:Product
# Properties:
- schema:name (xsd:string, required, max 100 chars)
- schema:description (xsd:string, optional, max 500 chars)
- schema:brand (xsd:string, optional, max 50 chars)
- schema:price (xsd:decimal, optional, min 0)
- schema:weight (xsd:decimal, optional, min 0)
- schema:color (xsd:string, optional, max 30 chars)
```

## Best Practices

### **Naming Conventions**
- **Target Classes**: Use standard schema.org prefixes when possible
- **Properties**: Use well-known properties from schema.org, FOAF, vCard
- **Custom Properties**: Use your own prefix (ex:, myapp:, etc.)

### **Constraint Guidelines**
- **Required Fields**: Use `sh:minCount 1` for mandatory information
- **Validation**: Add patterns for email, phone, postal codes
- **User Experience**: Provide helpful examples and descriptions
- **Data Quality**: Use appropriate data types and ranges

### **Common Patterns**
- **Names**: Capital first letter, rest lowercase
- **Email**: Standard email regex pattern
- **Phone**: Flexible phone number patterns
- **Dates**: Reasonable ranges for birth dates, events
- **IDs**: Format-specific patterns (ISBN, SKU, etc.)

## Quick Reference

### **Popular Target Classes**
- `schema:Person` - People and individuals
- `schema:Organization` - Companies and institutions
- `schema:PostalAddress` - Mailing addresses
- `schema:Product` - Products and items
- `schema:Event` - Events and activities

### **Essential Properties**
- `schema:name` - Names and titles
- `schema:description` - Descriptions and details
- `schema:email` - Email addresses
- `schema:telephone` - Phone numbers
- `schema:date` - Dates and times
- `schema:url` - Web addresses

### **Common Constraints**
- `sh:minCount 1` - Required field
- `sh:maxCount 1` - Single value only
- `sh:pattern "..."` - Format validation
- `sh:minLength/sh:maxLength` - Length limits
- `sh:minInclusive/sh:maxInclusive` - Value ranges

This guide should help you understand what target classes to use and what properties you can add to create comprehensive SHACL bricks for your schema constructor.
