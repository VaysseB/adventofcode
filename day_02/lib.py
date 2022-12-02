import io
import enum
import dataclasses


class Outcomes:  # (enum.Enum):

    @dataclasses.dataclass
    class Outcome:
        score: int
        symbol: str

        def __hash__(self):
            return id(self)

    LOST = Outcome(0, "X")
    DRAW = Outcome(3, "Y")
    WIN = Outcome(6, "Z")

    @classmethod
    def __len__(cls):
        return 3

    @classmethod
    def __getitem__(cls, i):
        return [cls.LOST, cls.DRAW, cls.WIN][i]

    @classmethod
    def __iter__(cls):
        return iter([cls.LOST, cls.DRAW, cls.WIN])



class Choices:  # (enum.Enum):

    @dataclasses.dataclass
    class Choice:
        elve: str
        our: str
        score: int

        def __hash__(self):
            return id(self)

        def against(self, choice):
            return Choices._situations[self][choice]

        def fulfill(self, outcome):
            return Choices._secrets[self][outcome]

    ROCK = Choice("A", "X", 1)
    PAPER = Choice("B", "Y", 2)
    SCISSORS = Choice("C", "Z", 3)

    _situations = {
        ROCK: {
            ROCK: Outcomes.DRAW,
            PAPER: Outcomes.LOST,
            SCISSORS: Outcomes.WIN,
        },
        PAPER: {
            ROCK: Outcomes.WIN,
            PAPER: Outcomes.DRAW,
            SCISSORS: Outcomes.LOST,
        },
        SCISSORS: {
            ROCK: Outcomes.LOST,
            PAPER: Outcomes.WIN,
            SCISSORS: Outcomes.DRAW,
        },
    }

    _secrets = {
        ROCK: {
            Outcomes.DRAW: ROCK,
            Outcomes.WIN: PAPER,
            Outcomes.LOST: SCISSORS,
        },
        PAPER: {
            Outcomes.DRAW: PAPER,
            Outcomes.WIN: SCISSORS,
            Outcomes.LOST: ROCK,
        },
        SCISSORS: {
            Outcomes.DRAW: SCISSORS,
            Outcomes.WIN: ROCK,
            Outcomes.LOST: PAPER,
        },
    }

    @classmethod
    def __len__(cls):
        return 3

    @classmethod
    def __getitem__(cls, i):
        return [cls.ROCK, cls.PAPER, cls.SCISSORS][i]

    @classmethod
    def __iter__(cls):
        return iter([cls.ROCK, cls.PAPER, cls.SCISSORS])


def solve(input: io.TextIOBase):
    our_score = 0
    secret_score = 0

    line = input.readline()
    while line:
        elve_letter, our_letter = line.rstrip("\n").partition(" ")[::2]
        elve_choice = next(choice for choice in Choices.__iter__() if choice.elve == elve_letter)

        #
        our_choice = next(choice for choice in Choices.__iter__() if choice.our == our_letter)
        outcome = our_choice.against(elve_choice)
        play_score = outcome.score + our_choice.score
        our_score += play_score

        #
        outcome = next(outcome for outcome in Outcomes.__iter__() if outcome.symbol == our_letter)
        our_choice = elve_choice.fulfill(outcome)
        play_score = outcome.score + our_choice.score
        secret_score += play_score

        #
        line = input.readline()

    yield our_score, None
    yield secret_score, None


def inline_solve(input: io.TextIOBase):
    elves, ours = list("ABC"), list("XYZ")
    play_score = list(range(3))
    outcome_score = list(range(0, 6+1, 3))

    x = [
        (elve, our)
        for line in input.read().split("\n")
        for elve, our in line.split(" ")
    ]
    x = list(x)
    yield x, None