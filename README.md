# Simulated Societies

Code behind the YouTube channel [Simulated Societies](https://www.youtube.com/@SimulatedSocieties): *We don't argue. We simulate.*

Every video asks one question about how the world works and answers it by running a simulation written for that video. This repository holds those simulations, the raw numbers quoted in each video, and the small engine that turns them into animation.

## Videos

| # | Video | Folder | Model |
|---|---|---|---|
| 001 | [Why the Rich Get Richer, Even in a Perfectly Fair Game](https://youtu.be/AwCPtJZvTmo) | `videos/001_yardsale` | Yard-sale model of wealth exchange (`sims/yardsale.py`) |
| 002 | Is Success Just Luck? We Replayed 1,000 Lives 10,000 Times | `videos/002_talentluck` | Talent vs Luck, Pluchino, Biondo & Rapisarda 2018 (`sims/talentluck.py`) |

## Run the experiments yourself

Python 3.12.

```
pip install -r requirements.txt
python videos/001_yardsale/experiments.py
python videos/002_talentluck/experiments.py
```

Each script uses fixed seeds and writes `results.json` in its folder. Every number spoken or shown in a video comes from that file, so you can change a rule in `sims/` or a parameter in `experiments.py`, run it again and see what moves.

## What is where

- `sims/`: the models, plain NumPy.
- `videos/NNN_name/experiments.py` and `results.json`: what was run for the video, and what came out.
- `videos/NNN_name/script.py`: the narration, written after the experiments.
- `videos/NNN_name/scenes.py`, `build.py`: the animation (Skia frames piped to ffmpeg).
- `engine/`: drawing helpers, the bubble world, the synthesized soundtrack, a flicker meter.

The narration audio is synthesized speech and is not included, so `build.py` will not render a full video without your own audio files in `videos/NNN_name/audio/`. The experiments run without it.

## Caveats

These are toy models. They are built to isolate one mechanism, not to describe a real economy or a real career, and nothing here is financial or career advice.

## License

MIT for the code (see `LICENSE`). The Space Grotesk font in `assets/fonts` is under the SIL Open Font License.
