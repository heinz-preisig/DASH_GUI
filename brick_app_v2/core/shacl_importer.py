"""
SHACL Importer
==============
Parse SHACL NodeShape definitions from Turtle (.ttl) files and convert them
into SHACLBrick JSON files stored in a brick library.

Public API
----------
    from brick_app_v2.core.shacl_importer import SHACLImporter

    importer = SHACLImporter(brick_core)          # or pass repository_path
    result   = importer.import_file(
                   ttl_path   = "/path/to/shapes.ttl",
                   library    = "my_library",
                   prefix     = "shapes",         # optional name prefix
               )
    # result: ImportResult(imported, skipped, errors, bricks)

    result = importer.import_directory(
                   directory  = "/path/to/ttl_dir",
                   per_file_libraries = True,      # one lib per file
                   combined_library   = "all",     # also write combined lib
                   library_prefix     = "digipass",
               )
"""

from __future__ import annotations

import json
import os
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from rdflib import Graph, URIRef, Literal, BNode, Namespace
    from rdflib.namespace import RDF, RDFS, SH, XSD
    _RDFLIB_OK = True
except ImportError:
    _RDFLIB_OK = False

DASH = Namespace("http://datashapes.org/dash#") if _RDFLIB_OK else None


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ImportResult:
    imported: int = 0
    skipped:  int = 0
    errors:   List[str] = field(default_factory=list)
    bricks:   List[Dict[str, Any]] = field(default_factory=list)

    def merge(self, other: "ImportResult") -> "ImportResult":
        return ImportResult(
            imported = self.imported + other.imported,
            skipped  = self.skipped  + other.skipped,
            errors   = self.errors   + other.errors,
            bricks   = self.bricks   + other.bricks,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "imported": self.imported,
            "skipped":  self.skipped,
            "errors":   self.errors,
            "brick_count": len(self.bricks),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _local_name(uri: Any) -> str:
    s = str(uri)
    for sep in ("#", "/"):
        if sep in s:
            return s.rsplit(sep, 1)[-1]
    return s


def _sanitize(name: str, max_len: int = 60) -> str:
    s = re.sub(r"[^\w\s-]", "", name).strip()
    s = re.sub(r"\s+", "_", s)
    return s[:max_len].lower() or "brick"


def _rdf_list(g: Graph, head: Any) -> List[Any]:
    items, node = [], head
    while node and node != RDF.nil:
        first = g.value(node, RDF.first)
        if first is not None:
            items.append(first)
        node = g.value(node, RDF.rest)
    return items


# ── Core parser ───────────────────────────────────────────────────────────────

class _ShapeParser:
    """Converts a loaded rdflib Graph into a list of brick dicts."""

    def __init__(self, g: Graph, source_file: str):
        self.g = g
        self.source_file = source_file

    # ── leaf property ─────────────────────────────────────────────────────

    def _parse_leaf(self, prop_bn: Any) -> Optional[Dict[str, Any]]:
        g = self.g
        path        = g.value(prop_bn, SH.path)
        label       = str(g.value(prop_bn, RDFS.label) or "")
        datatype    = g.value(prop_bn, SH["datatype"])
        node_ref    = g.value(prop_bn, SH.node)
        node_kind   = g.value(prop_bn, SH.nodeKind)
        has_value   = g.value(prop_bn, SH.hasValue)
        in_head     = g.value(prop_bn, SH["in"])
        min_count   = int(g.value(prop_bn, SH.minCount) or 0)
        max_count_v = g.value(prop_bn, SH.maxCount)
        max_count   = int(max_count_v) if max_count_v is not None else None
        description = str(g.value(prop_bn, SH.description) or
                          g.value(prop_bn, RDFS.comment) or "")
        min_incl    = g.value(prop_bn, SH.minInclusive)
        max_incl    = g.value(prop_bn, SH.maxInclusive)
        single_line = g.value(prop_bn, DASH.singleLine) if DASH else None

        # Pure sub-shape reference with no leaf data → skip
        if (node_ref is not None and datatype is None
                and node_kind is None and has_value is None
                and in_head is None):
            return None

        in_values = [str(i) for i in _rdf_list(g, in_head)] if in_head else []

        # Derive template_type
        if has_value is not None:
            tmpl = "static_label"
        elif in_head is not None and node_kind is not None:
            tmpl = "dropdown_iri"
        elif datatype and "date" in str(datatype):
            tmpl = "date_field"
        elif datatype and "decimal" in str(datatype):
            tmpl = "decimal_with_unit"
        else:
            tmpl = "free_text"

        return {
            "path":          str(path) if path else "",
            "label":         label,
            "description":   description,
            "min_count":     min_count,
            "max_count":     max_count,
            "datatype":      str(datatype) if datatype else None,
            "node_kind":     str(node_kind) if node_kind else None,
            "in_values":     in_values,
            "has_value":     str(has_value) if has_value is not None else None,
            "min_inclusive": float(min_incl) if min_incl is not None else None,
            "max_inclusive": float(max_incl) if max_incl is not None else None,
            "single_line":   (str(single_line).lower() == "true")
                             if single_line is not None else None,
            "template_type": tmpl,
        }

    # ── xone branch ──────────────────────────────────────────────────────

    def _parse_xone_branch(self, branch_bn: Any) -> List[Dict[str, Any]]:
        props = []
        for prop_bn in self.g.objects(branch_bn, SH.property):
            lp = self._parse_leaf(prop_bn)
            if lp:
                props.append(lp)
        return props

    # ── one shape → one brick ─────────────────────────────────────────────

    def _parse_shape(self, shape_uri: Any) -> Dict[str, Any]:
        g = self.g
        name    = _local_name(shape_uri)
        tgt_cls = g.value(shape_uri, SH.targetClass)
        desc    = str(g.value(shape_uri, RDFS.comment) or
                      g.value(shape_uri, RDFS.label) or "")

        leaf_properties:  List[Dict]       = []
        xone_alternatives: List[List[Dict]] = []
        sub_refs: List[str]                = []

        for prop_bn in g.objects(shape_uri, SH.property):
            node_ref = g.value(prop_bn, SH.node)
            if node_ref is not None:
                sub_refs.append(_local_name(node_ref))
            lp = self._parse_leaf(prop_bn)
            if lp:
                leaf_properties.append(lp)

        xone_head = g.value(shape_uri, SH.xone)
        if xone_head:
            for branch_bn in _rdf_list(g, xone_head):
                branch = self._parse_xone_branch(branch_bn)
                if branch:
                    xone_alternatives.append(branch)

        if xone_alternatives:
            tmpl = "xone_choice"
        elif not leaf_properties and sub_refs:
            tmpl = "custom"
        elif leaf_properties:
            types = [lp.get("template_type", "free_text") for lp in leaf_properties]
            tmpl = Counter(types).most_common(1)[0][0]
        else:
            tmpl = "custom"

        tags = [f"source:{self.source_file}"]
        tags += [f"refs:{r}" for r in sub_refs[:5]]

        return {
            "brick_id":          str(uuid.uuid4()),
            "name":              name,
            "description":       desc,
            "template_type":     tmpl,
            "namespace":         "dpp",
            "target_class":      str(tgt_cls) if tgt_cls else str(shape_uri),
            "leaf_properties":   leaf_properties,
            "xone_alternatives": xone_alternatives,
            "tags":              tags,
            "object_type":       "NodeShape",
            "properties":        {},
            "constraints":       [],
            "targets":           [],
            "property_path":     "",
            "created_at":        "",
            "updated_at":        "",
            "metadata": {
                "source_iri":  str(shape_uri),
                "source_file": self.source_file,
            },
        }

    # ── public ────────────────────────────────────────────────────────────

    def parse_all(self) -> List[Dict[str, Any]]:
        return [self._parse_shape(uri)
                for uri in self.g.subjects(RDF.type, SH.NodeShape)]


# ── SHACLImporter ─────────────────────────────────────────────────────────────

class SHACLImporter:
    """
    Import SHACL .ttl files into a brick library.

    Parameters
    ----------
    brick_core_or_path:
        Either a BrickCore instance or a str/Path to the repository root.
        If None, uses the shared_library_manager path.
    """

    def __init__(self, brick_core_or_path=None):
        if not _RDFLIB_OK:
            raise ImportError("rdflib is required: pip install rdflib")

        if brick_core_or_path is None or isinstance(brick_core_or_path, (str, Path)):
            if brick_core_or_path is None:
                from pathlib import Path as _P
                _root = _P(__file__).resolve().parent.parent.parent
                self.repository_path = str(_root / "ShaclForm-library" / "bricks")
            else:
                self.repository_path = str(brick_core_or_path)
        else:
            # Assume BrickCore instance
            self.repository_path = brick_core_or_path.repository_path

        os.makedirs(self.repository_path, exist_ok=True)

    # ── internal helpers ──────────────────────────────────────────────────

    def _load_iri_index(self, lib_dir: Path) -> Dict[str, Path]:
        """
        Scan an existing library directory and return a mapping of
        source_iri → file path for every brick already written there.
        """
        index: Dict[str, Path] = {}
        if not lib_dir.exists():
            return index
        for fpath in lib_dir.glob("*.json"):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                iri = data.get("metadata", {}).get("source_iri")
                if iri:
                    index[iri] = fpath
            except Exception:
                pass
        return index

    # ── internal write ────────────────────────────────────────────────────

    def _write_bricks(self, bricks: List[Dict], library: str,
                      dedupe_iris: Optional[set] = None) -> ImportResult:
        lib_dir = Path(self.repository_path) / library
        lib_dir.mkdir(parents=True, exist_ok=True)

        # Build IRI → existing-file index for idempotent overwrites
        iri_index = self._load_iri_index(lib_dir)

        result = ImportResult()
        for brick in bricks:
            iri = brick["metadata"]["source_iri"]
            if dedupe_iris is not None:
                if iri in dedupe_iris:
                    result.skipped += 1
                    continue
                dedupe_iris.add(iri)

            # Reuse existing file path + brick_id if already imported
            if iri in iri_index:
                existing_path = iri_index[iri]
                try:
                    with open(existing_path) as f:
                        existing = json.load(f)
                    brick["brick_id"]   = existing["brick_id"]
                    brick["created_at"] = existing.get("created_at", "")
                except Exception:
                    pass
                fpath = existing_path
            else:
                safe  = _sanitize(brick["name"])
                fname = f"{safe}_{brick['brick_id']}.json"
                fpath = lib_dir / fname
                iri_index[iri] = fpath  # register for this run

            try:
                with open(fpath, "w") as f:
                    json.dump(brick, f, indent=2)
                result.imported += 1
                result.bricks.append(brick)
            except Exception as e:
                result.errors.append(f"{brick['name']}: {e}")

        return result

    # ── public: single file ───────────────────────────────────────────────

    def import_file(self, ttl_path: str | Path, library: str,
                    prefix: str = "",
                    dedupe_iris: Optional[set] = None) -> ImportResult:
        """
        Parse one .ttl file and write bricks into *library*.

        Parameters
        ----------
        ttl_path    : path to the Turtle file
        library     : target library name (created if absent)
        prefix      : optional string to prepend to brick names
        dedupe_iris : shared set of already-seen IRIs (for combined imports)
        """
        ttl_path = Path(ttl_path)
        result = ImportResult()

        if not ttl_path.exists():
            result.errors.append(f"File not found: {ttl_path}")
            return result

        g = Graph()
        try:
            g.parse(str(ttl_path), format="turtle")
        except Exception as e:
            result.errors.append(f"Parse error in {ttl_path.name}: {e}")
            return result

        parser = _ShapeParser(g, ttl_path.name)
        bricks = parser.parse_all()

        if prefix:
            for b in bricks:
                b["name"] = f"{prefix}_{b['name']}"

        written = self._write_bricks(bricks, library, dedupe_iris)
        return written

    # ── public: directory ─────────────────────────────────────────────────

    def import_directory(
        self,
        directory: str | Path,
        library_prefix:      str  = "imported",
        per_file_libraries:  bool = True,
        combined_library:    Optional[str] = None,
        glob:                str  = "*.ttl",
    ) -> Dict[str, ImportResult]:
        """
        Import all matching files in *directory*.

        Parameters
        ----------
        directory           : folder containing .ttl files
        library_prefix      : prefix for per-file library names
        per_file_libraries  : write one library per file
        combined_library    : if set, also write a deduplicated combined library
        glob                : file pattern (default "*.ttl")

        Returns
        -------
        dict mapping library_name → ImportResult
        """
        directory = Path(directory)
        ttl_files = sorted(directory.glob(glob))
        if not ttl_files:
            return {}

        results: Dict[str, ImportResult] = {}
        combined_iris: set = set()
        combined_bricks: List[Dict] = []

        for ttl_path in ttl_files:
            stem     = ttl_path.stem
            lib_name = f"{library_prefix}_{stem}" if library_prefix else stem

            g = Graph()
            try:
                g.parse(str(ttl_path), format="turtle")
            except Exception as e:
                results[lib_name] = ImportResult(errors=[f"Parse error: {e}"])
                continue

            parser = _ShapeParser(g, ttl_path.name)
            bricks = parser.parse_all()

            if per_file_libraries:
                r = self._write_bricks(bricks, lib_name)
                results[lib_name] = r

            if combined_library is not None:
                combined_bricks.extend(bricks)

        if combined_library and combined_bricks:
            r = self._write_bricks(combined_bricks, combined_library,
                                   dedupe_iris=combined_iris)
            results[combined_library] = r

        return results

    # ── public: common-parts library ──────────────────────────────────────

    def import_common(
        self,
        directory: str | Path,
        common_library: str,
        min_files: int = 2,
        glob: str = "*.ttl",
    ) -> ImportResult:
        """
        Parse all .ttl files in *directory*, find every NodeShape IRI that
        appears in at least *min_files* different files, and write those
        shapes into *common_library*.

        Parameters
        ----------
        directory       : folder containing .ttl files
        common_library  : target library name for shared shapes
        min_files       : minimum number of files a shape must appear in
                          (default 2 = shared by at least two files)
        glob            : file pattern (default "*.ttl")
        """
        directory = Path(directory)
        ttl_files = sorted(directory.glob(glob))
        if not ttl_files:
            return ImportResult(errors=[f"No files matching '{glob}' in {directory}"])

        # Pass 1: count how many files each IRI appears in
        iri_file_count: Dict[str, int]          = {}
        iri_to_brick:   Dict[str, Dict]         = {}  # last-seen brick per IRI
        iri_sources:    Dict[str, List[str]]    = {}  # all source files per IRI

        for ttl_path in ttl_files:
            g = Graph()
            try:
                g.parse(str(ttl_path), format="turtle")
            except Exception:
                continue
            parser = _ShapeParser(g, ttl_path.name)
            for brick in parser.parse_all():
                iri = brick["metadata"]["source_iri"]
                iri_file_count[iri] = iri_file_count.get(iri, 0) + 1
                iri_to_brick[iri]   = brick
                iri_sources.setdefault(iri, []).append(ttl_path.name)

        # Pass 2: keep only shapes present in >= min_files files
        common_bricks = []
        for iri, count in iri_file_count.items():
            if count >= min_files:
                brick = iri_to_brick[iri]
                # Record all source files in metadata and tags
                brick["metadata"]["found_in"] = iri_sources[iri]
                brick["metadata"]["file_count"] = count
                src_tag = f"common:{count}_files"
                if src_tag not in brick["tags"]:
                    brick["tags"].insert(0, src_tag)
                common_bricks.append(brick)

        if not common_bricks:
            return ImportResult(errors=[
                f"No shapes found in >= {min_files} files"
            ])

        return self._write_bricks(common_bricks, common_library)

    # ── public: raw turtle string ─────────────────────────────────────────

    def import_turtle_string(self, turtle: str, library: str,
                             source_name: str = "upload") -> ImportResult:
        """Parse a Turtle string (e.g. from a file upload) and import it."""
        g = Graph()
        try:
            g.parse(data=turtle, format="turtle")
        except Exception as e:
            return ImportResult(errors=[f"Parse error: {e}"])

        parser = _ShapeParser(g, source_name)
        bricks = parser.parse_all()
        return self._write_bricks(bricks, library)
