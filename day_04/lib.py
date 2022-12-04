import io
import enum
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


def solve(input: io.TextIOBase):
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

    yield len(overlaps[Overlap.COMPLETE]), None
    yield len(overlaps[Overlap.PARTIAL]) + len(overlaps[Overlap.COMPLETE]), None


def oneline_solve(input: io.TextIOBase):
    if False:
        yield
