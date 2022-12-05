import io
import string
import collections
import itertools
import dataclasses
import typing as tp

import utils

items = string.ascii_lowercase + string.ascii_uppercase


@dataclasses.dataclass
class ElveRuckSacks:
    raw: str
    rucksacks: tp.Tuple[tp.Counter[int], tp.Counter[int]]

    def unique(self) -> tp.Counter[int]:
        return collections.Counter(
            itertools.chain.from_iterable(rs.keys() for rs in self.rucksacks)
        )

    @classmethod
    def from_line(cls, raw: str) -> tp.Tuple["RuckSack", "RuckSack"]:
        midpoint = len(raw) // 2
        rucksacks = [
            collections.Counter(raw[:midpoint]),
            collections.Counter(raw[midpoint:]),
        ]
        return cls(raw, rucksacks)

    @classmethod
    def duplicate(self, other: "ElveRuckSacks") -> str:
        return other.unique().most_common(1)[0][0]

    @classmethod
    def badge(self, others: tp.List["ElveRuckSacks"]) -> str:
        allinone = collections.Counter(
            itertools.chain.from_iterable(
                elve_rs.unique().keys() for elve_rs in others
            )
        )
        return allinone.most_common(1)[0][0]


def priority_of(item):
    return items.index(item) + 1


def solve(input: io.TextIOBase):
    elves = collections.deque()

    for line in input.readlines():
        line = line.rstrip("\n")
        if not line:
            continue

        rucksacks = ElveRuckSacks.from_line(line)
        elves.append(rucksacks)

    total_prio = 0
    for elve in elves:
        total_prio += priority_of(ElveRuckSacks.duplicate(elve))

    total_badges = 0
    for i, group in enumerate(utils.group_slice(elves, 3)):
        total_badges += priority_of(ElveRuckSacks.badge(group))

    yield total_prio, None
    yield total_badges, None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
