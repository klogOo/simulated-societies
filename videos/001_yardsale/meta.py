"""Writes the upload metadata (title, description with chapters, tags) -> out/001_yardsale.meta.md
Run after build.py (needs build/timeline.json)."""
import json
from pathlib import Path
VID = Path(__file__).resolve().parent; ROOT = VID.parents[1]
tl = json.loads((VID / "build" / "timeline.json").read_text())
NAMES = {"hook": "A thousand people, one hundred dollars each", "rules": "The rules: the yard sale model",
         "run": "Running it: 10 to 100,000 rounds", "why": "Why +20% and -20% don't cancel",
         "solo": "One player, 100 fair bets, a million times", "worlds": "10,000 worlds: is the winner special?",
         "talent": "What if some people are better?", "tax": "One small rule that stops the collapse",
         "outro": "What this model can't tell you"}
def ts(t): t = int(t); return f"{t // 60}:{t % 60:02d}"
chapters = "\n".join(f"{ts(tl['scenes'][k])} {v}" for k, v in NAMES.items())
REPO = "<REPO_URL>"   # filled in when the public repository exists

md = f"""# Upload metadata - video 001

## Title (A/B candidates)
1. I Gave 1,000 People the Same Money. One Ended Up With 83% of It.
2. Why a Perfectly Fair Game Makes One Person Rich
3. 100,000 Fair Coin Flips Later, One Person Owns Everything

## Description
A thousand simulated people start with exactly $100. They trade on fair coin flips: nobody is smarter, nobody cheats. After 100,000 rounds, one of them holds 83% of all the money. This video runs the experiment, shows why it happens, and tests what changes it.

Everything on screen comes from simulations written for this video. Code and raw results: {REPO}

{chapters}

What we ran
- Main world: 1,000 agents, $100 each, stake = 20% of the poorer partner's wealth, fair coin, 100,000 rounds.
- One player, 100 fair bets of +/-20%, repeated 1,000,000 times.
- 10,000 separate worlds of 100 agents, 3,000 rounds each.
- Talent test: 100 of 1,000 agents win 55% of their flips; 200 runs of 10,000 rounds.
- Flat wealth tax of 0.1% and 1% per round, redistributed equally.

Sources
- A. Chakraborti, "Distributions of money in model markets of economy" (2002)
- B. Hayes, "Follow the Money", American Scientist (2002) - origin of the name "yard sale model"
- B. Boghosian, "Is Inequality Inevitable?", Scientific American (2019)
- US wealth shares: Federal Reserve, Distributional Financial Accounts, Q2 2026

This is a toy model, not a description of a real economy and not financial advice. Narration is synthesized speech; script, simulations, animation and music are original and made with code.

## Tags
wealth inequality, simulation, yard sale model, probability, economics explained, game theory, luck vs skill, coin flip, compounding, agent-based model, math, statistics

## Upload settings
- Category: Education. Made for kids: No. Paid promotion: No.
- Altered/synthetic content: not required by YouTube's rule (clearly non-realistic animation); the description discloses the synthetic narration anyway.
- Subtitles: out/001_yardsale.en.srt
- Thumbnails to A/B test: out/001_yardsale_thumb_A.png, out/001_yardsale_thumb_B.png
"""
(ROOT / "out" / "001_yardsale.meta.md").write_text(md, encoding="utf-8")
print("written")
