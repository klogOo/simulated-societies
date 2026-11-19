"""Scenes of video 001. Each factory takes the scene's cue sheet `q` and returns draw(canvas, t),
called once per frame in order. Every number on screen is read live from the simulation or from
results.json -- nothing is typed in by hand."""
import json, math
from pathlib import Path
import numpy as np
from engine import core as E
from engine.core import INK, MUTED, TEAL, GOLD, CORAL, SLATE, LINE, lerp
from engine.world import World, rounds_at, hud

RES = json.loads((Path(__file__).parent / "results.json").read_text())
CHANNEL = "TEN THOUSAND WORLDS"

SPEC = {
    "hook":   ["h1", "h2", ("gap", "lapse", 11.0), "h3", ("gap", "title", 5.0)],
    "rules":  ["r1", "r2", "r3", ("gap", "out", 0.6)],
    "run":    ["u1", ("gap", "g100", 5.0), "u2", ("gap", "g1k", 5.5), "u3", ("gap", "g10k", 6.5), "u4",
               ("gap", "g100k", 7.5), "u5"],
    "why":    ["w1", "w2", "w3", ("gap", "out", 0.6)],
    "solo":   ["s1", "s2", "s3", "s4", ("gap", "out", 0.6)],
    "worlds": ["m1", ("gap", "lapse", 5.5), "m2", "m3", ("gap", "out", 0.6)],
    "talent": ["k1", ("gap", "lapse", 6.0), "k2", "k3", ("gap", "out", 0.6)],
    "tax":    ["t1", ("gap", "lapse", 5.5), "t2", ("gap", "dial", 4.5), "t3", "t4", ("gap", "out", 0.6)],
    "outro":  ["o1", "o2", "o3", ("gap", "end", 15.0)],
}


def show(t, t0, d=0.5): return E.ramp(t, t0, t0 + d)
def span(t, t0, t1, f=0.4): return E.window(t, t0, t1, f)
def steps(t, t0, t1, n): return 0 if t < t0 else min(n, int(n * (t - t0) / max(1e-6, t1 - t0)) + 1)


def own_bar(c, x, y, w, h, top, bottom, a):
    E.rrect(c, x, y, w, h, 8, E.fill(LINE, a))
    for x0, frac, rgb in ((x, top, GOLD), (x + top * w, 1 - top - bottom, TEAL), (x + (1 - bottom) * w, bottom, CORAL)):
        if frac * w > 0.5: c.drawRect(E.skia.Rect.MakeXYWH(x0, y, frac * w, h), E.fill(rgb, a))


# ------------------------------------------------------------------ 1. hook
def hook(q):
    wd = World(1000, seed=1, cx=960, cy=560, R=440)
    L0, L1, T0 = q.s("lapse"), q.e("lapse"), q.s("title")
    keys = [(q.at("h1", "They're going to trade"), 0), (L0, 12), (L1 - 1.2, 100_000)]

    def draw(c, t):
        wd.run_to(rounds_at(t, keys)); wd.relax(t=t)
        wd.draw(c, 1 - 0.88 * show(t, T0 - 0.3, 0.8))
        a = span(t, 0.6, L0 + 0.6)
        E.text(c, "1,000 people", 110, 150, 64, INK, a, 700)
        E.text(c, "$100 each", 110, 212, 44, TEAL, a, 500)
        E.text(c, "every trade: a fair coin flip", 110, 262, 30, MUTED, a * show(t, q.at("h1", "Every trade is a fair")), 500)
        a = span(t, q.s("h2") - 0.1, L0 + 1.0, 0.25)                      # play button
        if a > 0:
            E.rrect(c, 850, 960, 220, 76, 38, E.fill(TEAL, a))
            p = E.skia.Path(); p.moveTo(892, 980); p.lineTo(892, 1016); p.lineTo(922, 998); p.close()
            c.drawPath(p, E.fill(E.BG, a)); E.text(c, "PLAY", 940, 1012, 38, E.BG, a, 700)
        a = span(t, L0 + 0.3, T0 - 0.2)
        E.text(c, "ROUND", 1810, 110, 24, MUTED, a, 600, "r")
        E.text(c, f"{wd.round:,}", 1810, 172, 60, INK, a, 700, "r")
        a = span(t, q.s("h3") + 0.2, T0 - 0.2)
        if a > 0:
            gx, gy, gr = wd.top_xy_r()
            E.line(c, gx + gr * 0.74, gy - gr * 0.74, 1400, 262, INK, 2.5, a * 0.7)
            E.text(c, "ONE PERSON", 1410, 262, 26, MUTED, a, 600)
            E.text(c, E.pct(wd.st["richest"]), 1410, 370, 120, GOLD, a, 700)
            E.text(c, "of all the money", 1410, 420, 38, INK, a, 500)
        a = span(t, q.at("h3", "Half the population"), T0 - 0.2)
        E.text(c, "POOREST 500 PEOPLE", 110, 870, 26, MUTED, a, 600)
        E.text(c, E.money(wd.st["bottom50"] * 100_000), 110, 955, 90, CORAL, a, 700)
        E.text(c, "between all of them", 110, 1002, 32, INK, a, 500)
        a = show(t, T0 + 0.4, 0.7)
        E.text(c, f"{CHANNEL}  ·  EXPERIMENT 001", 960, 420, 28, MUTED, a, 600, "c")
        E.text(c, "The Fair Game", 960, 560, 124, INK, a, 700, "c")
        E.text(c, "That Only One Person Wins", 960, 680, 84, GOLD, a, 700, "c")
    return draw


