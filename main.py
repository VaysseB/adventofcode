import sys
import io
import dataclasses
import json
import pathlib
import itertools
import functools
import pprint
import typing as tp

import click
import requests

root = pathlib.Path(__file__).parent.resolve()


@dataclasses.dataclass
class Day:
    path: pathlib.Path
    number: int

    def input_url(self):
        return f"https://adventofcode.com/2022/day/{self.number}/input"

    def input_path(self, *, n_example=None) -> pathlib.Path:
        if n_example is None:
            return self.path / "input.txt"

        return self.path / f"input_ex{n_example}.txt"

    def result_path(self, n: int) -> pathlib.Path:
        return self.path / f"result_q{n}.txt"

    @classmethod
    def from_number(cls, num: int, root: pathlib.Path) -> "Day":
        path = (root / f"day_{num:02}").resolve()
        day = cls(path, num)

        if not path.exists():
            prompt.missing(day, f"day #{num}")
            sys.exit(1)

        return day

    def _import_func(self, name: str):
        module = __import__(self.path.name + ".lib").lib
        func = getattr(module, "solve", None)
        assert (
            func is not None
        ), f"missing `{name}(...)` function from module {module!r}"

        func = getattr(module, name, None)
        assert (
            func is not None
        ), f"missing `solve(...)` function from module {module!r}"
        assert callable(func), f"not a function {func!r}"

        return func

    def solve_func(self, oneline=False):
        return self._import_func("oneline_solve" if oneline else "solve")


class Prompt:
    _t_title = "***"
    _t_result = "result"
    _t_infos = "infos"
    _t_verified = "(oneline)"
    _t_mismatch = "(oneline)"
    _t_unchecked = "---"
    _t_gen_error = "error"

    _titles = [
        _t_title,
        _t_result,
        _t_infos,
        _t_verified,
        _t_mismatch,
        _t_unchecked,
        _t_gen_error,
    ]

    def __init__(self):
        self._column = 1 + max(len(title) for title in self._titles)

    def _prefix(
        self,
        day: Day,
        occurence: tp.Optional[int],
        text: str,
        *,
        continue_=False,
    ):
        if occurence is None:
            num = f"{day.number}   "
        else:
            num = f"{day.number}.{occurence + 1} "

        if continue_:
            return " " * len(num) + f" {text:>{self._column}}"

        return f"{num} {text:>{self._column}}"

    def title(self, day: Day, title: str):
        print(self._prefix(day, None, "***"), title, "***")

    def result(self, day: Day, occurence: int, result):
        print(self._prefix(day, occurence, self._t_result), ">", result)

    def infos(self, day: Day, occurence: int, infos):
        print(
            self._prefix(day, occurence, self._t_infos, continue_=True),
            ">",
            "",
            end="",
        )
        pprint.pprint(infos)

    def verified(self, day: Day, occurence: int):
        print(
            self._prefix(day, occurence, self._t_verified, continue_=True),
            "-same-",
        )

    def mismatch(self, day: Day, occurence: int, result):
        print(
            self._prefix(day, occurence, self._t_mismatch, continue_=True),
            "!=",
            result,
        )

    def unchecked(self, day: Day, occurence: int):
        print(self._prefix(day, occurence, self._t_unchecked, continue_=True))

    def missing(self, day: Day, what: str):
        print(self._prefix(day, None, self._t_gen_error), ": missing", what)


prompt = Prompt()


class _Executor:
    def __init__(self, day: Day, title: str):
        self.day = day
        self.title = title

    def solve(self, count: int):
        prompt.title(self.day, self.title)
        results = self.solve_main(count)
        self.solve_oneline(results)

    def solve_main(self, count: int) -> tp.Iterator[int]:
        raise NotImplementedError()

    def solve_oneline(self, expected_results: tp.Iterable[int]):
        raise NotImplementedError()


