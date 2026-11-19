"""Tiny code-first video engine: Skia drawing helpers + ffmpeg frame pipe."""
import math, subprocess
from pathlib import Path
import numpy as np
import skia
import imageio_ffmpeg

W, H, FPS = 1920, 1080, 30
ROOT = Path(__file__).resolve().parents[1]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Palette (RGB)
BG = (10, 14, 26); PANEL = (19, 26, 44); LINE = (44, 56, 86)
INK = (233, 237, 246); MUTED = (132, 145, 172)
TEAL = (62, 205, 192); GOLD = (255, 198, 74); CORAL = (255, 110, 104); SLATE = (60, 76, 112)
CREAM = (255, 240, 190)

# ---------- math ----------
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ramp(t, t0, t1, e=ease): return e((t - t0) / max(1e-9, t1 - t0))
def window(t, t0, t1, fade=0.4): return min(ramp(t, t0, t0 + fade), 1 - ramp(t, t1 - fade, t1))
def mix(c1, c2, t): return tuple(lerp(a, b, t) for a, b in zip(c1, c2))
def back(t, s=1.6): t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s)  # overshoot pop

# ---------- paint / text ----------
def col(rgb, a=1.0): return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(255 * clamp(a)))
def fill(rgb, a=1.0): return skia.Paint(AntiAlias=True, Color=col(rgb, a))
def stroke(rgb, w=2.0, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

_BASE = skia.Typeface.MakeFromFile(str(ROOT / "assets/fonts/SpaceGrotesk.ttf"))
_TF, _FONT = {}, {}
def _typeface(weight):
    if weight not in _TF:
        VP = skia.FontArguments.VariationPosition
        coords = VP.Coordinates([VP.Coordinate(int.from_bytes(b"wght", "big"), float(weight))])
        args = skia.FontArguments(); args.setVariationDesignPosition(VP(coords))
        _TF[weight] = _BASE.makeClone(args)
    return _TF[weight]
def font(size, weight=500):
    k = (round(size, 1), weight)
    if k not in _FONT:
        f = skia.Font(_typeface(weight), k[0]); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        _FONT[k] = f
    return _FONT[k]

def text(c, s, x, y, size=40, rgb=INK, a=1.0, weight=500, align="l"):
    """Draw text with baseline at y. Returns width."""
    if a <= 0.003: return 0
    f = font(size, weight); w = f.measureText(s)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    c.drawString(s, x, y, f, fill(rgb, a))
    return w

def money(v):
    if v >= 1000: return f"${v:,.0f}"
    if v >= 10: return f"${v:.0f}"
    if v >= 0.995: return f"${v:.2f}"
    if v >= 0.005: return f"{v * 100:.0f}¢"
    return "<1¢"
def pct(v, d=0):
    if 0 < v < 0.001: return "<0.1%"
    return f"{v * 100:.{d}f}%"

# ---------- shapes ----------
def rrect(c, x, y, w, h, r, paint): c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint)
def panel(c, x, y, w, h, a=1.0, r=22):
    rrect(c, x, y, w, h, r, fill(PANEL, 0.92 * a)); rrect(c, x, y, w, h, r, stroke(LINE, 1.5, a))
def line(c, x0, y0, x1, y1, rgb=MUTED, w=2.0, a=1.0): c.drawLine(x0, y0, x1, y1, stroke(rgb, w, a))
def polyline(c, pts, rgb, w=2.0, a=1.0):
    if len(pts) < 2: return
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    c.drawPath(p, stroke(rgb, w, a))
def arrow(c, x0, y0, x1, y1, rgb=INK, w=4.0, a=1.0, head=16):
    ang = math.atan2(y1 - y0, x1 - x0)
    line(c, x0, y0, x1, y1, rgb, w, a)
    for s in (-1, 1):
        line(c, x1, y1, x1 - head * math.cos(ang + s * 0.5), y1 - head * math.sin(ang + s * 0.5), rgb, w, a)

def blob(c, x, y, r, rgb, a=1.0, look=(0.0, 0.0), ring=None, eyes=True):
    """The channel's character: a round fellow with two eyes."""
    if r <= 0 or a <= 0.003: return
    c.drawCircle(x, y, r, fill(rgb, a))
    if ring is not None and r >= 3:
        rw = min(6.0, max(2.0, r * 0.12)); c.drawCircle(x, y, r - rw / 2, stroke(ring, rw, a))
    e = clamp((r - 7.0) / 4.0) if eyes else 0.0          # eyes fade in with size: no popping, no sub-pixel twinkle
    if e > 0.02:
        ea = a * e
        c.drawCircle(x - r * 0.3, y - r * 0.38, r * 0.34, fill((255, 255, 255), 0.13 * ea))  # soft highlight
        ex, ey, er = r * 0.33, -r * 0.1, r * 0.2
        px, py = look[0] * er * 0.5, look[1] * er * 0.5
        for s in (-1, 1):
            c.drawCircle(x + s * ex, y + ey, er, fill((255, 255, 255), ea))
            c.drawCircle(x + s * ex + px, y + ey + py, er * 0.52, fill((14, 18, 32), ea))

_bg = None
def background(c):
    global _bg
    if _bg is None:
        s = skia.Surface(W, H); k = s.getCanvas(); k.clear(col(BG))
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeRadial((W / 2, H * 0.46), W * 0.62,
                    [col((26, 36, 66)), col(BG)]))
        k.drawRect(skia.Rect.MakeWH(W, H), p)
        dot = fill((255, 255, 255), 0.035)
        for gx in range(40, W, 60):
            for gy in range(30, H, 60): k.drawCircle(gx, gy, 1.6, dot)
        _bg = s.makeImageSnapshot()
    c.drawImage(_bg, 0, 0)

def wealth_rgb(w):
    """Vectorised wealth -> colour: slate (broke) -> teal ($100) -> gold -> cream (very rich)."""
    t = np.log10(np.maximum(np.asarray(w, dtype=float), 1e-4) / 100.0)
    stops = np.array([-2.0, 0.0, 1.0, 2.5]); cols = np.array([SLATE, TEAL, GOLD, CREAM], dtype=float)
    return np.stack([np.interp(t, stops, cols[:, k]) for k in range(3)], axis=-1)

# ---------- rendering ----------
def render(draw, dur, out, fps=FPS, snap=None):
    """draw(canvas, t) is called once per frame, in order. If `snap` is a dict {t: png_path},
    only those frames are saved as PNG (preview mode) and no video is written."""
    surf = skia.Surface(W, H); c = surf.getCanvas()      # native premul BGRA (much faster than a numpy-backed one)
    n = int(round(dur * fps))
    proc = None
    if snap is None:
        proc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                                 "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                 "-crf", "17", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
        todo = None
    else:
        todo = {int(round(t * fps)): p for t, p in snap.items()}
    for i in range(n):
        background(c)
        draw(c, i / fps)
        f = 1 - window(i / fps, 0, dur, 0.45)          # every scene dips to dark at both ends
        if f > 0: c.drawRect(skia.Rect.MakeWH(W, H), fill(BG, f))
        if proc: proc.stdin.write(surf.makeImageSnapshot().tobytes())
        elif i in todo:
            surf.makeImageSnapshot().save(str(todo[i]), skia.kPNG)
            if i >= max(todo): break
    if proc:
        proc.stdin.close(); proc.wait()
    return n