# ------------------------------------------------------------------ 2. rules
def rules(q):
    rng = np.random.default_rng(5)
    tr = [dict(ts=q.at("r1", "each of them puts"), tf=q.at("r1", "Then they flip"), tw=q.at("r1", "Winner takes") + 0.6,
               win=1, a=100.0, b=50.0, num=False),
          dict(ts=q.at("r2", "they each put in ten") - 0.4, tf=q.at("r2", "The coin treats"), tw=q.e("r2") - 0.9,
               win=0, a=100.0, b=50.0, num=True)]
    a, b, t = 110.0, 40.0, q.s("r3") + 1.4
    while t < q.total - 2.0:                                             # they keep trading in the background
        w = int(rng.random() < 0.5); tr.append(dict(ts=t, tf=t + 0.45, tw=t + 1.0, win=w, a=a, b=b, num=True))
        s = 0.2 * min(a, b); a, b = (a + s, b - s) if w == 0 else (a - s, b + s); t += 1.8
    for x in tr:
        x["s"] = 0.2 * min(x["a"], x["b"])
        x["a2"], x["b2"] = (x["a"] + x["s"], x["b"] - x["s"]) if x["win"] == 0 else (x["a"] - x["s"], x["b"] + x["s"])
    R3 = q.s("r3")
    caps = [(0.4, "Two people meet at random."), (q.at("r1", "They look at whoever"), "Find whoever has less."),
            (tr[0]["ts"], "Each puts in 20% of that amount."), (tr[0]["tf"], "Flip a fair coin."),
            (tr[0]["tw"], "Winner takes the pot."), (q.s("r2"), "$100 meets $50. Each puts in $10."),
            (tr[1]["tf"], "Same coin for both: 50 / 50."), (R3 - 0.3, None)]
    bullets = [("No one has an edge", 400), ("Money is never created or destroyed", 960), ("It only moves", 1560)]

    def amounts(t):
        cur = (100.0, 50.0)
        for x in tr:
            if t < x["ts"] - 0.7: break
            j = E.ramp(t, x["ts"] - 0.7, x["ts"] - 0.25); k = E.ramp(t, x["tw"], x["tw"] + 0.5)
            cur = (lerp(lerp(cur[0], x["a"], j), x["a2"], k), lerp(lerp(cur[1], x["b"], j), x["b2"], k))
        return cur

    def draw(c, t):
        g = E.ramp(t, R3 - 0.2, R3 + 0.9); k = lerp(1, 0.5, g)
        enter = E.ease_out(t / 1.0)
        ax, bx, y = lerp(-250, lerp(600, 800, g), enter), lerp(2170, lerp(1320, 1120, g), enter), lerp(620, 850, g)
        ma, mb = amounts(t)
        ra, rb = 125 * math.sqrt(ma / 100) * k, 125 * math.sqrt(mb / 100) * k
        cx, ty = 960, y + 30 * k
        cur = next((x for x in tr if x["ts"] <= t <= x["tw"] + 0.5), None)
        flipping = cur is not None and cur["tf"] <= t <= cur["tw"]
        rgb = E.wealth_rgb(np.array([ma, mb]))
        E.blob(c, ax, y, ra, rgb[0], 1, (0.7, -0.7) if flipping else (1, 0))
        E.blob(c, bx, y, rb, rgb[1], 1, (-0.7, -0.7) if flipping else (-1, 0))
        nv = show(t, q.s("r2") - 0.2)
        E.text(c, E.money(ma), ax, y - ra - 26 * k, 60 * k, INK, nv, 700, "c")
        E.text(c, E.money(mb), bx, y - rb - 26 * k, 60 * k, INK, nv, 700, "c")
        a = span(t, q.at("r1", "They look at whoever"), tr[0]["ts"] + 1.2, 0.3)       # "has less" tag
        if a > 0:
            c.drawCircle(bx, y, rb + 16, E.stroke(CORAL, 4, a)); E.text(c, "has less", bx, y + rb + 64, 36, CORAL, a, 600, "c")
        if cur:
            pin, pout = E.ramp(t, cur["ts"], cur["ts"] + 0.45), E.ramp(t, cur["tw"], cur["tw"] + 0.45)
            wx = ax if cur["win"] == 0 else bx
            for sx, off in ((ax, -40 * max(k, 0.8)), (bx, 40 * max(k, 0.8))):
                px = lerp(lerp(sx, cx + off, pin), wx, pout); py = lerp(lerp(y, ty + 150 * k, pin), y, pout)
                al = min(1, pin * 4) * (1 - pout ** 3)
                kc = max(k, 0.8)
                c.drawCircle(px, py, 36 * kc, E.fill(GOLD, al)); c.drawCircle(px, py, 36 * kc, E.stroke((180, 130, 30), 3 * kc, al))
                E.text(c, E.money(cur["s"]) if cur["num"] else "20%", px, py + 8 * kc, 23 * kc, E.BG, al, 700, "c")
            ca = span(t, cur["tf"], cur["tw"] + 0.25, 0.15)                              # the coin
            if ca > 0:
                rw = 50 * k * abs(math.cos((t - cur["tf"]) * 13)); cy = y - 250 * k - 30 * k * math.sin((t - cur["tf"]) * 3)
                c.drawOval(E.skia.Rect.MakeLTRB(cx - rw, cy - 50 * k, cx + rw, cy + 50 * k), E.fill(GOLD, ca))
                c.drawOval(E.skia.Rect.MakeLTRB(cx - rw, cy - 50 * k, cx + rw, cy + 50 * k), E.stroke((180, 130, 30), 4 * k, ca))
            if cur is tr[1]:
                a5 = span(t, cur["tf"], cur["tw"], 0.25)
                E.text(c, "50%", ax, y + ra + 80, 54, TEAL, a5, 700, "c"); E.text(c, "50%", bx, y + rb + 80, 54, TEAL, a5, 700, "c")
        for i, (t0, s) in enumerate(caps[:-1]):
            E.text(c, s, 960, 170, 52, INK, span(t, t0, caps[i + 1][0], 0.25), 600, "c")
        E.text(c, "Studied by physicists and economists since the early 2000s", 960, 190, 32, MUTED, show(t, R3 + 0.3), 500, "c")
        E.text(c, "The Yard Sale Model", 960, 320, 110, INK, show(t, q.at("r3", "It's called")), 700, "c")
        for s, x in bullets:
            a = show(t, q.at("r3", s)); w = E.font(34, 600).measureText(s) + 90
            if a > 0:
                E.panel(c, x - w / 2, 420, w, 76, a, 38); c.drawCircle(x - w / 2 + 36, 458, 9, E.fill(TEAL, a))
                E.text(c, s, x - w / 2 + 60, 470, 34, INK, a, 600)
    return draw


