#!/usr/bin/env python3
"""Writes neurone.alea: the voices, the timing, the captions. The
perceptron itself lives in the work: the edition draws the points, and the
weights are grown step by step by the perceptron rule (alea's `grow`), so
every edition learns its own line.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from episode import GAP, caption, layout, measure

SEED = "0xa1a1"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 0.95)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、どうやって学ぶのですか。", 0, "The novice asked: how does a machine learn?"),
        ("m2", "M", "師は、皿が二つある秤を渡した。", 1.2, "Master Foo handed him a scale with 2 pans."),
        ("m3", "M", "師は言った。重りを置け。間違えたら、動かせ。", 1.2, "Master Foo said: put the weights on. When it is wrong, move them."),
    ], 1.0),
    ("cell", "1 / 4   the cell", [
        ("n1", "N", "A neuron is a small machine. Inputs come in, each through a wire with a weight.", 0, ""),
        ("n2", "N", "It adds them up: a heavy weight counts more. If the sum passes a threshold, it fires: one. If not: zero.", 1.2, "It adds them up: a heavy weight counts more. If the sum passes a threshold, it fires: 1. If not: 0."),
    ], 1.0),
    ("line", "2 / 4   the line", [
        ("n3", "N", "With two inputs, the neuron draws a line. On one side it fires, on the other it does not.", 0, "With 2 inputs, the neuron draws a line. On 1 side it fires, on the other it does not."),
        ("n4", "N", "At first the weights are random, and the line is wrong.", 1.2, ""),
    ], 0.8),
    ("learn", "3 / 4   the rule", [
        ("n5", "N", "Learning is a rule: show it a point. If it is wrong, move the weights a little toward the right answer.", 0, ""),
        ("n6", "N", "Point by point, the line swings. After a few passes, it is never wrong again.", 1.2, ""),
        ("n7", "N", "That is a perceptron, from nineteen fifty-eight. One cell. It can learn any line.", 1.4, "That is a perceptron, from 1958. 1 cell. It can learn any line."),
    ], 1.0),
    ("xor", "4 / 4   the limit", [
        ("n8", "N", "But some problems are not a line: here, the opposite corners go together.", 0, ""),
        ("n9", "N", "One neuron can swing forever and never find it. For that, you need several, in layers. Next time.", 1.2, "1 neuron can swing forever and never find it. For that, you need several, in layers. Next time."),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "千回の間違いのあと、秤は正しく傾いた。", 0, "After 1 000 mistakes, the scale tipped right."),
        ("m5", "M", "師は言った。一つの秤では、引けない線もある。", 1.2, "Master Foo said: there are lines 1 scale cannot draw."),
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
    w("""// Neurone — Thus Spoke Master Foo, AI 01: the perceptron. A novice asks
// how a machine learns; Master Foo hands him a scale with two pans. A
// neuron: inputs on weighted wires, a sum, a threshold, it fires or not.
// With two inputs it is a line; at first the line is wrong; the rule
// (show it a point; if wrong, move the weights toward the answer) swings
// the line until it is never wrong again (Rosenblatt, 1958). Then the
// limit: the opposite corners together, which no line separates. The
// edition draws the points; the weights are grown step by step by the
// rule itself (`grow`), so each edition learns its own line. Master Foo
// speaks Japanese, translated in the captions.
""")
    for f in ["koan", "cell", "line", "learn"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Neurone {")
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
    w("""  // ── the points: two kinds, drawn by the edition; and the four corners, the opposite ones together ──
  let N = 12
  let px = join([~between(0.1, 0.4) for q in range(6)], [~between(0.6, 0.9) for q in range(6)])
  let py = join([~between(0.2, 0.5) for q in range(6)], [~between(0.5, 0.8) for q in range(6)])
  let lab = join([-1 for q in range(6)], [1 for q in range(6)])
  let qx = [0.22 + ~between(-0.05, 0.05), 0.78 + ~between(-0.05, 0.05), 0.22 + ~between(-0.05, 0.05), 0.78 + ~between(-0.05, 0.05)]
  let qy = [0.22 + ~between(-0.05, 0.05), 0.78 + ~between(-0.05, 0.05), 0.78 + ~between(-0.05, 0.05), 0.22 + ~between(-0.05, 0.05)]
  let qlab = [1, 1, -1, -1]
  // ── the perceptron, grown: at each step one point is shown (step k, point k mod N);
  // if it is on the wrong side, the weights move a little toward it (the x * 0 keeps the rule
  // alive: a rule that reads neither x nor y is folded into a constant) ──
  let S = 144
  let lr = 0.12
  let w10 = 0.15
  let w20 = -0.25
  let b0 = 0.05
  grow over 4 for 144 {
    w1 = w10
      then w1 + x * 0 + lr * sum([((floor(t * S + 0.5) % N) == q) * (lab[q] * (w1 * px[q] + w2 * py[q] + b) <= 0) * lab[q] * px[q] for q in range(N)])
    w2 = w20
      then w2 + x * 0 + lr * sum([((floor(t * S + 0.5) % N) == q) * (lab[q] * (w1 * px[q] + w2 * py[q] + b) <= 0) * lab[q] * py[q] for q in range(N)])
    b = b0
      then b + x * 0 + lr * sum([((floor(t * S + 0.5) % N) == q) * (lab[q] * (w1 * px[q] + w2 * py[q] + b) <= 0) * lab[q] for q in range(N)])
    v1 = 0.3
      then v1 + x * 0 + lr * sum([((floor(t * S + 0.5) % 4) == q) * (qlab[q] * (v1 * qx[q] + v2 * qy[q] + c) <= 0) * qlab[q] * qx[q] for q in range(4)])
    v2 = 0.2
      then v2 + x * 0 + lr * sum([((floor(t * S + 0.5) % 4) == q) * (qlab[q] * (v1 * qx[q] + v2 * qy[q] + c) <= 0) * qlab[q] * qy[q] for q in range(4)])
    c = -0.2
      then c + x * 0 + lr * sum([((floor(t * S + 0.5) % 4) == q) * (qlab[q] * (v1 * qx[q] + v2 * qy[q] + c) <= 0) * qlab[q] for q in range(4)])
  }
