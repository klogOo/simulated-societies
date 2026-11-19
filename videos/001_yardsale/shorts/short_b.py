"""Short B: +20% then -20% is $96 -> one player, 100 fair bets: average $100, typical $13, 86% below start.
Paths use the same construction as scenes.solo (seed 22); the quoted numbers come from results.json."""
import math
import numpy as np
from engine import core as E
from engine import vertical as V
from engine.core import INK, MUTED, TEAL, GOLD, CORAL, LINE
from common import Plan, end_card
from narration import SOLO
import captions

PLAN = Plan(["b1", ("gap", "pause", 0.9), "b2", ("tail", "loop", 1.35)])


def show(t, t0, d=0.4): return E.ramp(t, t0, t0 + d)


def factory():
    P = PLAN
    CX = V.CX
    B2, END = P.s["b2"], P.s["loop"]
    t_lose, t_back, t_no = P.at("then lose"), P.at("Are you"), P.at("No.")
    t_one, t_over, t_avg = P.at("Now give"), P.at("and run"), P.at("On average")
    t_typ, t_86, t_be, t_cta = P.at("But the typical"), P.at("86%"), P.at("To break"), P.at("The full")
    t_56 = P.at("you'd need")
    # --- the 100-bet chart (log money axis)
    st = np.random.default_rng(22).random((260, 100)) < 0.5
    paths = np.concatenate([np.full((260, 1), 100.0), 100 * np.cumprod(np.where(st, 1.2, 0.8), 1)], 1)
    X0, X1, YB, YT = 170, 880, 1190, 600
    def Y(v): return YB - (np.log10(np.clip(v, 0.1, 1e4)) + 1) / 5 * (YB - YT)
    PX = X0 + np.arange(101) / 100 * (X1 - X0); PY = Y(paths)
    two = SOLO["two_step"] / 100                                      # 0.96 per win+loss pair
    med = Y(100 * two ** (np.arange(101) / 2))
    lo = paths[:, -1] < 100
    cache = {}

    def group_path(mask):
        p = E.skia.Path()
        for i in np.flatnonzero(mask):
            if i == 0: continue
            p.moveTo(PX[0], PY[i, 0])
            for j in range(1, 101): p.lineTo(PX[j], PY[i, j])
        return p

    def hook(c, t, a):
        """Phase 1, also the loop target: one blob whose AREA is its money."""
        m = 100.0
        m = E.lerp(m, 120.0, E.ramp(t, 0.12, 0.75, E.ease_out))
        m = E.lerp(m, 100 * two, E.ramp(t, t_lose + 0.35, t_lose + 0.95, E.ease_out))
        r = 200 * math.sqrt(m / 100)
        bx, by = CX, 900
        ga = a * show(t, t_lose + 0.35)
        if ga > 0:                                                   # where $100 was
            for k in range(36):
                a0 = k * 10.0
                p = E.skia.Path(); p.addArc(E.skia.Rect.MakeLTRB(bx - 200, by - 200, bx + 200, by + 200), a0, 5.0)
                c.drawPath(p, E.stroke(INK, 3, ga * 0.75))
            E.text(c, "was $100", bx + 150, by - 205, 30, MUTED, ga, 600)
        rgb = E.wealth_rgb(np.array([m]))[0]
        E.blob(c, bx, by, r, rgb, a, (0.0, -0.3))
        E.text(c, E.money(round(m)), bx, by + r + 110, 96, INK, a, 700, "c")
        up, dn = a * E.window(t, 0.12, t_lose + 0.35, 0.2), a * show(t, t_lose + 0.35)
        E.text(c, "+20%", V.SAFE[2] - 40, by - 250, 64, TEAL, up, 700, "r")
        E.text(c, "−20%", V.SAFE[2] - 40, by - 250, 64, CORAL, dn * (1 - show(t, t_no)), 700, "r")
        E.text(c, f"−${100 - SOLO['two_step']:.0f}", V.SAFE[2] - 40, by - 250, 64, CORAL, a * show(t, t_no), 700, "r")
        # top text
        E.text(c, "+20%, then −20%", V.MARGIN, 310, 96, GOLD, a, 700)
        q = show(t, t_no - 0.05, 0.25)
        E.text(c, "Back to $100?", V.MARGIN, 410, 72, INK, a * (1 - q), 600)
        E.text(c, f"No. {E.money(SOLO['two_step'])}.", V.MARGIN, 410, 72, CORAL, a * q, 700)

    def chart(c, t, a):
        for v, lab in ((0.1, "10¢"), (1, "$1"), (10, "$10"), (100, "$100"), (1000, "$1,000"), (10000, "$10,000")):
            E.line(c, X0, Y(v), X1, Y(v), LINE, 1.5, a); E.text(c, lab, X0 - 14, Y(v) + 9, 26, MUTED, a, 500, "r")
        for n in (0, 50, 100): E.text(c, str(n), PX[n], YB + 42, 28, MUTED, a, 500, "c")
        E.text(c, "bets", PX[100], YB + 80, 26, MUTED, a, 500, "r")
        if t > t_over + 3.0:
            if not cache:
                cache["lo"], cache["hi"] = group_path(lo), group_path(~lo)
            k = show(t, t_86, 0.6)
            c.drawPath(cache["hi"], E.stroke(TEAL, 1.6, a * 0.22))
            c.drawPath(cache["lo"], E.stroke(E.mix(TEAL, CORAL, k), 1.6, a * E.lerp(0.22, 0.30, k)))
        elif t > t_over:
            for i in range(1, 260):
                m = int(100 * E.clamp((t - t_over - i / 260 * 1.8) / 0.8))
                if m > 0: E.polyline(c, list(zip(PX[: m + 1], PY[i, : m + 1])), TEAL, 1.6, a * 0.22)
        m = int(100 * E.clamp((t - t_one) / 2.6))
        if m > 0: E.polyline(c, list(zip(PX[: m + 1], PY[0, : m + 1])), INK, 4, a * E.lerp(1, 0.5, show(t, t_over + 1)))
        g = a * show(t, t_avg)
        for xs in range(X0, X1, 30): E.line(c, xs, Y(100), xs + 15, Y(100), INK, 3.5, g)
        E.text(c, f"average {E.money(SOLO['mean'])}", X1, Y(100) - 16, 32, INK, g, 700, "r")
        gm = int(100 * show(t, t_typ, 1.2))
        if gm > 0:
            E.polyline(c, list(zip(PX[: gm + 1], med[: gm + 1])), GOLD, 6, a)
            E.text(c, f"typical {E.money(SOLO['median'])}", X1, med[100] + 50, 34, GOLD, a * show(t, t_typ + 0.9), 700, "r")

    def stats(c, t, a):
        cols = [(V.MARGIN, "AVERAGE", E.money(SOLO["mean"]), INK, t_avg + 0.6),
                (V.MARGIN + 290, "TYPICAL", E.money(SOLO["median"]), GOLD, t_typ + 0.8),
                (V.MARGIN + 560, "BELOW START", E.pct(SOLO["lost"]), CORAL, t_86)]
        for x, lab, v, rgb, t0 in cols:
            al = a * show(t, t0)
            E.text(c, lab, x, 410, 26, MUTED, al, 600); E.text(c, v, x, 495, 84, rgb, al, 700)

    def grid(c, t, a):
        if a <= 0.003: return
        n = 0 if t < t_56 else min(SOLO["wins_needed"], int(SOLO["wins_needed"] * (t - t_56) / 1.4) + 1)
        x0, y0, s = CX - 4.5 * 62, 640, 62
        for i in range(100):
            xx, yy = x0 + (i % 10) * s, y0 + (i // 10) * s
            c.drawCircle(xx, yy, 22, E.fill(GOLD, a) if i < n else E.stroke(MUTED, 2.5, a * 0.6))
        E.text(c, f"{n} wins out of 100", CX, 1292, 56, INK, a * show(t, t_56), 700, "c")
        # (caption sits at 1395; this line is above it)

    def draw(c, t):
        u = E.ramp(t, END, P.last)
        h = 1 - show(t, P.e["b1"] + 0.1, 0.5)                       # hook fades out after b1
        if u > 0 or h > 0: hook(c, t if u == 0 else 0.0, max(h, u))
        ca = show(t, P.e["b1"] + 0.3, 0.5) * (1 - show(t, t_be - 0.1)) * (1 - u)
        if ca > 0:
            chart(c, t, ca)
            E.text(c, "1 player · 100 fair bets", V.MARGIN, 290, 64, INK, ca, 700)
            E.text(c, "each bet: +20% or −20%", V.MARGIN, 345, 38, MUTED, ca, 500)
        sa = show(t, P.e["b1"] + 0.3, 0.5) * (1 - show(t, t_cta - 0.1)) * (1 - u)
        if sa > 0:
            stats(c, t, sa)
            ha = sa * show(t, t_be - 0.1)
            E.text(c, "To break even:", V.MARGIN, 300, 72, INK, ha, 700)
        grid(c, t, show(t, t_be - 0.1) * (1 - show(t, t_cta - 0.1)) * (1 - u))
        end_card(c, show(t, t_cta - 0.1, 0.5) * (1 - u))
        captions.draw_caption(c, P.cards, t)
    return draw
