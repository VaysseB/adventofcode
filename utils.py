import math
import itertools
import dataclasses
import collections
import string
import typing as tp


def group_slice(
    items: tp.Iterable[tp.T], count: int, strict=True
) -> tp.Iterable[tp.T]:
    if count <= 0:
        raise RuntimeError(f"expected positive count, not {count}")

    group = collections.deque()
    for item in iter(items):
        if len(group) < count:
            group.append(item)
        else:
            yield tuple(group)
            group.clear()
            group.append(item)

    if group and len(group) != count:
        raise RuntimeError(
            f"items length is not a multiple of {count}, rest is {len(group)}"
        )

    if group:
        yield tuple(group)


def sliding_window(
    items: tp.Iterable[tp.T], count: int, underflow_ok=False
) -> tp.Iterable[tp.T]:
    if count <= 0:
        raise RuntimeError(f"expected positive count, not {count}")

    items = iter(items)

    window = collections.deque(itertools.islice(items, count))

    if len(window) < count and not underflow_ok:
        raise RuntimeError(
            f"no window because {count} is greater than elements in {items}"
        )

    yield tuple(window)

    for item in items:
        window.popleft()
        window.append(item)
        yield tuple(window)


def gen_names(corpus: tp.List[str]=string.ascii_lowercase, min_length: int=1) -> tp.Iterable[str]:
    corpus = list(corpus)
    yield from iter(
        "".join(next(itertools.islice(
            itertools.product(corpus, repeat=min_length + (x // len(corpus))),
            x % len(corpus),
            x % len(corpus) + 1
        )))
        for x in itertools.count(0)
    )


class Copier:
    """
    Deep copy utility with extended support of standard Python object.
    Such as: dataclasses, collections.deque.
    """

    _immutable = (int, float, bool, str)

    def __call__(self, **kwargs):
        assert len(kwargs) == 1
        name, target = next(iter(kwargs.items()))
        return self._copy(target, ((), "=", name))

    def _copy(self, target, path):
        if target is None:
            return

        ttype = type(target)
        newest = None

        if isinstance(target, self._immutable):
            newest = target
        elif ttype in self._ctable:
            newest = self._ctable[ttype](self, target, path)
        elif dataclasses.is_dataclass(target):
            newest = self._copy_dataclass(target, path)

        if type(newest) is ttype:
            return newest
        elif newest is None:
            raise RuntimeError(
                f"cannot copy instance of {type(target)!r} at '{self._join_path(path)}'"
            )
        else:
            raise RuntimeError(
                f"expected copied type {type(target)!r}, not {type(newest)!r}"
            )

    def _join_path(self, head_path) -> tp.Optional[str]:
        parts = collections.deque()

        while head_path:
            head_path, access, piece = head_path
            midpoint = int(math.ceil(len(access) * 0.5))
            piece = str(piece) if len(access) % 2 else repr(piece)
            text = access[:midpoint] + piece + access[midpoint:]
            parts.insert(0, text)

        return "".join(parts) or None

    def _iter_index(self, target, path, access="[]"):
        return (
            self._copy(item, (path, access, i)) for i, item in enumerate(target)
        )

    def _iter_key(self, target, path, access="[]"):
        return (
            (self._copy(key, path), self._copy(value, (path, access, key)))
            for key, value in target
        )

    def _copy_list(self, target, path):
        return list(self._iter_index(target, path))

    def _copy_tuple(self, target, path):
        return tuple(self._iter_index(target, path))

    def _copy_queue(self, target, path):
        return collections.deque(self._iter_index(target, path))

    def _copy_dict(self, target, path):
        return dict(self._iter_key(target.items(), path))

    def _copy_dataclass(self, target, path):
        members = dict(
            (
                self._copy(field.name, (path, ".", field.name)),
                self._copy(
                    getattr(target, field.name), (path, ".", field.name)
                ),
            )
            for field in dataclasses.fields(target)
        )
        return type(target)(**members)

    _ctable = {
        list: _copy_list,
        tuple: _copy_tuple,
        dict: _copy_dict,
        collections.deque: _copy_queue,
    }


copy = Copier()
