#!/usr/bin/env python3
"""Writes cle.alea: the voices, the timing, the captions, and the numbers
of the exchange: a clock of 23 hours, jumps of 5 (a generator mod 23), the
secrets 6 and 15, the results 8 and 19, the key 2: the classic example,
checked here by Python. The voice says the numbers, so they are the same
in every edition.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from episode import GAP, caption, layout, measure

SEED = "0xa163"
EN_ENGINE = "../voices/kokoro.py"
JA_ENGINE = "../voices/kokoro-ja.py"
NARRATOR = ("af_heart", 0.95)
MASTER = ("jm_kumo", 0.82)

P, G, SA, SB = 23, 5, 6, 15
SEQ = [pow(G, k, P) for k in range(1, P)]           # 5, 2, 10, 4… the generator's walk
PATH = [pow(G, k, P) for k in range(SA + 1)]         # 1, 5, 2, 10, 4, 20, 8
A, B = pow(G, SA, P), pow(G, SB, P)
KEY = pow(B, SA, P)
assert KEY == pow(A, SB, P) and sorted(SEQ) == list(range(1, P))

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。皆が聞いている広場で、どうやって秘密を分かち合えますか。", 0, "The novice asked: in a square where everyone listens, how can two share a secret?"),
        ("m2", "M", "師は言った。それぞれ、数をひとつ選び、誰にも言うな。", 1.2, "Master Foo said: each of you, choose a number, and tell no one."),
        ("m3", "M", "あとは、すべて声に出して言え。", 1.0, "Then say everything else out loud."),
    ], 1.0),
    ("clock", "1 / 4   the clock", [
        ("n1", "N", "Arithmetic on a clock. This one has twenty-three hours.", 0, ""),
        ("n2", "N", "Twenty plus five is not twenty-five: it is two. Numbers wrap around.", 1.0, ""),
        ("n3", "N", "Twenty-three is prime: it cannot be cut into equal parts.", 1.2, ""),
        ("n4", "N", "So jumping by five, again and again, visits every hour before coming back.", 1.2, ""),
    ], 0.8),
    ("oneway", "2 / 4   one way", [
        ("n5", "N", "Forward is easy: start at one, multiply by five six times. You land on eight.", 0, ""),
        ("n6", "N", "Backward is not: from eight, how many jumps? You can only try them all.", 1.2, ""),
        ("n7", "N", "On a clock with hundreds of digits, that takes forever. This is the discrete logarithm.", 1.2, ""),
    ], 0.5),
    ("exchange", "3 / 4   the exchange", [
        ("n8", "N", "Now, two strangers in the square. The clock and the jump are said aloud: twenty-three, five.", 0, ""),
        ("n9", "N", "Each chooses a secret number of jumps, and tells no one: six, and fifteen.", 1.0, ""),
        ("n10", "N", "Each jumps their secret, and says the result: eight, and nineteen.", 1.0, ""),
        ("n11", "N", "Then each takes the other's number, and jumps their own secret again.", 1.2, ""),
        ("n12", "N", "Both land on two. The same number: a key, known to them alone.", 1.0, ""),
        ("n13", "N", "Everyone heard twenty-three, five, eight, nineteen. Without a secret, there is no way to two.", 1.2, ""),
    ], 0.5),
    ("lock", "4 / 4   the lock", [
        ("n14", "N", "This is the lock in your browser: the same idea, with numbers of hundreds of digits.", 0, ""),
        ("n15", "N", "A key no one carried. Made together, in the open.", 1.4, ""),
    ], 0.5),
    ("end", "", [
        ("m4", "M", "広場の皆が、すべての言葉を聞いた。", 0, "Everyone in the square heard every word."),
        ("m5", "M", "そして、鍵を知ったのは二人だけだった。", 1.2, "And only the two of them knew the key."),
        ("m6", "M", "その時、弟子は悟った。", 1.4, "And the novice was enlightened."),
    ], 2.5),
]
TRANSITIONS = ["wipe(0.8, angle: 0, softness: 0.12)", "pixels(0.6, size: 0.05)", "wipe(0.7, angle: 90, softness: 0.1)",
               "morph(0.8, amount: 0.15)", "wipe(0.8, angle: 180, softness: 0.12)", "morph(1.2, amount: 0.2)"]


def alist(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def main():
    total, starts, lengths, at = layout(SCENES, lambda text, who: measure(text, who, HERE, NARRATOR, MASTER, EN_ENGINE, JA_ENGINE))
    S = dict(zip([s[0] for s in SCENES], starts))
    L = dict(zip([s[0] for s in SCENES], lengths))
    allines = [l for s in SCENES for l in s[2]]
    order = [l[0] for l in allines]
    who = {l[0]: l[1] for l in allines}
    text = {l[0]: l[2] for l in allines}
    gaps = {l[0]: l[3] for l in allines}
    english = {l[0]: (l[4] or l[2]) for l in allines}
    firsts = {s[2][0][0] for s in SCENES}

    out = []
    w = out.append
    w("""// Clé — Thus Spoke Master Foo, 04: how do two strangers agree on a secret
