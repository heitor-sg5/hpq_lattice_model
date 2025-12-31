class Cube:
    def __init__(self, index, aa, properties, position=None):
        self.index = index # position in sequence
        self.aa = aa # amino acid type (single letter code)
        self.hydrophobicity = properties.get("hydrophobicity", 0.0) # get hydrophobicity score
        self.charge = properties.get("charge", 0) # get charge
        self.position = position  # tuple (x, y, z)

    def set_position(self, position):
        self.position = position