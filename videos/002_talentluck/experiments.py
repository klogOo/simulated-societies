"""Runs every experiment quoted in video 002 and writes results.json.
Usage: .venv/Scripts/python.exe videos/002_talentluck/experiments.py      (~5 min with 4 processes)

Model: sims/talentluck.py (Pluchino, Biondo & Rapisarda 2018). One fixed population of 1,000 people
(talent and seats fixed, seed 0) is replayed through many independent 40-year histories."""
import json, sys, time
from pathlib import Path
import multiprocessing as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from sims.talentluck import people, run, C0

OUT = Path(__file__).parent / "results.json"
N, H, CHUNK = 1000, 10_000, 500
T, P = people(N, seed=0)
RANK = T.argsort().argsort()                     # 0 = least talented, 999 = most talented
TOP = int(T.argmax())


def chunk(k):
    return run(T, P, CHUNK, np.random.default_rng([7, k]), snap=(40,))


def fund_rule(kind, budget=1000.0):
    def f(s, C, rng):
        if s % 10: return None                  # every 5 years (10 steps of 6 months)
        add = np.zeros_like(C); Hh = C.shape[0]
        if kind == "equal": add += budget / N
        elif kind == "random25":
            pick = rng.random(C.shape).argsort(1)[:, : N // 4]; np.put_along_axis(add, pick, budget / (N // 4), 1)
        elif kind == "best25":
            key = C + rng.random(C.shape) * 1e-6     # random tie-break among equal capitals
            pick = (-key).argsort(1)[:, : N // 4]; np.put_along_axis(add, pick, budget / (N // 4), 1)
        elif kind == "best10":
            key = C + rng.random(C.shape) * 1e-6
            pick = (-key).argsort(1)[:, : N // 10]; np.put_along_axis(add, pick, budget / (N // 10), 1)
        return add
    return f


def fund_chunk(args):
    kind, k = args
    r = run(T, P, CHUNK, np.random.default_rng([11, k]), fund=None if kind == "none" else fund_rule(kind))
    C = r["C"]; tal = T > 0.7
    return kind, dict(talented_up=float((C[:, tal] > C0).mean()), top_up=float((C[:, TOP] > C0).mean()),
                      everyone_up=float((C > C0).mean()))


def moved_chunk(k):
    """Years 20-40 in a FRESH world: same people and seats, new events (as if everyone moved somewhere new)."""
    return run(T, P, CHUNK, np.random.default_rng([13, k]), steps=40)["C"]


SENS = {"base": (0.1, 500), "sd005": (0.05, 500), "sd02": (0.2, 500), "ev250": (0.1, 250), "ev1000": (0.1, 1000)}


def sens_chunk(args):
    name, k = args
    sd, ne = SENS[name]
    Ts, Ps = people(N, seed=0, sd=sd)
    r = run(Ts, Ps, CHUNK, np.random.default_rng([17, k]), n_events=ne)
    C = r["C"]; rk = ranks(C, np.random.default_rng([18, k])); win = rk.argmin(1); top = int(Ts.argmax())
    y = np.log2(C / C0); x = np.broadcast_to(Ts, C.shape)
    rr = np.corrcoef(x.ravel(), y.ravel())[0, 1]
    return name, dict(top_win=float((win == top).mean()), top_top10=float((rk[:, top] < 10).mean()),
                      winner_pctile=float((Ts[None, :] < Ts[win][:, None]).mean()), r2_talent=float(rr * rr),
                      top_up=float((C[:, top] > C0).mean()))


def ranks(C, rng):
    """0 = richest. Ties broken at random (capital takes discrete values)."""
    key = C + rng.random(C.shape) * 1e-6
    return (-key).argsort(1).argsort(1)


def derive(R):
    """Numbers quoted in the video that are simple functions of the measured ones."""
    from math import erfc, sqrt
    from sims.talentluck import SIZE, STEPS, N_EVENTS
    z = R["exchange"]["sd_per_lucky"]
    R["derived"] = dict(
        model=dict(c0=C0, steps=STEPS, years=STEPS / 2, events=N_EVENTS, world=SIZE, talent_mean=0.6, talent_sd=0.1),
        lucky_sd_one_in=float(1 / (0.5 * erfc(z / sqrt(2)))),               # 1 person in X is that many SDs above average
        top_lose=1 - R["replay"]["top_win"],
        winner_capital_multiple=R["one"]["winner_capital"] / C0,
        leader_lucky_ratio=R["track"]["best_lucky_next"] / R["track"]["everyone_lucky_next"],
        leader_doubling_multiple=2 ** R["track"]["best_first_half_doublings"],
        winner_lucky_ratio=R["replay"]["winner_lucky_mean"] / R["replay"]["pop_lucky_mean"],
    )
    return R


if __name__ == "__main__" and "--derive" in sys.argv:          # recompute derived numbers only
    OUT.write_text(json.dumps(derive(json.loads(OUT.read_text())), indent=1)); print(json.loads(OUT.read_text())["derived"])
elif __name__ == "__main__":
    t0 = time.time(); R = {}
    R["population"] = dict(n=N, talent_mean=float(T.mean()), talent_sd=float(T.std()), talent_max=float(T.max()),
                           talent_min=float(T.min()), top_id=TOP, above_07=int((T > 0.7).sum()))

    # ---- 1. one featured history (used on screen) ----
    one = run(T, P, 1, np.random.default_rng(2026), trace=True)
    C = one["C"][0]; w = int(C.argmax()); srt = np.sort(C)[::-1]
    R["one"] = dict(seed=2026, winner=w, winner_capital=float(C[w]), winner_talent=float(T[w]),
                    winner_talent_rank=int(N - RANK[w]), winner_lucky=int(one["L"][0, w]), winner_unlucky=int(one["U"][0, w]),
                    top_capital=float(C[TOP]), top_lucky=int(one["L"][0, TOP]), top_unlucky=int(one["U"][0, TOP]),
                    top_rank=int((C > C[TOP]).sum() + 1),
                    top20_share=float(srt[:200].sum() / srt.sum()), below_start=float((C < C0).mean()),
                    above_start=float((C > C0).mean()), neutral=float(((one["L"][0] + one["U"][0]) == 0).mean()),
                    max_lucky=int(one["L"][0].max()), max_unlucky=int(one["U"][0].max()))
    print("one", time.time() - t0, R["one"])

    with mp.Pool(4) as pool:
        parts = pool.map(chunk, range(H // CHUNK))
        print("replay", time.time() - t0)
        fparts = pool.map(fund_chunk, [(kd, k) for kd in ("none", "equal", "random25", "best25", "best10") for k in range(4)])
        print("funding", time.time() - t0)
        moved = np.concatenate(pool.map(moved_chunk, range(H // CHUNK)))
        print("moved", time.time() - t0)
        sparts = pool.map(sens_chunk, [(nm, k) for nm in SENS for k in range(2)])
        print("sensitivity", time.time() - t0)

    C = np.concatenate([p["C"] for p in parts]); L = np.concatenate([p["L"] for p in parts])
    U = np.concatenate([p["U"] for p in parts]); LS = np.concatenate([p["LS"] for p in parts])
    C40 = np.concatenate([p["snaps"][40] for p in parts])
    rng = np.random.default_rng(99)
    rk = ranks(C, rng); hr = np.arange(H)

    # ---- 2. 10,000 histories of the same 1,000 people ----
    win = rk.argmin(1)
    wins = np.bincount(win, minlength=N)
    wt = T[win]
    deciles = np.digitize(RANK, np.arange(100, N, 100))           # 0..9 talent decile
    R["replay"] = dict(
        histories=H,
        top_wins=int(wins[TOP]), top_win=float(wins[TOP] / H), top_top10=float((rk[:, TOP] < 10).mean()),
        top_top100=float((rk[:, TOP] < 100).mean()),
        top_median_rank=float(np.median(rk[:, TOP]) + 1), top_up=float((C[:, TOP] > C0).mean()),
        top_down=float((C[:, TOP] < C0).mean()), top_same=float((C[:, TOP] == C0).mean()),
        winner_talent_mean=float(wt.mean()), winner_talent_median=float(np.median(wt)),
        winner_talent_pctile=float((T[None, :] < wt[:, None]).mean()),     # avg share of population less talented than the winner
        winner_from_top10pct=float((RANK[win] >= 900).mean()), winner_below_mean=float((wt < T.mean()).mean()),
        winner_is_top=float((win == TOP).mean()),
        winner_lucky_mean=float(L[hr, win].mean()), winner_unlucky_mean=float(U[hr, win].mean()),
        winner_unlucky_zero=float((U[hr, win] == 0).mean()),
        pop_lucky_mean=float(L.mean()), pop_unlucky_mean=float(U.mean()),
        most_wins_id=int(wins.argmax()), most_wins=int(wins.max()), most_wins_talent_rank=int(N - RANK[wins.argmax()]),
        ever_won=int((wins > 0).sum()),
        win_by_decile=[float(wins[deciles == d].sum() / H) for d in range(10)],
        top10_talent_mean=float(np.broadcast_to(T, (H, N))[rk < 10].mean()),
        wins_by_person=wins.tolist(),
        top20_share=float(np.mean(np.sort(C, 1)[:, -200:].sum(1) / C.sum(1))),
        neutral=float(((L + U) == 0).mean()), talented_up=float((C[:, T > 0.7] > C0).mean()),
        everyone_up=float((C > C0).mean()), everyone_down=float((C < C0).mean()),
    )
    # how many times more likely the most talented is to win than a random person
    R["replay"]["top_win_vs_avg"] = R["replay"]["top_win"] * N
    R["replay"]["winners"] = win.tolist()                       # winner of each history, in order (drawn on screen)
    # the talent ranks of the people who won most often
    R["replay"]["top5_winners_talent_rank"] = [int(N - RANK[i]) for i in wins.argsort()[::-1][:5]]
    R["replay"]["top5_winners_wins"] = [int(wins[i]) for i in wins.argsort()[::-1][:5]]
    print("replay stats", time.time() - t0)

    # ---- 3. exchange rate: talent vs lucky breaks ----
    y = np.log2(C / C0).ravel(); X = np.column_stack([np.ones(y.size), np.repeat(T[None], H, 0).ravel(), L.ravel(), U.ravel()])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    def r2(cols):
        Xs = X[:, [0] + cols]; b = np.linalg.lstsq(Xs, y, rcond=None)[0]; e = y - Xs @ b
        return float(1 - e.var() / y.var())
    sd = float(T.std())
    R["exchange"] = dict(b_talent=float(beta[1]), b_lucky=float(beta[2]), b_unlucky=float(beta[3]),
                         sd_talent_doublings=float(beta[1] * sd), lucky_per_sd=float(beta[1] * sd / beta[2]),
                         sd_per_lucky=float(beta[2] / (beta[1] * sd)), sd_per_unlucky=float(-beta[3] / (beta[1] * sd)),
                         r2_talent=r2([1]), r2_events=r2([2, 3]), r2_all=r2([1, 2, 3]))
    # concrete pair: average-talent people with one more lucky break vs. the most talented
    mid = np.abs(T - T.mean()) < 0.01
    R["exchange"]["mid_n"] = int(mid.sum())
    R["exchange"]["mid_mean_log2"] = float(np.log2(C[:, mid] / C0).mean())
    R["exchange"]["top_mean_log2"] = float(np.log2(C[:, TOP] / C0).mean())
    R["exchange"]["mid_lucky_mean"] = float(L[:, mid].mean())
    # P(finish in top 1%) given the number of lucky events met, for average talent vs the most talented
    tab = {}
    for k in range(0, 6):
        m_mid = (L[:, mid] == k); m_top = (L[:, TOP] == k)
        tab[k] = dict(mid=float((rk[:, mid][m_mid] < 10).mean()) if m_mid.any() else None,
                      top=float((rk[:, TOP][m_top] < 10).mean()) if m_top.any() else None,
                      share_mid=float(m_mid.mean()), share_top=float(m_top.mean()))
    R["exchange"]["top1pct_by_lucky"] = tab
    print("exchange", time.time() - t0)

    # ---- 4. track record: pick the best performer after 20 years ----
    rk40 = ranks(C40, rng)
    g2 = np.log2(C / C40)                                           # doublings in years 20-40
    best = rk40.argmin(1); top10_40 = rk40 < 10
    R["track"] = dict(
        best_talent_mean=float(T[best].mean()), best_talent_pctile=float((RANK[best] / (N - 1)).mean()),
        best_is_top=float((best == TOP).mean()), best_capital_mean=float(C40[hr, best].mean()),
        best_capital_median=float(np.median(C40[hr, best])),
        best_still_top10=float((rk[hr, best] < 10).mean()), best_still_first=float((rk[hr, best] == 0).mean()),
        best_next_doublings=float(g2[hr, best].mean()), everyone_next_doublings=float(g2.mean()),
        top_next_doublings=float(g2[:, TOP].mean()),
        best_next_up=float((g2[hr, best] > 0).mean()), best_next_down=float((g2[hr, best] < 0).mean()),
        everyone_next_up=float((g2 > 0).mean()), everyone_next_down=float((g2 < 0).mean()),
        top_next_up=float((g2[:, TOP] > 0).mean()), top_next_down=float((g2[:, TOP] < 0).mean()),
        top10_talent_mean=float(np.mean([T[top10_40[h]].mean() for h in range(H)])),
        top10_next_doublings=float(g2[top10_40].mean()), top10_still=float((rk[top10_40] < 10).mean()),
        best_first_half_doublings=float(np.log2(C40[hr, best] / C0).mean()),
    )
    # mean talent of a random person, for comparison
    R["track"]["random_talent_mean"] = float(T.mean())
    # Why does the year-20 leader keep winning? Count their lucky/unlucky events in years 20-40 (same seat) ...
    L40 = np.concatenate([p["snaps"][("L", 40)] for p in parts]); U40 = np.concatenate([p["snaps"][("U", 40)] for p in parts])
    L2, U2 = L - L40, U - U40
    R["track"].update(best_lucky_next=float(L2[hr, best].mean()), best_unlucky_next=float(U2[hr, best].mean()),
                      everyone_lucky_next=float(L2.mean()), everyone_unlucky_next=float(U2.mean()),
                      best_lucky_first=float(L40[hr, best].mean()), everyone_lucky_first=float(L40.mean()))
    # ... and what happens if they (and everyone) are moved to a fresh world for years 20-40
    gm = np.log2(moved / C0)
    R["track"].update(moved_best_doublings=float(gm[hr, best].mean()), moved_everyone_doublings=float(gm.mean()),
                      moved_top_doublings=float(gm[:, TOP].mean()), moved_best_up=float((gm[hr, best] > 0).mean()),
                      moved_top_up=float((gm[:, TOP] > 0).mean()), moved_everyone_up=float((gm > 0).mean()))
    # neighbourhood luck: correlation between a seat's lucky-minus-unlucky events in years 0-20 and 20-40
    a1 = (L40 - U40).astype(float); a2 = (L2 - U2).astype(float)
    R["track"]["luck_persistence_corr"] = float(np.corrcoef(a1.ravel(), a2.ravel())[0, 1])
    R["sensitivity"] = {}
    for nm, d in sparts: R["sensitivity"].setdefault(nm, []).append(d)
    R["sensitivity"] = {k: {m: float(np.mean([d[m] for d in v])) for m in v[0]} for k, v in R["sensitivity"].items()}
    R["sensitivity_meta"] = {k: dict(talent_sd=v[0], events=v[1], histories=2 * CHUNK) for k, v in SENS.items()}
    R["replay"]["top_top_half"] = float((rk[:, TOP] < 500).mean())
    print("track", time.time() - t0)

    # ---- 5. funding: same budget (1,000 units every 5 years), different rules ----
    F = {}
    for kind, d in fparts: F.setdefault(kind, []).append(d)
    R["funding"] = {k: {m: float(np.mean([d[m] for d in v])) for m in v[0]} for k, v in F.items()}
    R["funding_meta"] = dict(budget_per_round=1000, rounds=8, histories=4 * CHUNK, talented="talent > 0.7")

    derive(R)
    R["seconds"] = time.time() - t0
    OUT.write_text(json.dumps(R, indent=1))
    print(json.dumps({k: v for k, v in R.items() if k not in ("replay",)}, indent=1))
    print(json.dumps({k: v for k, v in R["replay"].items() if k != "wins_by_person"}, indent=1))