class ExampleExecutor(_Executor):
    def __init__(self, day: Day):
        super().__init__(day, "example training")

    def solve_main(self, count: int) -> tp.Iterator[int]:
        for occurence in range(count):
            with self.validate_input(occurence) as ifile:
                solver = self.day.solve_func()(ifile)

                try:
                    for _ in range(occurence):
                        next(solver)
                except StopIteration:
                    pass

                try:
                    result, infos = next(solver)
                except StopIteration:
                    return
                else:
                    prompt.result(self.day, occurence, result)

                    if infos is not None:
                        prompt.infos(self.day, occurence, infos)

                    yield result

    def solve_oneline(self, expected_results: tp.Iterable[int]):
        for occurence, expected in enumerate(expected_results):
            with self.validate_input(occurence) as ifile:
                maybe_func = self.day.solve_func(oneline=True)

                if maybe_func:
                    solver = maybe_func(ifile)

                    try:
                        for _ in range(occurence):
                            next(solver)
                    except StopIteration:
                        pass

                    try:
                        result, infos = next(solver)
                    except StopIteration:
                        prompt.unchecked(self.day, occurence)
                    else:
                        if result == expected:
                            prompt.verified(self.day, occurence)
                        else:
                            prompt.mismatch(self.day, occurence, result)

                else:
                    prompt.unchecked(self.day, occurence)

    def validate_input(self, occurence: int) -> io.TextIOBase:
        input_path = self.day.input_path(n_example=occurence + 1)

        if not input_path.exists():
            prompt.missing(self.day, f"example file at {input_path}")
            sys.exit(1)

        return input_path.open(mode="r")


class ProblemExecutor(_Executor):
    def __init__(self, day: Day, get_session_cookie: tp.Callable[[], str]):
        super().__init__(day, "real case")
        self.get_session_cookie = get_session_cookie

    def solve_main(self, count: int) -> tp.Iterator[int]:
        with self.validate_input() as ifile:
            solver = self.day.solve_func()(ifile)

            for occurence, (result, infos) in enumerate(solver):
                assert (
                    occurence
                ) < count, f"unexpected #{occurence} (max {count})"

                prompt.result(self.day, occurence, result)

                if infos is not None:
                    prompt.infos(self.day, occurence, infos)

                self.persist_output(occurence, result, infos)

                yield result

                ifile.seek(0)

    def solve_oneline(self, expected_results: tp.Iterable[int]):
        with self.validate_input() as ifile:
            maybe_func = self.day.solve_func(oneline=True)

            if not maybe_func:
                for occurence, _ in enumerate(expected_results):
                    prompt.unchecked(self.day, occurence)

                return

            solver = iter(maybe_func(ifile))

            for occurence, expected in enumerate(expected_results):
                try:
                    result, _ = next(solver)
                except StopIteration:
                    prompt.unchecked(self.day, occurence)
                else:
                    if result == expected:
                        prompt.verified(self.day, occurence)
                    else:
                        prompt.mismatch(self.day, occurence, result)

                ifile.seek(0)

    def validate_input(self) -> io.TextIOBase:
        input_path = self.day.input_path()

        if not input_path.exists():
            self.download_binary(self.day.input_url(), input_path)

        return input_path.open(mode="r")

    def persist_output(self, occurence: int, result: int, infos):
        storage = {"_result": result}

        if infos is not None:
            storage["infos"] = infos

        result_path = self.day.result_path(occurence + 1)
        self.save_to(storage, result_path)

    def download_binary(self, url: str, path: pathlib.Path):
        cookies = dict(session=self.get_session_cookie())

        res = requests.get(url, cookies=cookies)
        assert res.status_code == 200, res.text

        with path.open(mode="wb") as ofile:
            for chunk in res.iter_content(chunk_size=128):
                ofile.write(chunk)

    def save_to(self, content, path: pathlib.Path):
        json.dump(content, path.open("w"))


@click.command()
@click.argument("day", type=click.IntRange(1, 25), nargs=-1, required=True)
def cli(day: list[int]):
    @functools.lru_cache
    def get_session_cookie() -> str:
        return (root / "session_cookie.txt").read_text().rstrip()

    for number in day:
        day = Day.from_number(number, root)

        # first check with example
        executors = [
            ExampleExecutor(day),
            ProblemExecutor(day, get_session_cookie),
        ]
        for executor in executors:
            executor.solve(2)


if __name__ == "__main__":
    cli()
