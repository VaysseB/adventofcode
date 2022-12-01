import json
import pathlib
import collections
import itertools
import pprint

import requests


def download_input(url: str, path: pathlib.Path, session_cookie: str):
    cookies = dict(session=session_cookie)

    res = requests.get(url, cookies=cookies)
    assert res.status_code == 200, res.text

    with path.open(mode="wb") as ofile:
        for chunk in res.iter_content(chunk_size=128):
            ofile.write(chunk)


def save_output(content, path: pathlib.Path):
    json.dump(content, path.open("w"))


def solve(path: pathlib.Path):
    # input parsing
    elves_calories = collections.deque()

    with path.open("r") as ifile:
        elves_calories.append([])

        line = ifile.readline()
        while line:
            if line == "\n":
                elves_calories.append([])
            else:
                elves_calories[-1].append(int(line.rstrip("\n")))

            #
            line = ifile.readline()

    # calculate maximums
    elves_sum_calories = (sum(calories) for calories in elves_calories)
    maximums = sorted(enumerate(elves_sum_calories), key=(lambda p: p[1]), reverse=True)
    top_3 = list(itertools.islice(maximums, 3))

    yield {"_result": top_3[0][1], "info": { "info": top_3[0]}}
    yield {"_result": sum(calories for _, calories in top_3), "info": {"top3": top_3}}


if __name__ == "__main__":
    test_path = pathlib.Path(__file__).parent.resolve()
    input_path = test_path / "input.txt"
    example_input_path = test_path / "example_input.txt"
    output_q1_path = test_path / "result_q1.txt"
    output_q2_path = test_path / "result_q2.txt"

    session_cookie_path = test_path.parent / "session_cookie.txt"

    input_url = "https://adventofcode.com/2022/day/1/input"

    if not input_path.exists():
        assert session_cookie_path.exists(), f"missing session cookie file: {session_cookie_path}"
        download_input(input_url, input_path, session_cookie=session_cookie_path.read_text().rstrip())

    solver = solve(input_path)

    result_q1 = next(solver)
    pprint.pprint(result_q1)
    save_output(result_q1, output_q1_path)

    result_q2 = next(solver)
    pprint.pprint(result_q2)
    save_output(result_q2, output_q2_path)