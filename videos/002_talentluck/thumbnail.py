"""Thumbnails for video 002 (1280x720). Same brand family as 001 (palette, font, blob characters, dark field)
but a different concept: one focal blob, no crowd.
  A: the most talented blob (brightest talent colour) while lucky breaks drift past it.   "TALENT ISN'T ENOUGH"
  B: an average blob hit by one big lucky break (gold ring), growing.                      "LUCK BEAT TALENT"
Rules: one focal object, <= 3 big words, 3 main colours, legible at 168x94 (preview sheet is rendered too).
Usage: python videos/002_talentluck/thumbnail.py -> out/002_talentluck_thumb_{A,B}.png + _preview.png"""
import sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
import numpy as np, skia
from engine import core as E
from engine.field import talent_rgb

W, H = 1920, 1080


def glow(c, x, y, r, rgb, a):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((x, y), r, [E.col(rgb, a), E.col(rgb, 0.0)])); c.drawCircle(x, y, r, p)


def dot(c, x, y, r, rgb, a=1.0):
    c.drawCircle(x, y, r * 2.1, E.fill(rgb, 0.16 * a)); c.drawCircle(x, y, r, E.fill(rgb, a))


def headline(c, s, y, size, rgb, x=90):
    f = E.font(size, 700)
    sh = skia.Paint(AntiAlias=True, Color=E.col((0, 0, 0), 0.75)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    c.drawString(s, x + 6, y + 8, f, sh); c.drawString(s, x, y, f, E.fill(rgb))
    return f.measureText(s)


def variant_a(c):
    gx, gy, gr = 1450, 610, 300
    rng = np.random.default_rng(3)
    for k in range(26):                                   # lucky breaks drifting past, all missing
        t = k / 25
        x = lerp_(1000, 1900, rng.random()); y = lerp_(40, 1060, rng.random())
        if math.hypot(x - gx, y - gy) < gr + 70 or x < 1120: continue
        dot(c, x, y, rng.uniform(11, 17), E.GOLD if rng.random() < 0.7 else E.CORAL, 0.9)
    glow(c, gx, gy, gr * 1.7, (205, 255, 246), 0.22)
    E.blob(c, gx, gy, gr, talent_rgb(0.91), look=(0.55, -0.85))
    c.drawOval(skia.Rect.MakeXYWH(gx - 34, gy + 105, 68, 30), E.fill((30, 60, 70)))       # a flat, unimpressed mouth
    return [("TALENT", E.INK, 190, 380), ("ISN'T", E.INK, 150, 560), ("ENOUGH", E.GOLD, 190, 760)], gx - gr


def variant_b(c):
    gx, gy, gr = 1440, 600, 270
    glow(c, gx, gy, gr * 1.9, E.GOLD, 0.30)
    c.drawCircle(gx, gy, gr + 38, E.stroke(E.GOLD, 14, 0.95)); c.drawCircle(gx, gy, gr + 78, E.stroke(E.GOLD, 6, 0.45))
    E.blob(c, gx, gy, gr, talent_rgb(0.55), look=(-0.6, -0.8))
    c.drawOval(skia.Rect.MakeXYWH(gx - 42, gy + 92, 84, 70), E.fill((20, 50, 52)))         # "wow"
    dot(c, gx - 250, gy - 300, 46, E.GOLD)                                                    # the lucky break that hit it
    return [("LUCK", E.GOLD, 220, 400), ("BEAT", E.INK, 170, 590), ("TALENT", E.TEAL, 170, 780)], gx - gr - 80


def lerp_(a, b, t): return a + (b - a) * t


out_dir = ROOT / "out"; previews = []
for name, fn in (("A", variant_a), ("B", variant_b)):
    s = skia.Surface(W, H); c = s.getCanvas(); E.background(c)
    lines, limit = fn(c)
    for txt, rgb, size, y in lines:
        w = headline(c, txt, y, size, rgb)
        assert 90 + w < limit - 10, f"{name}: '{txt}' runs into the blob ({90 + w:.0f}px > {limit:.0f})"
    img = s.makeImageSnapshot().resize(1280, 720, skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    path = out_dir / f"002_talentluck_thumb_{name}.png"; img.save(str(path), skia.kPNG); print(path)
    previews.append(img)

# feed-size check sheet: 320x180 (search) and 168x94 (suggested / home on small screens)
ps = skia.Surface(2 * 340 + 30, 320); pc = ps.getCanvas(); pc.clear(skia.Color(255, 255, 255))
for i, img in enumerate(previews):
    x = 10 + i * 350
    pc.drawImageRect(img, skia.Rect.MakeXYWH(x, 10, 320, 180), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    pc.drawImageRect(img, skia.Rect.MakeXYWH(x, 210, 168, 94), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
ps.makeImageSnapshot().save(str(out_dir / "002_talentluck_thumb_preview.png"), skia.kPNG)
