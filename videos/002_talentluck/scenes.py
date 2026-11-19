"""Scenes of video 002 (Talent vs Luck). Each factory takes the scene's cue sheet `q` and returns draw(canvas, t),
called once per frame in order. Every number on screen is read from results.json or live from the simulation
(the featured history is re-run here with the exact call used in experiments.py)."""
import json, math
from pathlib import Path
import numpy as np
import skia
from engine import core as E
from engine.core import INK, MUTED, TEAL, GOLD, CORAL, SLATE, LINE, lerp
from engine.field import Field, steps_at, talent_rgb
from sims.talentluck import people, run, C0

RES = json.loads((Path(__file__).parent / "results.json").read_text())
CHANNEL = "SIMULATED SOCIETIES"
POP, ONE, REP, EXC, TRK, FUN, SEN, DER = (RES[k] for k in ("population", "one", "replay", "exchange", "track",
                                                           "funding", "sensitivity", "derived"))
T, P = people(1000, seed=0)
N = len(T)
RANK = N - T.argsort().argsort()                    # 1 = most talented
TOPI, WIN = POP["top_id"], ONE["winner"]
_one = run(T, P, 1, np.random.default_rng(ONE["seed"]), trace=True)          # == experiments.py featured history
assert float(_one["C"][0, WIN]) == ONE["winner_capital"]
TR = _one["trace"]
DIM = (112, 62, 74)

SPEC = {
    "cold":     ["c1", ("gap", "lapse", 9.0), "c2", "c3", ("gap", "title", 5.0)],
    "rules":    ["r1", "r2", "r3", ("gap", "out", 0.6)],
    "rewind":   ["w1", ("gap", "lapse", 8.0), "w2", "w3", "w4", "w5", ("gap", "out", 0.6)],
    "exchange": ["x1", "x2", "x3", "x4", ("gap", "out", 0.6)],
    "record":   ["k1", ("gap", "hold", 2.0), "k2", "k3", "k4", "k5", ("gap", "out", 0.8)],
    "support":  ["p1", "p2", "p3", ("gap", "out", 1.0)],
    "limits":   ["l1", "l2", "l3", ("gap", "out", 0.6)],
    "outro":    ["o1", ("gap", "end", 12.0)],
}


def show(t, t0, d=0.5): return E.ramp(t, t0, t0 + d)
def span(t, t0, t1, f=0.4): return E.window(t, t0, t1, f)
def pc(v, d=0): return E.pct(v, d)
def num(v): return f"{v:,.0f}"


def label_line(c, x0, y0, x1, y1, a, rgb=INK):
    E.line(c, x0, y0, x1, y1, rgb, 2.5, a * 0.7); c.drawCircle(x1, y1, 5, E.fill(rgb, a * 0.7))


def chip(c, s, x, y, a, size=34, rgb=INK, dot=None):
    w = E.font(size, 600).measureText(s) + (90 if dot else 64)
    E.panel(c, x, y, w, size + 40, a, (size + 40) / 2)
    if dot: c.drawCircle(x + 36, y + (size + 40) / 2, 9, E.fill(dot, a))
    E.text(c, s, x + (60 if dot else 32), y + (size + 40) / 2 + size * 0.36, size, rgb, a, 600)
    return w


def hbar(c, x, y, w, h, frac, rgb, a, bg=True):
    if bg: E.rrect(c, x, y, w, h, h / 2.6, E.fill(LINE, a))
    if frac * w > 1: E.rrect(c, x, y, max(h * 0.8, frac * w), h, h / 2.6, E.fill(rgb, a))


def cached(draw_fn, w=E.W, h=E.H):
    s = skia.Surface(w, h); k = s.getCanvas(); k.clear(skia.Color(0, 0, 0, 0)); draw_fn(k); return s.makeImageSnapshot()


