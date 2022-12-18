import io
import dataclasses
import collections
from typing import Dict, Set, List, Tuple, Sequence, Deque

import utils

import operation

IdType = int
Item = int


@dataclasses.dataclass
class Monkey:
    id: IdType
    worry_levels: Deque[Item]
    operation: operation.OpFunc
    nexts: Sequence["Monkey"]


def parse(input: io.TextIOBase) -> Dict[IdType, Monkey]:
    monkeys_links: Deque[Tuple[Monkey, List[IdType]]] = collections.deque()

    while True:
        monkeys_links.append(parse_monkey(input))

        line = input.readline()
        if not line:
            break

    monkeys = {monkey.id: monkey for monkey, _ in monkeys_links}

    for monkey, next_ids in monkeys_links:
        monkey.nexts = tuple(monkeys[id] for id in next_ids)

    return monkeys


def parse_monkey(input: io.TextIOBase) -> Tuple[Monkey, List[IdType]]:
    opbuild = operation.Builder()
    next_ids: List[IdType] = []

    # parse 'Monkey 0:'
    line = input.readline().rstrip("\n")

    header = "Monkey "
    assert line.startswith(header), "not a valid items line"
    assert line.endswith(":"), "not a valid items line"

    id = int(line[len(header) : -1])

    # parse 'Starting items: 56, 60'
    line = input.readline().rstrip("\n")

    header = "  Starting items: "
    assert line.startswith(header), "not a valid items line"

    worry_levels = [int(x) for x in line[len(header) :].split(",")]

    # parse 'Operation: new = old + 6'
    line = input.readline().rstrip("\n")

    header = "  Operation: new = old "
    assert line.startswith(header), "not a valid operation line"

    op, _, other = line[len(header) :].partition(" ")

    if other == "old":
        if op == "*":
            opbuild.mul_self()
    elif other.isdigit():
        if op == "+":
            opbuild.add(int(other))
        elif op == "*":
            opbuild.mul(int(other))

    # parse 'Test: divisible by 10'
    line = input.readline().rstrip("\n")

    header = "  Test: divisible by "
    assert line.startswith(header), "not a valid test divisible line"

    opbuild.test(int(line[len(header) :]))

    # parse 'If true: throw to monkey 1'
    line = input.readline().rstrip("\n")

    header = "    If true: throw to monkey "
    assert line.startswith(header), "not a valid test true line"

    next_ids.insert(0, int(line[len(header) :]))

    # parse 'If false: throw to monkey 1'
    line = input.readline().rstrip("\n")

    header = "    If false: throw to monkey "
    assert line.startswith(header), "not a valid test false line"

    next_ids.insert(0, int(line[len(header) :]))

    # done
    monkey = Monkey(id, collections.deque(worry_levels), opbuild.done(), [])
    return monkey, next_ids


def play(monkeys: Dict[IdType, Monkey], counters: List[utils.Counter]):
    assert len(monkeys) == len(counters)

    for monkey, counter in zip(monkeys.values(), counters):
        counter.value += len(monkey.worry_levels)

        while monkey.worry_levels:
            item = monkey.worry_levels.popleft()
            receiver, worry = monkey.operation(item, monkey.nexts)
            monkeys[receiver.id].worry_levels.append(worry)
