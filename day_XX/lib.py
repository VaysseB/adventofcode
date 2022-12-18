import io

import typing as tp


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:

        for line in input.readlines():
            line = line.rstrip("\n")
            if not line:
                break

        answers.append(None)

    yield answers[0], None


def solve_golf(inputs: tp.List[io.TextIOBase]):
    if False:
        yield
