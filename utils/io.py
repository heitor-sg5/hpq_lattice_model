import json
import os

from core.config import DATA_DIR

def load_residue_props():
    """Load residue properties from JSON file."""
    with open(os.path.join(DATA_DIR, "residues.json")) as f:
        return json.load(f)