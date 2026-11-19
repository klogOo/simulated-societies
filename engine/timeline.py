"""Cue sheet for one scene: narration lines and named gaps laid end to end."""
import re


def _weights(text):
    cum, tot = [], 0.0
    for ch in text:
        cum.append(tot)
        tot += 1 + (7 if ch in ".?!:" else 3 if ch in ",;" else 0)   # punctuation = pause
    return cum, tot


class Cues:
    def __init__(self, spec, durs, texts, pad=0.65):
        """spec items: "line_id" or ("gap", name, seconds)."""
        self._s, self._e, self.texts, self.lines, self.gaps = {}, {}, texts, [], []
        t = 0.3
        for item in spec:
            if isinstance(item, tuple):
                _, name, secs = item
                self._s[name], self._e[name] = t, t + secs
                self.gaps.append((name, t, t + secs)); t += secs
            else:
                self._s[item], self._e[item] = t, t + durs[item]
                self.lines.append((item, t)); t += durs[item] + pad
        self.total = t + 0.3

    def s(self, k): return self._s[k]
    def e(self, k): return self._e[k]

    def at(self, line, phrase, lead=0.0):
        """Approximate time a phrase is spoken (speech is ~linear in characters + pauses)."""
        text = self.texts[line]; i = text.index(phrase)
        cum, tot = _weights(text)
        return self._s[line] + (self._e[line] - self._s[line]) * 0.985 * cum[i] / tot + lead

    def sentences(self):
        """[(start, end, sentence)] for captions."""
        out = []
        for lid, _ in self.lines:
            text = self.texts[lid]; cum, tot = _weights(text); d = self._e[lid] - self._s[lid]
            for m in re.finditer(r"[^.?!]+[.?!]+", text):
                a = self._s[lid] + d * cum[m.start()] / tot
                b = self._s[lid] + d * (cum[m.end() - 1] + 1) / tot
                out.append((a, min(b, self._e[lid]), m.group().strip()))
        return out
