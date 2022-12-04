import io
import string
import collections
import itertools

items = string.ascii_lowercase + string.ascii_uppercase


def priority_of(item):
    return items.index(item) + 1


def solve(input: io.TextIOBase):
    total_prio = 0

    for line in input.readlines():
        line = line.rstrip("\n")
        if not line:
            continue

        midpoint = len(line) // 2

        first_rucksack = collections.Counter(line[:midpoint])
        second_rucksack = collections.Counter(line[midpoint:])

        unique_in_rucksack = collections.Counter(
            itertools.chain(first_rucksack.keys(), second_rucksack.keys())
        )
        duplicate = unique_in_rucksack.most_common()[0][0]

        priority = priority_of(duplicate)
        total_prio += priority

    yield total_prio, None


def oneline_solve(input: io.TextIOBase):
    if False:
        yield
