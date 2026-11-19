"""Flicker meter. I can't watch the video, so this measures it.
For each 2-second window it decodes the frames and reports, over the pixels where anything happens:
  blink  = energy of pixels that change and immediately change BACK (A -> B -> A). This is flicker.
  motion = plain frame-to-frame change. A bubble gliding across the screen scores here, not in blink.
(An earlier version used the temporal second difference; that is ~2x motion for any moving hard edge,
so it cannot tell a smooth time-lapse from shimmer. Kept out on purpose.)
Usage: python -m engine.flicker out/video.mp4 3 12 118 ...   (window start times, seconds)"""
import subprocess, sys
import numpy as np
import imageio_ffmpeg

W, H = 960, 540


def measure(path, t0, dur=2.0):
    raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error", "-ss", str(t0), "-t", str(dur), "-i", str(path),
                          "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    a, b = f[1:-1] - f[:-2], f[2:] - f[1:-1]
    blink = np.where(a * b < 0, np.minimum(np.abs(a), np.abs(b)), 0.0)
    motion = np.abs(f[1:] - f[:-1])
    active = motion.mean(0) > 0.05
    if not active.any(): return 0.0, 0.0, 0.0
    return float(blink[:, active].mean()), float(motion[:, active].mean()), float(active.mean())


if __name__ == "__main__":
    for t in sys.argv[2:]:
        bl, mo, area = measure(sys.argv[1], float(t))
        print(f"t={float(t):6.1f}s  blink={bl:5.2f}  motion={mo:5.2f}  moving area={area * 100:4.1f}%")