# ------------------------------------------------------------------ 3. run
def run(q):
    wd = World(1000, seed=1, cx=640, cy=530, R=420)
    keys = [(1.2, 0), (q.at("u1", "After ten rounds") + 1.0, 10), (q.s("g100"), 10), (q.e("g100") - 0.4, 100),
            (q.s("g1k"), 100), (q.e("g1k") - 0.4, 1000), (q.s("g10k"), 1000), (q.e("g10k") - 0.4, 10_000),
            (q.at("u4", "Keep going"), 10_000), (q.e("g100k") - 0.8, 100_000)]

    def draw(c, t):
        wd.run_to(rounds_at(t, keys)); wd.relax(t=t); wd.draw(c)
        hud(c, wd, 1250, 240, show(t, 0.4))
        x0, x1, y = 220, 1060, 1030; p = math.log10(max(wd.round, 1)) / 5
        E.line(c, x0, y, x1, y, LINE, 4); E.line(c, x0, y, lerp(x0, x1, p), y, TEAL, 4)
        for k, lab in enumerate(["1", "10", "100", "1,000", "10,000", "100,000"]):
            xx = lerp(x0, x1, k / 5); c.drawCircle(xx, y, 7, E.fill(TEAL if p >= k / 5 - 1e-6 else LINE))
            E.text(c, lab, xx, y - 20, 22, MUTED, 1, 500, "c")
        E.text(c, "rounds", x1 + 26, y + 8, 22, MUTED)
        E.text(c, "Every trade was a fair coin flip.", 1530, 880, 34, INK, show(t, q.s("u5") + 0.2), 600, "c")
    return draw


