class EnergyModel:
    def __init__(self, alpha=0.2, eps_HH=1.0, eps_HP=0.3, eps_PP=0.1, eps_Q=1.0):
        self.alpha = alpha # scales hydrophobic exposure energy
        self.eps_HH = eps_HH # energy gain for hydrophobic-hydrophobic contact
        self.eps_HP = eps_HP # energy penalty for hydrophobic-polar contact
        self.eps_PP = eps_PP # energy gain for polar-polar contact
        self.eps_Q = eps_Q # energy for charge-charge interaction

    def pair_energy(self, a, b):
        e = 0.0
        # Hydrophobic interactions
        if a.hydrophobicity > 0 and b.hydrophobicity > 0:
            e -= self.eps_HH # favorable, energy decreases
        elif a.hydrophobicity > 0 or b.hydrophobicity > 0:
            e += self.eps_HP # penalty, energy increases
        
        # Polar interactions
        if a.hydrophobicity < 0 and b.hydrophobicity < 0:
            e -= self.eps_PP # favorable, energy decreases

        # Charge interactions
        if a.charge != 0 and b.charge != 0:
            if a.charge * b.charge < 0: # opposite charge
                e -= self.eps_Q # favorable, energy decreases
            else: # same charge
                e += self.eps_Q # penalty, energy increases
        return e

    # Compute energy (= alpha * H * exposed) due to solvent exposure
    def compute_solvent_energy(self, cube, lattice):
        exposed = 6
        for nbr in lattice.get_neighbours(cube.position):
            if lattice.is_occupied(nbr):
                exposed -= 1
        if cube.hydrophobicity > 0:
            return self.alpha * cube.hydrophobicity * exposed
        return 0.0

    # Compute contact energy contribution for a single residue
    def compute_contact_energy(self, cube, chain, lattice, seen_pairs=None):
        energy = 0.0
        if seen_pairs is None:
            seen_pairs = set() # fallback for single-residue call
        for nbr_pos in lattice.get_neighbours(cube.position):
            if not lattice.is_occupied(nbr_pos):
                continue
            other = chain.get_cube_at(nbr_pos)
            if other is None or abs(cube.index - other.index) <= 1:
                continue
            pair = tuple(sorted((cube.index, other.index)))
            if pair in seen_pairs:
                continue
            e = self.pair_energy(cube, other)
            energy += e / 2 # split between both residues
            seen_pairs.add(pair)
        return energy

    # Compute local energies for the entire chain
    def compute_local_energies(self, chain):
        local = {c.index: 0.0 for c in chain.residues}
        lattice = chain.lattice
        seen_pairs = set() # shared across all residues

        for cube in chain.residues:
            # Solvent energy
            local[cube.index] += self.compute_solvent_energy(cube, lattice)
            # Contact energy
            local[cube.index] += self.compute_contact_energy(cube, chain, lattice, seen_pairs)
        return local