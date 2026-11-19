"""Talent vs Luck (Pluchino, Biondo & Rapisarda 2018), reimplemented with numpy.

N people sit at fixed patches of a 201x201 torus. Talent ~ Normal(0.6, 0.1) truncated to [0, 1].
N_E event-points (half lucky, half unlucky) random-walk: every step (6 months) each one moves 2 patches
in a random direction. An event "hits" a person when it lies within distance 1 of their patch
(the event does not disappear). Lucky hit: capital doubles with probability = talent. Unlucky hit:
capital halves. 80 steps = 40 years. Everybody starts with capital 10.

`run` simulates many independent histories at once for the SAME people (same talent, same seats);
only the events and the coin draws differ between histories."""
import numpy as np

SIZE, STEPS, N_EVENTS, C0 = 201, 80, 500, 10.0
OFFS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


def people(n=1000, seed=0, mean=0.6, sd=0.1, size=SIZE):
    rng = np.random.default_rng(seed)
    t = rng.normal(mean, sd, n)
    while ((t < 0) | (t > 1)).any():                      # truncated normal: redraw outside [0, 1]
        bad = (t < 0) | (t > 1); t[bad] = rng.normal(mean, sd, bad.sum())
    cells = rng.choice(size * size, n, replace=False)
    return t, np.stack([cells // size, cells % size], 1)


def _grid(pos, size):
    g = np.full((size, size), -1, np.int64); g[pos[:, 0], pos[:, 1]] = np.arange(len(pos)); return g


def run(talent, pos, H, rng, steps=STEPS, n_events=N_EVENTS, size=SIZE, snap=(), fund=None, trace=False):
    """Returns dict: C (H,N) final capital, L/U (H,N) lucky/unlucky events met, LS (H,N) lucky events used,
    snaps {step: C copy}. fund(step, C, rng) -> additive capital (H,N) or None, called every step.
    trace=True (H must be 1): also per-step event positions and hits, for animation."""
    N = len(talent); g = _grid(pos, size)
    C = np.full((H, N), C0); L = np.zeros((H, N), np.int32); U = np.zeros_like(L); LS = np.zeros_like(L)
    ex = rng.random((H, n_events)) * size; ey = rng.random((H, n_events)) * size
    lucky = np.zeros((H, n_events), bool); lucky[:, : n_events // 2] = True
    snaps, tr = {}, dict(ex=[ex[0].copy()], ey=[ey[0].copy()], hits=[], lucky=lucky[0].copy())
    hh = np.repeat(np.arange(H)[:, None], n_events, 1)
    for s in range(1, steps + 1):
        a = rng.random((H, n_events)) * 2 * np.pi
        ex = (ex + 2 * np.cos(a)) % size; ey = (ey + 2 * np.sin(a)) % size
        rx, ry = np.rint(ex).astype(np.int64), np.rint(ey).astype(np.int64)
        hit_h, hit_a, hit_l, hit_e = [], [], [], []
        for dx, dy in OFFS:
            cx, cy = (rx + dx) % size, (ry + dy) % size
            ddx = (ex - cx + size / 2) % size - size / 2; ddy = (ey - cy + size / 2) % size - size / 2
            ag = g[cx, cy]; m = (ag >= 0) & (ddx * ddx + ddy * ddy <= 1.0)
            if m.any():
                hit_h.append(hh[m]); hit_a.append(ag[m]); hit_l.append(lucky[m]); hit_e.append(np.nonzero(m)[1])
        if hit_h:
            h, ag, lk, ev = (np.concatenate(v) for v in (hit_h, hit_a, hit_l, hit_e))
            use = lk & (rng.random(len(h)) < talent[ag])
            np.add.at(L, (h[lk], ag[lk]), 1); np.add.at(U, (h[~lk], ag[~lk]), 1); np.add.at(LS, (h[use], ag[use]), 1)
            mult = np.where(lk, np.where(use, 2.0, 1.0), 0.5)
            np.multiply.at(C, (h, ag), mult)
            if trace: tr["hits"].append([(int(a_), bool(l_), bool(u_), int(e_)) for a_, l_, u_, e_ in zip(ag, lk, use, ev)])
        elif trace: tr["hits"].append([])
        if fund is not None:
            f = fund(s, C, rng)
            if f is not None: C += f
        if trace: tr["ex"].append(ex[0].copy()); tr["ey"].append(ey[0].copy()); tr.setdefault("C", []).append(C[0].copy())
        if s in snap: snaps[s] = C.copy(); snaps[("L", s)] = L.copy(); snaps[("U", s)] = U.copy()
    out = dict(C=C, L=L, U=U, LS=LS, snaps=snaps)
    if trace: out["trace"] = tr
    return out


def batched(talent, pos, H, seed, chunk=1000, **kw):
    """Same as run() for many histories, in chunks (memory). Concatenates the arrays."""
    parts = []
    for k in range(0, H, chunk):
        parts.append(run(talent, pos, min(chunk, H - k), np.random.default_rng([seed, k]), **kw))
    out = {key: np.concatenate([p[key] for p in parts]) for key in ("C", "L", "U", "LS")}
    out["snaps"] = {s: np.concatenate([p["snaps"][s] for p in parts]) for s in parts[0]["snaps"]}
    return out
