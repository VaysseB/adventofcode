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
    def _look(cls, lines: tp.List[tp.List[Tree]], way: int) -> tp.Iterable[Tree]:
        assert way in [1, -1], "invalid parameter 'way'"

        for line in lines:
            line = list(line)
            assert line, "line is empty"

            if way < 0:
                line = list(reversed(line))

            yield line[0]

            for prev, next in zip(line[:-1], line[1:]):
                if prev.height > next.height:
                    break
                elif prev.height < next.height:
                    yield next

    def count_visible(self) -> int:
        left_seen = self._look(self._by_rows, 1)
        right_seen = self._look(self._by_rows, -1)
        top_seen = self._look(self._by_columns, 1)
        bottom_seen = self._look(self._by_columns, -1)
        return set(itertools.chain(left_seen, right_seen, top_seen, bottom_seen))


def solve(input: io.TextIOBase):

    raw = []
    for line in input.readlines():
        line = line.rstrip("\n")
        if not line:
            break

        raw.append([int(x) for x in line])

    forest = Forest.from_raw(raw)
    yield len(forest.count_visible()), None

    if False:
        yield


def solve_golf(input: io.TextIOBase):
    if False:
        yield
