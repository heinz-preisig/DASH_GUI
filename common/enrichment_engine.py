"""
EnrichmentEngine - Semantic-aware GUI enrichment for SHACL properties

Resolution order:
  1. ProMo dimensional signature  (SI exponent tuple → widget_rules.ttl)
  2. Cached ontology graph query  (any predicate in widget_rules.ttl)
  3. IRI namespace prefix match   (fallback, opt-in HTTP dereference later)
  4. Plain text input             (no rule matched)

No ontology names are hardcoded here.  All knowledge lives in widget_rules.ttl.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_RULES_FILE = Path(__file__).parent / "widget_rules.ttl"

# SI dimension order used throughout: (mass, length, time, temperature, current, amount, luminosity)
_DIM_KEYS = (
    "http://example.org#unit_mass",
    "http://example.org#unit_length",
    "http://example.org#unit_time",
    "http://example.org#unit_temperature",
    "http://example.org#unit_current",
    "http://example.org#unit_amount",
    "http://example.org#unit_light",
)

# ProMo predicate → dimension index
_PROMO_PRED_INDEX: Dict[str, int] = {
    "http://example.org#unit_mass":        0,
    "http://example.org#unit_length":      1,
    "http://example.org#unit_time":        2,
    "http://example.org#unit_temperature": 3,
    "http://example.org#unit_current":     4,
    "http://example.org#unit_amount":      5,
    "http://example.org#unit_light":       6,
}

# Canonical label for each QUDT unit IRI (used for display only)
_UNIT_LABELS: Dict[str, str] = {
    "http://qudt.org/vocab/unit/K":          "K",
    "http://qudt.org/vocab/unit/DEG_C":      "°C",
    "http://qudt.org/vocab/unit/DEG_F":      "°F",
    "http://qudt.org/vocab/unit/PA":         "Pa",
    "http://qudt.org/vocab/unit/KiloPA":     "kPa",
    "http://qudt.org/vocab/unit/MegaPA":     "MPa",
    "http://qudt.org/vocab/unit/BAR":        "bar",
    "http://qudt.org/vocab/unit/PSI":        "psi",
    "http://qudt.org/vocab/unit/ATM":        "atm",
    "http://qudt.org/vocab/unit/J":          "J",
    "http://qudt.org/vocab/unit/KiloJ":      "kJ",
    "http://qudt.org/vocab/unit/MegaJ":      "MJ",
    "http://qudt.org/vocab/unit/W-HR":       "Wh",
    "http://qudt.org/vocab/unit/KiloW-HR":   "kWh",
    "http://qudt.org/vocab/unit/CAL":        "cal",
    "http://qudt.org/vocab/unit/KiloCAL":    "kcal",
    "http://qudt.org/vocab/unit/KiloGM":     "kg",
    "http://qudt.org/vocab/unit/GM":         "g",
    "http://qudt.org/vocab/unit/MilliGM":    "mg",
    "http://qudt.org/vocab/unit/TON_Metric": "t",
    "http://qudt.org/vocab/unit/LB":         "lb",
    "http://qudt.org/vocab/unit/OZ":         "oz",
    "http://qudt.org/vocab/unit/M":          "m",
    "http://qudt.org/vocab/unit/CentiM":     "cm",
    "http://qudt.org/vocab/unit/MilliM":     "mm",
    "http://qudt.org/vocab/unit/KiloM":      "km",
    "http://qudt.org/vocab/unit/IN":         "in",
    "http://qudt.org/vocab/unit/FT":         "ft",
    "http://qudt.org/vocab/unit/MI":         "mi",
    "http://qudt.org/vocab/unit/SEC":        "s",
    "http://qudt.org/vocab/unit/MIN":        "min",
    "http://qudt.org/vocab/unit/HR":         "h",
    "http://qudt.org/vocab/unit/DAY":        "day",
    "http://qudt.org/vocab/unit/MOL":        "mol",
    "http://qudt.org/vocab/unit/MilliMOL":   "mmol",
    "http://qudt.org/vocab/unit/MicroMOL":   "µmol",
    "http://qudt.org/vocab/unit/KiloMOL":    "kmol",
    "http://qudt.org/vocab/unit/W":          "W",
    "http://qudt.org/vocab/unit/KiloW":      "kW",
    "http://qudt.org/vocab/unit/MegaW":      "MW",
    "http://qudt.org/vocab/unit/HP":         "hp",
    "http://qudt.org/vocab/unit/M3":         "m³",
    "http://qudt.org/vocab/unit/L":          "L",
    "http://qudt.org/vocab/unit/MilliL":     "mL",
    "http://qudt.org/vocab/unit/GAL":        "gal",
    "http://qudt.org/vocab/unit/FT3":        "ft³",
    "http://qudt.org/vocab/unit/M2":         "m²",
    "http://qudt.org/vocab/unit/CentiM2":    "cm²",
    "http://qudt.org/vocab/unit/FT2":        "ft²",
    "http://qudt.org/vocab/unit/IN2":        "in²",
    "http://qudt.org/vocab/unit/M-PER-SEC":  "m/s",
    "http://qudt.org/vocab/unit/KiloM-PER-HR": "km/h",
    "http://qudt.org/vocab/unit/MI-PER-HR":  "mph",
    "http://qudt.org/vocab/unit/FT-PER-SEC": "ft/s",
    "http://qudt.org/vocab/unit/UNITLESS":   "—",
    "http://qudt.org/vocab/unit/A":          "A",
    "http://qudt.org/vocab/unit/MilliA":     "mA",
    "http://qudt.org/vocab/unit/V":          "V",
    "http://qudt.org/vocab/unit/MilliV":     "mV",
    "http://qudt.org/vocab/unit/KiloV":      "kV",
    "http://qudt.org/vocab/unit/CD":         "cd",
}


@dataclass
class EnrichmentContext:
    """Enrichment result for a single sh:class IRI"""
    class_iri: str
    label: str = ""
    description: str = ""
    widget: str = "text"                      # widget type from widget_rules.ttl
    resolution: str = "none"                  # how the widget was determined
    enrichments: Dict[str, Any] = field(default_factory=dict)


class WidgetRules:
    """
    Loads widget_rules.ttl and exposes:
      - rules_by_datatype   : {datatype_iri → rule_dict}          (Layer 0)
      - rules_by_signature  : {sig_tuple → rule_dict}             (Layer 1)
      - rules_by_predicate  : {predicate_iri → rule_dict}         (Layer 2)
      - rules_by_namespace  : [(namespace_prefix, rule_dict), ...]  (Layer 3)
    """

    DASHGUI = "http://example.org/dashgui#"

    def __init__(self, rules_file: Path = _RULES_FILE):
        self.rules_by_datatype:  Dict[str, Dict] = {}
        self.rules_by_signature: Dict[Tuple[int, ...], Dict] = {}
        self.rules_by_predicate: Dict[str, Dict] = {}
        self.rules_by_namespace: List[Tuple[str, Dict]] = []
        self.rules_by_subclassof: List[Tuple[str, Dict]] = []
        self._load(rules_file)

    def _load(self, rules_file: Path):
        try:
            from rdflib import Graph, RDF, URIRef, Literal
            g = Graph()
            g.parse(str(rules_file), format="turtle")
            ns = self.DASHGUI
            WIDGET_RULE = URIRef(ns + "WidgetRule")
            for rule_node in g.subjects(RDF.type, WIDGET_RULE):
                rule = self._parse_rule(g, rule_node)
                for dt in rule.get("trigger_datatypes", []):
                    self.rules_by_datatype[dt] = rule
                if "sig" in rule:
                    self.rules_by_signature[rule["sig"]] = rule
                for pred in rule.get("trigger_predicates", []):
                    self.rules_by_predicate[pred] = rule
                for nspc in rule.get("trigger_namespaces", []):
                    self.rules_by_namespace.append((nspc, rule))
                for subclass in rule.get("trigger_subclassof", []):
                    self.rules_by_subclassof.append((subclass, rule))
        except Exception as e:
            print(f"Warning: could not load widget_rules.ttl: {e}")

    def _parse_rule(self, g, rule_node) -> Dict:
        from rdflib import URIRef, Literal
        ns = self.DASHGUI

        def _one(pred):
            for o in g.objects(rule_node, URIRef(ns + pred)):
                return str(o)
            return None

        def _all(pred):
            return [str(o) for o in g.objects(rule_node, URIRef(ns + pred))]

        def _list_items(pred):
            from rdflib.collection import Collection
            items = []
            for o in g.objects(rule_node, URIRef(ns + pred)):
                try:
                    items = [str(i) for i in Collection(g, o)]
                except Exception:
                    items = [str(o)]
            return items

        rule: Dict[str, Any] = {
            "widget":     _one("widget") or "text",
            "label":      _one("label") or "",
        }

        sig_str = _one("dimensionalSignature")
        if sig_str:
            try:
                rule["sig"] = tuple(int(x) for x in sig_str.strip().split())
            except ValueError:
                pass

        datatypes = _all("triggerDatatype")
        if datatypes:
            rule["trigger_datatypes"] = datatypes

        preds = _all("triggerPredicate")
        if preds:
            rule["trigger_predicates"] = preds

        namespaces = _all("triggerNamespace")
        if namespaces:
            rule["trigger_namespaces"] = namespaces

        subclassof = _all("triggerSubClassOf")
        if subclassof:
            rule["trigger_subclassof"] = subclassof

        si_unit = _one("siUnit")
        if si_unit:
            rule["si_unit"] = si_unit

        alt_units = _list_items("alternativeUnits")
        if alt_units:
            rule["alternative_units"] = alt_units

        return rule


class EnrichmentEngine:
    """
    Provides semantic enrichment for SHACL property classes.

    Resolution order:
      1. ProMo dimensional signature (reads promo:unit_* exponents from any loaded graph)
      2. Cached ontology predicate query (checks widget_rules.ttl triggerPredicates)
      3. IRI namespace prefix match (widget_rules.ttl triggerNamespace)
      4. Fallback: plain text
    """

    def __init__(self, ontology_manager=None):
        self.ontology_manager = ontology_manager
        self.rules = WidgetRules()
        self._cache: Dict[str, EnrichmentContext] = {}

    def enrich(self, class_iri: str) -> EnrichmentContext:
        """
        Return enrichment context for a semantic class IRI (or prefixed name).
        Always returns an EnrichmentContext; widget=="text" means no enrichment found.
        """
        if class_iri in self._cache:
            return self._cache[class_iri]

        full_iri = self._expand_common_prefixes(class_iri)
        label = self._get_label(full_iri)
        description = self._get_description(full_iri)

        ctx = (
            self._try_dimensional(full_iri, label, description)
            or self._try_predicate(full_iri, label, description)
            or self._try_namespace(full_iri, label, description)
            or self._try_subclassof(full_iri, label, description)
            or EnrichmentContext(
                class_iri=full_iri,
                label=label or full_iri.split("/")[-1].split("#")[-1],
                description=description,
                widget="text",
                resolution="none",
            )
        )
        self._cache[class_iri] = ctx
        return ctx

    def enrich_datatype(self, datatype_iri: str) -> EnrichmentContext:
        """
        Layer 0: resolve widget purely from sh:datatype.
        Called by frontends directly with the property's datatype value.
        Returns EnrichmentContext; widget=="text" means no special widget.
        """
        if not datatype_iri:
            return EnrichmentContext(class_iri="", label="", widget="text", resolution="none")
        full_iri = self._expand_common_prefixes(datatype_iri)
        rule = self.rules.rules_by_datatype.get(full_iri)
        if rule:
            return EnrichmentContext(
                class_iri=full_iri,
                label=rule.get("label", datatype_iri),
                widget=rule["widget"],
                resolution="datatype",
            )
        return EnrichmentContext(
            class_iri=full_iri,
            label=datatype_iri,
            widget="text",
            resolution="none",
        )

    # ── Resolution layer 4: rdfs:subClassOf inheritance ──────────────────────

    def _try_subclassof(self, iri: str, label: str, desc: str) -> Optional[EnrichmentContext]:
        """
        Check if the class is a subclass of any triggerSubClassOf class in widget_rules.ttl.
        Follows rdfs:subClassOf chain up to 3 levels.
        """
        if not self.ontology_manager or not self.rules.rules_by_subclassof:
            return None
        try:
            from rdflib import URIRef, RDFS
            node = URIRef(iri)
            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue
                # Collect class and its superclasses (up to 3 levels)
                candidates = [node]
                current = [node]
                for _ in range(3):
                    parents = []
                    for c in current:
                        for p in graph.objects(c, RDFS.subClassOf):
                            if isinstance(p, URIRef):
                                parents.append(p)
                                candidates.append(p)
                    current = parents
                    if not current:
                        break
                # Check each candidate against rules
                for candidate in candidates:
                    candidate_iri = str(candidate)
                    for trigger_class, rule in self.rules.rules_by_subclassof:
                        if candidate_iri == trigger_class:
                            enrichments = {}
                            if rule.get("widget") == "entity_lookup":
                                enrichments = {"entity_type": rule.get("label", ""), "has_entity_lookup": True}
                            return EnrichmentContext(
                                class_iri=iri,
                                label=label or iri.split("/")[-1].split("#")[-1],
                                description=desc,
                                widget=rule["widget"],
                                resolution="subclassof",
                                enrichments=enrichments,
                            )
            return None
        except Exception:
            return None

    # ── Resolution layer 1: ProMo dimensional signature ──────────────────────

    def _try_dimensional(self, iri: str, label: str, desc: str) -> Optional[EnrichmentContext]:
        """
        Look for promo:unit_* integer exponents on the class node in any loaded graph.
        Build a dimensional signature tuple and look it up in widget_rules.ttl.
        """
        if not self.ontology_manager:
            return None

        try:
            from rdflib import URIRef, Literal
            PROMO = "http://example.org#"
            dim_preds = {
                URIRef(PROMO + "unit_mass"):        0,
                URIRef(PROMO + "unit_length"):      1,
                URIRef(PROMO + "unit_time"):        2,
                URIRef(PROMO + "unit_temperature"): 3,
                URIRef(PROMO + "unit_current"):     4,
                URIRef(PROMO + "unit_amount"):      5,
                URIRef(PROMO + "unit_light"):       6,
            }

            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue
                node = URIRef(iri)
                exponents = {}
                for pred, idx in dim_preds.items():
                    for obj in graph.objects(node, pred):
                        try:
                            exponents[idx] = int(obj)
                        except (ValueError, TypeError):
                            pass
                if exponents:
                    sig = tuple(exponents.get(i, 0) for i in range(7))
                    rule = self.rules.rules_by_signature.get(sig)
                    if rule:
                        return self._make_unit_context(iri, label, desc, rule, "dimensional")
            return None
        except Exception:
            return None

    # ── Resolution layer 2: cached ontology graph predicate query ────────────

    def _try_predicate(self, iri: str, label: str, desc: str) -> Optional[EnrichmentContext]:
        """
        For each triggerPredicate in widget_rules.ttl, check whether the class node
        in any cached graph has that predicate as a subject.
        Also follows one rdfs:subClassOf step.
        """
        if not self.ontology_manager or not self.rules.rules_by_predicate:
            return None

        try:
            from rdflib import URIRef, RDFS
            node = URIRef(iri)

            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue

                candidates = [node]
                for parent in graph.objects(node, RDFS.subClassOf):
                    candidates.append(parent)

                for candidate in candidates:
                    for pred_iri, rule in self.rules.rules_by_predicate.items():
                        pred_node = URIRef(pred_iri)
                        objects = list(graph.objects(candidate, pred_node))
                        if objects:
                            enrichments = {}
                            if rule.get("widget") == "unit_dropdown":
                                unit_iris = [str(o) for o in objects]
                                enrichments = self._build_unit_enrichment(rule, unit_iris)
                            elif rule.get("widget") == "property_suggestions":
                                props = self._get_property_suggestions(graph, candidate)
                                enrichments = {"suggested_properties": props, "has_suggestions": bool(props)}
                            elif rule.get("widget") == "skos_selector":
                                enrichments = self._build_skos_enrichment(graph, candidate, objects, rule)
                            return EnrichmentContext(
                                class_iri=iri,
                                label=label or iri.split("/")[-1].split("#")[-1],
                                description=desc,
                                widget=rule["widget"],
                                resolution="predicate",
                                enrichments=enrichments,
                            )
            return None
        except Exception:
            return None

    # ── Resolution layer 3: IRI namespace prefix match ───────────────────────

    def _try_namespace(self, iri: str, label: str, desc: str) -> Optional[EnrichmentContext]:
        """Match the class IRI against triggerNamespace prefixes in widget_rules.ttl."""
        for namespace, rule in self.rules.rules_by_namespace:
            if iri.startswith(namespace):
                enrichments: Dict[str, Any] = {}
                if rule.get("widget") == "property_suggestions":
                    props = self._get_property_suggestions_from_cache(iri)
                    enrichments = {"suggested_properties": props, "has_suggestions": bool(props)}
                return EnrichmentContext(
                    class_iri=iri,
                    label=label or iri.split("/")[-1].split("#")[-1],
                    description=desc,
                    widget=rule["widget"],
                    resolution="namespace",
                    enrichments=enrichments,
                )
        return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_unit_context(self, iri, label, desc, rule, resolution) -> EnrichmentContext:
        alt_units = rule.get("alternative_units", [])
        si_unit = rule.get("si_unit", "")
        enrichments = self._build_unit_enrichment(rule, alt_units if alt_units else ([si_unit] if si_unit else []))
        return EnrichmentContext(
            class_iri=iri,
            label=label or rule.get("label", iri.split("/")[-1].split("#")[-1]),
            description=desc,
            widget=rule["widget"],
            resolution=resolution,
            enrichments=enrichments,
        )

    def _build_unit_enrichment(self, rule: Dict, unit_iris: List[str]) -> Dict[str, Any]:
        si_unit = rule.get("si_unit", unit_iris[0] if unit_iris else "")
        unit_labels = {u: _UNIT_LABELS.get(u, u.split("/")[-1]) for u in unit_iris}
        return {
            "quantity_kind": rule.get("label", ""),
            "si_unit": si_unit,
            "applicable_units": unit_iris,
            "unit_labels": unit_labels,
            "has_units": bool(unit_iris),
        }

    def _build_skos_enrichment(self, graph, class_node, objects, rule) -> Dict[str, Any]:
        """Build SKOS concept scheme enrichment with available concepts."""
        from rdflib import URIRef, RDF, RDFS, SKOS
        concepts = []
        # Get the concept scheme URI(s) from the objects
        scheme_uris = [str(o) for o in objects]
        # Find all concepts in the scheme
        for scheme_uri in scheme_uris:
            scheme_ref = URIRef(scheme_uri)
            for concept in graph.subjects(SKOS.inScheme, scheme_ref):
                concept_iri = str(concept)
                # Get prefLabel if available
                label = concept_iri.split("/")[-1].split("#")[-1]
                for lbl in graph.objects(concept, SKOS.prefLabel):
                    label = str(lbl)
                    break
                if not any(c["iri"] == concept_iri for c in concepts):
                    concepts.append({"iri": concept_iri, "label": label})
            # Also look for top concepts
            for concept in graph.objects(scheme_ref, SKOS.hasTopConcept):
                concept_iri = str(concept)
                label = concept_iri.split("/")[-1].split("#")[-1]
                for lbl in graph.objects(concept, SKOS.prefLabel):
                    label = str(lbl)
                    break
                if not any(c["iri"] == concept_iri for c in concepts):
                    concepts.append({"iri": concept_iri, "label": label})
        return {
            "concept_scheme": scheme_uris[0] if scheme_uris else "",
            "concepts": sorted(concepts, key=lambda x: x["label"]),
            "has_concepts": bool(concepts),
        }

    def _get_property_suggestions(self, graph, class_node) -> List[str]:
        """Extract rdfs:domain-matching properties from a graph for a class node."""
        try:
            from rdflib import RDF, RDFS, OWL, URIRef
            props = []
            for prop in graph.subjects(RDFS.domain, class_node):
                name = str(prop).split("/")[-1].split("#")[-1]
                props.append(name)
            return sorted(props)
        except Exception:
            return []

    def _get_property_suggestions_from_cache(self, class_iri: str) -> List[str]:
        """Look up rdfs:domain properties across all cached ontology graphs."""
        if not self.ontology_manager:
            return []
        try:
            from rdflib import URIRef, RDFS
            node = URIRef(class_iri)
            props = []
            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue
                for prop in graph.subjects(RDFS.domain, node):
                    name = str(prop).split("/")[-1].split("#")[-1]
                    if name not in props:
                        props.append(name)
            return sorted(props)
        except Exception:
            return []

    def _get_label(self, iri: str) -> str:
        if not self.ontology_manager:
            return ""
        try:
            from rdflib import URIRef, RDFS
            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue
                for lbl in graph.objects(URIRef(iri), RDFS.label):
                    return str(lbl)
        except Exception:
            pass
        return ""

    def _get_description(self, iri: str) -> str:
        if not self.ontology_manager:
            return ""
        try:
            from rdflib import URIRef, RDFS
            for ont_data in self.ontology_manager.ontologies.values():
                graph = ont_data.get("graph")
                if graph is None:
                    continue
                for comment in graph.objects(URIRef(iri), RDFS.comment):
                    return str(comment)
        except Exception:
            pass
        return ""

    def _expand_common_prefixes(self, prefixed: str) -> str:
        """Expand well-known prefixed names to full IRIs."""
        if not prefixed:
            return ""
        if "://" in prefixed:
            return prefixed
        prefixes = {
            "xsd":    "http://www.w3.org/2001/XMLSchema#",
            "rdf":    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
            "qudt":   "http://qudt.org/vocab/quantitykind/",
            "unit":   "http://qudt.org/vocab/unit/",
            "schema": "https://schema.org/",
            "foaf":   "http://xmlns.com/foaf/0.1/",
            "brick":  "https://brickschema.org/schema/Brick#",
            "promo":  "http://example.org#",
            "skos":   "http://www.w3.org/2004/02/skos/core#",
            "ex":     "http://example.org/",
        }
        if ":" in prefixed:
            prefix, local = prefixed.split(":", 1)
            if prefix in prefixes:
                return prefixes[prefix] + local
        return prefixed

    def to_dict(self, ctx: EnrichmentContext) -> Dict[str, Any]:
        """Serialise an EnrichmentContext for JSON responses."""
        return {
            "class_iri":   ctx.class_iri,
            "label":       ctx.label,
            "description": ctx.description,
            "widget":      ctx.widget,
            "resolution":  ctx.resolution,
            "enrichments": ctx.enrichments,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
_enrichment_engine: Optional[EnrichmentEngine] = None


def get_enrichment_engine(ontology_manager=None) -> EnrichmentEngine:
    """Get or create the singleton EnrichmentEngine."""
    global _enrichment_engine
    if _enrichment_engine is None:
        _enrichment_engine = EnrichmentEngine(ontology_manager)
    elif ontology_manager is not None and _enrichment_engine.ontology_manager is None:
        _enrichment_engine.ontology_manager = ontology_manager
    return _enrichment_engine
