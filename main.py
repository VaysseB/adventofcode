import sys
import io
import dataclasses
import pathlib
import itertools
import functools
import collections
import contextlib
import pprint
import typing as tp

import click
import requests

# main folder
root = pathlib.Path(__file__).parent.resolve()


@dataclasses.dataclass
class Day:
    """
    Access to day's solution implementation.
    """

    number: int
    path: pathlib.Path

    @classmethod
    def list_from(cls, root: pathlib.Path) -> tp.Iterable["Day"]:
        days = collections.deque()
        for path in root.iterdir():
            if path.name.startswith("day_") and path.is_dir():
                try:
                    num = int(path.name[4:])
                except ValueError:
                    pass
                else:
                    days.append(cls(num, path))

        yield from sorted(days, key=lambda day: day.number)

    @classmethod
    def from_number(cls, num: int, root: pathlib.Path) -> "Day":
        path = (root / f"day_{num:02}").resolve()
        day = cls(num, path)

        if not path.exists():
            case = Case(num, None)
            prompt.missing(case, f"day #{num}")
            sys.exit(1)

        return day

    def input_url(self) -> str:
        return f"https://adventofcode.com/2022/day/{self.number}/input"

    def _path_of(self, name: str, example_index: int) -> str:
        # rule for suffix
        # index < 0  -> ''
        # index == 0 -> '_ex'
        # index == 1 -> '_ex2'
        suffix = "_ex" * (example_index >= 0) + str(example_index + 1) * (
            example_index > 0
        )
        return self.path / f"{name}{suffix}.txt"

    def input_path(self, *, example_index=-1) -> pathlib.Path:
        return self._path_of("input", example_index)

    def result_path(self, *, example_index=-1) -> pathlib.Path:
        return self._path_of("result", example_index)

    def _import_func(self, name: str) -> tp.Any:
        """
        Return function by name from day's module.
        Error if not found.
        """
        module = __import__(self.path.name + ".lib").lib

        func = getattr(module, name, None)
        assert (
            func is not None
        ), f"missing `{name}(...)` function from module {module!r}"
        assert callable(func), f"not a function {func!r}"

        return func

    def solve_func(self, golf=False) -> tp.Callable[[io.TextIOBase], None]:
        """Return solve function."""
        return self._import_func("solve_golf" if golf else "solve")


@dataclasses.dataclass
class Case:
    day_num: int
    anwser_num: tp.Optional[int]
    golf_answer: bool = False
    example_data: bool = False

    def about(self, anwser_num: int) -> "Case":
        assert self.anwser_num is None
        return type(self)(
            **{**dataclasses.asdict(self), "anwser_num": anwser_num}
        )


class Prompt:
    """
    Console output prompt.
    """

    def __init__(self):
        self._prefix_max_len = 1 + 2 + 3
        self._title_max_len = 10

    def _prefix(self, case: Case, header: str, *, continue_=False):
        parts = []

        if case.anwser_num is None:
            parts.append(f"{case.day_num}")
        else:
            parts.append(f"{case.day_num}.{case.anwser_num + 1}")

        if case.golf_answer or case.example_data:
            parts.append(".")

            if case.golf_answer:
                parts.append("g")

            if case.example_data:
                parts.append("x")

        num = "".join(parts)

        if False and continue_:
            num = " " * len(num)

        return f"{num:<{self._prefix_max_len}} {header:>{self._title_max_len}}"

    def title(self, case: Case, title: str):
        p = self._prefix(case, "***")
        print(p, title, "***")

    def result_unchecked(self, case: Case, result):
        p = self._prefix(case, "unchecked", continue_=True)
        print(p, ">", result)

    def infos(self, case: Case, infos):
        p = self._prefix(case, "infos", continue_=True)
        print(p, "", end="")
        pprint.pprint(infos)

    def verified(self, case: Case, result):
        p = self._prefix(case, "valid", continue_=True)
        print(p)

    def mismatch(self, case: Case, result, expected):
        p = self._prefix(case, "wrong", continue_=True)
        print(p, ">", expected, "!=", result)

    def not_implemented(self, case: Case):
        p = self._prefix(case, "---", continue_=True)
        print(p)

    def missing(self, case: Case, what: str):
        p = self._prefix(case, "error")
        print(p, ": missing", what)


prompt = Prompt()


