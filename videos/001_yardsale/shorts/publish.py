"""Publish the two Shorts cut from video 001. Usage: python videos/001_yardsale/shorts/publish.py
A goes public now; B is scheduled (publishAt). State in shorts/published.json so reruns never upload twice."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from engine import youtube as Y

FULL = "https://youtu.be/AwCPtJZvTmo"
DISC = "Narration is synthesized speech; simulation, animation and music are original and made with code."
SHORTS = {
 "a": dict(file="out/001_short_a.mp4", publish_at=None,
           title="1,000 People, Fair Coin Flips. One Ends Up With 83%.",
           description=("1,000 people start with $100 each and trade on fair coin flips. Nobody cheats, nobody is smarter, "
                        "and one person still ends up with 83% of all the money.\n"
                        f"Full experiment, and why it happens: {FULL}\n{DISC}\n#shorts #inequality #simulation"),
           tags=["why the rich get richer", "wealth inequality", "simulation", "yard sale model", "coin flip", "economics", "probability"]),
 "b": dict(file="out/001_short_b.mp4", publish_at="2026-11-19T22:00:00Z",
           title="Win 20%, Lose 20%. Why Aren't You Back to $100?",
           description=("+20% then -20% leaves you at $96. Give one player 100 fair bets like that: the average still ends at $100, "
                        "but the typical player ends with $13 and 86% finish below where they started.\n"
                        f"Full experiment: {FULL}\n{DISC}\n#shorts #math #probability"),
           tags=["probability", "math", "volatility drag", "coin flip", "simulation", "compounding", "why the rich get richer"]),
}

if __name__ == "__main__":
    out = Path(__file__).with_name("published.json")
    state = json.loads(out.read_text()) if out.exists() else {}
    for k, s in SHORTS.items():
        if k in state: print(k, "already uploaded", state[k]); continue
        vid = Y.upload(ROOT / s["file"], s["title"], s["description"], s["tags"], publish_at=s["publish_at"])
        state[k] = {"id": vid, "publish_at": s["publish_at"] or "now"}; out.write_text(json.dumps(state))
        print(k, "https://youtube.com/shorts/" + vid, s["publish_at"] or "public now")
