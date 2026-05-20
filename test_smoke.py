#!/usr/bin/env python3
"""
Smoke tests — verify core classes instantiate without errors.
Run with: uv run python -m pytest test_smoke.py -v
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


# ── Shared Library ────────────────────────────────────────────────────────────

def test_shared_library_manager_imports():
    from common.library_manager import SharedLibraryManager
    assert SharedLibraryManager is not None


def test_shared_library_manager_instantiates():
    from common.library_manager import SharedLibraryManager
    mgr = SharedLibraryManager()
    assert mgr is not None
    assert mgr.base_path.exists(), f"Library base path does not exist: {mgr.base_path}"
