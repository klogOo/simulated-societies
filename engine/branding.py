"""Channel art: avatar (800x800) and banner (2048x1152, text inside the 1235x338 all-device safe area).
Usage: python -m engine.branding -> out/channel_avatar.png, out/channel_banner.png"""
import math
from pathlib import Path
import numpy as np, skia
from engine import core as E

OUT = Path(__file__).resolve().parents[1] / "out"

def glow(c, x, y, r, rgb, a):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((x, y), r, [E.col(rgb, a), E.col(rgb, 0.0)]))
    c.drawCircle(x, y, r, p)

def bg(c, w, h):
    c.clear(E.col(E.BG))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((w / 2, h / 2), max(w, h) * 0.6, [E.col((26, 36, 66)), E.col(E.BG)]))
    c.drawRect(skia.Rect.MakeWH(w, h), p)

def avatar():
    s = skia.Surface(800, 800); c = s.getCanvas(); bg(c, 800, 800)
    glow(c, 400, 420, 380, E.GOLD, 0.35)
    E.blob(c, 400, 420, 250, E.GOLD, look=(0.0, 0.0))
    for x, y, r in [(150, 640, 34), (660, 650, 30), (120, 200, 26), (690, 190, 24)]:
        E.blob(c, x, y, r, E.TEAL, look=((400 - x) / 300, (420 - y) / 300))
    s.makeImageSnapshot().save(str(OUT / "channel_avatar.png"), skia.kPNG)

def banner():
    W, H = 2048, 1152; s = skia.Surface(W, H); c = s.getCanvas(); bg(c, W, H)
    rng = np.random.default_rng(3)
    cx, cy = W / 2, H / 2
    for _ in range(1400):                                     # the crowd, outside the safe area text
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        if abs(x - cx) < 640 and abs(y - cy) < 190: continue
        d = math.hypot(x - (cx + 520), y - cy)
        rgb = E.TEAL if rng.random() < 0.25 else E.SLATE
        E.blob(c, x, y, rng.uniform(8, 16), rgb, 0.8, look=((cx + 520 - x) / d, (cy - y) / d))
    glow(c, cx + 520, cy, 260, E.GOLD, 0.35)
    E.blob(c, cx + 520, cy, 130, E.GOLD, look=(-0.9, 0.0))
    E.text(c, "SIMULATED", cx - 600, cy - 18, 120, E.INK, 1, 700)
    E.text(c, "SOCIETIES", cx - 600, cy + 92, 120, E.GOLD, 1, 700)
    E.text(c, "We don't argue. We simulate.", cx - 596, cy + 150, 40, E.MUTED, 1, 500)
    s.makeImageSnapshot().save(str(OUT / "channel_banner.jpg"), skia.kJPEG, 92)

if __name__ == "__main__":
    avatar(); banner(); print("ok")
