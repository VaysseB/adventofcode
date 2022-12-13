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


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input, length in zip(inputs, [4, 14]):
        starts = collections.deque()

        for line in input.readlines():
            line = line.rstrip("\n")
            if not line:
                break

            ds = DataStream(line)
            starts.append(ds.start_of(length))
        
        answers.append(starts)

    yield ",".join(map(str, answers[0])), None
    yield ",".join(map(str, answers[1])), None


def solve_golf(inputs: tp.List[io.TextIOBase]):
    if False:
        yield