""")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ニ", "ュ", "ー", "ロ", "ン"], episode: "AI 01  ·  neuron", accent: {a})',
        "cell": lambda a: f'Cell(inputs0: {lt("n1.words[5]", "cell")}, wires0: {lt("n1.words[10]", "cell")}, sum0: {lt("n2.words[1]", "cell")}, thresh0: {lt("n2.words[14]", "cell")}, fire0: {lt("n2.words[16]", "cell")}, again0: {lt("n2.words[18]", "cell")}, accent: {a})',
        "line": lambda a: f'Line(px: px, py: py, lab: lab, w1: w10, w2: w20, b: b0, points0: {lt("n3.start - 0.8", "line")}, line0: {lt("n3.words[6]", "line")}, fire0: {lt("n3.words[13]", "line")}, wrong0: {lt("n4.words[9]", "line")}, accent: {a})',
        "learn": lambda a: f'Learn(px: px, py: py, lab: lab, w1: w1, w2: w2, b: b, S: S, l0: {lt("n5.words[4]", "learn")}, l1: {lt("n6.end + 0.5", "learn")}, done: "never wrong again", accent: {a})',
        "xor": lambda a: f'Learn(px: qx, py: qy, lab: qlab, w1: v1, w2: v2, b: c, S: S, l0: {lt("n9.words[0]", "xor")}, l1: {lt("n9.end + 1.0", "xor")}, done: "no line", accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ニ", "ュ", "ー", "ロ", "ン"], episode: "AI 01  ·  neuron", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 01", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
    for k, vid in enumerate(order):
        nxt = order[k + 1] if k + 1 < len(order) else None
        w(caption(vid, english[vid], nxt, english[vid] != text[vid]))
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
  let knock = synth {{ lowpass(noise(), cutoff: 700, resonance: 0.5) * perc(attack: 0.002, release: 0.12) * note.velocity + sine(note.freq) * perc(release: 0.1) * 0.5 }}
  let chord = synth {{
    let env = adsr(attack: 0.3, decay: 0.6, sustain: 0.8, release: 2.5)
    chorus(lowpass(saw(note.freq) + saw(note.freq * 1.004) + sine(note.freq * 0.5), cutoff: 1200, resonance: 0.15) * env, depth: 0.6)
  }}
  // the temple bell when the master speaks; the scale handed over
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern scale = repeat 1 event(t: m2.start / total + 0.6 * m2.duration / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the cell: the inputs, the wires, the sum filling, the fire, the second try
  pattern inputs = repeat 3 event(t: (n1.words[5] + 0.04 * {L["cell"]} * i) / total, x: 0.2, y: 0.4 + 0.15 * i, intensity: 0.5)
  pattern fires = repeat 1 event(t: n2.words[16] / total, x: 0.86, y: 0.5, size: 0.08, intensity: 0.9)
  pattern silent = repeat 1 event(t: (n2.words[18] + 0.15 * {L["cell"]}) / total, x: 0.86, y: 0.5, size: 0.04, intensity: 0.4)
  // the line drawn, the wrong points ringed
  pattern drawn = repeat 1 event(t: n3.words[6] / total, x: 0.5, y: 0.5, size: 0.08, intensity: 0.7)
  pattern wrongs = repeat 4 event(t: (n4.words[9] + 0.12 * i) / total, x: 0.3 + 0.1 * i, y: 0.4, intensity: 0.6)
  // the steps: a tick at each, slowly then faster; a knock when the line moves is in the scene's own moments (unknown here), so every step ticks and the pass changes ring
  pattern steps = repeat 96 event(t: (n5.words[4] + (n6.end + 0.5 - n5.words[4]) * ((i + 1) / 96) ^ (1 / 1.8)) / total, x: 0.3 + 0.4 * (i % 2), y: 0.6 - 0.3 * (i % 12) / 12, intensity: 0.35 + 0.3 * ((i % 12) == 0))
  pattern settled = repeat 3 event(t: (n6.end + 0.5) / total, x: 0.5, y: [0.5, 0.4, 0.3][i], size: 0.1, intensity: 0.7)
  pattern xsteps = repeat 96 event(t: (n9.words[0] + (n9.end + 1.0 - n9.words[0]) * ((i + 1) / 96) ^ (1 / 1.8)) / total, x: 0.3 + 0.4 * (i % 2), y: 0.6 - 0.3 * (i % 4) / 4, intensity: 0.35 + 0.3 * ((i % 4) == 0))
  pattern never = repeat 1 event(t: (n9.end + 1.0) / total, x: 0.5, y: 0.7, size: 0.1, intensity: 0.8)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(scale, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(inputs, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.4),
    notes(fires, instrument: chord, scale: "major", key: 110, gain: 0.45),
    notes(silent, instrument: knock, scale: "hirajoshi", key: 110, gain: 0.4),
    notes(drawn, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(wrongs, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.45),
    notes(steps, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(settled, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(xsteps, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(never, instrument: knock, scale: "hirajoshi", key: 82, gain: 0.6),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['learn'] + L['learn'] * 0.5) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "neurone.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
