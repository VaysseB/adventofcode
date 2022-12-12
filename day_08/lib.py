import io
import itertools
import dataclasses
import string
import typing as tp

import utils


@dataclasses.dataclass
class Forest:

    @dataclasses.dataclass(unsafe_hash=True)
    class Tree:
        id: str
        height: int

    @dataclasses.dataclass()
    class View:
        left: int = 0
        right: int = 0
        up: int = 0
        down: int = 0

        def score(self) -> int:
            return self.left * self.right * self.up * self.down

    _by_rows: tp.List[tp.List[Tree]]
    _by_columns: tp.List[tp.List[Tree]]

    @classmethod
    def from_raw(cls, raw: tp.List[tp.List[int]]):
        make_names = iter(utils.gen_names())

        by_rows = [
            [cls.Tree(next(make_names), height) for height in line]
            for line in raw
        ]
        by_columns = list(zip(*by_rows))
        return cls(by_rows, by_columns)

    @classmethod
    def _count_visible(cls, lines: tp.List[tp.List[Tree]], way: int) -> tp.Iterable[Tree]:
        assert way in [1, -1], "invalid parameter 'way'"

        for line in lines:
            line = list(line)
            assert line, "line is empty"

            if way < 0:
                line = list(reversed(line))

            yield line[0]
            tallest = line[0]

            for curr in line[1:]:
                if tallest.height >= curr.height:
                    continue

                yield curr
                tallest = curr

    def all_visible(self) -> int:
        left_seen = self._count_visible(self._by_rows, 1)
        right_seen = self._count_visible(self._by_rows, -1)
        top_seen = self._count_visible(self._by_columns, 1)
        bottom_seen = self._count_visible(self._by_columns, -1)
        return set(itertools.chain(left_seen, right_seen, top_seen, bottom_seen))

    def scenic(self, target_x: int, target_y: int) -> View:
        view = self.View()
        target = self._by_rows[target_y][target_x]

        for current in reversed(self._by_rows[target_y][:target_x]):
            view.left += 1
            if target.height <= current.height:
                break

        for current in self._by_rows[target_y][target_x+1:]:
            view.right += 1
            if target.height <= current.height:
                break

        for current in reversed(self._by_columns[target_x][:target_y]):
            view.up += 1
            if target.height <= current.height:
                break

        for current in self._by_columns[target_x][target_y+1:]:
            view.down += 1
            if target.height <= current.height:
                break

        return view

    def best_scenic(self) -> View:
        return max(
            (score
            for y, line in enumerate(self._by_rows[1:-1], start=1)
            for x, _ in enumerate(line[1:-1], start=1)
            for score in [self.scenic(x, y)]),
            key=self.View.score
        )


def solve(input: io.TextIOBase):

    raw = []
    for line in input.readlines():
        line = line.rstrip("\n")
        if not line:
            break

        raw.append([int(x) for x in line])

    forest = Forest.from_raw(raw)

    yield len(forest.all_visible()), None
    yield forest.best_scenic().score(), None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
