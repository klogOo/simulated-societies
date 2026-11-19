"""A bubble world: every person is a blob whose AREA is their wealth.
Total area is conserved, like the money."""
import math
import numpy as np
from scipy.spatial import cKDTree
from sims.yardsale import step, stats
from . import core as E


class World:
    def __init__(self, n=1000, seed=1, cx=960, cy=540, R=420, f=0.2, tax=0.0, skill=None, hues=False):
        self.n, self.cx, self.cy, self.R, self.f, self.tax, self.skill = n, cx, cy, R, f, tax, skill
        self.rng = np.random.default_rng(seed)          # ONLY for the economy -> reproduces experiments.py
        lay = np.random.default_rng(seed + 9999)        # layout / cosmetics
        self.w = np.full(n, 100.0); self.disp = self.w.copy(); self.round = 0
        k = lay.permutation(n) + 0.5                     # sunflower packing, shuffled seats
        rad = R * 0.97 * np.sqrt(k / n); ang = k * 2.39996323
        self.x = rad * np.cos(ang); self.y = rad * np.sin(ang)
        self.xd, self.yd, self.t = self.x.copy(), self.y.copy(), 0.0
        self.xm, self.ym = self.x.copy(), self.y.copy()
        self.l1 = np.full(n, math.log(100.0)); self.l2 = self.l1.copy()
        self.lookx, self.looky, self._tick = 0.0, 0.0, 0
        self.r0 = R * math.sqrt(0.70 / n)
        self.cam = self.cam1 = 1.0
        self.phase = lay.random(n) * 6.283
        self.hue = None
        if hues:                                         # colour by seat instead of wealth
            h = np.arange(n) / n
            self.hue = np.stack([_hsv(hh, 0.62, 1.0) for hh in h])
        self.st = stats(self.w)

    def run_to(self, target):
        target = int(target)
        while self.round < target:
            step(self.w, self.rng, self.f, self.tax, self.skill); self.round += 1
        self.st = stats(self.w)

    def radii(self):
        return np.maximum(self.r0 * np.sqrt(np.maximum(self.disp, 0) / 100.0), 1.1).astype(np.float32)

    def relax(self, iters=12, t=0.0):
        """Resolve overlaps. Stable by construction: corrections are AVERAGED over a bubble's contacts
        (summing them makes a packed crowd vibrate), nothing random is injected, and what is drawn is a
        smoothed copy of the physics positions. A static crowd is therefore perfectly still."""
        # Sizes follow wealth through a two-stage low-pass in log space (wealth moves multiplicatively).
        # One stage still lets the per-frame randomness of a time-lapse through, and the crowd "boils".
        lw = np.log(np.maximum(self.w, 1e-9))
        self.l1 += 0.16 * (lw - self.l1); self.l2 += 0.16 * (self.l1 - self.l2)
        self.disp = np.exp(self.l2)
        n = self.n
        r = np.maximum(self.radii(), 2.2).astype(np.float64); r2 = r * r
        x, y = self.x.astype(np.float64), self.y.astype(np.float64)
        order = np.argsort(r, kind="stable"); K = min(n, 48)
        L, S = order[n - K:], order[:n - K]               # K largest: dense maths; the rest: neighbour search
        inS = np.zeros(n, bool); inS[S] = True; colsL = np.arange(K)
        shareL = r2[None, L] / (r2[:, None] + r2[None, L]); rsL = r[:, None] + r[None, L]
        reach = 2 * float(r[S].max()) if len(S) else 0.0
        for _ in range(iters):
            ax = np.zeros(n); ay = np.zeros(n); cnt = np.zeros(n)
            if len(S) > 1:
                pr = cKDTree(np.column_stack([x[S], y[S]])).query_pairs(reach, output_type="ndarray")
                if len(pr):
                    i, j = S[pr[:, 0]], S[pr[:, 1]]
                    dx, dy = x[i] - x[j], y[i] - y[j]; d = np.hypot(dx, dy) + 1e-6
                    ov = r[i] + r[j] - d; m = ov > 0
                    i, j, dx, dy, d, ov = i[m], j[m], dx[m], dy[m], d[m], ov[m]
                    wi = r2[j] / (r2[i] + r2[j]); fx, fy = ov * dx / d, ov * dy / d
                    ax += np.bincount(i, fx * wi, n) - np.bincount(j, fx * (1 - wi), n)
                    ay += np.bincount(i, fy * wi, n) - np.bincount(j, fy * (1 - wi), n)
                    cnt += np.bincount(i, minlength=n) + np.bincount(j, minlength=n)
            dx = x[:, None] - x[None, L]; dy = y[:, None] - y[None, L]; d = np.hypot(dx, dy) + 1e-6
            ov = rsL - d; m = ov > 0; m[L, colsL] = False
            f = np.where(m, ov / d, 0.0)
            ax += (f * shareL * dx).sum(1); ay += (f * shareL * dy).sum(1); cnt += m.sum(1)
            back = np.where(inS[:, None], f * (1 - shareL), 0.0)          # reaction of small ones on the large
            ax[L] -= (back * dx).sum(0); ay[L] -= (back * dy).sum(0); cnt[L] += (m & inS[:, None]).sum(0)
            cnt = np.maximum(cnt, 1.0)
            x += ax / cnt; y += ay / cnt
        x *= 0.9985; y *= 0.9985                          # gentle pull to the centre, once per frame
        x -= 0.2 * float((x * r2).sum() / r2.sum()); y -= 0.2 * float((y * r2).sum() / r2.sum())   # keep the mass centred
        self.x, self.y = x, y
        self.xm += (x - self.xm) * 0.35; self.ym += (y - self.ym) * 0.35   # what we draw is a two-stage
        self.xd += (self.xm - self.xd) * 0.35; self.yd += (self.ym - self.yd) * 0.35   # low-pass of the physics
        vis = r > 3
        if vis.any():   # Camera pulls back if big bubbles leave the frame. It scales EVERY bubble, so the slightest
            # jitter here shimmers the whole crowd: aim from the smoothed positions and low-pass twice.
            tgt = min(1.0, self.R * 1.35 / float((np.abs(self.xd) + r)[vis].max()), self.R * 1.06 / float((np.abs(self.yd) + r)[vis].max()))
            self.cam1 += (tgt - self.cam1) * 0.07; self.cam += (self.cam1 - self.cam) * 0.07
        self.t = t

    def draw(self, c, a=1.0, ring_mask=None, ring_rgb=E.INK, scale=1.0, dim=None):
        scale = scale * self.cam
        r = self.radii() * scale
        rgb = self.hue if self.hue is not None else E.wealth_rgb(self.disp)
        sway = 0.9 * min(1.0, self.r0 / 10)               # slow, smooth drift (drawn only, never fed to physics)
        X = self.xd + sway * np.cos(self.phase + self.t * 0.9); Y = self.yd + sway * np.sin(self.phase * 1.7 + self.t * 0.7)
        top = int(np.argmax(self.disp))
        self.lookx += (X[top] - self.lookx) * 0.08; self.looky += (Y[top] - self.looky) * 0.08   # gaze glides when the leader changes
        tx, ty = self.lookx, self.looky
        bucket = np.round(np.log2(np.maximum(r, 1.0)) * 2)             # z-order changes only when a bubble changes size class
        for i in np.lexsort((np.arange(self.n), bucket)):
            px, py = self.cx + X[i] * scale, self.cy + Y[i] * scale
            lx, ly = tx - X[i], ty - Y[i]; m = math.hypot(lx, ly) + 1e-6
            k = min(1.0, m / (r[i] / scale + 1e-6))               # the leader itself looks straight ahead
            look = (k * lx / m, k * ly / m)                        # everyone watches the richest
            al = a * E.lerp(0.55, 1.0, E.clamp((r[i] - 1.3) / 1.5))
            if dim is not None and not dim[i]: al *= 0.25
            E.blob(c, px, py, float(r[i]), rgb[i], al, look,
                   ring=ring_rgb if (ring_mask is not None and ring_mask[i]) else None)

    def top_xy_r(self):
        i = int(np.argmax(self.disp))
        k = self.cam
        return self.cx + float(self.xd[i]) * k, self.cy + float(self.yd[i]) * k, float(self.radii()[i]) * k


