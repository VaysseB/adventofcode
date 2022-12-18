import io
import collections
import pprint
import typing as tp

import utils
import keep_away


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:

        monkeys = keep_away.parse(input)
        counters = [utils.Counter() for _ in range(len(monkeys))]

        for i in range(20):
            keep_away.play(monkeys, counters)

        answers.append(counters)
        break

    top = sorted(answers[0], key=utils.Counter.value.fget, reverse=True)
    yield (top[:2][0] * top[:2][1]).value, top


def solve_golf(inputs: tp.List[io.TextIOBase]):
    if False:
        yield
