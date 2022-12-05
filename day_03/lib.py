import io
import string
import collections
import itertools

items = string.ascii_lowercase + string.ascii_uppercase


def priority_of(item):
    return items.index(item) + 1


def solve(input: io.TextIOBase):
    total_prio = 0
    total_badges_3elve_group = 0

    last_group = collections.deque()

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

        last_group.append(unique_in_rucksack)
        if len(last_group) >= 3:
            unique_in_group = collections.Counter(
                itertools.chain.from_iterable(
                    elve_items.keys() for elve_items in last_group
                )
            )

            group_badge = unique_in_group.most_common(1)[0][0]
            total_badges_3elve_group += priority_of(group_badge)

            last_group.clear()

        duplicate = unique_in_rucksack.most_common(1)[0][0]

        priority = priority_of(duplicate)
        total_prio += priority

    yield total_prio, None
    yield total_badges_3elve_group, None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
