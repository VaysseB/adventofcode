import io
import collections
import dataclasses
import typing as tp

import utils


@dataclasses.dataclass
class DataStream:
    raw: tp.Iterable[tp.T]

    def start_of(self, distinct_count: int) -> int:
        for i, seq in enumerate(utils.sliding_window(self.raw, distinct_count)):
            if len(set(seq)) == distinct_count:
                return i + distinct_count
                break
        else:
            assert False, f"not found within {raw!r}"


def solve(input: io.TextIOBase):
    start_of_packet = collections.deque()
    start_of_message = collections.deque()

    for line in input.readlines():
        line = line.rstrip("\n")
        if not line:
            break

        ds = DataStream(line)
        start_of_packet.append(ds.start_of(4))
        start_of_message.append(ds.start_of(14))

    yield ",".join(map(str, start_of_packet)), None
    yield ",".join(map(str, start_of_message)), None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
