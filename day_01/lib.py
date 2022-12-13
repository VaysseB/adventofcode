import io
import collections
import itertools

import typing as tp


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:
        elves_calories = collections.deque()
        elves_calories.append([])

        line = input.readline()
        while line:
            if line == "\n":
                elves_calories.append([])
            else:
                elves_calories[-1].append(int(line.rstrip("\n")))

            #
            line = input.readline()

        # calculate maximums
        elves_sum_calories = (sum(calories) for calories in elves_calories)
        maximums = sorted(enumerate(elves_sum_calories), key=(lambda p: p[1]), reverse=True)

        answers.append(maximums)

    yield answers[0][0][1], None
    yield sum(calories for _, calories in itertools.islice(answers[1], 3)), None


def solve_golf(inputs: tp.List[io.TextIOBase]):
    input = inputs[0]

    top3 = list(
        itertools.islice(
            iter(
                sorted(
                    zip(
                        *reversed(
                            list(
                                zip(
                                    *enumerate(
                                        [
                                            sum(
                                                int(n)
                                                for n in t_seq.split("\n")
                                            )
                                            for t_seq in input.read()
                                            .rstrip("\n")
                                            .split("\n\n")
                                        ]
                                    )
                                )
                            )
                        )
                    ),
                    reverse=True,
                )
            ),
            3,
        )
    )

    yield top3[0][0], {"top": top3[0]}
    yield sum(list(zip(*top3))[0]), {"top3": top3}