// in a square where everyone listens? Arithmetic on a clock of 23 hours: 20
// + 5 = 2; 23 is prime, and jumping by 5 visits every hour (5 is a
// generator mod 23); forward is easy (1 × 5, six times, lands on 8),
// backward is not (from 8, how many jumps? the discrete logarithm). Each
// stranger keeps a secret number of jumps (6, 15), says the result aloud
// (8, 19), jumps their secret again on the other's number, and both land
// on 2: the key, that no one carried. This is the lock in the browser's
// bar, with numbers of hundreds of digits. The numbers are checked by
// gen.py. Master Foo speaks Japanese, translated in the captions.
""")
    for f in ["koan", "clock", "oneway", "exchange", "lock"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Cle {")
    w(f"  let total = {total}")
    w("  let T = t * total")
    w(f'  let EN = "{EN_ENGINE}"')
    w(f'  let JA = "{JA_ENGINE}"')
    w("")
    w("  // ── the voices: the master, in Japanese; the one who explains, in English ──")
    prev = None
    for vid in order:
        voice, speed = NARRATOR if who[vid] == "N" else MASTER
        engine = "EN" if who[vid] == "N" else "JA"
        when = f"{at[vid]:.2f}" if vid in firsts else f"{prev}.end + {gaps[vid] or GAP}"
        w(f'  let {vid} = say("{text[vid]}", at: {when}, engine: {engine}, voice: "{voice}", speed: {speed}, gain: 2.3)')
        prev = vid
    w("")
    w("  // ── the numbers: a clock of 23 hours, jumps of 5; the secrets, the results, the key (gen.py) ──")
    w(f"  let seq = {alist(SEQ)}")
    w(f"  let path = {alist(PATH)}")
    w("")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["カ", "ギ"], episode: "04  ·  key", big: "{KEY}", bigsize: 0.2, bigat: [{lt("m2.start + 0.55 * m2.duration", "koan")}, {lt("m3.end + 5", "koan")}], bigoff: {lt("m3.end + 0.5", "koan")}, accent: {a})',
        "clock": lambda a: f'Clock(seq: seq, add0: {lt("n2.words[0]", "clock")}, add1: {lt("n2.words[4]", "clock")}, prime0: {lt("n3.words[1]", "clock")}, jump0: {lt("n4.words[1]", "clock")}, jump1: {lt("n4.end + 0.8", "clock")}, accent: {a})',
        "oneway": lambda a: f'Oneway(path: path, a: {SA}, A: {A}, fwd0: {lt("n5.words[5]", "oneway")}, fwd1: {lt("n5.words[11]", "oneway")}, back0: {lt("n6.words[9]", "oneway")}, back1: {lt("n6.end + 0.8", "oneway")}, big: {lt("n7.words[2]", "oneway")}, accent: {a})',
        "exchange": lambda a: f'Exchange(a: {SA}, b: {SB}, A: {A}, B: {B}, key: {KEY}, public0: {lt("n8.words[8]", "exchange")}, secret0: {lt("n9.words[2]", "exchange")}, send0: {lt("n10.words[7]", "exchange")}, flight: 0.9 / {L["exchange"]}, '
                              f'again0: {lt("n11.words[2]", "exchange")}, key0: {lt("n12.words[2]", "exchange")}, heard0: {lt("n13.words[1]", "exchange")}, accent: {a})',
        "lock": lambda a: f'Lock(key: {KEY}, bar0: {lt("n14.words[3]", "lock")}, lock0: {lt("n14.words[8]", "lock")}, closing: 2.0 / {L["lock"]}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["カ", "ギ"], episode: "04  ·  key", big: "{KEY}", bigsize: 0.2, bigat: [{lt("m5.start + 0.6 * m5.duration", "end")}, {lt("m6.end + 5", "end")}], bigoff: {lt("m5.end + 0.6", "end")}, accent: {a})',
    }
    w("  let reel = timeline([")
    for k, (sc, _, _, _) in enumerate(SCENES):
        w(f"      scene(ink({args[sc](0)}, {args[sc](1)}), {L[sc]}),  {TRANSITIONS[k]},")
    w("  ], loop: 1)")
    w("")
    w("  // ── over it: the series, the step, the captions (the master's, translated, in vermilion) ──")
    w("  let adv = 0.021722")
    heads = [f'text("{h}", x: 0.06, y: -0.15, size: 0.03, font: "mono", align: "left") * (reel.index > {k} - 0.5) * (reel.index < {k} + 0.5)'
             for k, (_, h, _, _) in enumerate(SCENES) if h]
    w("  let header = merge(" + ", ".join(heads) + ") * 0.7")
    w('  let series = text("thus spoke master foo  ·  04", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
    for k, vid in enumerate(order):
        nxt = order[k + 1] if k + 1 < len(order) else None
        w(caption(vid, english[vid], nxt, who[vid] == "M"))
    w("  let said = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "N") + ")")
    w("  let spoken = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "M") + ")")
    w('  let dark = paint(merge(header, series, said), palette: ["#000000", "#1a1712"], range: [0, 1], alpha: merge(header, series, said))')
    w('  let red  = paint(spoken, palette: ["#000000", "#b8361f"], range: [0, 1], alpha: spoken)')
    w("  let look = film(vignette(overlay(reel, dark, red), amount: 0.06), amount: 0.035)")
    w(f"""
  // ── the sound ──
  let pad = synth {{
    let env = adsr(attack: 3, decay: 1, sustain: 0.9, release: 4)
    lowpass(saw(note.freq) + saw(note.freq * 1.003) + sine(note.freq * 0.5), cutoff: 260 + 300 * note.level, resonance: 0.2) * env
  }}
  let brush = synth {{ bandpass(noise(), cutoff: 1400, resonance: 0.3) * adsr(attack: 0.12, decay: 0.3, sustain: 0.3, release: 0.5) * note.velocity }}
  let tick = synth {{ highpass(noise(), cutoff: 4000, resonance: 0.2) * perc(release: 0.015) * note.velocity + sine(note.freq) * perc(release: 0.05) * 0.4 }}
  let chord = synth {{
    let env = adsr(attack: 0.3, decay: 0.6, sustain: 0.8, release: 2.5)
    chorus(lowpass(saw(note.freq) + saw(note.freq * 1.004) + sine(note.freq * 0.5), cutoff: 1200, resonance: 0.15) * env, depth: 0.6)
  }}
  // the temple bell when the master speaks; the key shown, twice
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern keyshown = repeat 2 event(t: [m2.start + 0.55 * m2.duration, m5.start + 0.6 * m5.duration][i] / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the hand's five hours; the 23 dots; the 22 jumps, each the pitch of its hour
  pattern hours = repeat 5 event(t: (n2.words[0] + (n2.words[4] - n2.words[0]) * (i + 1) / 5) / total, x: 0.5, y: 0.6 - 0.03 * i, intensity: 0.5)
  pattern dots = repeat 23 event(t: (n3.words[1] + {L["clock"]} * 0.006 * i) / total, x: 0.3 + 0.4 * (i % 4) / 3, y: 0.7, intensity: 0.3 + 0.5 * (i >= 20))
  pattern jumps = repeat 22 event(t: (n4.words[1] + (n4.end + 0.8 - n4.words[1]) * ((i + 1) / 22) ^ (1 / 1.6)) / total, x: 0.5 + 0.3 * sin(tau * seq[i] / 23), y: 0.9 - 0.7 * seq[i] / 23, intensity: 0.6)
  // forward: six jumps; backward: the tries; the clock growing
  pattern fwd = repeat 6 event(t: (n5.words[5] + (n5.words[11] - n5.words[5]) * (i + 1) / 6) / total, x: 0.5 + 0.3 * sin(tau * path[i + 1] / 23), y: 0.9 - 0.7 * path[i + 1] / 23, intensity: 0.6)
  pattern back = repeat 6 event(t: (n6.words[9] + (n6.end + 0.8 - n6.words[9]) * (i + 1) / 6) / total, x: 0.4, y: 0.5 - 0.05 * i, intensity: 0.45)
  pattern bigger = repeat 1 event(t: n7.words[2] / total, x: 0.5, y: 0.2, size: 0.2, intensity: 0.7)
  // the exchange: the numbers flying, the two keys landing together
  pattern sends = repeat 2 event(t: (n10.words[7] + i * (0.9 + 0.06 * {L["exchange"]})) / total, x: 0.2 + 0.6 * (1 - i), y: 0.5, size: 0.04, intensity: 0.7)
  pattern keys = repeat 2 event(t: n12.words[2] / total, x: 0.2 + 0.6 * i, y: 0.45, size: 0.1, intensity: 0.8)
  pattern heard = repeat 4 event(t: (n13.words[1] + 0.35 * i) / total, x: 0.5, y: 0.6, intensity: 0.4)
  // the lock closing, as in Requête
  pattern lock = repeat 3 event(t: (n14.words[8] + 2.0) / total, x: 0.5, y: 0.7 - i * 0.15, size: 0.08, intensity: 0.6)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(keyshown, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(hours, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.4),
    notes(dots, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(jumps, instrument: "kalimba", scale: "chromatic", key: 196, gain: 0.45),
    notes(fwd, instrument: "kalimba", scale: "chromatic", key: 196, gain: 0.45),
    notes(back, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.35),
    notes(bigger, instrument: brush, scale: "chromatic", key: 100, gain: 0.5),
    notes(sends, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(keys, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(heard, instrument: "wood", scale: "hirajoshi", key: 220, gain: 0.3),
    notes(lock, instrument: chord, scale: "major", key: 110, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['clock'] + L['clock'] * 0.95) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "cle.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
