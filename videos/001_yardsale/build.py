"""Build video 001.
  python build.py                      # render everything -> out/001_yardsale.mp4
  python build.py --only hook,run      # re-render some scenes, reuse the rest (--only none: remix audio only)
  python build.py --preview run:5,40   # save PNG frames of one scene at given seconds (fast check)
"""
import argparse, json, subprocess, sys, time
import multiprocessing as mp
from pathlib import Path

VID = Path(__file__).resolve().parent
ROOT = VID.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(VID))

import soundfile as sf
from engine import core as E
from engine.timeline import Cues
import script

BUILD = VID / "build"; OUT = ROOT / "out"
TEXT = {lid: txt for _, ls in script.SCENES for lid, txt in ls}
ORDER = [sid for sid, _ in script.SCENES]


def cues(sid):
    import scenes
    durs = {lid: sf.info(str(VID / "audio" / f"{lid}.wav")).duration for lid in TEXT}
    return Cues(scenes.SPEC[sid], durs, TEXT)


def render_scene(args):
    sid, fps, snap = args
    import scenes
    q = cues(sid); t0 = time.time()
    draw = getattr(scenes, sid)(q)
    if snap:
        E.render(draw, q.total, None, fps, snap={t: BUILD / f"prev_{sid}_{t:06.2f}.png" for t in snap})
    else:
        E.render(draw, q.total, BUILD / f"{sid}.mp4", fps)
    return sid, q.total, time.time() - t0


def srt_time(t):
    ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only"); ap.add_argument("--preview"); ap.add_argument("--fps", type=int, default=E.FPS)
    ap.add_argument("--jobs", type=int, default=5)
    a = ap.parse_args()
    BUILD.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

    if a.preview:
        sid, ts = a.preview.split(":")
        print(render_scene((sid, 10, [float(x) for x in ts.split(",")])))
        return

    todo = [] if a.only == "none" else a.only.split(",") if a.only else ORDER      # --only none = remix audio only
    if todo:
        with mp.Pool(min(a.jobs, len(todo))) as pool:
            for sid, dur, el in pool.imap_unordered(render_scene, [(s, a.fps, None) for s in todo]):
                print(f"  {sid}: {dur:.1f}s of video in {el:.0f}s", flush=True)

    # timeline of the whole film (scene length = whole frames, so audio never drifts)
    offs, t, lines, gaps, subs = {}, 0.0, [], [], []
    for sid in ORDER:
        q = cues(sid); offs[sid] = t
        lines += [(VID / "audio" / f"{lid}.wav", t + s) for lid, s in q.lines]
        gaps += [(t + g0, t + g1) for name, g0, g1 in q.gaps if name not in ("out", "title", "end")]
        subs += [(t + s, t + e, txt) for s, e, txt in q.sentences()]
        t += round(q.total * a.fps) / a.fps
    total = t
    (BUILD / "concat.txt").write_text("".join(f"file '{(BUILD / (s + '.mp4')).as_posix()}'\n" for s in ORDER))
    from engine import audio
    audio.mix(lines, gaps, total, BUILD / "audio.wav")
    final = OUT / "001_yardsale.mp4"
    subprocess.run([E.FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(BUILD / "concat.txt"),
                    "-i", str(BUILD / "audio.wav"), "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)], check=True)
    (OUT / "001_yardsale.en.srt").write_text(
        "".join(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{txt}\n\n" for i, (s, e, txt) in enumerate(subs, 1)), encoding="utf-8")
    (BUILD / "timeline.json").write_text(json.dumps({"total": total, "scenes": offs}, indent=1))
    print(f"done: {final}  ({total / 60:.2f} min)")


if __name__ == "__main__":
    main()
