import io
import collections
import itertools


def solve(input: io.TextIOBase):
    # input parsing
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
    maximums = sorted(
        enumerate(elves_sum_calories), key=(lambda p: p[1]), reverse=True
    )
    top_3 = list(itertools.islice(maximums, 3))

    yield top_3[0][1], {"top": top_3[0]}
    yield sum(calories for _, calories in top_3), {"top3": top_3}


def inline_solve(input: io.TextIOBase):
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
