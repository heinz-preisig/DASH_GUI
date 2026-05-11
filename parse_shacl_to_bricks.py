#!/usr/bin/env python3
"""
CLI wrapper around brick_app_v2.core.shacl_importer.SHACLImporter.

Usage
-----
    python parse_shacl_to_bricks.py <directory> [options]

    python parse_shacl_to_bricks.py /path/to/ttl_dir
    python parse_shacl_to_bricks.py /path/to/ttl_dir --prefix myproject
    python parse_shacl_to_bricks.py /path/to/ttl_dir --no-per-file
    python parse_shacl_to_bricks.py /path/to/ttl_dir --combined myproject_all
    python parse_shacl_to_bricks.py /path/to/file.ttl --library mylib

Options
-------
    <directory|file>        Source: a directory of .ttl files, or a single file
    --prefix PREFIX         Library name prefix for per-file libs  [default: imported]
    --library LIBRARY       Target library name (single-file mode only)
    --no-per-file           Skip writing individual per-file libraries
    --combined NAME         Also write a deduplicated combined library with this name
    --repo PATH             Path to brick repository root  [default: shared_libraries/bricks]
    --glob PATTERN          File glob pattern  [default: *.ttl]
"""

import argparse
import sys
from pathlib import Path

# Make the project importable regardless of cwd
_here = Path(__file__).resolve().parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from brick_app_v2.core.shacl_importer import SHACLImporter


def main():
    parser = argparse.ArgumentParser(
        description="Import SHACL NodeShapes from .ttl files into brick libraries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source", help="Directory of .ttl files or a single .ttl file")
    parser.add_argument("--prefix",    default="imported",
                        help="Library name prefix for per-file libraries (default: imported)")
    parser.add_argument("--library",   default=None,
                        help="Target library name (single-file mode)")
    parser.add_argument("--no-per-file", action="store_true",
                        help="Skip writing individual per-file libraries")
    parser.add_argument("--combined",  default=None, metavar="NAME",
                        help="Also write a deduplicated combined library")
    parser.add_argument("--common",    default=None, metavar="NAME",
                        help="Write a library of shapes shared across multiple files")
    parser.add_argument("--min-files", default=2, type=int, metavar="N",
                        help="Minimum file count for --common (default: 2)")
    parser.add_argument("--repo",      default=None, metavar="PATH",
                        help="Brick repository path (default: shared_libraries/bricks)")
    parser.add_argument("--glob",      default="*.ttl",
                        help="File glob pattern (default: *.ttl)")
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        sys.exit(f"ERROR: source not found: {source}")

    importer = SHACLImporter(args.repo)

    # ── Single file ──────────────────────────────────────────────────────
    if source.is_file():
        library = args.library or f"{args.prefix}_{source.stem}"
        print(f"Importing {source.name} → library '{library}' …")
        result = importer.import_file(source, library)
        print(f"  Imported: {result.imported}  Skipped: {result.skipped}")
        for e in result.errors:
            print(f"  ERROR: {e}")
        return

    # ── Directory ────────────────────────────────────────────────────────
    ttl_files = sorted(source.glob(args.glob))
    if not ttl_files:
        sys.exit(f"No files matching '{args.glob}' found in {source}")

    print(f"Found {len(ttl_files)} files in {source}\n")

    results = importer.import_directory(
        directory          = source,
        library_prefix     = args.prefix,
        per_file_libraries = not args.no_per_file,
        combined_library   = args.combined,
        glob               = args.glob,
    )

    if args.common:
        print(f"\nExtracting common parts (min {args.min_files} files) → '{args.common}' …")
        common_result = importer.import_common(
            directory      = source,
            common_library = args.common,
            min_files      = args.min_files,
            glob           = args.glob,
        )
        results[args.common] = common_result

    total_imported = total_skipped = 0
    for lib_name, result in results.items():
        status = f"{result.imported} imported, {result.skipped} skipped"
        if result.errors:
            status += f", {len(result.errors)} errors"
        print(f"  [{lib_name}]  {status}")
        for e in result.errors:
            print(f"    ERROR: {e}")
        total_imported += result.imported
        total_skipped  += result.skipped

    print(f"\nTotal: {total_imported} bricks written, {total_skipped} duplicates skipped")
    print(f"Repository: {importer.repository_path}")


if __name__ == "__main__":
    main()