# ------------------------------------------------------------------ 4. why
def why(q):
    S1, W2, W3 = q.s("w2") - 0.5, q.s("w2"), q.s("w3")
    base, sc = 800, 3.3
    bars = [(560, 100, q.at("w1", "Take a hundred"), TEAL), (880, 120, q.at("w1", "Win twenty percent"), GOLD),
            (1200, 96, q.at("w1", "Now lose twenty"), CORAL)]
    tp = q.at("w3", "Give the poor")

    def draw(c, t):
        a1 = 1 - show(t, S1, 0.4)
        if a1 > 0:
            E.line(c, 400, base, 1520, base, LINE, 3, a1)
            prev = 100
            for i, (x, v, t0, rgb) in enumerate(bars):
                g = E.ramp(t, t0, t0 + 0.8)
                if g > 0:
                    val = lerp(prev, v, g) if i else v; h = val * sc * (g if i == 0 else 1); al = a1 * min(1, g * 4)
                    E.rrect(c, x - 100, base - h, 200, h, 14, E.fill(rgb, al))
                    E.text(c, E.money(round(val)), x, base - h + 82, 64, E.BG, al, 700, "c")
                prev = v
            for xm, s1, s2, rgb, t0 in ((720, "+20%", "+$20", TEAL, bars[1][2]), (1040, "−20%", "−$24", CORAL, bars[2][2])):
                a = a1 * show(t, t0)
                E.arrow(c, xm - 70, base + 50, xm + 70, base + 50, rgb, 5, a)
                E.text(c, s1, xm, base + 120, 52, rgb, a, 700, "c"); E.text(c, s2, xm, base + 168, 34, MUTED, a, 500, "c")
            a = a1 * show(t, q.at("w1", "You are not back")); yy = base - 100 * sc
            for xs in range(430, 1500, 34): E.line(c, xs, yy, xs + 16, yy, INK, 2.5, a * 0.8)
            E.text(c, "$100", 1510, yy + 10, 30, INK, a, 600)
            E.text(c, "$4 short", 1330, base - 98 * sc + 56, 40, CORAL, a1 * show(t, q.at("w1", "You're at ninety-six")), 700)
            E.text(c, "+20% then −20% doesn't bring you back.", 960, 170, 60, INK, a1 * show(t, q.at("w1", "A win and a loss")), 700, "c")
            E.text(c, "The loss is taken from a bigger pile.", 960, 240, 40, MUTED, a1 * show(t, q.at("w1", "The loss is a slice")), 500, "c")
        a2 = show(t, W2 - 0.1, 0.5)
        if a2 > 0:
            kr = steps(t, W3 + 0.5, tp - 0.5, 10); kp = steps(t, tp + 0.3, q.e("w3") - 1.6, 10)
            rich, poor = 5000 - 10 * kr, 50 * 0.8 ** kp
            sw0, sw1 = q.at("w2", "every flip is a huge swing"), q.at("w2", "For the richer")
            vis = poor * (1 + 0.2 * math.sin((t - sw0) * 5) * span(t, sw0, sw1 + 1.0))
            px, py, rx, ry = 430, 540, 1400, 520
            pr, rr = 34 * math.sqrt(vis / 50), 300 * math.sqrt(rich / 5000)
            rgb = E.wealth_rgb(np.array([poor, rich]))
            E.blob(c, px, py, pr, rgb[0], a2, (1, 0)); E.blob(c, rx, ry, rr, rgb[1], a2, (-1, 0))
            E.text(c, E.money(poor), px, py - 80, 64, INK, a2, 700, "c")
            E.text(c, E.money(rich), rx, ry - 300 - 28, 64, INK, a2, 700, "c")
            a = a2 * span(t, q.at("w2", "The stake is always"), W3 - 0.2)
            if a > 0:
                c.drawCircle(820, 540, 46, E.fill(GOLD, a)); E.text(c, "$10", 820, 552, 34, E.BG, a, 700, "c")
                E.text(c, "the stake", 820, 462, 30, MUTED, a, 600, "c"); E.text(c, "20% of the poorer side", 820, 640, 28, MUTED, a, 500, "c")
            a = a2 * span(t, q.at("w2", "So for the poorer"), W3 - 0.2)
            E.text(c, "±20%", px, 930, 90, CORAL, a, 700, "c"); E.text(c, "of everything they have", px, 985, 30, MUTED, a, 500, "c")
            a = a2 * span(t, sw1, W3 - 0.2)
            E.text(c, "±0.2%", rx, 930, 90, TEAL, a, 700, "c"); E.text(c, "pocket change", rx, 985, 30, MUTED, a, 500, "c")
            a = show(t, W3)
            E.text(c, "Ten losses in a row", 870, 180, 64, INK, a, 700, "c")
            a = show(t, W3 + 0.5)
            E.text(c, f"−{(5000 - rich) / 50:.0f}%", rx, 930, 90, TEAL, a, 700, "c")
            E.text(c, f"after {kr} losses", rx, 985, 30, MUTED, a, 500, "c")
            a = show(t, tp + 0.3)
            E.text(c, f"−{(1 - poor / 50) * 100:.0f}%", px, 930, 90, CORAL, a, 700, "c")
            E.text(c, f"after {kp} losses", px, 985, 30, MUTED, a, 500, "c")
    return draw


