"""A career field (video 002, Talent vs Luck): people sit at FIXED seats; lucky (gold) and unlucky (coral)
events drift across the field. Blob size = capital, blob colour = talent.

Flicker rules carried over from world.py: positions never move (seats are fixed), sizes follow capital through
a two-stage low-pass in log space, draw order is stable (size class, then seat), nothing random per frame,
eyes fade in with size, events glide between simulation steps and fade at the torus edges instead of popping.
Draw calls must come in frame order (the smoothing is stateful)."""
import math
import numpy as np
from . import core as E

TALENT_STOPS = np.array([0.35, 0.60, 0.85])
TALENT_COLS = np.array([(78, 92, 140), E.TEAL, (205, 255, 246)], dtype=float)


def talent_rgb(t):
    t = np.asarray(t, dtype=float)
    return np.stack([np.interp(t, TALENT_STOPS, TALENT_COLS[:, k]) for k in range(3)], axis=-1)


class Field:
    def __init__(self, talent, pos, trace, x0, y0, side, size=201, r0=8.5, expo=0.27, c0=10.0):
        self.T, self.n, self.size = np.asarray(talent), len(talent), size
        self.x0, self.y0, self.side = x0, y0, side
        self.px = x0 + (pos[:, 0] + 0.5) / size * side
        self.py = y0 + (pos[:, 1] + 0.5) / size * side
        self.ex, self.ey = np.array(trace["ex"]), np.array(trace["ey"])     # (steps+1, E)
        self.lucky = np.asarray(trace["lucky"])
        self.Cs = np.vstack([np.full(self.n, c0)] + [np.asarray(c) for c in trace["C"]])   # (steps+1, N)
        self.hits = [[]] + trace["hits"]                                     # hits[s] happen at step s
        self.steps = len(self.Cs) - 1
        self.r0, self.expo, self.c0 = r0, expo, c0
        self.l1 = np.zeros(self.n); self.l2 = np.zeros(self.n)                # smoothed log2(C / c0)
        self.rgb = talent_rgb(self.T)
        self.step_f, self.reached, self.t = 0.0, {0: 0.0}, 0.0
        self.lookx = self.looky = None

    # ---------------------------------------------------------------- state
    def update(self, t, step_f, k=0.2):
        """Advance to simulation time step_f (float, 0..steps) at wall time t."""
        step_f = E.clamp(step_f, 0, self.steps)
        s = int(math.floor(step_f + 1e-9))
        for j in range(int(math.floor(self.step_f + 1e-9)) + 1, s + 1): self.reached.setdefault(j, t)
        self.step_f, self.t = step_f, t
        tgt = np.log2(np.maximum(self.Cs[s], 1e-12) / self.c0)
        self.l1 += k * (tgt - self.l1); self.l2 += k * (self.l1 - self.l2)

    def snap(self):
        """Jump the smoothed sizes to the current target (use when a scene starts mid-history)."""
        s = int(math.floor(self.step_f + 1e-9)); self.l1[:] = self.l2[:] = np.log2(np.maximum(self.Cs[s], 1e-12) / self.c0)

    def step(self): return int(math.floor(self.step_f + 1e-9))
    def capital(self): return self.Cs[self.step()]

    def radii(self, scale=1.0):
        return np.maximum(self.r0 * scale * np.exp2(self.expo * self.l2), 2.2 * scale)

    def xy(self, i): return float(self.px[i]), float(self.py[i])

    # ---------------------------------------------------------------- drawing
    def draw_events(self, c, a=1.0, rad=5.0):
        if a <= 0.003: return
        s = self.step(); u = self.step_f - s
        s1 = min(s + 1, self.steps)
        x0, y0 = self.ex[s], self.ey[s]
        dx = (self.ex[s1] - x0 + self.size / 2) % self.size - self.size / 2
        dy = (self.ey[s1] - y0 + self.size / 2) % self.size - self.size / 2
        x = (x0 + dx * u) % self.size; y = (y0 + dy * u) % self.size          # linear: no stop-go at step boundaries
        edge = np.minimum(np.minimum(x, self.size - x), np.minimum(y, self.size - y))
        al = np.clip(edge / 3.0, 0, 1) * a
        X = self.x0 + x / self.size * self.side; Y = self.y0 + y / self.size * self.side
        for i in range(len(X)):
            if al[i] < 0.01: continue
            rgb = E.GOLD if self.lucky[i] else E.CORAL
            c.drawCircle(float(X[i]), float(Y[i]), rad * 2.0, E.fill(rgb, 0.10 * al[i]))
            c.drawCircle(float(X[i]), float(Y[i]), rad, E.fill(rgb, 0.92 * al[i]))

    def draw_flashes(self, c, a=1.0, life=0.9, scale=1.0, only=None):
        """Expanding rings at people when an event reaches them: gold = capital doubled, faint gold = luck not
        used (talent check failed), coral = capital halved."""
        if a <= 0.003: return
        r = self.radii(scale)
        for s, ts in self.reached.items():
            age = self.t - ts
            if s == 0 or age > life or age < 0: continue
            g = age / life
            for ag, lk, use, _ in self.hits[s]:
                if only is not None and not only[ag]: continue
                rgb = E.GOLD if lk else E.CORAL
                al = a * (1 - g) ** 1.5 * (0.45 if (lk and not use) else 1.0) * min(1.0, age / 0.12)   # fade in: no pop
                c.drawCircle(float(self.px[ag]), float(self.py[ag]), float(r[ag]) + 4 + 22 * E.ease_out(g),
                             E.stroke(rgb, 3.0 if (use or not lk) else 2.0, al))

    def draw(self, c, a=1.0, dim=None, ring=None, ring_rgb=E.INK, look_at=None, scale=1.0, dim_a=0.22):
        if a <= 0.003: return
        r = self.radii(scale)
        if look_at is not None:
            if self.lookx is None: self.lookx, self.looky = look_at
            self.lookx += (look_at[0] - self.lookx) * 0.08; self.looky += (look_at[1] - self.looky) * 0.08
        bucket = np.round(np.log2(np.maximum(r, 1.0)) * 2)
        for i in np.lexsort((np.arange(self.n), bucket)):
            if self.lookx is not None:
                lx, ly = self.lookx - self.px[i], self.looky - self.py[i]; m = math.hypot(lx, ly) + 1e-6
                k = min(1.0, m / (r[i] * 3 + 1e-6)); look = (k * lx / m, k * ly / m)
            else:
                look = (0.0, 0.0)
            al = a * (dim_a if (dim is not None and not dim[i]) else 1.0)
            E.blob(c, float(self.px[i]), float(self.py[i]), float(r[i]), self.rgb[i], al, look,
                   ring=ring_rgb if (ring is not None and ring[i]) else None)

    def frame(self, c, a=1.0, pad=18):
        E.rrect(c, self.x0 - pad, self.y0 - pad, self.side + 2 * pad, self.side + 2 * pad, 26, E.fill(E.PANEL, 0.55 * a))
        E.rrect(c, self.x0 - pad, self.y0 - pad, self.side + 2 * pad, self.side + 2 * pad, 26, E.stroke(E.LINE, 1.5, a))


def steps_at(t, keys):
    """keys: [(time, step), ...] ascending. Linear interpolation (careers advance at a steady pace)."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, s0), (t1, s1) in zip(keys, keys[1:]):
        if t <= t1: return s0 + (s1 - s0) * E.clamp((t - t0) / max(1e-9, t1 - t0))
    return keys[-1][1]
