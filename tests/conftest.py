"""
Shared pytest configuration for the DASH_GUI test suite.
Ensures the project root is on sys.path so all imports work uniformly.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
