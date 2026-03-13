class Lattice:
    def __init__(self):
        self.occupied = set()  # occupied positions (x, y, z)
        self._cubes = {}       # position -> Cube for fast lookup

    def is_occupied(self, position):
        return tuple(position) in self.occupied  # check if a lattice position is occupied

    def get_cube(self, position):
        return self._cubes.get(tuple(position))

    def add_cube(self, cube):
        pos = tuple(cube.position)
        if self.is_occupied(pos):
            raise ValueError(f"Position {pos} already occupied")
        self.occupied.add(pos)  # mark the cube's position as occupied
        self._cubes[pos] = cube

    def remove_cube(self, cube):
        pos = tuple(cube.position)
        self.occupied.discard(pos)  # remove a cube from the lattice
        self._cubes.pop(pos, None)

    def get_neighbours(self, position):
        x, y, z = position
        return [
            (x + 1, y, z), (x - 1, y, z),
            (x, y + 1, z), (x, y - 1, z),
            (x, y, z + 1), (x, y, z - 1)
        ] # return 6 neighboring faces in 3d lattice to check contacts and available moves