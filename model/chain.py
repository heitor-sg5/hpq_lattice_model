from model.cube import Cube

class PeptideChain:
    def __init__(self, residue_props, lattice):
        self.residues = [] # list of Cube objects
        self.residue_props = residue_props
        self.lattice = lattice

    # Initialize chain in a linear configuration along x-axis.
    def initialize_linear(self, sequence):
        for i, aa in enumerate(sequence):
            properties = self.residue_props.get(aa)
            if properties is None:
                raise ValueError(f"Unknown amino acid: {aa}")
            pos = (i, i % 2, 0) # zigzag pattern of y alternating 0/1 (x increases linearly)
            cube = Cube(index=i, aa=aa, properties=properties, position=pos)
            self.residues.append(cube)
            self.lattice.add_cube(cube)

    def get_cube_at(self, position):
        for cube in self.residues:
            if cube.position == position:
                return cube # return the cube at a given position
        return None

    # Returns chain structure as a dict
    def get_structure(self):
        return {
            "sequence": "".join([c.aa for c in self.residues]),
            "residues": [
                {
                    "index": c.index,
                    "aa": c.aa,
                    "x": c.position[0],
                    "y": c.position[1],
                    "z": c.position[2],
                    "H": c.hydrophobicity,
                    "Q": c.charge
                }
                for c in self.residues
            ]
        }

    # Returns state of the chain for logging
    def get_log_state(self):
        return {
            "length": len(self.residues),
            "residues": [
                {
                    "index": c.index,
                    "aa": c.aa,
                    "position": c.position,
                    "H": c.hydrophobicity,
                    "Q": c.charge
                }
                for c in self.residues
            ]
        }