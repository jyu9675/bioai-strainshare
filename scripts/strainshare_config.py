"""Compatibility shim.

The canonical STANDARD now lives in the installable package (``strainshare.config``) so
there is a single source of truth for every threshold. The numbered legacy scripts import
``strainshare_config`` by name; this re-exports the package so they pick up the same values.
"""
import os
import sys

# make the in-repo package importable even without `pip install`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strainshare.config import STANDARD, SPEC_VERSION, load_config, _deep_update  # noqa: F401,E402
