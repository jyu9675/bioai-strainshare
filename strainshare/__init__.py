"""strainshare — a standardized, contamination-aware framework for cross-body-site
bacterial strain sharing (e.g. gut <-> cervicovaginal).

The public API mirrors the pipeline stages:
    strainshare.analysis    shared-strain call + within/between null + contamination (M1/M2)
    strainshare.generalist  generalist-strain filter (M5)
    strainshare.direction   longitudinal-only transmission direction (M4)
    strainshare.plots        figures
    strainshare.benchmark   coverage-floor / precision-edge benchmarks
    strainshare.config       the versioned threshold STANDARD (single source of truth)
"""
from .config import STANDARD, SPEC_VERSION, load_config

__version__ = "0.1.0"
__all__ = ["STANDARD", "SPEC_VERSION", "load_config", "__version__"]
