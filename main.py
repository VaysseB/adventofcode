import sys
import io
import dataclasses
import pathlib
import itertools
import functools
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

    def input_path(self, *, use_example=False) -> pathlib.Path:
        return self.path / f"input{'_ex' * use_example}.txt"

    def result_path(self, *, use_example=False) -> pathlib.Path:
        return self.path / f"result{'_ex' * use_example}.txt"

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

    def about(self, anwser_num: int) -> 'Case':
        assert self.anwser_num is None
        return type(self)(**{**dataclasses.asdict(self), "anwser_num": anwser_num})


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
        day_case = Case(self.day.number, None, golf_answer=golf_mode, example_data=example_run)

        expected = self.load_results(day_case)

        create_solver = self.day.solve_func(golf=day_case.golf_answer)

        if create_solver is None:
            for answer_num, _ in enumerate(expected):
                prompt.not_implemented(day_case.about(answer_num))
            return

        with self.validate_input(day_case) as ifile:
            solver = create_solver(ifile)

            for answer_num, (raw, expect) in enumerate(itertools.zip_longest(solver, expected)):
                case = day_case.about(answer_num)

                if case.anwser_num:
                    ifile.seek(0)

                if raw is None:
                    prompt.not_implemented(case)
                    continue

                result, infos = raw

                if expect is None:
                    prompt.result_unchecked(case, result)
                elif result == expect:
                    prompt.verified(case, result)
                else:
                    prompt.mismatch(case, result, expect)

    def validate_input(self, case: Case) -> io.TextIOBase:
        """Check input validity and return a read-only file descriptor."""
        input_path = self.day.input_path(use_example=case.example_data)

        if not input_path.exists():
            if case.example_data:
                prompt.missing(case, f"example file at {input_path}")
                sys.exit(1)

            self.download_binary(self.day.input_url(), input_path)

        return input_path.open(mode="r")

    def load_results(self, case: Case) -> tp.List[tp.Dict[str, tp.Any]]:
        """Load result if it exists."""
        result_path = self.day.result_path(use_example=case.example_data)

        if not result_path.exists():
            return []

        return [int(line) for line in result_path.read_text().splitlines(keepends=False) if line]

    def download_binary(self, url: str, path: pathlib.Path):
        cookies = dict(session=self.get_session_cookie())

        res = requests.get(url, cookies=cookies)
        assert res.status_code == 200, res.text

        with path.open(mode="wb") as ofile:
            for chunk in res.iter_content(chunk_size=128):
                ofile.write(chunk)


@click.command()
@click.option("-x", "--example", is_flag=True, help="Run with example data.")
@click.option("-g", "--golf", is_flag=True, help="Run code golf solution.")
@click.argument("day", type=click.IntRange(1, 25), nargs=-1, required=True)
def cli(day: tp.List[int], example: bool, golf: bool):

    # fetch cookie from file and cache it if required
    @functools.lru_cache()
    def get_session_cookie() -> str:
        return (root / "session_cookie.txt").read_text().rstrip()

    for number in day:
        day = Day.from_number(number, root)

        # first check with example
        situations = itertools.compress(*zip(
            ({"example_run": True, "golf_mode": False}, example),
            ({"example_run": False, "golf_mode": False}, True),
            ({"example_run": True, "golf_mode": True}, example and golf),
            ({"example_run": False, "golf_mode": True}, golf),
        ))

        executor = Executor(day, get_session_cookie)

        for kwargs in situations:
            executor.solve(**kwargs)


if __name__ == "__main__":
    cli()