def _hsv(h, s, v):
    i = int(h * 6) % 6; f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return (r * 255, g * 255, b * 255)


def rounds_at(t, keys):
    """keys: [(time, round), ...] ascending. Geometric interpolation between keys (time-lapse feel)."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, r0), (t1, r1) in zip(keys, keys[1:]):
        if t <= t1:
            if r1 <= r0: return r0
            u = (t - t0) / (t1 - t0)
            a, b = max(r0, 1), max(r1, 1)
            return r0 + (a * (b / a) ** u - a)
    return keys[-1][1]


def hud(c, wd, x, y, a=1.0, title="WHO OWNS THE MONEY"):
    """Score panel: round counter, ownership bar, three stats. Numbers are live from the world."""
    if a <= 0.003: return
    wd._hud_k = getattr(wd, "_hud_k", 0) + 1                      # numbers refresh at 10 Hz (calmer to read), exact when paused
    if wd._hud_k % 3 == 0 or wd.round == getattr(wd, "_hud_round", -1) or not hasattr(wd, "_hud_st"): wd._hud_st = wd.st
    wd._hud_round = wd.round
    st = wd._hud_st; n1 = max(1, wd.n // 100); w = 560
    E.panel(c, x, y, w, 560, a)
    E.text(c, "ROUND", x + 36, y + 62, 24, E.MUTED, a, 600)
    E.text(c, f"{wd.round:,}", x + w - 36, y + 70, 54, E.INK, a, 700, "r")
    E.line(c, x + 36, y + 96, x + w - 36, y + 96, E.LINE, 1.5, a)
    E.text(c, title, x + 36, y + 142, 24, E.MUTED, a, 600)
    bx, by, bw, bh = x + 36, y + 162, w - 72, 44
    mid = max(0.0, 1 - st["top1"] - st["bottom50"])
    segs = [(st["top1"], E.GOLD), (mid, E.TEAL), (st["bottom50"], E.CORAL)]
    E.rrect(c, bx, by, bw, bh, 10, E.fill(E.LINE, a))
    px = bx
    for frac, rgb in segs:
        if frac * bw > 0.5: c.drawRect(E.skia.Rect.MakeXYWH(px, by, frac * bw, bh), E.fill(rgb, a))
        px += frac * bw
    rows = [(E.GOLD, f"Richest 1%  ({n1} people)", E.pct(st["top1"])),
            (E.TEAL, "Person in the middle has", E.money(st["median"])),
            (E.CORAL, f"Poorest half  ({wd.n // 2} people) share",
             f"{E.pct(st['bottom50'], 1 if st['bottom50'] < 0.1 else 0)}  ·  {E.money(st['bottom50'] * float(wd.w.sum()))}")]
    for k, (rgb, label, val) in enumerate(rows):
        yy = y + 282 + k * 96
        c.drawCircle(x + 48, yy - 34, 9, E.fill(rgb, a))
        E.text(c, label, x + 70, yy - 24, 27, E.MUTED, a, 500)
        E.text(c, val, x + 70, yy + 30, 50, E.INK, a, 700)
