import io
import collections
import dataclasses
import typing as tp


class FileSystem:
    @dataclasses.dataclass
    class Node:
        name: str
        parent: tp.Optional["Node"]  # None=root
        content_size: tp.Optional[int]  # None=folder   something=file

        _entries: tp.Dict[str, "Node"] = dataclasses.field(default_factory=dict)
        _total_size_cache: tp.Optional[int] = None
        _path: str = ""

        def __post_init__(self):
            if self.parent:
                self._path = self.parent.path() + "/" + self.name
                self._entries[".."] = self.parent
            else:
                self._path = ""

        def __str__(self):
            if not self.parent:
                return f"Folder({self.name!s}, x{len(self._entries)})"
            elif self.is_dir():
                return f"Folder({self.name!s}, x{len(self._entries) - 1})"
            return f"File({self.name!s}, size={self.content_size})"

        __repr__ = __str__

        def is_dir(self) -> bool:
            return self.content_size is None

        def is_file(self) -> bool:
            return self.content_size is not None

        def path(self) -> str:
            return self._path

        def children(self) -> tp.Iterator["Node"]:
            for _, entry in sorted(self._entries.items(), key=(lambda p: p[0])):
                if entry is not self.parent:
                    yield entry

        def total_size(self) -> int:
            if self._total_size_cache is None:
                self._total_size_cache = (self.content_size or 0) + sum(
                    child.total_size() for child in self.children()
                )

            return self._total_size_cache

        def _new(self, name: str, content_size: tp.Optional[int]):
            if not self.is_dir():
                raise RuntimeError("can only add folder under another folder")
            elif name in self._entries:
                raise RuntimeError(f"entry already exist {name!r} in {self.path()}")

            child = FileSystem.Node(name, self, content_size)
            self._entries[name] = child
            return child

        def new_folder(self, name: str) -> "Node":
            return self._new(name, None)

        def new_file(self, name: str, size: int) -> "Node":
            return self._new(name, size)

    def __init__(self):
        self.root = self.Node("/", None, None)
        self.current = self.root

    def move(self, name: str):
        assert name, "empty name"

        child = self.current._entries.get(name, None)
        if child:
            self.current = child
        elif name == "/":
            self.current = self.root
        else:
            raise RuntimeError(f"file/folder {name!r} does not exist at {self.current.path()!r}")

        return self

    def iterdir(self) -> tp.Iterable[Node]:
        assert (
            self.current.is_dir()
        ), f"not a folder {self.current.path()!r}"

        nodes = collections.deque([self.current])

        while nodes:
            current = nodes.popleft()
            yield current
            nodes.extendleft(current.children())


def solve(inputs: tp.List[io.TextIOBase]):
    answers = []

    for input in inputs:
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
            
        answers.append(fs)

    # Part One
    limit_size = 100000
    folders_under_limit = [
        node
        for node in answers[0].move("/").iterdir()
        if node.is_dir() and node.total_size() < limit_size
    ]
    sum_under_limit = sum(node.total_size() for node in folders_under_limit)
    yield sum_under_limit, folders_under_limit

    # Part Two
    disk_size = 70000000
    update_size = 30000000
    unused_size = disk_size - answers[1].root.total_size()
    to_free_size = update_size - unused_size
    assert to_free_size > 0, "nothing to delete needed"
    candidates = (
        node
        for node in answers[1].move("/").iterdir()
        if node.is_dir() and node.total_size() >= to_free_size
    )
    candidates = sorted(candidates, key=FileSystem.Node.total_size)
    yield next(iter(candidates)).total_size(), [(c.path(), c.total_size()) for c in candidates]


def solve_golf(inputs: tp.List[io.TextIOBase]):
    if False:
        yield
