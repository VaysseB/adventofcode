import io
import re
import dataclasses
import collections
import typing as tp


@dataclasses.dataclass
class Column:
    id: str
    crates: tp.List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Dock:
    columns: tp.Dict[str, Column]

    @classmethod
    def from_lines(cls, ruler, lines):
        columns = [Column(id) for id in ruler.split()]
        column_index = [ruler.index(column.id) for column in columns]

        for line in reversed(lines):
            for i, column in zip(column_index, columns):
                crate = line[i:i+1]
                if crate and not crate.isspace():
                    column.crates.append(crate)

        return cls({column.id: column for column in columns})

    def apply(self, inst: 'Instruction'):
        start = self.columns[inst.start_id]
        crates = [start.crates.pop() for _ in range(inst.count)]

        dest = self.columns[inst.dest_id]
        dest.crates.extend(crates)
    
    def top_crates(self) -> tp.List[str]:
        return [
            column.crates[-1]
            for column in self.columns.values()
        ]


re_inst = re.compile("^move (?P<count>.+) from (?P<start_id>.+) to (?P<dest_id>.+)$")

@dataclasses.dataclass
class Instruction:
    count: int
    start_id: str
    dest_id: str

    @classmethod
    def from_line(cls, line):
        match = re_inst.match(line)
        assert match, f"invalid line '{line}'"
        return cls(int(match.group("count")), match.group("start_id"), match.group("dest_id"))


def solve(input: io.TextIOBase):

    buffer = collections.deque()
    re_ruler = re.compile("^[0-9 ]*$")

    lines = (line.rstrip("\n") for line in input.readlines() if not line.isspace())
    dock: Dock = None

    # fetch dock status
    for line in lines:
        match_ruler = re_ruler.match(line)

        if match_ruler:
            dock = Dock.from_lines(line, buffer)
            break
        
        buffer.append(line)

    assert dock is not None, "no dock"

    # fetch instructions
    buffer.clear()
    for line in lines:
        inst = Instruction.from_line(line)
        buffer.append(inst)
    
    for inst in buffer:
        dock.apply(inst)

    yield "".join(dock.top_crates()), None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
