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