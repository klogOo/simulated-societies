"""Thumbnails for video 001 (1280x720).
Design rules (adapted from inference-sh/skills youtube-thumbnail-design + charlie947 youtube-thumbnail):
3 colours max, <=6 words, bold sans + contrast shadow, one focal subject (the winner) with eyes
looking at the text, nothing important in the bottom corners, must read at 120 px wide.
The scene is the simulation's real outcome: one blob owns most of the money, the rest are nearly broke.
Usage: python videos/001_yardsale/thumbnail.py  ->  out/001_yardsale_thumb_{A,B}.png (+ _preview.png)"""
import sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
import numpy as np, skia
from engine import core as E

W, H = 1920, 1080                       # draw at 1080p, save at 1280x720
GX, GY, GR = 1440, 560, 330             # the winner

def crowd(c, rng):
    """999 near-broke blobs packed around the winner, all looking at it."""
    pts = []
    tries = 0
    while len(pts) < 999 and tries < 200000:
        tries += 1
        x, y = rng.uniform(-20, W + 20), rng.uniform(-20, H + 20)
        d = math.hypot(x - GX, y - GY)
        if d < GR + 26: continue
        if x < 1060 and 120 < y < 960 and rng.random() < 0.93: continue   # keep the text area mostly clear
        pts.append((x, y))
    for x, y in pts:
        d = math.hypot(x - GX, y - GY)
        r = rng.uniform(9, 15) * (0.75 + 0.5 * math.exp(-(d - GR) / 500))
        lx, ly = (GX - x) / d, (GY - y) / d
        a = 0.95 if x > 1000 else 0.45
        E.blob(c, x, y, r, E.SLATE, a, look=(lx, ly))

def winner(c):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((GX, GY), GR * 1.9, [E.col(E.GOLD, 0.45), E.col(E.GOLD, 0.0)]))
    c.drawCircle(GX, GY, GR * 1.9, p)
    E.blob(c, GX, GY, GR, E.GOLD, look=(-0.9, -0.25))
    # open "wow" mouth: the winner is as surprised as everyone else
    c.drawOval(skia.Rect.MakeXYWH(GX - 40, GY + 95, 80, 62), E.fill((70, 40, 10)))

def headline(c, s, y, size, rgb, x=90):
    f = E.font(size, 700)
    sh = skia.Paint(AntiAlias=True, Color=E.col((0, 0, 0), 0.75))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    c.drawString(s, x + 6, y + 8, f, sh)
    c.drawString(s, x, y, f, E.fill(rgb))
    return f.measureText(s)

VARIANTS = {   # (text, colour, size, baseline)
    "A": [("1,000 PEOPLE", E.INK, 150, 330), ("A FAIR GAME", E.TEAL, 150, 500), ("ONLY 1 WINNER", E.GOLD, 132, 680)],
    "B": [("FAIR GAME.", E.TEAL, 170, 360), ("ONE PLAYER", E.INK, 130, 540), ("OWNS 83%", E.GOLD, 170, 730)],
}

out_dir = ROOT / "out"; previews = []
for name, lines in VARIANTS.items():
    s = skia.Surface(W, H); c = s.getCanvas()
    E.background(c); rng = np.random.default_rng(7)
    crowd(c, rng); winner(c)
    for txt, rgb, size, y in lines:
        w = headline(c, txt, y, size, rgb)
        assert 90 + w < GX - GR - 10, f"{name}: '{txt}' runs into the winner ({90 + w:.0f}px)"
    img = s.makeImageSnapshot().resize(1280, 720, skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    path = out_dir / f"001_yardsale_thumb_{name}.png"; img.save(str(path), skia.kPNG); print(path)
    previews.append(img)

# 120px / 320px check sheet: how it looks in the feed and in mobile search
ps = skia.Surface(2 * 340 + 30, 400); pc = ps.getCanvas(); pc.clear(skia.Color(255, 255, 255))
for i, img in enumerate(previews):
    x = 10 + i * 350
    pc.drawImageRect(img, skia.Rect.MakeXYWH(x, 10, 320, 180), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    pc.drawImageRect(img, skia.Rect.MakeXYWH(x, 210, 120, 68), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
ps.makeImageSnapshot().save(str(out_dir / "001_yardsale_thumb_preview.png"), skia.kPNG)
