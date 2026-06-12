"""
Enrichment engine tests — one test per resolution layer.

Layer 0  triggerDatatype   sh:datatype → widget (no graph needed)
Layer 1  dimensional sig   ProMo SI exponents → unit_dropdown
Layer 2  graph predicate   live rdflib query (e.g. qudt:applicableUnit)
Layer 3  namespace prefix  IRI prefix match
fallback                   plain text when nothing matches
"""
import json
import pytest


# ── widget_rules.ttl loading ──────────────────────────────────────────────────

def test_widget_rules_loads():
    from brick_app.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    assert len(r.rules_by_datatype)  >= 8,  f"Expected ≥8 datatype rules, got {len(r.rules_by_datatype)}"
    assert len(r.rules_by_signature) >= 10, f"Expected ≥10 signature rules, got {len(r.rules_by_signature)}"
    assert len(r.rules_by_predicate) >= 2,  f"Expected ≥2 predicate rules, got {len(r.rules_by_predicate)}"
    assert len(r.rules_by_namespace) >= 2,  f"Expected ≥2 namespace rules, got {len(r.rules_by_namespace)}"


# ── Layer 0: triggerDatatype ──────────────────────────────────────────────────

@pytest.mark.parametrize("datatype,expected_widget", [
    ("xsd:boolean",     "boolean_toggle"),
    ("xsd:date",        "date_picker"),
    ("xsd:dateTime",    "date_picker"),
    ("xsd:anyURI",      "uri_input"),
    ("rdf:langString",  "language_text"),
    ("xsd:decimal",     "decimal_input"),
    ("xsd:integer",     "integer_input"),
    ("xsd:string",      "text"),
])
def test_layer0_datatype(datatype, expected_widget):
    from brick_app.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype(datatype)
    assert ctx.widget == expected_widget, f"{datatype}: expected {expected_widget!r}, got {ctx.widget!r}"
    assert ctx.resolution == "datatype"


def test_layer0_unknown_datatype_fallback():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("xsd:hexBinary")
    assert ctx.widget == "text"
    assert ctx.resolution == "none"


# ── Layer 1: dimensional signature ───────────────────────────────────────────

@pytest.mark.parametrize("sig,label", [
    ((0, 0, 0, 1, 0, 0, 0), "Temperature"),
    ((1, -1, -2, 0, 0, 0, 0), "Pressure"),
    ((1, 2, -2, 0, 0, 0, 0), "Energy"),
    ((1, 0, 0, 0, 0, 0, 0), "Mass"),
    ((0, 1, 0, 0, 0, 0, 0), "Length"),
    ((0, 0, 1, 0, 0, 0, 0), "Time"),
    ((0, 0, 0, 0, 0, 1, 0), "Amount"),
    ((1, 2, -3, 0, 0, 0, 0), "Power"),
])
def test_layer1_signature_registered(sig, label):
    from brick_app.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    rule = r.rules_by_signature.get(sig)
    assert rule is not None, f"No rule for {label} signature {sig}"
    assert rule["widget"] == "unit_dropdown"


def test_layer1_temperature_units_include_kelvin_and_celsius():
    from brick_app.core.enrichment_engine import WidgetRules
    rule = WidgetRules().rules_by_signature[(0, 0, 0, 1, 0, 0, 0)]
    units = rule.get("alternative_units", [])
    assert any("K" in u and "DEG" not in u for u in units), "Kelvin missing from temperature units"
    assert any("DEG_C" in u for u in units), "°C missing from temperature units"


def test_layer1_pressure_units_include_pascal_and_bar():
    from brick_app.core.enrichment_engine import WidgetRules
    rule = WidgetRules().rules_by_signature[(1, -1, -2, 0, 0, 0, 0)]
    units = rule.get("alternative_units", [])
    assert any("PA" in u and "Kilo" not in u and "Mega" not in u for u in units), "Pascal missing"
    assert any("BAR" in u for u in units), "bar missing from pressure units"


