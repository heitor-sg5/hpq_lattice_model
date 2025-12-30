class EnergyModel:
    def __init__(self, alpha=0.2, eps_HH=1.0, eps_HP=0.3, eps_Q=1.0):
        self.alpha = alpha # scales hydrophobic exposure energy
        self.eps_HH = eps_HH # energy gain for hydrophobic-hydrophobic contact
        self.eps_HP = eps_HP # energy penalty for hydrophobic-polar contact
        self.eps_Q = eps_Q # energy for charge-charge interaction

    def pair_energy(self, a, b):
        e = 0.0
        # Hydrophobic interactions
        if a.hydrophobicity > 0 and b.hydrophobicity > 0:
            e -= self.eps_HH # favorable, energy decreases
        elif a.hydrophobicity > 0 or b.hydrophobicity > 0:
            e += self.eps_HP # penalty, energy increases

        # Charge interactions
        if a.charge != 0 and b.charge != 0:
            if a.charge * b.charge < 0:
                e -= self.eps_Q # opposite charges attract
            else:
                e += self.eps_Q # same charge repels
        return e

    # Compute energy (= alpha * H * exposed) due to solvent exposure
    def compute_solvent_energy(self, chain, indices=None):
        energy = 0.0
        lattice = chain.lattice
        residues = chain.residues if indices is None else [chain.residues[i] for i in indices]

        for cube in residues:
            exposed = 6 # max neighbours in cubic lattice
            for nbr in lattice.get_neighbours(cube.position):
                if lattice.is_occupied(nbr):
                    exposed -= 1
            if cube.hydrophobicity > 0:
                energy += self.alpha * cube.hydrophobicity * exposed
        return energy

    # Compute pairwise contact energy (= sum(pair_energy) / 2) for non-bonded neighbours
    def compute_contact_energy(self, chain, indices=None):
        energy = 0.0
        lattice = chain.lattice
        residues = chain.residues if indices is None else [chain.residues[i] for i in indices]
        seen_pairs = set()

        for cube in residues:
            for nbr_pos in lattice.get_neighbours(cube.position):
                if not lattice.is_occupied(nbr_pos):
                    continue
                other = chain.get_cube_at(nbr_pos)
                if other is None or abs(cube.index - other.index) <= 1:
                    continue # skip bonded neighbours
                pair = tuple(sorted((cube.index, other.index)))
                if pair in seen_pairs:
                    continue # avoid double counting
                energy += self.pair_energy(cube, other)
                seen_pairs.add(pair)
        return energy / 2

    # Total energy = solvent exposure + contact interactions
    def compute_total_energy(self, chain):
        return self.compute_solvent_energy(chain) + self.compute_contact_energy(chain)

    def compute_local_energies(self, chain):
        local = {c.index: 0.0 for c in chain.residues}
        seen_pairs = set()

        # Pairwise contact energies
        for c in chain.residues:
            for nbr_pos in chain.lattice.get_neighbours(c.position):
                if chain.lattice.is_occupied(nbr_pos):
                    other = chain.get_cube_at(nbr_pos)
                    if other and abs(c.index - other.index) > 1:
                        pair = tuple(sorted((c.index, other.index)))
                        if pair in seen_pairs:
                            continue
                        e = self.pair_energy(c, other)
                        local[c.index] += e / 2 # half energy to each residue
                        local[other.index] += e / 2
                        seen_pairs.add(pair)

        # Solvent exposure contribution
        for c in chain.residues:
            exposed = 6
            for nbr in chain.lattice.get_neighbours(c.position):
                if chain.lattice.is_occupied(nbr):
                    exposed -= 1
            if c.hydrophobicity > 0:
                local[c.index] += self.alpha * c.hydrophobicity
        return local