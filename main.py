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

    def input_path(self, *, use_example=False) -> pathlib.Path:
        return self.path / ("input_ex.txt" if use_example else "input.txt")

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

    def solve(self):
        prompt.title(self.day, self.title)

        results = self.solve_main()
        self.solve_oneline(results)

    def solve_main(self) -> tp.Iterator[int]:
        with self.validate_input() as ifile:
            solver = self.day.solve_func()(ifile)

            for occurence, (result, infos) in enumerate(solver):
                if occurence:
                    ifile.seek(0)

                prompt.result(self.day, occurence, result)

                if infos is not None:
                    prompt.infos(self.day, occurence, infos)

                self.persist_output(occurence, result, infos)

                yield result

    def solve_oneline(self, expected_results: tp.Iterable[int]):
        with self.validate_input() as ifile:
            maybe_func = self.day.solve_func(oneline=True)

            if maybe_func is None:
                for occurence, _ in enumerate(expected_results):
                    prompt.unchecked(self.day, occurence)

                return

            solver = maybe_func(ifile)

            for occurence, expected in enumerate(expected_results):
                if occurence:
                    ifile.seek(0)

                try:
                    result, infos = next(solver)
                except StopIteration:
                    prompt.unchecked(self.day, occurence)
                else:
                    if result == expected:
                        prompt.verified(self.day, occurence)
                    else:
                        prompt.mismatch(self.day, occurence, result)

    def validate_input(self) -> io.TextIOBase:
        raise NotImplementedError()

    def persist_output(self, occurence: int, result: int, infos):
        raise NotImplementedError()


class ExampleExecutor(_Executor):
    def __init__(self, day: Day):
        super().__init__(day, "example training")

    def validate_input(self) -> io.TextIOBase:
        input_path = self.day.input_path(use_example=True)

        if not input_path.exists():
            prompt.missing(self.day, f"example file at {input_path}")
            sys.exit(1)

        return input_path.open(mode="r")

    def persist_output(self, occurence: int, result: int, infos):
        pass


class ProblemExecutor(_Executor):
    def __init__(self, day: Day, get_session_cookie: tp.Callable[[], str]):
        super().__init__(day, "real case")
        self.get_session_cookie = get_session_cookie

    def validate_input(self) -> io.TextIOBase:
        input_path = self.day.input_path(use_example=False)

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
        json.dump(content, path.open("w"), cls=CustomEncoder)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        import collections

        if isinstance(obj, collections.deque):
            return list(obj)

        import enum

        if isinstance(obj, enum.Enum):
            return {obj.name: obj.value}

        import dataclasses

        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        to_json = getattr(obj, "to_json", None)
        if to_json and callable(to_json):
            return to_json()

        return super().default(obj)


@click.command()
@click.option("-x", "--example", is_flag=True, help="Example-only run.")
@click.argument("day", type=click.IntRange(1, 25), nargs=-1, required=True)
def cli(day: list[int], example: bool):
    @functools.lru_cache
    def get_session_cookie() -> str:
        return (root / "session_cookie.txt").read_text().rstrip()

    for number in day:
        day = Day.from_number(number, root)

        # first check with example
        executors: list[_Executor] = [
            ExampleExecutor(day),
        ]

        if not example:
            executors.append(ProblemExecutor(day, get_session_cookie))

        for executor in executors:
            executor.solve()


if __name__ == "__main__":
    cli()
