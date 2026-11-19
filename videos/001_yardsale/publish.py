"""Publish video 001. Usage: python videos/001_yardsale/publish.py  -> prints the video id (saved to published.json)."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from engine import youtube as Y

# SEO: "why the rich get richer" is the strongest YouTube autocomplete phrase for this topic (checked 2026-11-18);
# the thumbnail carries the setup (1,000 people / fair game / 1 winner), so the title carries the question.
TITLE = "Why the Rich Get Richer, Even in a Perfectly Fair Game"
DESCRIPTION = """Why do the rich get richer, even when nobody cheats? A thousand simulated people start with exactly $100 and trade on fair coin flips. Nobody is smarter, nobody is luckier on average. After 100,000 rounds, one of them owns 83% of all the money.

This video runs that wealth inequality experiment (the "yard sale model"), shows why +20% and -20% don't cancel out, tests whether the winner is special or just lucky, adds real skill to the mix, and finds one small rule that stops the collapse.

0:00 A thousand people, one hundred dollars each
0:49 The rules: the yard sale model
1:28 Running it: 10 to 100,000 rounds
2:41 Why +20% and -20% don't cancel
3:31 One player, 100 fair bets, a million times
4:24 10,000 worlds: is the winner special?
5:20 What if some people are better?
6:05 One small rule that stops the collapse
7:11 What this model can't tell you

What we ran
- Main world: 1,000 agents, $100 each, stake = 20% of the poorer partner's wealth, fair coin, 100,000 rounds.
- One player, 100 fair bets of +/-20%, repeated 1,000,000 times.
- 10,000 separate worlds of 100 agents, 3,000 rounds each.
- Talent test: 100 of 1,000 agents win 55% of their flips; 200 runs of 10,000 rounds.
- Flat wealth tax of 0.1% and 1% per round, redistributed equally.

Code and raw results: https://github.com/klogOo/simulated-societies

Sources
- A. Chakraborti, "Distributions of money in model markets of economy" (2002)
- B. Hayes, "Follow the Money", American Scientist (2002), origin of the name "yard sale model"
- B. Boghosian, "Is Inequality Inevitable?", Scientific American (2019)
- US wealth shares: Federal Reserve, Distributional Financial Accounts, Q2 2026

This is a toy model, not a description of a real economy and not financial advice. Narration is synthesized speech; script, simulations, animation and music are original and made with code.

#simulation #economics #probability"""
TAGS = ["why the rich get richer", "wealth inequality", "yard sale model", "simulation", "agent based model",
        "economics explained", "probability", "luck vs skill", "is inequality inevitable", "coin flip",
        "compounding", "game theory", "math", "statistics"]

if __name__ == "__main__":
    out = ROOT / "videos/001_yardsale/published.json"
    state = json.loads(out.read_text()) if out.exists() else {}
    if "id" not in state:
        state["id"] = Y.upload(ROOT / "out/001_yardsale.mp4", TITLE, DESCRIPTION, TAGS); out.write_text(json.dumps(state))
    vid = state["id"]; print("video", vid)
    if not state.get("thumb"):
        Y.set_thumbnail(vid, ROOT / "out/001_yardsale_thumb_A.png"); state["thumb"] = "A"; out.write_text(json.dumps(state))
    if not state.get("captions"):
        Y.add_captions(vid, ROOT / "out/001_yardsale.en.srt"); state["captions"] = ["en"]; out.write_text(json.dumps(state))
    print("https://youtu.be/" + vid)
