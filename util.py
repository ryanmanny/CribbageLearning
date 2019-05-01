from itertools import combinations, chain


def powerset_min_len(iterable, min_len=2):
    """
    From recipes section in itertools docs
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min_len, len(s)+1))
