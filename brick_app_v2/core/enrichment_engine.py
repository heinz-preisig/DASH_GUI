"""
EnrichmentEngine - Semantic awareness for SHACL properties

Queries loaded ontologies to provide context-aware UI enrichment
based on sh:class links (e.g., qudt:Mass → unit dropdown)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class EnrichmentContext:
    """Contextual information about a semantic class"""
    class_iri: str
    label: str = ""
    description: str = ""
    source_ontology: str = ""  # qudt, schema, foaf, brick, etc.
    enrichments: Dict[str, Any] = field(default_factory=dict)


class EnrichmentEngine:
    """
    Provides semantic enrichment for property classes.
    
    Queries loaded ontologies via OntologyManager to extract:
    - QUDT: applicable units for quantity kinds
    - Schema.org/FOAF: related properties, expected ranges
    - Brick: equipment relationships, sensor types
    """
    
    def __init__(self, ontology_manager=None):
        self.ontology_manager = ontology_manager
        # Cache for enrichment results
        self._cache: Dict[str, EnrichmentContext] = {}
    
    def enrich(self, class_iri: str) -> Optional[EnrichmentContext]:
        """
        Get enrichment context for a semantic class.
        
        Args:
            class_iri: Full IRI or prefixed name (e.g., "qudt:Mass", "foaf:Person")
            
        Returns:
            EnrichmentContext or None if class not found
        """
        # Check cache
        if class_iri in self._cache:
            return self._cache[class_iri]
        
        # Expand prefixed name if needed
        full_iri = self._expand_prefix(class_iri)
        
        # Determine source ontology from IRI
        source = self._detect_source(full_iri)
        
        # Query ontology manager for label/description if available
        label = ""
        description = ""
        
        if self.ontology_manager:
            label = self._get_label(full_iri)
            description = self._get_description(full_iri)
        
        # Always do ontology-specific enrichment (works with or without ontology_manager)
        enrichments = {}
        if source == "qudt":
            enrichments = self._enrich_qudt(full_iri)
        elif source == "schema":
            enrichments = self._enrich_schema_org(full_iri)
        elif source == "foaf":
            enrichments = self._enrich_foaf(full_iri)
        elif source == "brick":
            enrichments = self._enrich_brick(full_iri)
        
        context = EnrichmentContext(
            class_iri=full_iri,
            label=label or class_iri.split("/")[-1].split("#")[-1],
            description=description,
            source_ontology=source,
            enrichments=enrichments
        )
        
        # Cache and return
        self._cache[class_iri] = context
        return context
    
    def _expand_prefix(self, prefixed: str) -> str:
        """Expand prefixed name to full IRI"""
        if "://" in prefixed:
            return prefixed
        
        # Common prefix mappings
        prefixes = {
            "qudt": "http://qudt.org/vocab/quantitykind/",
            "unit": "http://qudt.org/vocab/unit/",
            "schema": "https://schema.org/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "brick": "https://brickschema.org/schema/Brick#",
            "ex": "http://example.org/",
        }
        
        if ":" in prefixed:
            prefix, local = prefixed.split(":", 1)
            if prefix in prefixes:
                return prefixes[prefix] + local
        
        return prefixed
    
    def _detect_source(self, iri: str) -> str:
        """Detect source ontology from IRI"""
        if "qudt.org" in iri:
            return "qudt"
        elif "schema.org" in iri:
            return "schema"
        elif "foaf" in iri or "xmlns.com/foaf" in iri:
            return "foaf"
        elif "brickschema.org" in iri:
            return "brick"
        elif "w3.org/ns/shacl" in iri:
            return "shacl"
        return "other"
    
    def _get_label(self, iri: str) -> str:
        """Get rdfs:label from ontology manager"""
        if not self.ontology_manager:
            return ""
        # Try to get from cached ontologies
        for ont_name, ont_data in getattr(self.ontology_manager, 'ontologies', {}).items():
            classes = ont_data.get('classes', {})
            if iri in classes:
                return classes[iri].get('label', '')
        return ""
    
    def _get_description(self, iri: str) -> str:
        """Get rdfs:comment from ontology manager"""
        if not self.ontology_manager:
            return ""
        for ont_name, ont_data in getattr(self.ontology_manager, 'ontologies', {}).items():
            classes = ont_data.get('classes', {})
            if iri in classes:
                return classes[iri].get('comment', '')
        return ""
    
    def _enrich_qudt(self, quantity_iri: str) -> Dict[str, Any]:
        """
        Enrich QUDT quantity kinds with applicable units.
        
        Example: qudt:Mass → units [kg, g, lb, oz, ...]
        """
        units = []
        
        # Common QUDT quantity → units mapping
        quantity_units = {
            "Mass": ["unit:KiloGM", "unit:GM", "unit:LB", "unit:OZ"],
            "Length": ["unit:M", "unit:CentiM", "unit:MilliM", "unit:FT", "unit:IN"],
            "Temperature": ["unit:K", "unit:DEG_C", "unit:DEG_F"],
            "Time": ["unit:SEC", "unit:MIN", "unit:HR", "unit:DAY"],
            "ElectricCurrent": ["unit:A", "unit:MilliA"],
            "AmountOfSubstance": ["unit:MOL"],
            "LuminousIntensity": ["unit:CD"],
            "Force": ["unit:N", "unit:LB_F"],
            "Pressure": ["unit:PA", "unit:KiloPA", "unit:BAR", "unit:PSI"],
            "Energy": ["unit:J", "unit:KiloJ", "unit:W-HR", "unit:KiloW-HR"],
            "Power": ["unit:W", "unit:KiloW", "unit:MegaW", "unit:HP"],
            "Volume": ["unit:M3", "unit:L", "unit:MilliL", "unit:GAL"],
            "Area": ["unit:M2", "unit:CM2", "unit:FT2"],
            "Speed": ["unit:M-PER-SEC", "unit:KM-PER-HR", "unit:MI-PER-HR"],
            "Frequency": ["unit:HZ", "unit:KiloHZ", "unit:MegaHZ"],
            "Voltage": ["unit:V", "unit:MilliV", "unit:KiloV"],
            "Current": ["unit:A", "unit:MilliA"],
        }
        
        # Extract quantity name from IRI
        quantity_name = quantity_iri.split("/")[-1].split("#")[-1]
        
        # Look up units
        for qty, unit_list in quantity_units.items():
            if qty.lower() in quantity_name.lower() or quantity_name.lower() in qty.lower():
                units.extend(unit_list)
        
        # Get user-friendly unit labels
        unit_labels = {}
        unit_uris = {}
        for u in units:
            # Convert prefixed to label
            label = u.replace("unit:", "").replace("-", " ").replace("_", " ")
            # Common expansions
            label = label.replace("Kilo GM", "kg")
            label = label.replace("GM", "g")
            label = label.replace("LB", "lb")
            label = label.replace("OZ", "oz")
            label = label.replace("M PER SEC", "m/s")
            label = label.replace("KM PER HR", "km/h")
            label = label.replace("DEG C", "°C")
            label = label.replace("DEG F", "°F")
            label = label.replace("W HR", "Wh")
            label = label.replace("PER", "/")
            unit_labels[u] = label
            unit_uris[u] = self._expand_prefix(u)
        
        return {
            "quantity_kind": quantity_name,
            "applicable_units": units,
            "unit_labels": unit_labels,
            "unit_uris": unit_uris,
            "has_units": len(units) > 0
        }
    
    def _enrich_schema_org(self, class_iri: str) -> Dict[str, Any]:
        """
        Enrich Schema.org classes with related properties.
        
        Example: schema:Person → common properties [givenName, familyName, email]
        """
        # Common schema.org class → property mappings
        class_properties = {
            "Person": ["givenName", "familyName", "email", "telephone", "address", "birthDate", "jobTitle"],
            "Organization": ["name", "url", "email", "telephone", "address", "foundingDate"],
            "PostalAddress": ["streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry"],
            "Product": ["name", "description", "brand", "sku", "gtin", "price", "availability"],
            "Event": ["name", "startDate", "endDate", "location", "organizer", "eventStatus"],
            "Place": ["name", "address", "geo", "telephone", "url"],
        }
        
        class_name = class_iri.split("/")[-1].split("#")[-1]
        
        # Find matching class (case-insensitive)
        suggested_props = []
        for cls, props in class_properties.items():
            if cls.lower() in class_name.lower() or class_name.lower() in cls.lower():
                suggested_props = props
                break
        
        return {
            "class_name": class_name,
            "suggested_properties": suggested_props,
            "has_suggestions": len(suggested_props) > 0,
            "property_prefix": "schema:"
        }
    
    def _enrich_foaf(self, class_iri: str) -> Dict[str, Any]:
        """
        Enrich FOAF classes with related properties.
        
        Example: foaf:Person → [name, mbox, homepage, depiction]
        """
        foaf_properties = {
            "Person": ["name", "mbox", "homepage", "depiction", "phone", "workplaceHomepage"],
            "Agent": ["name", "mbox"],
            "Organization": ["name", "homepage", "member"],
            "Group": ["name", "member"],
        }
        
        class_name = class_iri.split("/")[-1].split("#")[-1]
        
        suggested_props = foaf_properties.get(class_name, ["name"])
        
        return {
            "class_name": class_name,
            "suggested_properties": suggested_props,
            "has_suggestions": len(suggested_props) > 0,
            "property_prefix": "foaf:"
        }
    
    def _enrich_brick(self, class_iri: str) -> Dict[str, Any]:
        """
        Enrich Brick classes with equipment relationships.
        
        Example: brick:Temperature_Sensor → [measures, hasLocation]
        """
        brick_properties = {
            "Temperature_Sensor": ["measures", "hasLocation", "hasOutput"],
            "Humidity_Sensor": ["measures", "hasLocation"],
            "CO2_Sensor": ["measures", "hasLocation"],
            "Air_Flow_Sensor": ["measures", "hasLocation"],
            "Pressure_Sensor": ["measures", "hasLocation"],
            "Equipment": ["hasLocation", "isPartOf", "feeds"],
            "HVAC_Equipment": ["hasLocation", "feeds", "isFedBy"],
            "Zone": ["hasPart", "isPartOf"],
            "Room": ["hasPart", "isPartOf", "area"],
        }
        
        class_name = class_iri.split("/")[-1].split("#")[-1]
        
        # Try exact match first, then partial
        suggested_props = brick_properties.get(class_name, [])
        if not suggested_props:
            for cls, props in brick_properties.items():
                if cls.lower() in class_name.lower() or class_name.lower() in cls.lower():
                    suggested_props = props
                    break
        
        return {
            "class_name": class_name,
            "suggested_properties": suggested_props,
            "has_suggestions": len(suggested_props) > 0,
            "property_prefix": "brick:"
        }
    
    def to_dict(self, context: EnrichmentContext) -> Dict[str, Any]:
        """Convert context to dictionary for JSON serialization"""
        return {
            "class_iri": context.class_iri,
            "label": context.label,
            "description": context.description,
            "source_ontology": context.source_ontology,
            "enrichments": context.enrichments
        }


# Singleton instance
_enrichment_engine = None

def get_enrichment_engine(ontology_manager=None) -> EnrichmentEngine:
    """Get or create singleton enrichment engine"""
    global _enrichment_engine
    if _enrichment_engine is None:
        _enrichment_engine = EnrichmentEngine(ontology_manager)
    return _enrichment_engine
