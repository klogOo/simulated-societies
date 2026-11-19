"""Shared pieces of the two Shorts: timeline of narration lines, phrase lookup, end card."""
from pathlib import Path
import soundfile as sf
from engine import core as E
from engine import vertical as V
import narration, captions

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "audio"
FPS = V.FPS


class Plan:
    """Lays narration lines and gaps end to end. spec: ["a1", ("gap", "lapse", 3.0), "a2", ("tail", 1.3)]."""
    def __init__(self, spec, lead=0.10, after=0.10):
        self.s, self.e, self.lines, self.gaps, self.words = {}, {}, [], [], []
        t = lead
        for item in spec:
            if isinstance(item, tuple):
                kind, name, secs = item
                self.s[name], self.e[name] = t, t + secs
                if kind == "gap": self.gaps.append((t, t + secs))
                t += secs
            else:
                d = sf.info(str(AUDIO / f"{item}.wav")).duration
                self.s[item], self.e[item] = t, t + d
                self.lines.append((AUDIO / f"{item}.wav", t))
                self.words += captions.words(narration.MARKUP[item], AUDIO / f"{item}.wav", t)
                t += d + after
        n = int(round(t * FPS))
        self.total = n / FPS                     # whole frames
        self.last = (n - 1) / FPS                # time of the last frame (the loop lands exactly here)
        self.cards = captions.chunks(self.words)

    def at(self, phrase, after=0.0):
        """Start time of the first caption word sequence that begins with `phrase` (shown text), after `after`."""
        sh = [w[2] for w in self.words]
        for i in range(len(sh)):
            if self.words[i][0] >= after and " ".join(sh[i:i + 8]).startswith(phrase): return self.words[i][0]
        raise KeyError(phrase)


def end_card(c, a, y=560):
    """Points to the long video. Text only inside the safe area."""
    if a <= 0.003: return
    x0, x1 = V.MARGIN, V.SAFE[2] - 18
    E.panel(c, x0, y, x1 - x0, 430, a)
    E.text(c, "THE FULL EXPERIMENT", x0 + 44, y + 70, 28, E.MUTED, a, 600)
    E.text(c, "Why the Rich", x0 + 44, y + 165, 82, E.INK, a, 700)
    E.text(c, "Get Richer", x0 + 44, y + 255, 82, E.GOLD, a, 700)
    E.text(c, "even in a perfectly fair game", x0 + 44, y + 315, 38, E.INK, a, 500)
    E.text(c, "8-minute video on the channel", x0 + 44, y + 385, 34, E.TEAL, a, 600)
