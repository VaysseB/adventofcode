import enum
import math
import dataclasses
import collections
import typing as tp


def group_slice(items: tp.Iterable[tp.T], count: int, strict=True) -> tp.Iterable[tp.T]:
    if count == 0:
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
        raise RuntimeError(f"items length is not a multiple of {count}, rest is {len(group)}")

    if group:
        yield tuple(group)


class Copier:
    _immutable = (type(None), int, float, bool, str)

    def __call__(self, **kwargs):
        assert len(kwargs) == 1
        name, target = next(iter(kwargs.items()))
        return self._copy(target, ((), "=", name))

    def _copy(self, target, path):
        if isinstance(target, self._immutable):
            return target

        copyfunc = getattr(self, f"_copy_{type(target).__name__}", None)
        if copyfunc is not None:
            newest = copyfunc(target, path)
            assert type(newest) is type(target), f"expected copied type {type(target)!r}, not {type(newest)!r}"
            return newest

        if dataclasses.is_dataclass(target):
            newest = self._copy_dataclass(target, path)
            assert type(newest) is type(target), f"expected copied type {type(target)!r}, not {type(newest)!r}"
            return newest

        msg = f"cannot copy instance of {type(target)!r}"
        path_str = self._join_path(path)
        if path_str:
            msg += f"at '{path_str}'"
        raise RuntimeError(msg)

    def _join_path(self, head_path) -> tp.Optional[str]:
        parts = collections.deque()

        while head_path:
            head_path, access, piece = head_path
            midpoint = int(math.ceil(len(access) * 0.5))
            piece = (str(piece) if len(access) % 2 else repr(piece))
            text = access[:midpoint] + piece + access[midpoint:]
            parts.insert(0, text)

        return "".join(parts) or None

    def _iter_index(self, target, path, access="[]"):
        return (self._copy(item, (path, access, i)) for i, item in enumerate(target))

    def _iter_key(self, target, path, access="[]"):
        return ((self._copy(key, path), self._copy(value, (path, access, key))) for key, value in target)

    def _copy_list(self, target, path):
        return list(self._iter_index(target, path))

    def _copy_tuple(self, target, path):
        return tuple(self._iter_index(target, path))

    def _copy_queue(self, target, path):
        return collections.queue(self._iter_index(target, path))

    def _copy_dict(self, target, path):
        return dict(self._iter_key(target.items(), path))

    def _copy_dataclass(self, target, path):
        members = dict(
            (
                self._copy(field.name, (path, ".", field.name)),
                self._copy(getattr(target, field.name), (path, ".", field.name))
            )
            for field in dataclasses.fields(target)
        )
        return type(target)(**members)

copy = Copier()