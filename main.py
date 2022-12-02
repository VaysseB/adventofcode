import dataclasses
import json
import pathlib
import pprint

import click
import requests


@dataclasses.dataclass
class Day:
    path: pathlib.Path
    number: int

    def input_url(self):
        return f"https://adventofcode.com/2022/day/{self.number}/input"

    def input_path(self, *, example=False) -> pathlib.Path:
        return self.path / ("example_" * example + "input.txt")

    def result_path(self, n: int) -> pathlib.Path:
        return self.path / f"result_q{n}.txt"

    @classmethod
    def from_number(cls, num: int, root: pathlib.Path) -> 'Day':
        path = (root / f"day_{num:02}").resolve()
        assert path.exists(), f"day {num} does not exist: {path}"
        return cls(path, num)

    def _import_func(self, name: str):
        module = __import__(self.path.name + ".lib").lib
        func = getattr(module, "solve", None)
        assert func is not None, f"missing `{name}(...)` function from module {module!r}"

        func = getattr(module, name, None)
        assert func is not None, f"missing `solve(...)` function from module {module!r}"
        assert callable(func), f"not a function {func!r}"

        return func

    def solve_func(self):
        return self._import_func("solve")

    def inline_solve_func(self):
        return self._import_func("inline_solve")


def download_binary(url: str, path: pathlib.Path, session_cookie: str):
    cookies = dict(session=session_cookie)

    res = requests.get(url, cookies=cookies)
    assert res.status_code == 200, res.text

    with path.open(mode="wb") as ofile:
        for chunk in res.iter_content(chunk_size=128):
            ofile.write(chunk)


def save_to(content, path: pathlib.Path):
    json.dump(content, path.open("w"))


def solve(path: pathlib.Path):
    pass


@click.command()
@click.option("-x", "--example", is_flag=True, help="Use example input.")
@click.argument("day", type=click.IntRange(1, 25), nargs=-1, required=True)
def cli(day: [int], example=False):
    root = pathlib.Path(__file__).parent.resolve()

    for day in day:
        day = Day.from_number(day, root)

        input_path = day.input_path(example=example)
        if not input_path.exists():
            session_cookie = (root.parent / "session_cookie.txt").read_text().rstrip()
            download_binary(day.input_url(), input_path, session_cookie)

        with input_path.open(mode="r") as ifile:
            results = []

            # solve problem
            solver = day.solve_func()(ifile)

            column = len(" checked?")

            for i, (result, infos) in enumerate(solver, start=1):
                numtext = f"{day.number}.{i}"
                emptypf = " " * len(numtext)

                print(numtext, f"{'result':>{column}}", ">", result)

                if not example:
                    storage = { "_result": result }

                    if infos is not None:
                        storage["infos"] = infos

                    result_path = day.result_path(i)
                    save_to(storage, result_path)

                if infos is not None:
                    print(emptypf, f"{'infos':>{column}}", ">", "", end="")
                    pprint.pprint(infos)

                results.append(result)

            # check with inline function
            isolve_func = day.inline_solve_func()
            if isolve_func is not None:
                print(f"verify with inline ...")

                assert ifile.seekable()
                ifile.seek(0)

                isolver = isolve_func(ifile)


                for i, (actual_res, (inline_res, _)) in enumerate(zip(results, isolver), start=1):
                    numtext = f"{day.number}.{i}"

                    ok = (actual_res == inline_res)
                    if ok:
                        print(numtext, f"{'checked?':>{column}}", "> ok")
                    else:
                        print(numtext, f"{'checked?':>{column}}", "> mismatch -", inline_res)


if __name__ == "__main__":
    cli()