import io
import collections
import dataclasses
import typing as tp


class FileSystem:
    @dataclasses.dataclass
    class Node:
        name: str
        parent: tp.Optional["Node"]
        own_size: tp.Optional[int]  # None=folder   something=file
        children: tp.List["Node"] = dataclasses.field(default_factory=list)
        _total_size_cache: tp.Optional[int] = None

        def __str__(self):
            if self.is_dir():
                return f"Folder({self.name!r}, x{len(self.children)})"
            return f"File({self.name!r}, size={self.own_size})"

        __repr__ = __str__

        def is_dir(self) -> bool:
            return self.own_size is None

        def is_file(self) -> bool:
            return self.own_size is not None

        def total_size(self) -> int:
            if self._total_size_cache is None:
                self._total_size_cache = (self.own_size or 0) + sum(
                    c.total_size() for c in self.children
                )

            return self._total_size_cache

        def new_folder(self, name: str):
            if not self.is_dir():
                raise RuntimeError("can only add folder under another folder")

            child = FileSystem.Node(name, self, None)
            self.children.append(child)
            return child

        def new_file(self, name: str, size: int):
            if not self.is_dir():
                raise RuntimeError("can only add file under a folder")

            child = FileSystem.Node(name, self, size)
            self.children.append(child)
            return child

    def __init__(self):
        self.root = self.Node("/", None, None)
        self.current = self.root

    def move(self, name: str):
        assert name, "empty name"

        if name == "/":
            self.current = self.root
        elif name == ".":
            pass
        elif name == "..":
            if self.current.parent is None:
                assert self.current is self.root
            else:
                self.current = self.current.parent
        else:
            for child in self.current.children:
                if child.name == name:
                    self.current = child
                    break
            else:
                raise RuntimeError(f"invalid name {name!r}")

        return self

    def iterdir(self) -> tp.Iterable[Node]:
        assert (
            self.current.is_dir()
        ), f"expected folder to iterate over, not file {self.current.name!r}"

        nodes = collections.deque([self.current])

        while nodes:
            current = nodes.popleft()
            yield current
            nodes.extend(current.children)


def solve(input: io.TextIOBase):
    fs = FileSystem()

    for line in input.readlines():
        line = line.rstrip("\n")

        starter = line[0:1]
        if starter == "$":
            cmd, _, tail = line[1:].lstrip(" ").partition(" ")
            if cmd == "cd":
                path = tail
                fs.move(path)
            elif cmd == "ls":
                pass
            else:
                raise RuntimeError("unexpected command")
        elif starter == "d":
            _, _, name = line.partition(" ")
            fs.current.new_folder(name)
        else:
            assert starter.isdigit(), "expected file size"
            size, _, name = line.partition(" ")
            fs.current.new_file(name, int(size))

    # Part One
    limit_size = 100000
    folders_under_limit = [
        node
        for node in fs.move("/").iterdir()
        if node.is_dir() and node.total_size() < limit_size
    ]
    sum_under_limit = sum(node.total_size() for node in folders_under_limit)
    yield sum_under_limit, folders_under_limit

    # Part Two
    disk_size = 70000000
    update_size = 30000000
    unused_size = disk_size - fs.root.total_size()
    to_free_size = update_size - unused_size
    assert to_free_size > 0, "nothing to delete needed"
    candidates = (
        node
        for node in fs.move("/").iterdir()
        if node.is_dir() and node.total_size() >= to_free_size
    )
    candidates = sorted(candidates, key=FileSystem.Node.total_size)
    yield next(iter(candidates)).name, None


def solve_golf(input: io.TextIOBase):
    if False:
        yield
