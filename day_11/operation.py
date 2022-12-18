import typing

V = typing.TypeVar("V", int, int)
M = typing.TypeVar("M")

OpFunc = typing.Callable[[V, typing.Sequence[M]], typing.Tuple[M, V]]


class Builder:
    def __init__(self):
        self._op_func = None
        self._test_func = None

    def add(self, cte: V) -> "Builder":
        def op_add(value: V) -> V:
            return cte + value

        self._op_func = op_add
        return self

    def mul(self, cte: V) -> "Builder":
        def op_mul(value: V) -> V:
            return cte * value

        self._op_func = op_mul
        return self

    def mul_self(self) -> "Builder":
        def op_self_mul(value: V) -> V:
            return value * value

        self._op_func = op_self_mul
        return self

    def test(self, test_value: V) -> "Builder":
        def test_div(value: V) -> bool:
            return value % test_value == 0

        self._test_func = test_div
        return self

    def done(self) -> OpFunc:
        assert self._op_func is not None, "no operation defined"
        assert self._test_func is not None, "no test defined"

        def apply(value: V, choices: typing.Sequence[M]) -> typing.Tuple[M, V]:
            value = self._op_func(value) // 3
            index = self._test_func(value)
            return choices[int(index)], value

        return apply
