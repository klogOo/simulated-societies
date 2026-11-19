"""Vertical (9:16) output for Shorts. Adds to engine.core without changing it: same palette, font,
blobs and background look, on a 1080x1920 canvas, and no forced dip-to-black (Shorts loop).

Shorts UI covers the top 10%, the bottom 20% and the right 15% of the frame; SAFE is what is left."""
import subprocess
import skia
from . import core as E

VW, VH, FPS = 1080, 1920, 30
SAFE = (0, int(VH * 0.10), int(VW * 0.85), int(VH * 0.80))      # x0, y0, x1, y1 = 0, 192, 918, 1536
MARGIN = 64
CX = (MARGIN + SAFE[2]) / 2                                       # horizontal centre of the usable area

_bg = {}
def background(c, w=VW, h=VH):
    """Same radial glow + dot grid as core.background, sized for any canvas."""
    if (w, h) not in _bg:
        s = skia.Surface(w, h); k = s.getCanvas(); k.clear(E.col(E.BG))
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeRadial((w / 2, h * 0.46), max(w, h) * 0.55,
                    [E.col((26, 36, 66)), E.col(E.BG)]))
        k.drawRect(skia.Rect.MakeWH(w, h), p)
        dot = E.fill((255, 255, 255), 0.035)
        for gx in range(30, w, 60):
            for gy in range(30, h, 60): k.drawCircle(gx, gy, 1.6, dot)
        _bg[(w, h)] = s.makeImageSnapshot()
    c.drawImage(_bg[(w, h)], 0, 0)


def fit_size(s, size, weight, max_w):
    """Largest font size <= size at which s fits in max_w."""
    w = E.font(size, weight).measureText(s)
    return size if w <= max_w else size * max_w / w


def render(draw, dur, out, fps=FPS, w=VW, h=VH, snap=None):
    """Like core.render, but any canvas size and no fade at the ends (draw() owns every frame).
    snap = {t: png_path} saves only those frames (preview) and writes no video."""
    surf = skia.Surface(w, h); c = surf.getCanvas()
    n = int(round(dur * fps)); proc = None; todo = None
    if snap is None:
        proc = subprocess.Popen([E.FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                                 "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                 "-crf", "17", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    else:
        todo = {min(n - 1, int(round(t * fps))): p for t, p in snap.items()}
    for i in range(n):
        background(c, w, h)
        draw(c, i / fps)
        if proc: proc.stdin.write(surf.makeImageSnapshot().tobytes())
        elif i in todo:
            surf.makeImageSnapshot().save(str(todo[i]), skia.kPNG)
            if i >= max(todo): break
    if proc:
        proc.stdin.close(); proc.wait()
    return n
