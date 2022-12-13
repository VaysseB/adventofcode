import re
import io
import enum
import pathlib
import dataclasses
import typing as tp


class Overlap(enum.Enum):
    PARTIAL = 1
    COMPLETE = 2


@dataclasses.dataclass
class Range:
    first: int
    last: int

    def overlap(self, other: "Range") -> tp.Optional[Overlap]:
        if self.first <= other.first:
            if other.last <= self.last:
                return Overlap.COMPLETE
            elif other.first <= self.last:
                return Overlap.PARTIAL

        return None

    def overlap_between(self, other: "Range") -> tp.Optional[Overlap]:
        x = [self.overlap(other), other.overlap(self)]
        return sorted(x, key=(lambda x: getattr(x, "value", 0)), reverse=True)[
            0
        ]


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:
        overlaps = {Overlap.COMPLETE: [], Overlap.PARTIAL: []}

        for line in input.readlines():
            line = line.rstrip("\n")
            if not line:
                continue

            r1, r2 = line.split(",")
            first = Range(*map(int, r1.split("-")))
            second = Range(*map(int, r2.split("-")))

            code = first.overlap_between(second)
            if code:
                overlaps[code].append((first, second))

        answers.append(overlaps)

    yield len(answers[0][Overlap.COMPLETE]), None
    yield len(answers[1][Overlap.PARTIAL]) + len(answers[1][Overlap.COMPLETE]), None


def solve_golf(inputs: tp.List[io.TextIOBase]):
    input = inputs[0]

    res = list(
        [
            (line.rstrip("\n"), (start_f <= start_l and end_f >= end_l))
            for line in input.readlines()
            if line and not line.isspace()
            for (start_f, end_f), (start_l, end_l) in [
                sorted(
                    [int(num) for num in pair.split("-")]
                    for pair in line.strip("\n").split(",")
                )
            ]
        ]
    )

    yield sum(dict(res).values()), None  # res
