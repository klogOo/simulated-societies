"""Build the two vertical Shorts of video 001.
  python build.py                    # render both -> out/001_short_a.mp4, out/001_short_b.mp4
  python build.py --only a           # one of them
  python build.py --preview a:0,5,30 # PNG frames only (fast check), saved in shorts/build/
"""
import argparse, subprocess, sys, time
import multiprocessing as mp
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))

from engine import core as E
from engine import vertical as V

BUILD = HERE / "build"; OUT = ROOT / "out"


def mod(k):
    import short_a, short_b
    return {"a": short_a, "b": short_b}[k]


def render(args):
    k, snap = args
    m = mod(k); t0 = time.time()
    if snap:
        V.render(m.factory(), m.PLAN.total, None, snap={t: BUILD / f"prev_{k}_{t:06.2f}.png" for t in snap})
    else:
        V.render(m.factory(), m.PLAN.total, BUILD / f"short_{k}_video.mp4")
    return k, m.PLAN.total, time.time() - t0


def finish(k):
    from engine import audio
    P = mod(k).PLAN
    wav = BUILD / f"short_{k}_audio.wav"
    audio.mix(P.lines, P.gaps, P.total, wav)
    final = OUT / f"001_short_{k}.mp4"
    subprocess.run([E.FFMPEG, "-y", "-loglevel", "error", "-i", str(BUILD / f"short_{k}_video.mp4"), "-i", str(wav),
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", str(final)], check=True)
    print(f"done: {final}  ({P.total:.2f} s)")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="a,b"); ap.add_argument("--preview")
    a = ap.parse_args()
    BUILD.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    if a.preview:
        k, ts = a.preview.split(":")
        print(render((k, [float(x) for x in ts.split(",")]))); return
    todo = a.only.split(",")
    with mp.Pool(min(2, len(todo))) as pool:                  # at most 2 render processes
        for k, dur, el in pool.imap_unordered(render, [(k, None) for k in todo]):
            print(f"  {k}: {dur:.1f}s of video in {el:.0f}s", flush=True)
    for k in todo: finish(k)


if __name__ == "__main__":
    main()
