"""
Regression tests for Git hygiene.

Ensures that compiled Python files and IDE metadata are not tracked in Git,
which was the source of "local changes will be overwritten by merge" errors.
"""

import subprocess

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_no_pycache_tracked():
    """Compiled Python files must not be tracked by Git."""
    tracked = _git_ls_files()
    bad = [
        path
        for path in tracked
        if "__pycache__" in path or path.endswith((".pyc", ".pyo"))
    ]
    assert not bad, f"Tracked compiled Python files found: {bad}"


def test_gitignore_ignores_pycache():
    """.gitignore must contain the standard Python cache patterns."""
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore not found"
    content = gitignore.read_text()
    assert "__pycache__/" in content, "Missing __pycache__/ rule in .gitignore"
    assert "*.py[cod]" in content, "Missing *.py[cod] rule in .gitignore"