# ------------------------------------------------------------------ 5. solo
def solo(q):
    k = np.random.default_rng(2).binomial(100, 0.5, 1_000_000)             # same draw as experiments.py
    final = 100 * 1.2 ** k * 0.8 ** (100 - k)
    step_ = math.log10(1.5); c50 = 2 + 50 * math.log10(1.2) + 50 * math.log10(0.8)   # one bar per number of wins
    edges = c50 + (np.arange(-12, 18) - 0.5) * step_
    hist, _ = np.histogram(np.clip(np.log10(final), edges[0] + 1e-6, edges[-1] - 1e-6), edges); hist = hist / hist.max()
    st = np.random.default_rng(22).random((260, 100)) < 0.5
    paths = np.concatenate([np.full((260, 1), 100.0), 100 * np.cumprod(np.where(st, 1.2, 0.8), 1)], 1)
    X0, X1, Y0, Y1 = 210, 1250, 900, 220
    def Y(v): return Y0 - (np.log10(np.clip(v, 0.1, 1e4)) + 1) / 5 * (Y0 - Y1)
    PX = X0 + np.arange(101) / 100 * (X1 - X0); PY = Y(paths)
    med = Y(100 * 0.96 ** (np.arange(101) / 2))
    t1, tm = q.at("s1", "Take one player"), q.at("s1", "Then repeat")
    S2, S3, S4 = q.s("s2"), q.s("s3"), q.s("s4")
    R = RES["solo"]; cache = {}

    def draw(c, t):
        ca = 1 - 0.85 * show(t, S4 - 0.2)
        for v, lab in ((0.1, "10¢"), (1, "$1"), (10, "$10"), (100, "$100"), (1000, "$1,000"), (10000, "$10,000")):
            E.line(c, X0, Y(v), X1, Y(v), LINE, 1.5, ca); E.text(c, lab, X0 - 18, Y(v) + 9, 26, MUTED, ca, 500, "r")
        for n in (0, 25, 50, 75, 100): E.text(c, str(n), PX[n], Y0 + 42, 26, MUTED, ca, 500, "c")
        E.text(c, "number of bets", (X0 + X1) / 2, Y0 + 92, 26, MUTED, ca, 500, "c")
        E.text(c, "One player. 100 fair bets of ±20% each.", X0, 150, 46, INK, ca, 700)
        n_run = 1 if t < tm else int(min(1e6, 10 ** (6 * E.clamp((t - tm) / max(0.5, q.e("s1") - tm - 0.3)))))
        E.text(c, f"players simulated: {n_run:,}", 1810, 150, 32, MUTED, ca * show(t, t1), 500, "r")
        if t > tm + 3.8:                                                    # all revealed -> one cached path
            if "p" not in cache:
                p = E.skia.Path()
                for i in range(1, 260):
                    p.moveTo(PX[0], PY[i, 0])
                    for j in range(1, 101): p.lineTo(PX[j], PY[i, j])
                cache["p"] = p
            c.drawPath(cache["p"], E.stroke(TEAL, 1.5, 0.16 * ca))
        else:
            for i in range(1, 260):
                m = int(100 * E.clamp((t - tm - i / 260 * 2.6) / 1.0))
                if m > 0: E.polyline(c, list(zip(PX[: m + 1], PY[i, : m + 1])), TEAL, 1.5, 0.16)
        m = int(100 * E.clamp((t - t1) / 3.0))
        if m > 0: E.polyline(c, list(zip(PX[: m + 1], PY[0, : m + 1])), INK, 3.5, ca * lerp(1, 0.55, show(t, tm + 1)))
        a = ca * show(t, q.at("s2", "The average result"))
        for xs in range(X0, X1, 30): E.line(c, xs, Y(100), xs + 15, Y(100), INK, 3, a)
        E.text(c, "average: $100", X1 - 12, Y(100) - 16, 32, INK, a, 700, "r")
        a = ca * show(t, q.at("s2", "a handful of enormous"))
        E.text(c, "a few huge winners", 900, 285, 30, GOLD, a, 600, "r"); E.arrow(c, 915, 277, 1010, 300, GOLD, 3, a, 12)
        gm = int(100 * show(t, q.at("s2", "The typical one"), 1.4))
        if gm > 0: E.polyline(c, list(zip(PX[: gm + 1], med[: gm + 1])), GOLD, 5, ca)
        g = E.ramp(t, S2 - 0.3, S2 + 1.0)                                   # histogram of all 1,000,000 endings
        if g > 0:
            bh = step_ / 5 * (Y0 - Y1)
            for j in range(len(hist)):
                mid = (edges[j] + edges[j + 1]) / 2; rgb = CORAL if mid < 2 else TEAL
                yb = Y0 - (mid + 1) / 5 * (Y0 - Y1)
                if Y1 - 4 <= yb <= Y0 + 4: c.drawRect(E.skia.Rect.MakeXYWH(1310, yb - bh / 2 + 1.5, hist[j] * 240 * g, bh - 3), E.fill(rgb, ca))
            E.text(c, "where all 1,000,000 ended up", 1310, Y1 - 24, 26, MUTED, ca * g, 500)
        a = ca * show(t, q.at("s2", "The typical one") + 0.4)
        E.text(c, "typical player ends with", 1590, 560, 28, MUTED, a, 600); E.text(c, E.money(R["median"]), 1590, 650, 84, GOLD, a, 700)
        a = ca * show(t, q.at("s2", "Eighty-six percent"))
        E.text(c, E.pct(R["lost"]), 1590, 790, 96, CORAL, a, 700)
        E.text(c, "end with less than", 1590, 836, 28, MUTED, a, 500); E.text(c, "they started with", 1590, 870, 28, MUTED, a, 500)
        a = span(t, S3, S4 - 0.1)                                           # 56 wins out of 100
        if a > 0:
            E.rrect(c, 330, 290, 860, 470, 22, E.fill(E.BG, a)); E.panel(c, 330, 290, 860, 470, a)
            n = steps(t, S3 + 0.3, S3 + 2.6, R["wins_needed"])
            for i in range(100):
                xx, yy = 400 + (i % 10) * 38, 350 + (i // 10) * 38
                c.drawCircle(xx, yy, 14, E.fill(GOLD, a) if i < n else E.stroke(MUTED, 2, a * 0.6))
            E.text(c, str(n), 820, 470, 130, GOLD, a, 700)
            E.text(c, "wins out of 100", 820, 530, 36, INK, a, 600); E.text(c, "just to break even", 820, 576, 32, MUTED, a, 500)
            E.text(c, f"chance of that: {E.pct(1 - R['lost'])}", 820, 680, 44, CORAL, a * show(t, q.at("s3", "A fair coin rarely")), 700)
        E.text(c, "Fair on average.", 960, 400, 104, INK, show(t, q.at("s4", "The game is fair")), 700, "c")
        E.text(c, "Bad for almost everybody.", 960, 530, 104, CORAL, show(t, q.at("s4", "and bad for")), 700, "c")
        E.text(c, "And the poorer partner is always the one playing it.", 960, 660, 44, INK, show(t, q.at("s4", "And in every trade")), 500, "c")
        a = show(t, q.at("s4", "So money drifts"))
        E.text(c, "So money drifts uphill.", 930, 790, 64, GOLD, a, 700, "c"); E.arrow(c, 1310, 800, 1380, 740, GOLD, 6, a, 20)
    return draw


# ------------------------------------------------------------------ 6. ten thousand worlds
def worlds(q):
    R = RES["worlds"]; wins = np.array(R["wins_by_seat"])
    ws = [World(100, seed=1000 + i, cx=242 + 205 * (i % 8), cy=335 + 200 * (i // 8), R=86, hues=True) for i in range(32)]
    tb = q.at("m1", "So we built")
    keys = [(q.at("m1", "Same rules"), 0), (q.e("m1") + 0.3, 15), (q.e("lapse") - 0.5, 3000)]
    tc, M3 = q.at("m2", "Each of the hundred seats"), q.s("m3")
    cards = [(200, "AFTER 10 ROUNDS", R["r10"]["ahead"], "of eventual winners", "were already ahead", q.at("m3", "After just ten")),
             (720, "AFTER 200 ROUNDS", R["r200"]["top_half"], "were already", "in the top half", q.at("m3", "After two hundred")),
             (1240, "AFTER 200 ROUNDS", R["r200"]["top10"], "were already", "in the top ten", q.at("m3", "and usually"))]

    def draw(c, t):
        r = rounds_at(t, keys)
        chart, cd = span(t, tc - 0.2, M3 - 0.2), show(t, M3)
        ga = 1 - 0.88 * max(chart, cd); rings = show(t, q.at("m2", "somebody ended up on top"))
        a = span(t, 0.3, tb + 0.2)                                           # "did they earn it?"
        if a > 0:
            E.blob(c, 960, 600, 190, GOLD, a, (0, -0.4)); E.text(c, "Did they earn it?", 960, 300, 84, INK, a, 700, "c")
        for i, wd in enumerate(ws):
            s = E.back((t - tb - i * 0.06) / 0.5) if t > tb + i * 0.06 else 0
            if s <= 0: continue
            wd.run_to(r); wd.relax(t=t); wd.draw(c, ga, scale=s)
            if rings > 0:
                x, y, rr = wd.top_xy_r(); c.drawCircle(x, y, rr + 5, E.stroke(INK, 3, rings * ga))
        a = show(t, tb)
        nw = 32 if t < q.s("lapse") else int(32 * (10_000 / 32) ** E.clamp((t - q.s("lapse")) / 3.6))
        E.text(c, f"{nw:,} worlds", 156, 128, 68, INK, a, 700)
        E.text(c, "100 people each  ·  same rules  ·  different coin flips  ·  showing 32", 156, 180, 30, MUTED, a, 500)
        E.text(c, f"round {ws[0].round:,}", 1763, 128, 44, INK, a, 600, "r")
        E.text(c, f"winner holds {E.pct(R['winner_share'])} on average", 1763, 180, 30, GOLD, a * rings, 600, "r")
        if chart > 0:
            E.panel(c, 240, 270, 1440, 620, chart)
            E.text(c, "How often each seat won, across 10,000 worlds", 300, 345, 42, INK, chart, 700)
            g = E.ramp(t, tc, tc + 1.2)
            for i in range(100):
                h = wins[i] * 2.6 * g
                c.drawRect(E.skia.Rect.MakeXYWH(310 + i * 13.0, 790 - h, 9.5, h), E.fill(ws[0].hue[i], chart))
            yy = 790 - 100 * 2.6
            for xs in range(300, 1620, 30): E.line(c, xs, yy, xs + 15, yy, INK, 2.5, chart * g)
            E.text(c, "average: 100 wins = 1%", 1620, yy - 16, 30, INK, chart * g, 600, "r")
            E.text(c, "seat 1", 310, 832, 24, MUTED, chart, 500); E.text(c, "seat 100", 1606, 832, 24, MUTED, chart, 500, "r")
            E.text(c, "No seat is special. Who wins is pure luck.", 960, 850, 38, GOLD, chart * show(t, q.at("m2", "Who wins is pure")), 700, "c")
        E.text(c, "Early luck sticks.", 960, 330, 76, INK, show(t, q.at("m3", "And early luck")), 700, "c")
        for x, lab, v, d1, d2, t0 in cards:
            a = show(t, t0, 0.4)
            if a > 0:
                E.panel(c, x, 400, 480, 340, a); E.text(c, lab, x + 40, 462, 26, MUTED, a, 600)
                E.text(c, E.pct(v), x + 40, 600, 130, GOLD, a, 700)
                E.text(c, d1, x + 40, 660, 32, INK, a, 500); E.text(c, d2, x + 40, 702, 32, INK, a, 500)
        E.text(c, "A few lucky flips at the start. The arithmetic does the rest.", 960, 840, 46, INK,
               show(t, q.at("m3", "A few lucky flips")), 600, "c")
    return draw


# ------------------------------------------------------------------ 7. talent
def talent(q):
    R = RES["talent"]
    skill = np.zeros(1000); skill[:100] = 0.05
    wd = World(1000, seed=100, cx=640, cy=505, R=370, skill=skill)       # seed 100 = first run of experiments.py
    mask = skill > 0
    tr, K2, K3 = q.at("k1", "Let's give a hundred"), q.s("k2"), q.s("k3")
    keys = [(q.e("k1") - 0.8, 0), (q.s("lapse"), 6), (q.e("lapse") - 0.5, 10_000)]
    rows = [(q.at("k2", "In ninety-eight"), R["skilled_winner"], "of runs: the richest", "person was skilled"),
            (q.at("k2", "together the skilled"), R["skilled_share"], "of all the money ended", "up with the skilled")]

    def draw(c, t):
        wd.run_to(rounds_at(t, keys)); wd.relax(t=t)
        wd.draw(c, ring_mask=mask if t > tr else None)
        a = show(t, tr)
        c.drawCircle(140, 50, 13, E.stroke(INK, 4, a)); E.text(c, "100 skilled players: they win 55% of their flips", 170, 62, 34, INK, a, 600)
        E.text(c, f"round {wd.round:,}", 1810, 64, 40, INK, show(t, q.e("k1") - 0.8), 600, "r")
        a = span(t, K2, K3 - 0.2)
        if a > 0:
            E.panel(c, 1250, 250, 560, 360, a); E.text(c, "200 RUNS OF THIS WORLD", 1286, 312, 24, MUTED, a, 600)
            for i, (t0, v, d1, d2) in enumerate(rows):
                al = a * show(t, t0); yy = 420 + i * 130
                E.text(c, E.pct(v), 1286, yy, 84, GOLD, al, 700)
                E.text(c, d1, 1480, yy - 40, 28, INK, al, 500); E.text(c, d2, 1480, yy - 4, 28, INK, al, 500)
        a = show(t, K3)
        if a > 0:
            E.panel(c, 1250, 180, 560, 700, a); E.text(c, "THE 100 SKILLED PLAYERS", 1286, 240, 24, MUTED, a, 600)
            sw = np.sort(wd.w[:100])[::-1]
            for i, v in enumerate(sw):
                rgb = GOLD if v >= 100 else CORAL if v >= 1 else (112, 62, 74)
                c.drawCircle(1318 + (i % 10) * 47, 300 + (i // 10) * 47, 17, E.fill(rgb, a))
            for yy, rgb, t0, s in ((788, CORAL, q.at("k3", "Eighty percent"), f"{E.pct(R['skilled_below'])} finished below their $100"),
                                   (832, (112, 62, 74), q.at("k3", "Nearly two thirds"), f"{E.pct(R['skilled_broke'])} finished with under $1")):
                al = a * show(t, t0); c.drawCircle(1296, yy - 10, 10, E.fill(rgb, al)); E.text(c, s, 1320, yy, 30, INK, al, 600)
            E.text(c, "dots: this run   ·   percentages: average of 200 runs", 1286, 866, 20, MUTED, a, 500)
        a = show(t, q.at("k3", "Talent decides"))
        if a > 0:
            E.panel(c, 130, 905, 1020, 140, a)
            E.text(c, "Talent decides which group the winner comes from.", 640, 962, 36, INK, a, 700, "c")
            E.text(c, "It doesn't rescue most of the talented.", 640, 1012, 36, GOLD, a, 700, "c")
    return draw


# ------------------------------------------------------------------ 8. tax
def tax(q):
    wd = World(1000, seed=1, cx=640, cy=540, R=420, tax=0.001)
    D0, D1, T4 = q.s("dial"), q.e("dial"), q.s("t4")
    keys = [(q.at("t1", "Every round"), 0), (q.s("lapse"), 8), (q.e("lapse") - 0.5, 10_000), (D0 + 0.8, 10_000), (D1 - 0.4, 13_000)]
    tu = q.at("t2", "If that shape looks familiar")
    US = (0.325, 0.023)                                                    # Federal Reserve DFA, Q2 2026
    words = [("Greed", 520, q.at("t4", "greed")), ("Talent", 960, q.at("t4", "or talent")), ("Cheating", 1400, q.at("t4", "or cheating"))]

    def draw(c, t):
        if t >= D0 + 0.6: wd.tax = 0.01
        wd.run_to(rounds_at(t, keys)); wd.relax(t=t)
        dim = show(t, T4 + 0.1); wd.draw(c, 1 - 0.84 * dim)
        cmp = span(t, tu - 0.2, D0 - 0.1)
        hud(c, wd, 1250, 300, (1 - cmp) * (1 - dim) * show(t, 0.4))
        a = show(t, q.at("t1", "everybody pays")) * (1 - dim)
        rate = lerp(0.1, 1.0, E.ramp(t, D0 + 0.2, D0 + 1.3))
        if a > 0:
            E.panel(c, 1250, 170, 560, 104, a); E.text(c, "WEALTH TAX", 1286, 234, 24, MUTED, a, 600)
            E.text(c, f"{rate:.1f}% per round", 1774, 240, 46, GOLD, a, 700, "r")
        if cmp > 0:
            E.panel(c, 1250, 300, 560, 560, cmp); st = wd.st
            for yy, name, top, bot, src in ((370, "THIS MODEL", st["top1"], st["bottom50"], "0.1% wealth tax per round"),
                                            (620, "UNITED STATES", US[0], US[1], "Federal Reserve, Q2 2026")):
                E.text(c, name, 1286, yy, 28, INK, cmp, 700); E.text(c, src, 1774, yy, 22, MUTED, cmp, 500, "r")
                own_bar(c, 1286, yy + 22, 488, 44, top, bot, cmp)
                E.text(c, "richest 1%", 1286, yy + 108, 24, MUTED, cmp, 500); E.text(c, E.pct(top), 1286, yy + 160, 52, GOLD, cmp, 700)
                E.text(c, "poorest half", 1774, yy + 108, 24, MUTED, cmp, 500, "r"); E.text(c, E.pct(bot, 1), 1774, yy + 160, 52, CORAL, cmp, 700, "r")
        E.text(c, "Extreme inequality doesn't need", 960, 300, 48, INK, show(t, q.at("t4", "Extreme inequality")), 500, "c")
        for s, x, t0 in words:
            a = show(t, t0, 0.3); w = E.font(92, 700).measureText(s)
            E.text(c, s, x, 440, 92, MUTED, a, 700, "c")
            k = E.ramp(t, t0 + 0.45, t0 + 0.8)
            if k > 0: E.line(c, x - w / 2 - 14, 410, x - w / 2 - 14 + (w + 28) * k, 410, CORAL, 9)
        E.text(c, "Just fair exchange, left alone.", 960, 640, 88, GOLD, show(t, q.at("t4", "It's what fair exchange")), 700, "c")
        E.text(c, "Staying even takes something pushing the other way.", 960, 760, 46, INK, show(t, q.at("t4", "Staying even")), 500, "c")
    return draw


# ------------------------------------------------------------------ 9. outro
def outro(q):
    wd = World(300, seed=7, cx=960, cy=560, R=400, tax=0.01)
    O2, O3 = q.s("o2"), q.s("o3")
    chips = [("work", "work"), ("saving", "save"), ("invention", "invent"), ("new wealth", "create new wealth"),
             ("real trades aren't coin flips", "real trades")]
    widths = [E.font(34, 600).measureText(s) + 64 for s, _ in chips]
    x0 = 960 - (sum(widths) + 24 * (len(chips) - 1)) / 2

    def draw(c, t):
        wd.run_to(t * 3); wd.relax(t=t); wd.draw(c, 0.16)
        a1 = span(t, 0.3, O2 - 0.2)
        E.text(c, "This is a toy.", 960, 250, 110, INK, a1, 700, "c")
        E.text(c, "LEFT OUT ON PURPOSE", 960, 350, 26, MUTED, a1 * show(t, q.at("o1", "Real people")), 600, "c")
        x = x0
        for (s, cue), w in zip(chips, widths):
            a = a1 * show(t, q.at("o1", cue), 0.35)
            if a > 0: E.panel(c, x, 385, w, 72, a, 36); E.text(c, s, x + 32, 433, 34, INK, a, 600)
            x += w + 24
        a = a1 * show(t, q.at("o1", "Its point is narrow"))
        E.text(c, "Take away every unfair advantage,", 960, 640, 56, INK, a, 500, "c")
        E.text(c, "and the gap still opens.", 960, 740, 88, GOLD, a1 * show(t, q.at("o1", "and the gap")), 700, "c")
        a2 = span(t, O2, O3 - 0.2)
        E.text(c, "A simulation can't settle the argument.", 960, 480, 60, INK, a2, 500, "c")
        E.text(c, "It can show what happens by default.", 960, 600, 80, GOLD, a2 * show(t, q.at("o2", "But it can tell")), 700, "c")
        a3 = show(t, O3)
        if a3 > 0:
            E.panel(c, 150, 280, 770, 400, a3); E.text(c, "RUN YOUR OWN WORLD", 200, 350, 26, MUTED, a3, 600)
            E.text(c, "All the code is linked", 200, 440, 60, INK, a3, 700); E.text(c, "in the description.", 200, 512, 60, INK, a3, 700)
            E.text(c, "Change the rules. See what breaks.", 200, 600, 34, TEAL, a3, 500)
        a4 = show(t, q.at("o3", "And next time"))
        if a4 > 0:
            E.panel(c, 1000, 280, 770, 400, a4); E.text(c, "NEXT EXPERIMENT", 1050, 350, 26, MUTED, a4, 600)
            E.text(c, "Is success talent", 1050, 440, 66, GOLD, a4, 700); E.text(c, "or luck?", 1050, 518, 66, GOLD, a4, 700)
            E.text(c, "10,000 simulated careers", 1050, 600, 34, INK, a4, 500)
        E.text(c, CHANNEL, 960, 860, 44, INK, a3, 700, "c")
        E.text(c, "We don't argue. We simulate.", 960, 912, 30, MUTED, a3, 500, "c")
    return draw
