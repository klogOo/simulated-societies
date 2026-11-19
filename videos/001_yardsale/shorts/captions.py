"""Word-level caption timing without a speech-to-text call: phrase boundaries (punctuation) are snapped
to the pauses measured in the voice file, and words inside a phrase share the time by length."""
import re
import numpy as np
import soundfile as sf
from engine import core as E
from engine import vertical as V
from narration import tokens


def pauses(wav, min_len=0.06, thr=0.012):
    x, sr = sf.read(str(wav), dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    hop = sr // 100
    e = np.sqrt(np.convolve(x * x, np.ones(hop) / hop, "same")[::hop])
    loud = np.flatnonzero(e >= thr)
    s0, s1 = loud[0] / 100, (loud[-1] + 1) / 100
    out, i, n = [], 0, len(e)
    while i < n:
        if e[i] < thr:
            j = i
            while j < n and e[j] < thr: j += 1
            a, b = i / 100, j / 100
            if (j - i) / 100 >= min_len and a > s0 and b < s1: out.append((a, b))
            i = j
        else: i += 1
    return s0, s1, out, len(x) / sr


def words(markup, wav, offset=0.0):
    """[(t_start, t_end, shown, is_number, phrase_end)] in absolute seconds."""
    tk = tokens(markup)
    s0, s1, sil, _ = pauses(wav)
    ends = [i for i, (sp, _, _) in enumerate(tk) if re.search(r"[,.?!]$", sp)]
    if ends and ends[-1] == len(tk) - 1: ends = ends[:-1]
    # weight of each token = characters + pause weight after punctuation (as engine.timeline)
    wt = np.array([len(sp) + 1 + (7 if sp[-1] in ".?!" else 3 if sp[-1] in ",;" else 0) for sp, _, _ in tk], float)
    cum = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
    exp = [s0 + (s1 - s0) * cum[i + 1] for i in ends]
    # monotone nearest match of boundaries to pauses
    match, used = {}, -1
    for b, te in enumerate(exp):
        best = None
        for k in range(used + 1, len(sil)):
            c = (sil[k][0] + sil[k][1]) / 2
            if abs(c - te) < 0.8 and (best is None or abs(c - te) < abs((sil[best][0] + sil[best][1]) / 2 - te)): best = k
        if best is not None: match[b] = best; used = best
    # anchors: (token index where speech resumes, time)
    pts = [(0, s0, s0)]                          # (token idx, end of previous phrase, start of this phrase)
    for b, i in enumerate(ends):
        if b in match: a, z = sil[match[b]]; pts.append((i + 1, a, z))
    pts.append((len(tk), s1, s1))
    times = np.zeros(len(tk) + 1)
    for (i0, _, t0), (i1, t1, _) in zip(pts, pts[1:]):     # spread tokens between anchors by weight
        seg = wt[i0:i1].copy()
        if len(seg): seg[-1] = len(tk[i1 - 1][0]) + 1              # the pause after the span is measured, not guessed
        w = np.concatenate([[0], np.cumsum(seg)])
        times[i0:i1 + 1] = t0 + (t1 - t0) * w / max(w[-1], 1e-9)
    out = []
    for k, (sp, sh, num) in enumerate(tk):
        out.append((offset + times[k], offset + times[k + 1], sh, num, k in ends or k == len(tk) - 1))
    return out


def chunks(ws, max_words=3, max_chars=16):
    """Group words into caption cards: a few words, never across a sentence or comma."""
    out, cur = [], []
    for w in ws:
        txt = " ".join(x[2] for x in cur + [w])
        if cur and (len(cur) >= max_words or len(txt) > max_chars):
            out.append(cur); cur = []
        cur.append(w)
        if w[4]: out.append(cur); cur = []
    if cur: out.append(cur)
    cards = []
    for i, c in enumerate(out):
        t0 = c[0][0] - 0.06
        nxt = out[i + 1][0][0] - 0.06 if i + 1 < len(out) else c[-1][1] + 0.6
        t1 = min(nxt, c[-1][1] + 0.45) if c[-1][4] else nxt
        cards.append((t0, t1, [(x[2].rstrip(","), x[3]) for x in c]))
    return cards


def draw_caption(c, cards, t, y=1395, size=86, a=1.0):
    """Big bold words, numbers in gold, on a dark pill. Pops in with a small overshoot."""
    for t0, t1, ws in cards:
        if not (t0 <= t < t1): continue
        k = E.back((t - t0) / 0.16, 2.2); al = a * E.clamp((t - t0) / 0.08) * E.clamp((t1 - t) / 0.08)
        if al <= 0.01: return
        s = " ".join(w for w, _ in ws)
        sz = V.fit_size(s, size, 700, V.SAFE[2] - V.MARGIN - 80) * (0.86 + 0.14 * k)
        f = E.font(sz, 700); sp = f.measureText(" ")
        wid = [f.measureText(w) for w, _ in ws]; tot = sum(wid) + sp * (len(ws) - 1)
        x = V.CX - tot / 2
        E.rrect(c, x - 34, y - sz * 0.92, tot + 68, sz * 1.28, 26, E.fill(E.BG, 0.72 * al))
        for (w, num), ww in zip(ws, wid):
            E.text(c, w, x, y, sz, E.GOLD if num else E.INK, al, 700)
            x += ww + sp
        return
