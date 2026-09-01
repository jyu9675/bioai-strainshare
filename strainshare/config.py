"""The strainshare STANDARD — single source of truth for every threshold.

Fixed, versioned, reference-based cutoffs so a shared-strain / translocation / direction
call means the same thing across studies and labs. Changing any value is a spec change ->
bump SPEC_VERSION so downstream results stay traceable. A YAML mirror ships at
``strainshare/strainshare_standard.yaml``.
"""
import copy
import os

SPEC_VERSION = "0.1.0"

STANDARD = {
    "spec_version": SPEC_VERSION,
    # the two body sites compared for cross-site sharing. Works for any pair present in the
    # metadata `bodysite` column: ["gut","vagina"], ["oral","gut"], ["mother","infant"],
    # ["donor","recipient"] (FMT), etc. Class/direction labels are derived from these names.
    "site_pair": ["gut", "vagina"],
    "shared_strain": {
        "popani_primary": 0.999,      # lead call (matches the pilot deck)
        "popani_canonical": 0.99999,  # inStrain canonical "same strain" — reported alongside
        "breadth_min": 0.5,           # percent_genome_compared floor for a valid comparison
        "coverage_min": 5,            # per-sample coverage floor upstream (profiling)
    },
    "contamination": {
        "bray_curtis_similar_max": 0.5,  # BC distance below this => similar community => contamination-like
    },
    "generalist_filter": {
        "between_shared_rate_max": 0.10,  # genome shared in >10% of between-person pairs => generalist
    },
    "direction": {
        "require_longitudinal": True,     # direction only from longitudinal timing, never from sharing
        "min_timepoints": 2,
    },
    "low_biomass": {
        "strainge_fallback_coverage_min": 0.5,  # route sub-threshold targets through StrainGE (M3)
    },
}

# YAML mirror shipped inside the package
_YAML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strainshare_standard.yaml")


def site_classes(cfg):
    """Return (site_a, site_b, within_class, between_class) derived from cfg['site_pair'].
    For the default ["gut","vagina"] this yields the historical names within_gut_vagina /
    between_gut_vagina, so existing outputs are unchanged."""
    a, b = cfg.get("site_pair", ["gut", "vagina"])
    return a, b, f"within_{a}_{b}", f"between_{a}_{b}"


def _deep_update(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path=None):
    """Return the STANDARD, optionally overlaid with a user YAML. Never hard-fails: if
    pyyaml is missing or the file is absent, fall back to built-in defaults so the pure
    Python analysis half runs with only pandas/numpy/matplotlib installed."""
    cfg = copy.deepcopy(STANDARD)
    if not path:
        return cfg
    if not os.path.exists(path):
        print(f"[config] {path} not found; using built-in STANDARD defaults")
        return cfg
    try:
        import yaml
    except ImportError:
        print("[config] pyyaml not installed; using built-in STANDARD defaults")
        return cfg
    with open(path) as fh:
        user = yaml.safe_load(fh) or {}
    return _deep_update(cfg, user)