# ------------------------------------------------------------------ 1. cold open: forty years, then the verdict
def cold(q):
    F = Field(T, P, TR, 90, 70, 940)
    L0, L1, C2, C3, TT = q.s("lapse"), q.e("lapse"), q.s("c2"), q.s("c3"), q.s("title")
    tg = q.at("c1", "The gold dots")
    keys = [(tg, 0), (L0, 1.5), (L1 - 0.4, 80)]
    lead = {"t": -1, "i": 0}
    X1 = 1120

    def draw(c, t):
        F.update(t, steps_at(t, keys))
        fa = show(t, 0.2, 0.8) * (1 - 0.85 * show(t, TT - 0.1, 0.8))
        foc = show(t, C2 - 0.2, 0.6)
        mask = np.zeros(N, bool); mask[WIN] = True; mask[TOPI] = True
        F.frame(c, fa)
        F.draw(c, fa, dim=mask if foc > 0 else None, dim_a=lerp(1, 0.22, foc), look_at=F.xy(WIN) if foc > 0 else None)
        F.draw_events(c, fa * show(t, tg - 0.3, 0.8) * (1 - 0.9 * foc))
        F.draw_flashes(c, fa * (1 - foc) * lerp(0.8, 0.35, show(t, L0, 0.6)), life=0.6 if t > L0 else 0.9)
        if foc > 0:                                                       # rings on the two people we talk about
            for i, rgb, t0 in ((WIN, GOLD, C2 - 0.2), (TOPI, TEAL, C3)):
                x, y = F.xy(i); r = float(F.radii()[i]); ra = fa * show(t, t0, 0.6)
                c.drawCircle(x, y, r + 12, E.stroke(rgb, 4, ra)); c.drawCircle(x, y, r + 24, E.stroke(rgb, 2, ra * 0.5))
        # ---- right column, part 1: who is who
        a = span(t, 0.6, C2 + 0.1) * (1 - foc)
        E.text(c, "1,000 people", X1, 190, 76, INK, a, 700)
        E.text(c, "40-year careers", X1, 250, 40, MUTED, a, 500)
        a2 = a * show(t, q.at("c1", "The brighter"))
        if a2 > 0:
            E.text(c, "COLOUR = TALENT", X1, 350, 26, MUTED, a2, 600)
            for k in range(60):
                rgb = talent_rgb(0.3 + 0.6 * k / 59)
                c.drawRect(skia.Rect.MakeXYWH(X1 + k * 9, 372, 9.5, 30), E.fill(rgb, a2))
            E.text(c, "less", X1, 440, 26, MUTED, a2, 500); E.text(c, "more", X1 + 540, 440, 26, MUTED, a2, 500, "r")
        a3 = a * show(t, q.at("c1", "Each of them starts"))
        E.text(c, "SIZE = SUCCESS", X1, 520, 26, MUTED, a3, 600)
        E.text(c, f"everyone starts at {num(C0)}", X1, 566, 38, INK, a3, 500)
        a4 = a * show(t, tg)
        if a4 > 0:
            c.drawCircle(X1 + 14, 655, 11, E.fill(GOLD, a4)); E.text(c, "lucky break", X1 + 44, 667, 38, INK, a4, 600)
        a5 = a * show(t, q.at("c1", "The red ones"))
        if a5 > 0:
            c.drawCircle(X1 + 14, 725, 11, E.fill(CORAL, a5)); E.text(c, "setback", X1 + 44, 737, 38, INK, a5, 600)
        # ---- live counters during the run
        a = span(t, tg, C2 + 0.2) * fa
        E.text(c, "YEAR", 1830, 860, 26, MUTED, a, 600, "r")
        E.text(c, f"{min(40, int(F.step_f / 2) + 1) if F.step_f > 0 else 0}", 1830, 960, 110, INK, a, 700, "r")
        if t - lead["t"] > 0.25:
            lead["t"] = t; lead["i"] = int(np.argmax(F.capital()))
        a = span(t, L0 + 0.5, C2 + 0.2) * fa
        if a > 0:
            i = lead["i"]
            E.text(c, "MOST SUCCESSFUL RIGHT NOW", X1, 860, 26, MUTED, a, 600)
            E.text(c, f"talent rank #{RANK[i]}", X1, 930, 56, GOLD, a, 700)
            E.text(c, f"of 1,000  ·  {num(F.capital()[i])} points", X1, 976, 30, MUTED, a, 500)
        # ---- the verdict
        a = span(t, C2 + 0.3, TT) * fa
        if a > 0:
            x, y = F.xy(WIN); r = float(F.radii()[WIN])
            label_line(c, x + r * 0.75, y - r * 0.75, X1 - 20, 225, a)
            E.text(c, "MOST SUCCESSFUL", X1, 210, 28, MUTED, a, 600)
            E.text(c, f"{num(ONE['winner_capital'])} points", X1, 300, 84, GOLD, a, 700)
            E.text(c, f"{num(DER['winner_capital_multiple'])}× where they started", X1, 350, 32, INK, a, 500)
            a1 = a * show(t, q.at("c2", "Their talent"))
            E.text(c, f"talent {ONE['winner_talent']:.2f}", X1, 430, 46, INK, a1, 700)
            E.text(c, f"{ONE['winner_talent_rank'] - 1} people were more talented", X1, 474, 32, CORAL,
                   a * show(t, q.at("c2", "Eight hundred")), 600)
        a = span(t, C3 + 0.2, TT) * fa
        if a > 0:
            x, y = F.xy(TOPI); r = float(F.radii()[TOPI])
            label_line(c, x + r + 4, y, X1 - 20, 640, a, TEAL)
            E.text(c, "MOST TALENTED", X1, 625, 28, MUTED, a, 600)
            E.text(c, f"talent {POP['talent_max']:.2f}", X1, 705, 72, TEAL, a * show(t, q.at("c3", "Their talent score")), 700)
            E.text(c, f"lucky breaks: {ONE['top_lucky']}   ·   setbacks: {ONE['top_unlucky']}", X1, 765, 34, INK,
                   a * show(t, q.at("c3", "not one lucky")), 600)
            E.text(c, f"ended with {num(ONE['top_capital'])}, exactly where they began", X1, 815, 32, MUTED,
                   a * show(t, q.at("c3", "They ended exactly")), 500)
        a = show(t, TT + 0.3, 0.7)
        E.text(c, f"{CHANNEL}  ·  EXPERIMENT 002", 960, 400, 28, MUTED, a, 600, "c")
        E.text(c, "Talent vs Luck", 960, 545, 140, INK, a, 700, "c")
        E.text(c, "the same 1,000 people, 10,000 lifetimes", 960, 650, 56, GOLD, a, 600, "c")
    return draw