# ── Layer 2: live graph predicate query ───────────────────────────────────────

def test_layer2_qudt_predicate_registered():
    from brick_app.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    assert "http://qudt.org/schema/qudt/applicableUnit" in r.rules_by_predicate


def test_layer2_qudt_mass_from_live_graph():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    from brick_app.core.ontology_manager import OntologyManager
    mgr = OntologyManager()
    if "qudt-quantity-type" not in mgr.ontologies:
        pytest.skip("qudt-quantity-type not in cache — run download_ontologies.py first")
    ctx = EnrichmentEngine(mgr).enrich("http://qudt.org/vocab/quantitykind/Mass")
    assert ctx.widget == "unit_dropdown", f"Expected unit_dropdown, got {ctx.widget!r}"
    assert ctx.resolution == "predicate"
    units = ctx.enrichments.get("applicable_units", [])
    assert len(units) > 5, f"Expected >5 QUDT units for Mass, got {len(units)}"
    assert any("KiloGM" in u for u in units), "kg (KiloGM) not in QUDT Mass units"


def test_layer2_qudt_temperature_from_live_graph():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    from brick_app.core.ontology_manager import OntologyManager
    mgr = OntologyManager()
    if "qudt-quantity-type" not in mgr.ontologies:
        pytest.skip("qudt-quantity-type not in cache")
    ctx = EnrichmentEngine(mgr).enrich("http://qudt.org/vocab/quantitykind/ThermodynamicTemperature")
    assert ctx.widget == "unit_dropdown"
    units = ctx.enrichments.get("applicable_units", [])
    assert any("K" in u for u in units), "Kelvin missing from QUDT temperature units"


# ── Layer 3: namespace prefix ─────────────────────────────────────────────────

@pytest.mark.parametrize("iri,expected_resolution", [
    ("foaf:Person",                          "namespace"),
    ("http://xmlns.com/foaf/0.1/Agent",      "namespace"),
    ("https://schema.org/PostalAddress",     "namespace"),
    ("https://schema.org/Person",            "namespace"),
])
def test_layer3_namespace(iri, expected_resolution):
    from brick_app.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich(iri)
    assert ctx.widget == "property_suggestions", f"{iri}: expected property_suggestions, got {ctx.widget!r}"
    assert ctx.resolution == expected_resolution


# ── Fallback ──────────────────────────────────────────────────────────────────

def test_fallback_unknown_iri():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich("http://example.org/totally/unknown/Thing")
    assert ctx.widget == "text"
    assert ctx.resolution == "none"


def test_fallback_empty_iri():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich("")
    assert ctx.widget == "text"


# ── Result serialisation ──────────────────────────────────────────────────────

def test_to_dict_is_json_serialisable():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    engine = EnrichmentEngine()
    for iri in ["xsd:boolean", "xsd:date", "foaf:Person",
                "http://example.org/unknown"]:
        ctx = engine.enrich_datatype(iri) if iri.startswith("xsd:") or iri.startswith("rdf:") \
              else engine.enrich(iri)
        d = engine.to_dict(ctx)
        assert json.dumps(d), f"to_dict result for {iri!r} is not JSON-serialisable"
        assert "widget" in d
        assert "resolution" in d


def test_to_dict_keys():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    engine = EnrichmentEngine()
    d = engine.to_dict(engine.enrich_datatype("xsd:boolean"))
    assert set(d.keys()) == {"class_iri", "label", "description", "widget", "resolution", "enrichments"}


# ── Caching ───────────────────────────────────────────────────────────────────

def test_enrich_result_is_cached():
    from brick_app.core.enrichment_engine import EnrichmentEngine
    engine = EnrichmentEngine()
    iri = "foaf:Person"
    ctx1 = engine.enrich(iri)
    ctx2 = engine.enrich(iri)
    assert ctx1 is ctx2, "Second call should return the cached object"
