"""Runs every experiment quoted in video 001 and writes results.json.
Usage: python videos/001_yardsale/experiments.py
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sims.yardsale import step, stats

OUT = Path(__file__).parent / "results.json"
R = {}
t0 = time.time()

# 1. Main world: 1,000 people, $100 each, 20% stake.
rng = np.random.default_rng(1)
w = np.full(1000, 100.0)
marks = [10, 100, 1000, 10_000, 100_000]
R["main"] = {}
for r in range(1, marks[-1] + 1):
    step(w, rng)
    if r in marks:
        R["main"][r] = stats(w)
print("main", time.time() - t0)

# 2. One person, 100 fair +-20% bets, a million times.
k = np.random.default_rng(2).binomial(100, 0.5, 1_000_000)
final = 100 * 1.2 ** k * 0.8 ** (100 - k)
need = math.floor(100 * math.log(1 / 0.8) / math.log(1.2 / 0.8)) + 1
R["solo"] = dict(mean=float(final.mean()), median=float(np.median(final)),
                 lost=float((final < 100).mean()), wins_needed=need,
                 two_step=100 * 1.2 * 0.8)

# 3. 10,000 worlds of 100 people: is the winner decided early?
rng = np.random.default_rng(3)
W = np.full((10_000, 100), 100.0)
snaps = {}
for r in range(1, 3001):
    step(W, rng)
    if r in (10, 50, 200, 3000):
        snaps[r] = W.copy()
win = snaps[3000].argmax(1)
rows = np.arange(len(win))
R["worlds"] = dict(winner_share=float((snaps[3000].max(1) / 10_000).mean()),
                   distinct_winners=int(len(np.unique(win))),
                   most_wins=int(np.bincount(win, minlength=100).max()),
                   least_wins=int(np.bincount(win, minlength=100).min()),
                   wins_by_seat=np.bincount(win, minlength=100).tolist())
for r in (10, 50, 200):
    rank = (snaps[r] > snaps[r][rows, win][:, None]).sum(1)  # 0 = richest
    R["worlds"][f"r{r}"] = dict(top10=float((rank < 10).mean()), top_half=float((rank < 50).mean()),
                               ahead=float((snaps[r][rows, win] > 100).mean()))
print("worlds", time.time() - t0)

# 4. Same main world with a small flat wealth tax, shared equally.
R["tax"] = {}
for tax in (0.001, 0.005, 0.01, 0.02):
    rng = np.random.default_rng(1)
    w = np.full(1000, 100.0)
    acc = []
    for r in range(20_000):
        step(w, rng, tax=tax)
        if r >= 10_000 and r % 100 == 0:
            acc.append(stats(w))
    R["tax"][tax] = {k: float(np.mean([a[k] for a in acc])) for k in acc[0]}
print("tax", time.time() - t0)

# 5. Talent: 100 of the 1,000 win 55% of flips against everyone else. 200 worlds.
res = dict(skilled_winner=[], skilled_below=[], unskilled_below=[], skilled_share=[], skilled_broke=[])
for seed in range(200):
    rng = np.random.default_rng(100 + seed)
    w = np.full(1000, 100.0)
    skill = np.zeros(1000)
    skill[:100] = 0.05
    for r in range(10_000):
        step(w, rng, skill=skill)
    res["skilled_winner"].append(bool(w.argmax() < 100))
    res["skilled_below"].append(float((w[:100] < 100).mean()))
    res["skilled_broke"].append(float((w[:100] < 1).mean()))
    res["unskilled_below"].append(float((w[100:] < 100).mean()))
    res["skilled_share"].append(float(w[:100].sum() / w.sum()))
R["talent"] = {k: float(np.mean(v)) for k, v in res.items()}
print("talent", time.time() - t0)

OUT.write_text(json.dumps(R, indent=1))
print(json.dumps({k: v for k, v in R.items() if k == "talent"}, indent=1))
