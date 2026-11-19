"""Yard-sale model of wealth exchange (Chakraborti 2002; Hayes 2002; Boghosian 2014+).

Every round, everyone is randomly paired. Each pair stakes a fraction `f` of the
POORER partner's wealth on a fair coin flip. Optional flat wealth tax `tax`
(fraction per round) is redistributed equally.
"""
import numpy as np


def step(w, rng, f=0.2, tax=0.0, skill=None):
    """Advance one round in place. `w` is (n,) or (worlds, n); n must be even.
    `skill` (1-D worlds only) shifts the coin: P(a wins) = 0.5 + skill[a] - skill[b]."""
    n = w.shape[-1]
    if w.ndim == 1:
        idx = rng.permutation(n)
        a, b = idx[: n // 2], idx[n // 2:]
        stake = f * np.minimum(w[a], w[b])
        p = 0.5 if skill is None else 0.5 + skill[a] - skill[b]
        d = np.where(rng.random(n // 2) < p, stake, -stake)
        w[a] += d
        w[b] -= d
    else:
        idx = rng.permuted(np.broadcast_to(np.arange(n), w.shape), axis=1)
        a, b = idx[:, : n // 2], idx[:, n // 2:]
        wa, wb = np.take_along_axis(w, a, 1), np.take_along_axis(w, b, 1)
        stake = f * np.minimum(wa, wb)
        d = np.where(rng.random(a.shape) < 0.5, stake, -stake)
        np.put_along_axis(w, a, wa + d, 1)
        np.put_along_axis(w, b, wb - d, 1)
    if tax:
        w += tax * (w.mean(axis=-1, keepdims=True) - w)
    return w


def stats(w):
    s = np.sort(w)
    n, tot = len(s), s.sum()
    gini = (2 * np.arange(1, n + 1) - n - 1).dot(s) / (n * tot)
    return dict(
        top1=float(s[-max(1, n // 100):].sum() / tot),
        richest=float(s[-1] / tot),
        bottom50=float(s[: n // 2].sum() / tot),
        below_start=float((w < 100).mean()),
        median=float(np.median(w)),
        gini=float(gini),
    )
