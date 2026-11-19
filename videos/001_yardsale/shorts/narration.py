"""Narration of the two Shorts. Markup {spoken|shown}: the voice says the left part, the caption shows
the right part. Every shown number is formatted from results.json, never typed in."""
import json, re
from pathlib import Path
from engine import core as E

RES = json.loads((Path(__file__).resolve().parents[1] / "results.json").read_text())
M1K, M100K, SOLO = RES["main"]["1000"], RES["main"]["100000"], RES["solo"]

# exact strings sent to text-to-speech (assert below keeps markup and audio in sync)
TTS = {
    "a1": "A thousand people. A hundred dollars each. They trade at random, and every trade is a fair coin flip. Nobody cheats. Nobody is smarter. Watch.",
    "a2": "After a thousand rounds, the poorest half share seventeen cents. Keep going, and one single person holds eighty-three percent of all the money. Fair rules. A wildly unfair result. The full experiment, and why it happens, is on the channel.",
    "b1": "Win twenty percent, then lose twenty percent. Are you back to a hundred dollars? No. You're at ninety-six.",
    "b2": "Now give one player a hundred fair bets like that, and run it over and over. On average, they end with a hundred dollars. Perfectly fair. But the typical player ends with thirteen. Eighty-six percent finish below where they started. To break even, you'd need fifty-six wins out of a hundred. The full experiment is on the channel.",
}

BOTTOM_1K = E.money(M1K["bottom50"] * 100_000)          # 17¢  (500 people share it; total money is $100,000)
RICHEST = E.pct(M100K["richest"])                        # 83%
MEAN, MEDIAN, LOST = E.money(SOLO["mean"]), E.money(SOLO["median"]), E.pct(SOLO["lost"])   # $100, $13, 86%
TWO = E.money(SOLO["two_step"]); NEED = str(SOLO["wins_needed"])                           # $96, 56

MARKUP = {
    "a1": "{A thousand|1,000} people. {A hundred dollars|$100} each. They trade at random, and every trade is a fair coin flip. Nobody cheats. Nobody is smarter. Watch.",
    "a2": f"After {{a thousand|1,000}} rounds, the poorest half share {{seventeen cents|{BOTTOM_1K}}}. Keep going, and one single person holds {{eighty-three percent|{RICHEST}}} of all the money. Fair rules. A wildly unfair result. The full experiment, and why it happens, is on the channel.",
    "b1": "Win {twenty percent|20%}, then lose {twenty percent|20%}. Are you back to {a hundred dollars|$100}? No. You're at {ninety-six|" + TWO + "}.",
    "b2": f"Now give one player {{a hundred|100}} fair bets like that, and run it over and over. On average, they end with {{a hundred dollars|{MEAN}}}. Perfectly fair. But the typical player ends with {{thirteen|{MEDIAN}}}. {{Eighty-six percent|{LOST}}} finish below where they started. To break even, you'd need {{fifty-six|{NEED}}} wins out of {{a hundred|100}}. The full experiment is on the channel.",
}


def tokens(markup):
    """[(spoken, shown, is_number)] one per caption word."""
    out = []
    for m in re.finditer(r"\{([^|}]*)\|([^}]*)\}(\S*)|(\S+)", markup):
        if m.group(4): out.append((m.group(4), m.group(4), False))
        else: out.append((m.group(1) + m.group(3), m.group(2) + m.group(3), True))
    return out


for k in TTS:
    assert " ".join(s for s, _, _ in tokens(MARKUP[k])) == TTS[k], k

if __name__ == "__main__":
    for s in "ab":
        ks = [k for k in TTS if k[0] == s]
        print(s, sum(len(TTS[k].split()) for k in ks), "words", sum(len(TTS[k]) for k in ks), "chars")
    print(BOTTOM_1K, RICHEST, MEAN, MEDIAN, LOST, TWO, NEED)
