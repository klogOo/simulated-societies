"""Writes the upload metadata (titles, description with chapters, tags) -> out/002_talentluck.meta.md
and prints the chapter block for publish.py. Run after build.py (needs build/timeline.json)."""
import json
from pathlib import Path
VID = Path(__file__).resolve().parent; ROOT = VID.parents[1]
tl = json.loads((VID / "build" / "timeline.json").read_text())
NAMES = {"cold": "1,000 careers, 40 years, one verdict", "rules": "The rules: the Talent vs Luck model",
         "rewind": "Replaying the same lives 10,000 times", "exchange": "What is talent worth, in lucky breaks?",
         "record": "Judging by track record (and why luck has an address)", "support": "Who should get the support?",
         "limits": "What this model can't tell you", "outro": "The short answer"}
def ts(t): t = int(t); return f"{t // 60}:{t % 60:02d}"
CHAPTERS = "\n".join(f"{ts(tl['scenes'][k])} {v}" for k, v in NAMES.items())
DURATION = ts(tl["total"])

if __name__ == "__main__":
    import publish as P
    md = f"""# Upload metadata - video 002 ({DURATION})

## Title candidates (<= 60 characters)
1. {P.TITLES[0]}  ({len(P.TITLES[0])} chars)  <- pick
2. {P.TITLES[1]}  ({len(P.TITLES[1])} chars)
3. {P.TITLES[2]}  ({len(P.TITLES[2])} chars)

Why 1: "is success luck" / "is success luck or hard work" lead YouTube autocomplete for this topic (checked 2026-11-18);
"talent vs luck" also autocompletes (it is the paper's title). The thumbnails carry the claim (TALENT ISN'T ENOUGH /
LUCK BEAT TALENT), so the title carries the question and the experiment instead of repeating the claim.

## Description
{P.DESCRIPTION}

## Tags
{", ".join(P.TAGS)}

## Upload settings
- Category: Education (27). Made for kids: No. Paid promotion: No.
- Altered/synthetic content: not required by YouTube's rule (clearly non-realistic animation); the description discloses the synthetic narration anyway.
- Subtitles: out/002_talentluck.en.srt
- Thumbnails to A/B test: out/002_talentluck_thumb_A.png (default), out/002_talentluck_thumb_B.png
- End screen / cards: cannot be set by API. Suggested: end screen element "Video: Why the Rich Get Richer..." (https://youtu.be/AwCPtJZvTmo) over the last 12 s.
"""
    (ROOT / "out" / "002_talentluck.meta.md").write_text(md, encoding="utf-8")
    print(CHAPTERS); print("written", DURATION)