# ------------------------------------------------------------------ 2. the rules
def rules(q):
    R2, R3 = q.s("r2"), q.s("r3")
    # dot-plot of the 1,000 real talents
    b = np.clip(((T - 0.2) / 0.02).astype(int), 0, 39); order = np.lexsort((T, b))
    hx, hy = np.zeros(N), np.zeros(N); cnt = np.zeros(40, int)
    for i in order:
        k = cnt[b[i]]; cnt[b[i]] += 1
        hx[i] = 260 + b[i] * 35 + 7 + (k % 3) * 10.5; hy[i] = 860 - (k // 3) * 10.5
    F = Field(T, P, TR, 90, 70, 940)
    sx, sy = F.px * 0.62 + 380, F.py * 0.62 + 160                        # start: a shrunken copy of the field
    rgb = talent_rgb(T)
    t_fly = 0.5
    F2 = Field(T, P, TR, 90, 70, 940)                                       # end state of the featured history
    demo = [  # (x, talent, kind, t_hit, outcome)
        (520, 0.9, "lucky", q.at("r2", "Someone with a talent") + 0.4, True),
        (960, 0.5, "lucky", q.at("r2", "Someone at point five") + 0.2, False),
        (1400, None, "bad", q.at("r2", "A setback halves") + 0.3, None)]

    def draw(c, t):
        # ---- r1: the bell curve
        a1 = 1 - show(t, R2 - 0.3, 0.5)
        if a1 > 0:
            g = np.clip((t - t_fly - (T - 0.2) * 2.2) / 1.1, 0, 1); g = g * g * (3 - 2 * g)
            X, Y = sx + (hx - sx) * g, sy + (hy - sy) * g
            for i in range(N):
                E.blob(c, float(X[i]), float(Y[i]), 4.8, rgb[i], a1, eyes=False)
            ax = show(t, 2.8)
            E.line(c, 250, 880, 1670, 880, LINE, 2, a1 * ax)
            for v in (0.2, 0.4, 0.6, 0.8, 1.0):
                xx = 260 + (v - 0.2) / 0.02 * 35; E.text(c, f"{v:.1f}", xx, 920, 26, MUTED, a1 * ax, 500, "c")
            E.text(c, "talent", 1690, 888, 28, MUTED, a1 * ax, 500)
            E.text(c, "The Talent vs Luck model", 960, 150, 72, INK, a1 * show(t, 0.4), 700, "c")
            E.text(c, "A. Pluchino, A. E. Biondo & A. Rapisarda (2018)", 960, 210, 32, MUTED, a1 * show(t, 0.8), 500, "c")
            a = a1 * show(t, q.at("r1", "Most people are near"))
            xm = 260 + (0.6 - 0.2) / 0.02 * 35 + 17
            E.text(c, "most people: near average", xm, 380, 34, INK, a, 600, "c"); E.arrow(c, xm, 395, xm, 470, INK, 3, a, 12)
            a = a1 * show(t, q.at("r1", "a few are exceptional"))
            xt, yt = float(hx[TOPI]), float(hy[TOPI])
            c.drawCircle(xt, yt, 13, E.stroke(TEAL, 3, a))
            E.text(c, "a few: exceptional", xt + 10, yt - 120, 34, TEAL, a, 600, "c"); E.arrow(c, xt + 10, yt - 105, xt, yt - 22, TEAL, 3, a, 12)
            E.text(c, "Talent never changes. Nobody moves.", 960, 1010, 40, GOLD, a1 * show(t, q.at("r1", "Nobody's talent")), 600, "c")
        # ---- r2: the two rules, acted out
        a2 = span(t, R2 - 0.1, R3 - 0.2)
        if a2 > 0:
            E.text(c, "Every 6 months, the events drift", 960, 140, 56, INK, a2, 700, "c")
            m = DER["model"]
            E.text(c, f"{m['events']} events  ·  {m['steps']} steps  ·  {m['years']:.0f} years", 960, 196, 32, MUTED, a2, 500, "c")
            for x, tal, kind, th, ok in demo:
                vis = a2 * show(t, R2 + (0.2 if tal == 0.9 else 0.5 if tal == 0.5 else 0.8))
                if vis <= 0: continue
                col = talent_rgb(tal) if tal is not None else talent_rgb(0.62)
                g = E.ramp(t, th + 0.35, th + 1.0, E.ease_out)
                k = (math.sqrt(2) if ok else 1.0) if kind == "lucky" else 1 / math.sqrt(2)
                rr = 78 * lerp(1, k, g)
                E.blob(c, x, 600, rr, col, vis, (0, -0.5))
                E.text(c, f"talent {tal:.1f}" if tal is not None else "anyone", x, 800, 40, INK, vis, 600, "c")
                u = E.ramp(t, th - 1.6, th, E.ease)                                   # the dot glides in
                da = vis * (1 - show(t, th + 0.1, 0.3))
                ex, ey = lerp(x - 260, x, u), lerp(330, 600 - 30, u)
                c.drawCircle(ex, ey, 26, E.fill(GOLD if kind == "lucky" else CORAL, 0.15 * da))
                c.drawCircle(ex, ey, 13, E.fill(GOLD if kind == "lucky" else CORAL, da))
                ring = span(t, th, th + 1.1, 0.2) * vis
                if ring > 0: c.drawCircle(x, 600, rr + 10 + 30 * E.ramp(t, th, th + 1.1), E.stroke(GOLD if kind == "lucky" else CORAL, 4, ring))
                if kind == "lucky":
                    E.text(c, f"{tal * 100:.0f}% chance to use it", x, 890, 32, GOLD, vis * show(t, th - 0.8), 600, "c")
                    E.text(c, "×2" if ok else "missed it", x, 960, 52 if ok else 40, GOLD if ok else MUTED, vis * show(t, th + 0.4), 700, "c")
                else:
                    E.text(c, "100% of the time", x, 890, 32, CORAL, vis * show(t, th - 0.8), 600, "c")
                    E.text(c, "÷2", x, 960, 52, CORAL, vis * show(t, th + 0.4), 700, "c")
        # ---- r3: back to the featured world, after 40 years
        a3 = show(t, R3 - 0.1, 0.6)
        if a3 > 0:
            if F2.step_f < 80: F2.update(t, 80); F2.snap()
            F2.t = t
            F2.frame(c, a3); F2.draw(c, a3)
            x, y = F2.xy(TOPI); ra = a3 * show(t, q.at("r3", "while our most talented"))
            c.drawCircle(x, y, 22, E.stroke(TEAL, 4, ra)); c.drawCircle(x, y, 34, E.stroke(TEAL, 2, ra * 0.5))
            X1 = 1120
            a = a3 * span(t, R3, q.at("r3", "This world is different"), 0.3)
            if a > 0:
                E.panel(c, X1, 220, 700, 250, a)
                E.text(c, "LAST VIDEO: THE YARD SALE GAME", X1 + 40, 285, 26, MUTED, a, 600)
                E.text(c, "pure coin flips", X1 + 40, 360, 54, INK, a, 700)
                E.text(c, "even skilled players mostly ended poor", X1 + 40, 420, 32, CORAL, a, 500)
            a = a3 * show(t, q.at("r3", "This world is different"))
            E.text(c, "This world rewards talent.", X1, 300, 54, TEAL, a, 700)
            E.text(c, "Every lucky break is worth more", X1, 360, 34, INK, a, 500)
            E.text(c, "to a more talented person.", X1, 402, 34, INK, a, 500)
            a = a3 * show(t, q.at("r3", "And still"))
            if a > 0:
                E.text(c, "AFTER 40 YEARS", X1, 540, 26, MUTED, a, 600)
                hbar(c, X1, 566, 700, 50, ONE["top20_share"], GOLD, a)
                E.text(c, f"top 20% hold {pc(ONE['top20_share'])}", X1, 690, 60, GOLD, a, 700)
                E.text(c, "of all the success", X1, 736, 34, INK, a, 500)
            a = a3 * show(t, q.at("r3", "while our most talented"))
            E.text(c, f"most talented: {num(C0)} → {num(ONE['top_capital'])}", X1, 850, 44, TEAL, a, 700)
    return draw


# ------------------------------------------------------------------ 3. rewind: 10,000 lives of the same people
def rewind(q):
    F = Field(T, P, TR, 490, 70, 940)
    tr0, tr1 = q.at("w1", "So we did something"), q.at("w1", "We kept the same")
    L0, L1 = q.s("lapse"), q.e("lapse")
    W2, W3, W4, W5 = q.s("w2"), q.s("w3"), q.s("w4"), q.s("w5")
    winners = np.array(REP["winners"]); H = len(winners)
    order = np.argsort(T)                                   # bars from least to most talented
    pos_of = np.empty(N, int); pos_of[order] = np.arange(N)
    rgb = talent_rgb(T[order])
    X0, BW, BASE, K = 160, 1.6, 880, 6.2
    state = {"n": 0, "counts": np.zeros(N)}
    wt = T[winners]
    tb = np.linspace(0.2, 1.0, 41)
    hp, _ = np.histogram(T, tb); hw, _ = np.histogram(wt, tb); hp = hp / hp.sum(); hw = hw / hw.sum()
    med = float(np.median(wt))

    def bars_n(t):
        if t < L0: return 0
        return int(round(H ** E.clamp((t - L0) / (L1 - L0 - 0.4))))

    def draw(c, t):
        # ---- the field rewinds
        fa = 1 - show(t, L0 - 0.4, 0.6)
        if fa > 0:
            if F.step_f == 0 and t < 1: F.update(t, 80); F.snap()
            F.update(t, 80 * (1 - E.ramp(t, tr0 - 1.2, tr0 + 1.6)))
            F.frame(c, fa); F.draw(c, fa); F.draw_events(c, fa * lerp(0.7, 0.15, span(t, tr0 - 1.2, tr0 + 1.6, 0.4)))   # fast rewind: dots fade
            a = fa * span(t, tr0 - 1.2, tr1 + 0.5, 0.3)
            if a > 0:
                for k in (0, 1):
                    x = 150 + k * 60; p = skia.Path(); p.moveTo(x + 50, 470); p.lineTo(x + 50, 610); p.lineTo(x, 540); p.close()
                    c.drawPath(p, E.fill(INK, a))
                E.text(c, "REWIND", 150, 680, 46, INK, a, 700)
                E.text(c, f"year {min(40, int(F.step_f / 2) + 1)}", 150, 730, 34, MUTED, a, 500)
            a = fa * show(t, tr1)
            for k, s in enumerate(("same people", "same talents", "same seats")):
                E.text(c, s, 1470, 380 + k * 70, 46, INK, a * show(t, tr1 + k * 0.6), 600)
            E.text(c, "different breaks", 1470, 620, 46, GOLD, a * show(t, q.at("w1", "each time with different")), 700)
        # ---- the chart of wins, growing history by history
        n = bars_n(math.floor(t * 10) / 10)                 # chart and counter refresh at 10 Hz
        if n > state["n"]:
            state["counts"] += np.bincount(winners[state["n"]:n], minlength=N); state["n"] = n
        ca = show(t, L0 - 0.2, 0.6) * (1 - show(t, W4 - 0.3, 0.5))
        if ca > 0:
            cnts = state["counts"][order]
            hi = show(t, W3 + 0.2)
            E.line(c, X0 - 10, BASE, X0 + N * BW + 10, BASE, LINE, 2, ca)
            for j in range(N):
                h = cnts[j] * K
                if h > 0.2:
                    al = ca * (lerp(1, 0.35, hi) if j < N - 1 else 1)
                    c.drawRect(skia.Rect.MakeXYWH(X0 + j * BW, BASE - h, BW + 0.3, h), E.fill(rgb[j], al))
            E.text(c, "← least talented", X0, BASE + 46, 28, MUTED, ca, 500)
            E.text(c, "most talented →", X0 + N * BW, BASE + 46, 28, MUTED, ca, 500, "r")
            E.text(c, "how often each person finished first", X0, 190, 44, INK, ca, 700)
            E.text(c, f"history {max(1, state['n']):,} of {H:,}", X0 + N * BW, 190, 36, GOLD, ca, 600, "r")
            # decile shares
            dv = REP["win_by_decile"]
            for d in range(10):
                ta = W2 + 1.0 if d not in (0, 9) else q.at("w2", "The most talented tenth") if d == 9 else q.at("w2", "The least talented")
                a = ca * show(t, ta) * (1 - hi)
                if a <= 0: continue
                x = X0 + d * 100 * BW
                E.rrect(c, x + 3, 300, 100 * BW - 6, BASE - 300, 10, E.fill(LINE, 0.18 * a))
                E.text(c, pc(dv[d]), x + 50 * BW, 290, 40 if d in (0, 9) else 28, GOLD if d == 9 else CORAL if d == 0 else MUTED, a, 700, "c")
            E.text(c, "share of all winners, by tenth of talent", X0 + N * BW / 2, 250, 28, MUTED, ca * show(t, W2 + 1.0) * (1 - hi), 500, "c")
            # the most talented person
            if hi > 0:
                xb = X0 + (N - 1) * BW; hb = cnts[-1] * K
                c.drawCircle(xb + 1, BASE - hb - 16, 12, E.stroke(TEAL, 3, ca * hi))
                E.panel(c, 1000, 300, 640, 470, ca * hi)
                E.text(c, "THE MOST TALENTED PERSON", 1040, 360, 26, MUTED, ca * hi, 600)
                E.text(c, f"{REP['top_wins']} wins", 1040, 450, 84, TEAL, ca * show(t, q.at("w3", "they finished first")), 700)
                E.text(c, f"out of {H:,} lives", 1040, 500, 32, INK, ca * show(t, q.at("w3", "they finished first")), 500)
                rows = [(q.at("w3", "That's about five"), f"{REP['top_win_vs_avg']:.1f}× a random person's chance", INK),
                        (q.at("w3", "it still means"), f"still loses {pc(DER['top_lose'], 1)} of the time", CORAL),
                        (q.at("w3", "They made the top ten"), f"top 10 in {pc(REP['top_top10'])} of lives", INK),
                        (q.at("w3", "and finished below"), f"below the start in {pc(REP['top_down'])}", CORAL)]
                for k, (t0, s, col) in enumerate(rows):
                    E.text(c, s, 1040, 575 + k * 50, 34, col, ca * show(t, t0), 600)
                E.line(c, xb + 1, BASE - hb - 30, 1640, 770, TEAL, 2, ca * hi * 0.6)
        # ---- who the winners are
        a4 = span(t, W4 - 0.1, W5 - 0.2)
        if a4 > 0:
            x0, x1, base, sc = 240, 1500, 860, 2600
            E.text(c, f"{REP['ever_won']} different people won at least once", 960, 180, 52, INK, a4, 700, "c")
            for j in range(40):
                x = x0 + j * (x1 - x0) / 40; w = (x1 - x0) / 40
                c.drawRect(skia.Rect.MakeXYWH(x + 2, base - hw[j] * sc, w - 4, hw[j] * sc), E.fill(GOLD, a4 * 0.9))
                E.rrect(c, x + 2, base - hp[j] * sc, w - 4, hp[j] * sc, 0, E.stroke(INK, 2, a4 * 0.7))
            E.line(c, x0, base, x1, base, LINE, 2, a4)
            for v in (0.2, 0.4, 0.6, 0.8, 1.0):
                E.text(c, f"{v:.1f}", x0 + (v - 0.2) / 0.8 * (x1 - x0), base + 40, 26, MUTED, a4, 500, "c")
            E.text(c, "talent", x1 + 20, base + 8, 26, MUTED, a4, 500)
            c.drawRect(skia.Rect.MakeXYWH(1560, 300, 30, 30), E.fill(GOLD, a4)); E.text(c, "winners", 1606, 326, 30, INK, a4, 600)
            E.rrect(c, 1560, 350, 30, 30, 0, E.stroke(INK, 2, a4)); E.text(c, "everyone", 1606, 376, 30, INK, a4, 600)
            a = a4 * show(t, q.at("w4", "The typical winner"))
            xm = x0 + (med - 0.2) / 0.8 * (x1 - x0)
            for ys in range(300, base, 26): E.line(c, xm, ys, xm, ys + 13, GOLD, 3, a)
            E.text(c, "typical winner:", xm + 16, 300, 30, MUTED, a, 500)
            E.text(c, f"more talented than {pc(REP['winner_talent_pctile'])}", xm + 16, 344, 36, GOLD, a, 700)
            a = a4 * show(t, q.at("w4", "One winner in four"))
            xa = x0 + (POP["talent_mean"] - 0.2) / 0.8 * (x1 - x0)
            E.text(c, f"{pc(REP['winner_below_mean'])} of winners had", 470, 470, 32, CORAL, a, 600, "c")
            E.text(c, "below-average talent", 470, 512, 32, CORAL, a, 600, "c")
            E.arrow(c, 560, 540, xa - 40, 700, CORAL, 3, a, 12)
        # ---- what the winners had
        a5 = show(t, W5 - 0.1, 0.5) * (1 - show(t, q.total - 0.9, 0.5))
        if a5 > 0:
            E.text(c, "What the winners had: luck", 960, 200, 64, INK, a5, 700, "c")
            for k, (lab, v, col, t0) in enumerate([("a winner, on average", REP["winner_lucky_mean"], GOLD, q.at("w5", "a winner met")),
                                                   ("a typical person", REP["pop_lucky_mean"], GOLD, q.at("w5", "A typical person"))]):
                a = a5 * show(t, t0); y = 400 + k * 190
                E.text(c, lab, 260, y - 40, 32, MUTED, a, 500)
                for j in range(int(math.ceil(v))):
                    part = min(1.0, v - j)
                    c.drawCircle(285 + j * 74, y + 30, 28, E.fill(LINE, a))
                    if part > 0: c.drawCircle(285 + j * 74, y + 30, 28 * math.sqrt(part), E.fill(col, a))
                E.text(c, f"{v:.1f} lucky breaks", 300 + int(math.ceil(v)) * 74, y + 46, 46, col, a, 700)
            a = a5 * show(t, q.at("w5", "And three winners"))
            E.text(c, f"{pc(REP['winner_unlucky_zero'])} of winners never had a single setback", 960, 900, 46, CORAL, a, 700, "c")
    return draw


# ------------------------------------------------------------------ 4. the exchange rate
def exchange(q):
    smp = run(T, P, 20, np.random.default_rng(5))                     # a sample of 20,000 careers for the scatter
    y = np.log2(smp["C"] / C0).ravel(); tx = np.broadcast_to(T, smp["C"].shape).ravel()
    br = (smp["L"] - smp["U"]).ravel().astype(float)
    jit = np.random.default_rng(6)
    jy, jb = jit.uniform(-0.35, 0.35, y.size), jit.uniform(-0.35, 0.35, y.size)
    PW, PH, PY = 700, 520, 260
    PX = (170, 1050)

    def ymap(v): return PY + PH / 2 - np.clip(v, -10, 10) / 10 * (PH / 2 - 10)

    def scat(k):
        X = PX[0] + (np.clip(tx, 0.2, 1.0) - 0.2) / 0.8 * PW
        Y = ymap(y + jy)
        p = E.fill(TEAL, 0.16)
        for i in range(0, y.size, 2): k.drawCircle(float(X[i]), float(Y[i]), 2.2, p)
        X2 = PX[1] + (np.clip(br + jb, -10, 10) + 10) / 20 * PW
        Y2 = ymap(y + jy)
        p = E.fill(GOLD, 0.16)
        for i in range(0, y.size, 2): k.drawCircle(float(X2[i]), float(Y2[i]), 2.2, p)
    img = {}
    X2, X3, X4 = q.s("x2"), q.s("x3"), q.s("x4")

    def draw(c, t):
        a1 = 1 - show(t, X3 - 0.3, 0.5)
        if a1 > 0:
            if "s" not in img: img["s"] = cached(scat)
            E.text(c, "What predicts where someone ends up?", 960, 150, 60, INK, a1 * show(t, 0.3), 700, "c")
            E.text(c, f"every person, every history  ·  showing a sample of {smp['C'].size:,} careers", 960, 200, 30, MUTED, a1 * show(t, 0.6), 500, "c")
            sa = a1 * show(t, 1.2, 0.8)
            for k, (x, lab, xl, xr) in enumerate(((PX[0], "TALENT", "0.2", "1.0"), (PX[1], "LUCKY BREAKS MINUS SETBACKS", "−10", "+10"))):
                ak = sa if k == 0 else a1 * show(t, q.at("x2", "Simply counting"), 0.8)
                E.panel(c, x - 30, PY - 30, PW + 60, PH + 60, ak)
                E.text(c, lab, x, PY + PH + 80, 26, MUTED, ak, 600)
                E.text(c, xl, x, PY + PH + 40, 24, MUTED, ak, 500); E.text(c, xr, x + PW, PY + PH + 40, 24, MUTED, ak, 500, "r")
                c.save(); c.clipRect(skia.Rect.MakeXYWH(x - 10, PY - 10, PW + 20, PH + 20))
                c.drawImage(img["s"], 0, 0, skia.SamplingOptions(), E.fill(INK, ak)); c.restore()
            E.text(c, "success ↑", PX[0] - 20, PY + 10, 24, MUTED, sa, 500, "r")
            for k, (t0, v, col, lab) in enumerate(((q.at("x2", "Talent, on its own"), EXC["r2_talent"], TEAL, "talent explains"),
                                                    (q.at("x2", "Simply counting"), EXC["r2_events"], GOLD, "the breaks explain"))):
                a = a1 * show(t, t0)
                x = PX[k]
                E.text(c, lab, x, 960, 32, INK, a, 600)
                E.text(c, pc(v, 1) if v < 0.01 else pc(v), x + PW, 966, 64, col, a, 700, "r")
                hbar(c, x, 990, PW, 24, v * E.ramp(t, t0, t0 + 1.2), col, a)
            E.text(c, "of the differences in success", 960, 1060, 26, MUTED, a1 * show(t, q.at("x2", "Talent, on its own")), 500, "c")
        a3 = span(t, X3 - 0.1, X4 - 0.2)
        if a3 > 0:
            E.text(c, "The exchange rate", 960, 170, 76, INK, a3, 700, "c")
            c.drawCircle(330, 470, 46, E.fill(GOLD, 0.18 * a3)); c.drawCircle(330, 470, 28, E.fill(GOLD, a3))
            E.text(c, "1 extra lucky break", 330, 580, 36, INK, a3, 600, "c")
            E.text(c, "=", 640, 500, 110, MUTED, a3 * show(t, q.at("x3", "is worth")), 700, "c")
            a = a3 * show(t, q.at("x3", "almost four"))
            bx, bw, by = 800, 900, 560
            if a > 0:
                pts = [(bx + i / 200 * bw, by - 260 * math.exp(-0.5 * ((i / 200 * 10 - 3) ** 2))) for i in range(201)]
                E.polyline(c, pts, TEAL, 4, a)
                E.line(c, bx, by, bx + bw, by, LINE, 2, a)
                xm = bx + 0.3 * bw; z = EXC["sd_per_lucky"]; xz = bx + (3 + z) / 10 * bw
                E.line(c, xm, by - 280, xm, by + 10, INK, 2, a); E.text(c, "average", xm, by + 46, 28, MUTED, a, 500, "c")
                g = E.ramp(t, q.at("x3", "almost four"), q.at("x3", "almost four") + 1.4)
                E.arrow(c, xm, by + 90, lerp(xm, xz, g), by + 90, GOLD, 5, a, 18)
                E.line(c, xz, by - 60, xz, by + 100, GOLD, 3, a * g)
                E.text(c, f"+{z:.1f} standard deviations of talent", lerp(xm, xz, 0.5), by + 150, 38, GOLD, a, 700, "c")
                E.text(c, f"the most gifted 1 in {num(DER['lucky_sd_one_in'])}", xz + 20, by - 80, 30, GOLD, a * show(t, q.at("x3", "That's the gap")), 600)
            a = a3 * show(t, q.at("x3", "One extra setback"))
            if a > 0:
                c.drawCircle(330, 860, 28, E.fill(CORAL, a)); E.text(c, "1 extra setback", 330, 960, 36, INK, a, 600, "c")
                E.text(c, "=", 640, 890, 110, MUTED, a, 700, "c")
                E.text(c, f"−{EXC['sd_per_unlucky']:.1f} standard deviations of talent", 800, 890, 52, CORAL, a, 700)
        a4 = show(t, X4 - 0.1, 0.5) * (1 - show(t, q.total - 0.9, 0.5))
        if a4 > 0:
            E.text(c, "Who won most often, across 10,000 lives?", 960, 210, 56, INK, a4, 700, "c")
            ws, rk = REP["top5_winners_wins"], REP["top5_winners_talent_rank"]
            for k in range(5):
                a = a4 * show(t, q.at("x4", "the people who won") + k * 0.35)
                x = 360 + k * 300
                E.blob(c, x, 470, 70, talent_rgb(T[np.argsort(-T)[rk[k] - 1]]), a, (0, -0.3))
                E.text(c, f"talent #{rk[k]}", x, 600, 40, TEAL, a, 700, "c")
                E.text(c, f"{ws[k]} wins", x, 648, 32, MUTED, a, 500, "c")
            E.text(c, "Talent shows up across many lives.", 960, 820, 54, INK, a4 * show(t, q.at("x4", "Talent shows up")), 700, "c")
            E.text(c, "In any single life, it's buried under the breaks.", 960, 900, 46, GOLD, a4 * show(t, q.at("x4", "In any single life")), 600, "c")
    return draw


# ------------------------------------------------------------------ 5. track records (and the address of luck)
def record(q):
    F = Field(T, P, TR, 90, 70, 940)
    C40 = np.asarray(TR["C"][39]); lead = int(np.argmax(C40))          # featured history: best record at year 20
    t0, t1 = q.at("k1", "So let's do"), q.at("k1", "and pick the person")
    keys = [(t0, 0), (t1 - 0.2, 40)]
    K2, K3, K4, K5 = q.s("k2"), q.s("k3"), q.s("k4"), q.s("k5")
    # lucky-minus-unlucky event density of the featured history, years 0-20 vs 20-40 (10x10 regions)
    NB = 10
    ex, ey = np.array(TR["ex"]), np.array(TR["ey"]); sgn = np.where(TR["lucky"], 1.0, -1.0)
    def dens(s0, s1):
        bx = (ex[s0:s1] / 201 * NB).astype(int).clip(0, NB - 1); by = (ey[s0:s1] / 201 * NB).astype(int).clip(0, NB - 1)
        m = np.zeros((NB, NB)); np.add.at(m, (bx.ravel(), by.ravel()), np.broadcast_to(sgn, bx.shape).ravel()); return m
    D1, D2 = dens(1, 41), dens(41, 81)
    dmax = max(np.abs(D1).max(), np.abs(D2).max())
    lx, ly = P[lead]
    X1 = 1120

    def heat(c, x0, y0, side, D, a, title):
        cs = side / NB
        for i in range(NB):
            for j in range(NB):
                v = D[i, j] / dmax
                col = GOLD if v > 0 else CORAL
                c.drawRect(skia.Rect.MakeXYWH(x0 + i * cs, y0 + j * cs, cs - 2, cs - 2), E.fill(col, a * min(1, abs(v)) * 0.95))
        E.rrect(c, x0 - 6, y0 - 6, side + 12, side + 12, 10, E.stroke(LINE, 2, a))
        px, py = x0 + (lx + 0.5) / 201 * side, y0 + (ly + 0.5) / 201 * side
        c.drawCircle(px, py, 16, E.stroke(INK, 4, a)); c.drawCircle(px, py, 5, E.fill(INK, a))
        E.text(c, title, x0 + side / 2, y0 - 26, 30, INK, a, 600, "c")

    def draw(c, t):
        F.update(t, steps_at(t, keys))
        fa = 1 - show(t, K4 - 0.3, 0.6)
        foc = show(t, t1, 0.5)
        if fa > 0:
            F.frame(c, fa)
            F.draw(c, fa * lerp(1, 0.9, foc), dim=np.arange(N) == lead if foc > 0 else None, dim_a=lerp(1, 0.25, foc),
                   look_at=F.xy(lead) if foc > 0 else None)
            F.draw_events(c, fa * (1 - 0.8 * foc) * lerp(1, 0.6, span(t, t0, t1, 0.5))); F.draw_flashes(c, fa * lerp(1, 0.35, span(t, t0, t1, 0.5)), life=0.6)
            a = fa * span(t, t0 - 0.3, t1 + 0.5)
            E.text(c, "YEAR", 1830, 860, 26, MUTED, a, 600, "r")
            E.text(c, f"{min(20, int(F.step_f / 2) + 1) if F.step_f > 0 else 0}", 1830, 960, 110, INK, a, 700, "r")
        a = span(t, 0.4, t0 + 0.3)
        E.text(c, "We never see talent.", X1, 330, 60, INK, a, 700)
        E.text(c, "We see track records.", X1, 410, 60, GOLD, a * show(t, q.at("k1", "We see track records")), 700)
        a = span(t, t1, K3 - 0.2)
        if a > 0:
            x, y = F.xy(lead); r = float(F.radii()[lead])
            label_line(c, x + r * 0.75, y - r * 0.75, X1 - 20, 225, a, GOLD)
            c.drawCircle(x, y, r + 12, E.stroke(GOLD, 4, a))
            E.text(c, "BEST RECORD AT YEAR 20", X1, 210, 28, MUTED, a, 600)
            E.text(c, f"{num(C40[lead])} points", X1, 290, 76, GOLD, a, 700)
            E.text(c, f"this history  ·  talent rank #{RANK[lead]}", X1, 340, 32, MUTED, a, 500)
            a1 = a * show(t, q.at("k1", "Their record looks"))
            E.panel(c, X1, 420, 700, 420, a1)
            E.text(c, "THE YEAR-20 LEADER, IN 10,000 HISTORIES", X1 + 36, 476, 24, MUTED, a1, 600)
            E.text(c, f"×{DER['leader_doubling_multiple']:.0f}", X1 + 36, 570, 76, GOLD, a1, 700)
            E.text(c, "typical growth so far", X1 + 300, 560, 30, INK, a1, 500)
            a2 = a * show(t, q.at("k2", "On average, more"))
            E.text(c, pc(TRK["best_talent_pctile"]), X1 + 36, 690, 76, TEAL, a2, 700)
            E.text(c, "of people are less talented", X1 + 300, 680, 30, INK, a2, 500)
            a2 = a * show(t, q.at("k2", "They were the most"))
            E.text(c, pc(TRK["best_is_top"], 2), X1 + 36, 800, 76, CORAL, a2, 700)
            E.text(c, "were the most talented", X1 + 300, 790, 30, INK, a2, 500)
        # ---- k3: they keep growing
        a3 = span(t, q.at("k3", "Over the next") - 0.3, q.at("k4", "Sitting in the same") - 0.1)
        if a3 > 0:
            E.panel(c, X1, 170, 720, 600, a3)
            E.text(c, "GREW AGAIN IN YEARS 20–40", X1 + 36, 230, 26, MUTED, a3, 600)
            rows = [("the year-20 leader", TRK["best_next_up"], GOLD, q.at("k3", "Forty percent")),
                    ("everyone", TRK["everyone_next_up"], MUTED, q.at("k3", "against twenty")),
                    ("the most talented person", TRK["top_next_up"], TEAL, q.at("k3", "and twenty-seven"))]
            for k, (lab, v, col, tt) in enumerate(rows):
                a = a3 * show(t, tt); yy = 300 + k * 130
                E.text(c, lab, X1 + 36, yy + 10, 32, INK, a, 600)
                hbar(c, X1 + 36, yy + 32, 480, 36, v * E.ramp(t, tt, tt + 1.0), col, a)
                E.text(c, pc(v), X1 + 680, yy + 64, 52, col, a, 700, "r")
            E.text(c, "Why, if the record mostly measures luck?", X1 + 360, 730, 30, INK, a3 * show(t, q.at("k3", "Why, if it")), 600, "c")
        # ---- k4: luck has an address
        a4 = span(t, K4 - 0.2, q.total - 0.2)
        if a4 > 0:
            E.text(c, "Luck has an address", 540, 160, 64, INK, a4, 700, "c")
            heat(c, 90, 330, 420, D1, a4 * show(t, K4 + 0.6), "years 0–20")
            heat(c, 570, 330, 420, D2, a4 * show(t, q.at("k4", "stays good for years")), "years 20–40")
            E.text(c, "gold: more lucky breaks drifting there  ·  red: more setbacks", 540, 820, 24, MUTED, a4 * show(t, K4 + 0.6), 500, "c")
            al = a4 * show(t, K4 + 0.6); c.drawCircle(380, 852, 10, E.stroke(INK, 3, al))
            E.text(c, "the leader's seat (this history)", 400, 860, 24, MUTED, al, 500)
            a = a4 * show(t, q.at("k4", "Sitting in the same")) * (1 - show(t, K5 - 0.2))
            if a > 0:
                E.panel(c, X1, 300, 720, 380, a)
                E.text(c, "LUCKY BREAKS MET IN YEARS 20–40", X1 + 36, 360, 26, MUTED, a, 600)
                E.text(c, f"{TRK['best_lucky_next']:.2f}", X1 + 36, 470, 90, GOLD, a, 700); E.text(c, "the year-20 leader", X1 + 260, 456, 32, INK, a, 600)
                E.text(c, f"{TRK['everyone_lucky_next']:.2f}", X1 + 36, 600, 90, MUTED, a, 700); E.text(c, "everyone", X1 + 260, 586, 32, INK, a, 600)
        # ---- k5: move everyone to a fresh world
        a5 = show(t, K5 - 0.1, 0.5) * (1 - show(t, q.total - 0.7, 0.5))
        if a5 > 0:
            E.panel(c, X1, 170, 720, 700, a5)
            E.text(c, "GREW IN YEARS 20–40", X1 + 36, 230, 26, MUTED, a5, 600)
            c.drawRect(skia.Rect.MakeXYWH(X1 + 36, 262, 24, 24), E.fill(GOLD, a5)); E.text(c, "same seat", X1 + 72, 284, 26, INK, a5, 500)
            c.drawRect(skia.Rect.MakeXYWH(X1 + 260, 262, 24, 24), E.fill(TEAL, a5)); E.text(c, "fresh world", X1 + 296, 284, 26, INK, a5, 500)
            ff = show(t, q.at("k5", "The leader's edge"))
            rows = [("the year-20 leader", TRK["best_next_up"], TRK["moved_best_up"], q.at("k5", "Twenty-two percent")),
                    ("everyone", TRK["everyone_next_up"], TRK["moved_everyone_up"], q.at("k5", "about the same")),
                    ("the most talented person", TRK["top_next_up"], TRK["moved_top_up"], q.at("k5", "The most talented person still"))]
            for k, (lab, v1, v2, tt) in enumerate(rows):
                yy = 340 + k * 150
                E.text(c, lab, X1 + 36, yy + 10, 32, INK, a5, 600)
                hbar(c, X1 + 36, yy + 30, 480, 26, v1, GOLD, a5)
                a = a5 * ff
                hbar(c, X1 + 36, yy + 64, 480, 26, v2 * E.ramp(t, tt - 0.3, tt + 0.7), TEAL, a)
                E.text(c, pc(v1), X1 + 680, yy + 54, 34, GOLD, a5, 700, "r")
                E.text(c, pc(v2), X1 + 680, yy + 90, 34, TEAL, a * show(t, tt - 0.3), 700, "r")
            E.text(c, "The record was real.", X1 + 360, 790, 44, INK, a5 * show(t, q.at("k5", "The record was real")), 700, "c")
            E.text(c, "It just wasn't about the person.", X1 + 360, 840, 40, GOLD, a5 * show(t, q.at("k5", "It just wasn't")), 600, "c")
    return draw


# ------------------------------------------------------------------ 6. who should get support?
def support(q):
    tal = np.nonzero(T > 0.7)[0]; tal = tal[np.argsort(-T[tal])]
    P1, P2, P3 = q.s("p1"), q.s("p2"), q.s("p3")
    rows = [("no support", FUN["none"]["talented_up"], q.at("p2", "With no support")),
            ("top 10% by success", FUN["best10"]["talented_up"], q.at("p2", "Give the budget")),
            ("top 25% by success", FUN["best25"]["talented_up"], q.at("p2", "The top quarter")),
            ("a random 25%", FUN["random25"]["talented_up"], q.at("p2", "A random quarter")),
            ("everyone, equally", FUN["equal"]["talented_up"], q.at("p2", "Split equally"))]
    meta = RES["funding_meta"]
    rng = np.random.default_rng(4); lit_order = rng.permutation(len(tal))

    def draw(c, t):
        a0 = show(t, 0.3) * (1 - show(t, q.total - 0.9, 0.6))
        E.text(c, "Who should get the support?", 960, 140, 70, INK, a0, 700, "c")
        E.text(c, f"{meta['budget_per_round']:,} points every 5 years  ·  same budget, different rules",
               960, 196, 32, MUTED, a0 * show(t, q.at("p1", "Every five years")), 500, "c")
        # current policy -> how many of the talented end ahead
        cur = None
        for lab, v, t0 in rows:
            if t >= t0: cur = v
        ga = a0 * show(t, q.at("p1", "and count how many"))
        if ga > 0:
            E.text(c, f"the {len(tal)} most talented people (talent > 0.7)", 470, 300, 30, MUTED, ga, 600, "c")
            nlit = int(round((cur or 0) * len(tal)))
            for k, i in enumerate(tal):
                x, y = 140 + (k % 13) * 52, 350 + (k // 13) * 52
                lit = lit_order[k] < nlit
                E.blob(c, x, y, 20, talent_rgb(T[i]), ga * (1 if lit else 0.35), (0, -0.4))
                if lit: c.drawCircle(x, y, 23, E.stroke(GOLD, 3, ga))
            E.text(c, "gold ring = ended their career ahead", 470, 975, 28, GOLD, ga * show(t, P2), 500, "c")
        for k, (lab, v, t0) in enumerate(rows):
            a = a0 * show(t, t0); yy = 330 + k * 130
            if a <= 0: continue
            E.text(c, lab, 1000, yy, 34, INK, a, 600)
            col = CORAL if k == 0 else GOLD if k >= 3 else MUTED
            hbar(c, 1000, yy + 22, 640, 34, v * E.ramp(t, t0, t0 + 0.9), col, a)
            E.text(c, pc(v), 1820, yy + 52, 52, col, a, 700, "r")
        E.text(c, "Rewarding past success mostly rewards past luck.", 960, 1050, 40, INK, a0 * show(t, P3), 700, "c")
    return draw


# ------------------------------------------------------------------ 7. what this model can't tell you
def limits(q):
    L2, L3 = q.s("l2"), q.s("l3")
    chips = [("talent is fixed", "Talent here is fixed"), ("luck ignores talent", "luck is completely"),
             ("people learn", "Real people learn"), ("people choose where to stand", "choose where to stand"),
             ("people try again", "try again"), ("success only doubles or halves", "And real success")]
    b, s2 = SEN["base"], SEN["sd02"]

    def draw(c, t):
        a1 = span(t, 0.3, L2 - 0.2)
        E.text(c, "What this model can't tell you", 960, 220, 76, INK, a1, 700, "c")
        for k, (s, cue) in enumerate(chips):
            a = a1 * show(t, q.at("l1", cue), 0.35)
            w = E.font(38, 600).measureText(s) + 64
            x = 960 - w / 2; y = 330 + k * 100
            if a > 0: chip(c, s, x, y, a, 38, INK if k < 2 else TEAL if k < 5 else INK)
        a2 = span(t, L2 - 0.1, L3 - 0.2)
        if a2 > 0:
            E.text(c, "Same people, talent twice as unequal", 960, 200, 64, INK, a2, 700, "c")
            E.text(c, f"{RES['sensitivity_meta']['sd02']['histories']:,} histories per setting", 960, 252, 28, MUTED, a2, 500, "c")
            E.panel(c, 330, 320, 1260, 500, a2)
            E.text(c, "talent spread (std. dev.)", 380, 400, 30, MUTED, a2, 600)
            E.text(c, f"{RES['sensitivity_meta']['base']['talent_sd']}", 1040, 395, 40, INK, a2, 700, "c")
            E.text(c, f"{RES['sensitivity_meta']['sd02']['talent_sd']}", 1380, 395, 40, GOLD, a2, 700, "c")
            E.text(c, "as in the paper", 1040, 428, 22, MUTED, a2, 500, "c"); E.text(c, "twice as unequal", 1380, 428, 22, MUTED, a2, 500, "c")
            E.line(c, 380, 456, 1540, 456, LINE, 1.5, a2)
            a = a2 * show(t, q.at("l2", "the typical winner gets"))
            E.text(c, "typical winner is more", 380, 540, 32, INK, a, 600); E.text(c, "talented than", 380, 582, 32, INK, a, 600)
            E.text(c, pc(b["winner_pctile"]), 1040, 575, 64, INK, a, 700, "c"); E.text(c, pc(s2["winner_pctile"]), 1380, 575, 64, GOLD, a, 700, "c")
            a = a2 * show(t, q.at("l2", "But talent still"))
            E.text(c, "talent explains", 380, 720, 32, INK, a, 600)
            E.text(c, pc(b["r2_talent"], 1), 1040, 735, 64, INK, a, 700, "c"); E.text(c, pc(s2["r2_talent"], 1), 1380, 735, 64, GOLD, a, 700, "c")
        a3 = show(t, L3 - 0.1, 0.5) * (1 - show(t, q.total - 0.9, 0.5))
        E.text(c, "Not proof that success is luck.", 960, 300, 72, INK, a3, 700, "c")
        E.text(c, "Not career advice.", 960, 390, 56, MUTED, a3 * show(t, q.at("l3", "and it isn't career")), 600, "c")
        a = a3 * show(t, q.at("l3", "Even in a world"))
        E.text(c, "Even in a world built to reward talent,", 960, 560, 50, INK, a, 500, "c")
        E.text(c, "a few random breaks can outweigh a lot of it.", 960, 640, 58, GOLD, a * show(t, q.at("l3", "a few random breaks")), 700, "c")
        E.text(c, "And a track record can't tell you which one you're looking at.", 960, 760, 42, INK, a * show(t, q.at("l3", "and a track record")), 500, "c")
    return draw


# ------------------------------------------------------------------ 8. close
def outro(q):
    F = Field(T, P, TR, 490, 70, 940)
    tp = q.at("o1", "If you want to see")

    def draw(c, t):
        F.update(t, 80 * E.ramp(t, 0, q.total - 2, lambda u: u)); F.draw(c, 0.14); F.draw_events(c, 0.10)
        a1 = span(t, 0.3, tp - 0.1)
        E.text(c, "Across 10,000 lives, talent shows.", 960, 460, 76, INK, a1, 700, "c")
        E.text(c, "In any one life, it's mostly the breaks.", 960, 580, 76, GOLD, a1 * show(t, q.at("o1", "In any one life")), 700, "c")
        a = show(t, tp)
        if a > 0:
            E.panel(c, 150, 250, 900, 420, a)
            E.text(c, "PREVIOUS EXPERIMENT", 200, 320, 26, MUTED, a, 600)
            E.text(c, "Why the Rich Get Richer,", 200, 410, 60, GOLD, a, 700)
            E.text(c, "Even in a Perfectly Fair Game", 200, 482, 54, GOLD, a, 700)
            E.text(c, "a fair game of pure coin flips", 200, 570, 34, INK, a, 500)
            a2 = show(t, q.at("o1", "Everything we ran"))
            E.panel(c, 1110, 250, 660, 420, a2)
            E.text(c, "WHAT WE RAN", 1160, 320, 26, MUTED, a2, 600)
            E.text(c, "Every experiment", 1160, 410, 60, INK, a2, 700)
            E.text(c, "is listed", 1160, 482, 54, INK, a2, 700)
            E.text(c, "in the description.", 1160, 554, 54, INK, a2, 700)
            E.text(c, CHANNEL, 960, 820, 44, INK, a, 700, "c")
            E.text(c, "We don't argue. We simulate.", 960, 872, 30, MUTED, a, 500, "c")
    return draw
