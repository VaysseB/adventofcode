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


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:
        elves = collections.deque()

        for line in input.readlines():
            line = line.rstrip("\n")
            if not line:
                continue

            rucksacks = ElveRuckSacks.from_line(line)
            elves.append(rucksacks)

        answers.append(elves)

    total_prio = sum(priority_of(ElveRuckSacks.duplicate(elve)) for elve in answers[0])
    yield total_prio, None

    total_badges = sum(
        priority_of(ElveRuckSacks.badge(group))
        for i, group in enumerate(utils.group_slice(answers[1], 3))
    )
    yield total_badges, None


def solve_golf(inputs: tp.List[io.TextIOBase]):
    if False:
        yield
