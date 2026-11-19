"""Soundtrack made from scratch with numpy: ambient pad + plucks + reverb, risers for time-lapses,
narration on top with ducking. No samples, no third-party music -> no Content ID claims."""
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve

SR = 44100
CHORDS = [  # (bass, notes) in Hz : Dm9, Bbmaj7, Fmaj9, C6/9
    (73.42, [146.83, 174.61, 220.00, 261.63, 329.63]),
    (58.27, [116.54, 146.83, 174.61, 220.00, 293.66]),
    (87.31, [174.61, 220.00, 261.63, 329.63, 392.00]),
    (65.41, [196.00, 261.63, 293.66, 329.63, 440.00]),
]
PENTA = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33]


def music(total, seed=3):
    rng = np.random.default_rng(seed)
    n = int(total * SR) + SR
    out = np.zeros((n, 2), np.float32)
    seg, ov = 8.0, 3.0
    t = np.arange(int((seg + ov) * SR)) / SR
    env = np.clip(t / ov, 0, 1) * np.clip((seg + ov - t) / ov, 0, 1)
    env = (env * env * (3 - 2 * env)).astype(np.float32)
    for k in range(int(total / seg) + 1):
        bass, notes = CHORDS[k % 4]
        s = np.zeros((len(t), 2), np.float32)
        for ch, det in ((0, 1.0015), (1, 0.9985)):
            v = 0.9 * np.sin(2 * np.pi * bass * t) + 0.25 * np.sin(2 * np.pi * bass * 2 * t)
            for f in notes:
                ph = rng.random() * 6.283
                v += 0.42 * np.sin(2 * np.pi * f * det * t + ph) + 0.10 * np.sin(2 * np.pi * f * 2 * det * t + ph)
                v += 0.20 * np.sin(2 * np.pi * f / det * t + ph * 1.7)
            s[:, ch] = v
        i0 = int(k * seg * SR); m = min(len(t), n - i0)
        if m > 0: out[i0:i0 + m] += (s * env[:, None])[:m] * 0.06
    # sparse plucks
    td = np.arange(int(2.2 * SR)) / SR
    for i in range(int(total / 1.0)):
        if rng.random() < 0.55:
            f = PENTA[rng.integers(len(PENTA))] * (2 if rng.random() < 0.2 else 1)
            p = (np.sin(2 * np.pi * f * td) + 0.3 * np.sin(4 * np.pi * f * td)) * np.exp(-td / 0.45) * 0.035
            pan = rng.random(); i0 = int((i + rng.choice([0, 0.5])) * SR); m = min(len(td), n - i0)
            out[i0:i0 + m, 0] += p[:m] * (1 - pan); out[i0:i0 + m, 1] += p[:m] * pan
    # reverb
    ti = np.arange(int(2.8 * SR)) / SR
    for ch in (0, 1):
        ir = (rng.standard_normal(len(ti)) * np.exp(-ti / 0.9)).astype(np.float32); ir /= np.sqrt((ir ** 2).sum())
        out[:, ch] = 0.6 * out[:, ch] + 0.5 * fftconvolve(out[:, ch], ir)[:n]
    return out[: int(total * SR)]


def riser(d):
    t = np.arange(int(d * SR)) / SR; u = t / d
    f = 90 * (5.0 ** u)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = (u ** 2) * np.clip((1 - u) / 0.06, 0, 1)
    s = (np.sin(ph) + 0.5 * np.sin(1.5 * ph) + 0.3 * np.sin(2 * ph)) * env * 0.05
    return np.stack([s, s], 1).astype(np.float32)


def mix(lines, gaps, total, out_wav):
    """lines: [(wav_path, start_s)], gaps: [(start_s, end_s)] time-lapse moments."""
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    for path, start in lines:
        x, sr = sf.read(str(path), dtype="float32"); assert sr == SR
        if x.ndim > 1: x = x.mean(1)
        i0 = int(start * SR); m = min(len(x), n - i0); voice[i0:i0 + m] += x[:m]
    voice *= 0.89 / max(1e-6, np.abs(voice).max())
    k = int(0.35 * SR); c = np.cumsum(np.concatenate([[0], np.abs(voice)]))
    env = (c[k:] - c[:-k]) / k; env = np.concatenate([env, np.zeros(n - len(env))])[:n]
    gate = (env > 0.01).astype(np.float32)
    k2 = int(0.6 * SR); c2 = np.cumsum(np.concatenate([np.zeros(k2 // 2), gate, np.zeros(k2)]))
    duck = ((c2[k2:] - c2[:-k2]) / k2)[:n]
    mus = music(total)
    mus *= (1.0 - 0.60 * duck)[:, None] * 0.75   # music sits ~16 dB under the voice
    fade = np.clip(np.arange(n) / (2 * SR), 0, 1) * np.clip((n - np.arange(n)) / (3 * SR), 0, 1)
    mus *= fade[:, None].astype(np.float32)
    for g0, g1 in gaps:
        r = riser(g1 - g0); i0 = int(g0 * SR); m = min(len(r), n - i0); mus[i0:i0 + m] += r[:m]
    out = mus + voice[:, None]
    out /= max(1.0, np.abs(out).max() / 0.97)
    sf.write(str(out_wav), out, SR, subtype="PCM_16")
