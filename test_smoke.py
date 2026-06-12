#!/usr/bin/env python3
"""
DEPRECATED — tests have moved to tests/
Run with: uv run python -m pytest tests/ -v
This file is kept only so old bookmarks do not break.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ── Brick App ─────────────────────────────────────────────────────────────────

def test_brick_core_simple_imports():
    from brick_app_v2.core.brick_core_simple import SHACLBrick, BrickCore
    assert SHACLBrick is not None
    assert BrickCore is not None


def test_brick_core_instantiates():
    from brick_app_v2.core.brick_core_simple import BrickCore
    core = BrickCore()
    assert core is not None


def test_ontology_manager_imports():
    from brick_app_v2.core.ontology_manager import OntologyManager
    assert OntologyManager is not None


def test_ontology_manager_instantiates():
    from brick_app_v2.core.ontology_manager import OntologyManager
    mgr = OntologyManager()
    assert mgr is not None


# ── Schema App ────────────────────────────────────────────────────────────────

def test_schema_core_imports():
    from schema_app_v2.core.schema_core import SchemaCore
    assert SchemaCore is not None


def test_schema_core_instantiates():
    from schema_app_v2.core.schema_core import SchemaCore
    core = SchemaCore()
    assert core is not None


def test_brick_integration_imports():
    from schema_app_v2.core.brick_integration import BrickIntegration
    assert BrickIntegration is not None


def test_shacl_export_imports():
    from schema_app_v2.core.shacl_export import SHACLExporter
    assert SHACLExporter is not None


def test_multi_tenant_backend_instantiates():
    from schema_app_v2.core.multi_tenant_backend import MultiTenantBackend
    backend = MultiTenantBackend()
    assert backend is not None


# ── Enrichment Engine ─────────────────────────────────────────────────────────

def test_widget_rules_loads():
    from brick_app_v2.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    assert len(r.rules_by_datatype) >= 8,   f"Expected ≥8 datatype rules, got {len(r.rules_by_datatype)}"
    assert len(r.rules_by_signature) >= 10, f"Expected ≥10 signature rules, got {len(r.rules_by_signature)}"
    assert len(r.rules_by_predicate) >= 2,  f"Expected ≥2 predicate rules, got {len(r.rules_by_predicate)}"
    assert len(r.rules_by_namespace) >= 2,  f"Expected ≥2 namespace rules, got {len(r.rules_by_namespace)}"


def test_layer0_datatype_boolean():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("xsd:boolean")
    assert ctx.widget == "boolean_toggle"
    assert ctx.resolution == "datatype"


def test_layer0_datatype_date():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("xsd:date")
    assert ctx.widget == "date_picker"
    assert ctx.resolution == "datatype"


def test_layer0_datatype_uri():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("xsd:anyURI")
    assert ctx.widget == "uri_input"
    assert ctx.resolution == "datatype"


def test_layer0_datatype_langstring():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("rdf:langString")
    assert ctx.widget == "language_text"
    assert ctx.resolution == "datatype"


def test_layer0_datatype_unknown_falls_back():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich_datatype("xsd:hexBinary")
    assert ctx.widget == "text"
    assert ctx.resolution == "none"


def test_layer1_temperature_signature():
    from brick_app_v2.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    rule = r.rules_by_signature.get((0, 0, 0, 1, 0, 0, 0))
    assert rule is not None, "No rule for temperature signature (0,0,0,1,0,0,0)"
    assert rule["widget"] == "unit_dropdown"
    units = rule.get("alternative_units", [])
    assert any("K" in u for u in units), "Kelvin not in temperature units"
    assert any("DEG_C" in u for u in units), "°C not in temperature units"


def test_layer1_pressure_signature():
    from brick_app_v2.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    rule = r.rules_by_signature.get((1, -1, -2, 0, 0, 0, 0))
    assert rule is not None, "No rule for pressure signature (1,-1,-2,0,0,0,0)"
    assert rule["widget"] == "unit_dropdown"
    assert any("PA" in u for u in rule.get("alternative_units", [])), "Pascal not in pressure units"


def test_layer1_energy_signature():
    from brick_app_v2.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    rule = r.rules_by_signature.get((1, 2, -2, 0, 0, 0, 0))
    assert rule is not None, "No rule for energy signature (1,2,-2,0,0,0,0)"
    assert rule["widget"] == "unit_dropdown"


def test_layer2_qudt_predicate_in_rules():
    from brick_app_v2.core.enrichment_engine import WidgetRules
    r = WidgetRules()
    assert "http://qudt.org/schema/qudt/applicableUnit" in r.rules_by_predicate, \
        "qudt:applicableUnit not registered as a trigger predicate"


def test_layer2_qudt_live_graph():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    from brick_app_v2.core.ontology_manager import OntologyManager
    mgr = OntologyManager()
    if "qudt-quantity-type" not in mgr.ontologies:
        import pytest; pytest.skip("qudt-quantity-type not in cache")
    engine = EnrichmentEngine(mgr)
    ctx = engine.enrich("http://qudt.org/vocab/quantitykind/Mass")
    assert ctx.widget == "unit_dropdown", f"Expected unit_dropdown, got {ctx.widget}"
    units = ctx.enrichments.get("applicable_units", [])
    assert len(units) > 5, f"Expected >5 units for Mass, got {len(units)}"
    assert any("KiloGM" in u for u in units), "kg not in Mass units from QUDT"


def test_layer3_foaf_namespace():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich("foaf:Person")
    assert ctx.widget == "property_suggestions"
    assert ctx.resolution == "namespace"


def test_layer3_schema_namespace():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich("https://schema.org/PostalAddress")
    assert ctx.widget == "property_suggestions"
    assert ctx.resolution == "namespace"


def test_fallback_unknown_iri():
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    ctx = EnrichmentEngine().enrich("http://example.org/totally/unknown/Thing")
    assert ctx.widget == "text"
    assert ctx.resolution == "none"


def test_to_dict_serialisable():
    import json
    from brick_app_v2.core.enrichment_engine import EnrichmentEngine
    engine = EnrichmentEngine()
    ctx = engine.enrich_datatype("xsd:boolean")
    d = engine.to_dict(ctx)
    assert json.dumps(d)  # must not raise
    assert d["widget"] == "boolean_toggle"
    assert d["resolution"] == "datatype"


def test_ontology_manager_stores_graph():
    from brick_app_v2.core.ontology_manager import OntologyManager
    mgr = OntologyManager()
    for name, data in mgr.ontologies.items():
        assert "graph" in data, f"Ontology '{name}' missing live graph"


# ── Shared Library ────────────────────────────────────────────────────────────

def test_shared_library_manager_imports():
    from common.library_manager import SharedLibraryManager
    assert SharedLibraryManager is not None


def test_shared_library_manager_instantiates():
    from common.library_manager import SharedLibraryManager
    mgr = SharedLibraryManager()
    assert mgr is not None
    assert mgr.base_path.exists(), f"Library base path does not exist: {mgr.base_path}"
