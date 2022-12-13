import io
import enum
import dataclasses
import itertools
import typing as tp

import utils


class RopePhysics:

    @dataclasses.dataclass(unsafe_hash=True)
    class Coord:
        x: int
        y: int

        def _add(self, other: 'Coord', _type=None) -> 'Coord':
            return (_type or type(self))(self.x + other.x, self.y + other.y)

        def _sub(self, other: 'Coord', _type=None) -> 'Coord':
            return (_type or type(self))(self.x - other.x, self.y - other.y)

    @dataclasses.dataclass(unsafe_hash=True)
    class Pos(Coord):

        def move(self, delta: 'Delta') -> 'Pos':
            return self._add(delta)

        def delta(self, other: 'Pos') -> 'Delta':
            return other._sub(self, RopePhysics.Delta)

    @dataclasses.dataclass(unsafe_hash=True)
    class Delta(Coord):

        @utils.classproperty
        def null(cls) -> 'Delta':
            return cls.__unit
    
    Delta._Delta__unit = Delta(0, 0)

    class Way(enum.Enum):
        UP = enum.auto()
        DOWN = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

        @classmethod
        def from_str(cls, text: str) -> 'Way':
            return next(way for way in cls if way.name.startswith(text))

    @dataclasses.dataclass(unsafe_hash=True)
    class Instruction:
        way: 'Way'
        count: int

        @classmethod
        def from_raw(cls, line: str) -> 'Instruction':
            way, _, count = line.partition(" ")
            return cls(RopePhysics.Way.from_str(way), int(count))

    _shifts = {
        Way.UP: Delta(0, -1),
        Way.DOWN: Delta(0, 1),
        Way.LEFT: Delta(-1, 0),
        Way.RIGHT: Delta(1, 0),
    }

    @dataclasses.dataclass
    class Rope:
        knots: tp.List['Pos']
        visited: tp.Set['Pos']

        @classmethod
        def create(cls, length: int):
            start = RopePhysics.Pos(0, 0)
            return cls([start for _ in range(length)], set([start]))

        def apply(self, instruction: 'Instruction'):
            for _ in range(instruction.count):
                self.knots[0] = self.knots[0].move(RopePhysics._shifts[instruction.way])

                for i in range(1, len(self.knots)):
                    self.knots[i] = self.follow(self.knots[i], self.knots[i-1])

                self.visited.add(self.knots[-1])

        def follow(self, follower: 'Pos', target: 'Pos') -> 'Pos':
            delta = follower.delta(target)
            movment = RopePhysics._follows[delta]
            return follower.move(movment)

    _follows = {
        # 0
        Delta.null: Delta.null,
        # 1-ortho
        Delta(+1,  0): Delta.null,
        Delta(-1,  0): Delta.null,
        Delta( 0, +1): Delta.null,
        Delta( 0, -1): Delta.null,
        # 1-diagonal
        Delta(-1, -1): Delta.null,
        Delta(-1, +1): Delta.null,
        Delta(+1, -1): Delta.null,
        Delta(+1, +1): Delta.null,
        # 2-ortho
        Delta(+2,  0): Delta(+1,  0),
        Delta(-2,  0): Delta(-1,  0),
        Delta( 0, +2): Delta( 0, +1),
        Delta( 0, -2): Delta( 0, -1),
        # 2-angled
        Delta(+2, +1): Delta(+1, +1),
        Delta(-2, +1): Delta(-1, +1),
        Delta(+1, +2): Delta(+1, +1),
        Delta(+1, -2): Delta(+1, -1),
        Delta(+2, -1): Delta(+1, -1),
        Delta(-2, -1): Delta(-1, -1),
        Delta(-1, +2): Delta(-1, +1),
        Delta(-1, -2): Delta(-1, -1),
        # 2-diagonal
        Delta(+2, +2): Delta(+1, +1),
        Delta(-2, +2): Delta(-1, +1),
        Delta(+2, -2): Delta(+1, -1),
        Delta(-2, -2): Delta(-1, -1),
    }

    @classmethod
    def debug_print(cls, positions: tp.Iterable['Pos'], min_size: 'Coord'=None):
        positions = list(positions)

        # find grid min/max
        top_left = cls.Pos(0, 0)
        bottom_right = cls.Pos(0, 0) if min_size is None else min_size
        for p in positions:
            top_left = cls.Pos(min(top_left.x, p.x), min(top_left.y, p.y))
            bottom_right = cls.Pos(max(bottom_right.x, p.x), max(bottom_right.y, p.y))

        # calculate dimension
        halfsize = cls.Pos(
            1 + max(abs(top_left.x), abs(bottom_right.x)),
            1 + max(abs(top_left.y), abs(bottom_right.y))
        )

        # create display text
        grid = [["."] * (1 + halfsize.x * 2) for _ in range(1 + halfsize.y * 2)]
        grid[halfsize.y][halfsize.x] = "s"
        for pos, letter in reversed(list(zip(positions, itertools.chain("H", map(str, range(1, len(positions))))))):
            grid[halfsize.y + pos.y][halfsize.x + pos.x] = letter

        # output
        print("=" * len(grid[0]))
        print("\n".join("".join(line) for line in grid))

        input()

def solve(inputs: tp.List[io.TextIOBase]):
    for input, tail_length in zip(inputs, [1, 9]):
        rope = RopePhysics.Rope.create(1 + tail_length)

        for line in input.readlines():
            line = line.rstrip("\n")
            if not line:
                break

            instruction = RopePhysics.Instruction.from_raw(line)
            rope.apply(instruction)

            # if tail_length > 2:
            #     RopePhysics.debug_print(rope.knots)

        yield len(rope.visited), None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