class Executor:
    """Day's solution execution handler."""

    def __init__(self, day: Day, get_session_cookie):
        self.day = day
        self.get_session_cookie = get_session_cookie

    def solve(self, example_run: bool, golf_mode: bool):
        # insert day path to enable local import
        sys.path.insert(0, str(self.day.path))

        day_case = Case(
            self.day.number,
            None,
            golf_answer=golf_mode,
            example_data=example_run,
        )

        expected = self.load_results(day_case)

        create_solver = self.day.solve_func(golf=day_case.golf_answer)

        # error, we should have a solver function
        # but we simply ignore it
        if create_solver is None:
            for answer_num, _ in enumerate(expected):
                prompt.not_implemented(day_case.about(answer_num))

            # clean
            sys.path.remove(str(self.day.path))
            return

        with contextlib.ExitStack() as estack:

            ifiles = self.validate_inputs(day_case)

            # close all files when done automatically
            for ifile in ifiles:
                estack.enter_context(ifile)

            # create solver
            solver = create_solver(ifiles)

            for answer_num, (raw, expect) in enumerate(
                itertools.zip_longest(solver, expected)
            ):
                # create case to give to prompt
                case = day_case.about(answer_num)

                # ignore day if not implemented
                if raw is None:
                    prompt.not_implemented(case)
                    continue

                # extract result
                result, infos = raw

                # convert result into the expected type if possible
                # to ease comparison
                try:
                    result = type(expect)(result)
                except Exception:
                    pass

                # handle every result
                # > not checked against known solution
                # > mismatch with solution
                # > same as solution
                if expect is None:
                    prompt.result_unchecked(case, result)

                    if infos is not None:
                        prompt.infos(case, infos)

                elif result == expect:
                    prompt.verified(case, result)
                else:
                    prompt.mismatch(case, result, expect)

                    if infos is not None:
                        prompt.infos(case, infos)

        # clean
        sys.path.remove(str(self.day.path))

    def validate_inputs(self, case: Case, count=2) -> tp.List[io.TextIOBase]:
        """Check input validity and return read-only file(s) descriptor."""
        paths = []

        if case.example_data:
            # check 2 files, maybe only one, but not none
            paths = [
                p
                for i in range(count)
                for p in [self.day.input_path(example_index=i)]
                if p.exists()
            ]

            if not paths:
                prompt.missing(case, f"input example file(s)")
                sys.exit(1)

        else:
            # single file expected
            input_path = self.day.input_path()

            if not input_path.exists():
                self.download_binary(self.day.input_url(), input_path)

            if not input_path.exists():
                prompt.missing(case, f"input file(s)")
                sys.exit(1)

            paths = [input_path]

        # we repeat path for as many wanted
        return [
            path.open(mode="r")
            for path in itertools.islice(itertools.cycle(paths), count)
        ]

    def load_results(self, case: Case) -> tp.List[tp.Dict[str, tp.Any]]:
        """Load result if it exists."""
        result_path = self.day.result_path(
            example_index=[-1, 0][case.example_data]
        )

        if not result_path.exists():
            return []

        return [
            line
            for line in result_path.read_text().splitlines(keepends=False)
            if line
        ]

    def download_binary(self, url: str, path: pathlib.Path):
        cookies = dict(session=self.get_session_cookie())

        res = requests.get(url, cookies=cookies)
        assert res.status_code == 200, res.text

        with path.open(mode="wb") as ofile:
            for chunk in res.iter_content(chunk_size=128):
                ofile.write(chunk)


@click.command()
@click.option("-x", "--example", is_flag=True, help="Run with example data.")
@click.option("-r", "--real", is_flag=True, help="Run with real data.")
@click.option("-g", "--golf", is_flag=True, help="Add code golf solution.")
@click.argument("day", type=click.IntRange(1, 25), nargs=-1)
def cli(day: tp.List[int], example: bool, real: bool, golf: bool):

    if not example and not real:
        example, real = True, True

    # fetch cookie from file and cache it if required
    @functools.lru_cache()
    def get_session_cookie() -> str:
        return (root / "session_cookie.txt").read_text().rstrip()

    days: tp.Iterable[Day] = [
        Day.from_number(number, root) for number in day
    ] or Day.list_from(root)

    situations = list(
        itertools.compress(
            *zip(
                ({"example_run": True, "golf_mode": False}, example),
                ({"example_run": False, "golf_mode": False}, real),
                ({"example_run": True, "golf_mode": True}, example and golf),
                ({"example_run": False, "golf_mode": True}, real and golf),
            )
        )
    )

    for day in days:
        executor = Executor(day, get_session_cookie)

        for kwargs in situations:
            executor.solve(**kwargs)


if __name__ == "__main__":
    cli()
