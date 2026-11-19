"""Short A: 1,000 people, $100 each, fair coin flips -> one person ends with 83%.
The world is the same seed as experiments.py, so every live number on screen is the one in results.json."""
import copy, math
import numpy as np
from engine import core as E
from engine import vertical as V
from engine.core import INK, MUTED, TEAL, GOLD, CORAL
from engine.world import World, rounds_at
from common import Plan, end_card
import captions

PLAN = Plan(["a1", ("gap", "lapse", 3.0), "a2", ("tail", "loop", 1.35)])


def show(t, t0, d=0.4): return E.ramp(t, t0, t0 + d)


def factory():
    P = PLAN
    CX, CY, R = V.CX, 900, 310
    wd = World(1000, seed=1, cx=CX, cy=CY, R=R)
    L0, A2, END = P.s["lapse"], P.s["a2"], P.s["loop"]
    t_poor, t_keep, t_83 = P.at("the poorest"), P.at("Keep going"), P.at("person holds")
    t_fair, t_cta = P.at("Fair rules"), P.at("The full")
    keys = [(0.0, 0), (2.0, 4), (L0, 14), (A2 + 0.2, 1000), (t_keep + 0.2, 1000), (t_83 + 0.9, 100_000)]
    state = {}

    def zoom(t): return 1 + 0.05 * math.sin(math.pi * E.clamp(t / L0))          # back to exactly 1 for the loop

    def intro_text(c, a):
        E.text(c, "1,000 people", V.MARGIN, 300, 100, INK, a, 700)
        E.text(c, "$100 each", V.MARGIN, 385, 66, TEAL, a, 600)
        E.text(c, "Every trade is a fair coin flip.", V.MARGIN, 455, 42, INK, a, 500)

    def draw(c, t):
        if t == 0:
            wd.relax(t=0.0); state["w0"] = copy.deepcopy(wd)            # frame 0, kept for the loop
        else:
            wd.run_to(rounds_at(t, keys)); wd.relax(t=t)
        u = E.ramp(t, END, P.last)                                         # loop: fade back into frame 0
        cta = show(t, t_cta - 0.1, 0.5) * (1 - u)
        if u < 1:
            wd.draw(c, (1 - 0.55 * show(t, t_cta - 0.1, 0.5)) * (1 - u), scale=zoom(t))
            ring = show(t, t_83 + 0.6) * (1 - show(t, t_cta - 0.1)) * (1 - u)
            if ring > 0:
                x, y, r = wd.top_xy_r(); c.drawCircle(x, y, r + 10, E.stroke(GOLD, 5, ring))
        if u > 0:
            copy.deepcopy(state["w0"]).draw(c, u, scale=E.lerp(0.82, 1.0, E.ease_out(u)))
        # top block
        intro_text(c, max(1 - show(t, L0 - 0.3, 0.35), u))
        a = show(t, L0 - 0.1, 0.35) * (1 - show(t, t_cta - 0.1)) * (1 - u)
        if a > 0:
            E.text(c, "ROUND", V.MARGIN, 250, 28, MUTED, a, 600)
            E.text(c, f"{wd.round:,}", V.MARGIN, 335, 84, INK, a, 700)
            xr = V.SAFE[2] - 24
            E.text(c, "ONE PERSON HOLDS", xr, 250, 28, MUTED, a, 600, "r")
            big = show(t, t_83 + 0.6)
            E.text(c, E.pct(wd.st["richest"]), xr, 335 + 60 * big, 84 + 70 * big, GOLD, a, 700, "r")
            pa = a * E.window(t, t_poor, t_keep + 0.6, 0.3)
            if pa > 0:
                E.text(c, "POOREST 500 PEOPLE SHARE", V.MARGIN, 420, 28, MUTED, pa, 600)
                E.text(c, E.money(wd.st["bottom50"] * float(wd.w.sum())), V.MARGIN, 500, 72, CORAL, pa, 700)
            fa = a * show(t, t_fair)
            E.text(c, "of all the money", xr, 445, 36, INK, a * big, 500, "r")
            E.text(c, "Fair rules.", V.MARGIN, 430, 44, TEAL, fa, 700)
            E.text(c, "Unfair result.", V.MARGIN, 485, 44, CORAL, a * show(t, P.at("A wildly")), 700)
        end_card(c, cta)
        captions.draw_caption(c, P.cards, t)
    return draw
