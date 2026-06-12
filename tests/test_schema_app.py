"""
Schema app tests — converted from schema_app/test_ui_metadata.py and
schema_app/test_shacl_export.py (previously broken script-style files).

Covers:
  - Schema / UIMetadata instantiation
  - Sequence management and reordering
  - Grouping and parent-child nesting
  - Serialisation round-trip
  - SHACL export (skipped if no schemas exist in the library)
"""
import pytest
from schema_app.core.schema_core import Schema, UIMetadata, SchemaCore


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_schema():
    return Schema(
        schema_id="test-schema-001",
        name="Product Schema",
        description="Test schema",
        root_brick_id="product-node",
        component_brick_ids=["company-prop", "name-prop", "address-node", "street-prop"],
    )


# ── Schema creation ───────────────────────────────────────────────────────────

def test_schema_creates_with_components(sample_schema):
    assert sample_schema.name == "Product Schema"
    assert len(sample_schema.component_brick_ids) == 4


# ── Sequence management ───────────────────────────────────────────────────────

def test_set_and_get_sequence(sample_schema):
    sample_schema.set_component_sequence("company-prop", 0)
    sample_schema.set_component_sequence("name-prop", 1)
    assert sample_schema.get_component_sequence("company-prop") == 0
    assert sample_schema.get_component_sequence("name-prop") == 1


def test_get_components_by_sequence(sample_schema):
    for i, bid in enumerate(sample_schema.component_brick_ids):
        sample_schema.set_component_sequence(bid, i)
    ordered = sample_schema.get_components_by_sequence()
    assert ordered == sample_schema.component_brick_ids


def test_reorder_component(sample_schema):
    for i, bid in enumerate(sample_schema.component_brick_ids):
        sample_schema.set_component_sequence(bid, i)
    sample_schema.reorder_component("street-prop", 1)
    seq = sample_schema.get_component_sequence("street-prop")
    assert seq == 1


# ── Grouping ──────────────────────────────────────────────────────────────────

def test_create_group_and_add_members(sample_schema):
    sample_schema.create_group("personal", "Personal Information", "Personal details", 0)
    sample_schema.add_component_to_group("name-prop", "personal")
    members = sample_schema.get_group_members("personal")
    assert "name-prop" in members


def test_get_groups_by_sequence(sample_schema):
    sample_schema.create_group("g1", "Group 1", "", 0)
    sample_schema.create_group("g2", "Group 2", "", 1)
    groups = sample_schema.get_groups_by_sequence()
    assert len(groups) >= 2


def test_get_components_without_group(sample_schema):
    sample_schema.create_group("g1", "G1", "", 0)
    sample_schema.add_component_to_group("name-prop", "g1")
    ungrouped = sample_schema.get_components_without_group()
    assert "name-prop" not in ungrouped
    assert "company-prop" in ungrouped


# ── Parent-child nesting ──────────────────────────────────────────────────────

def test_set_component_parent(sample_schema):
    sample_schema.set_component_parent("street-prop", "address-node")
    assert sample_schema.get_ui_parent("street-prop") == "address-node"


def test_get_ui_children(sample_schema):
    sample_schema.set_component_parent("street-prop", "address-node")
    children = sample_schema.get_ui_children("address-node")
    assert "street-prop" in children


def test_get_ui_tree(sample_schema):
    sample_schema.set_component_parent("street-prop", "address-node")
    tree = sample_schema.get_ui_tree()
    assert isinstance(tree, dict)


# ── Label and help text ───────────────────────────────────────────────────────

def test_set_and_get_label(sample_schema):
    sample_schema.set_component_label("name-prop", "Full Name")
    meta = sample_schema.get_component_ui_metadata("name-prop")
    assert meta.label == "Full Name"


def test_set_and_get_help_text(sample_schema):
    sample_schema.set_component_help_text("name-prop", "Enter full name")
    meta = sample_schema.get_component_ui_metadata("name-prop")
    assert meta.help_text == "Enter full name"


# ── Serialisation round-trip ──────────────────────────────────────────────────

def test_schema_to_dict(sample_schema):
    sample_schema.set_component_label("name-prop", "Full Name")
    d = sample_schema.to_dict()
    assert d["name"] == "Product Schema"
    assert "component_ui_metadata" in d


def test_schema_round_trip(sample_schema):
    sample_schema.set_component_label("name-prop", "Full Name")
    sample_schema.set_component_sequence("name-prop", 2)
    d = sample_schema.to_dict()
    restored = Schema.from_dict(d)
    assert restored.name == sample_schema.name
    assert len(restored.component_ui_metadata) == len(sample_schema.component_ui_metadata)
    assert restored.get_component_ui_metadata("name-prop").label == "Full Name"


# ── SHACL export ──────────────────────────────────────────────────────────────

def test_shacl_exporter_instantiates():
    from schema_app.core.shacl_export import SHACLExporter
    from schema_app.core.brick_integration import BrickIntegration
    exporter = SHACLExporter(BrickIntegration())
    assert exporter is not None


def test_shacl_export_produces_output():
    from schema_app.core.shacl_export import SHACLExporter
    from schema_app.core.brick_integration import BrickIntegration
    core = SchemaCore()
    schemas = core.get_all_schemas()
    if not schemas:
        pytest.skip("No schemas in library — create one first")
    schema = schemas[0]
    exporter = SHACLExporter(BrickIntegration())
    output = exporter.export_schema(schema)
    assert output and len(output) > 0
    assert "@prefix" in output or "sh:" in output
