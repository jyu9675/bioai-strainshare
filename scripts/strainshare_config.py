#!/usr/bin/env python3
"""
The strainshare STANDARD — single source of truth for every threshold in the pipeline.

This is the "VALENCIA-for-strains" core: fixed, versioned, reference-based cutoffs so a
shared-strain / translocation / direction call means the same thing across studies and
labs. Import STANDARD (or load_config) everywhere instead of hard-coding numbers.

Changing any value is a spec change -> bump SPEC_VERSION so downstream results stay traceable.
A machine-readable mirror lives in scripts/strainshare_standard.yaml.
"""
import copy
import os

SPEC_VERSION = "0.1.0"

STANDARD = {
    "spec_version": SPEC_VERSION,
    "shared_strain": {
        "popani_primary": 0.999,      # lead call (matches the pilot deck)
        "popani_canonical": 0.99999,  # inStrain canonical "same strain" — always reported alongside
        "breadth_min": 0.5,           # percent_genome_compared floor for a valid comparison
        "coverage_min": 5,            # per-sample coverage floor upstream (profiling)
    },
    "contamination": {
        # Bray-Curtis community DISTANCE below this => "similar community" => contamination-like.
        "bray_curtis_similar_max": 0.5,
    },
    "generalist_filter": {
        # a genome "shared" in more than this fraction of BETWEEN-person pairs is a
        # generalist / DB artifact, not a transmission marker.
        "between_shared_rate_max": 0.10,
    },
    "direction": {
        # direction is inferred ONLY from longitudinal acquisition timing, never from sharing.
        "require_longitudinal": True,
        "min_timepoints": 2,
    },
    "low_biomass": {
        # below inStrain's usable coverage, route the target through StrainGE (M3).
        "strainge_fallback_coverage_min": 0.5,
    },
}


def _deep_update(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path=None):
    """Return the STANDARD, optionally overlaid with a user YAML. Never hard-fails:
    if pyyaml is missing or the file is absent, fall back to built-in defaults so the
    Windows analysis half runs with only pandas/numpy/matplotlib installed."""
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


if __name__ == "__main__":
    import json
    print(f"strainshare standard v{SPEC_VERSION}")
    print(json.dumps(STANDARD, indent=2))
