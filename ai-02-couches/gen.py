#!/usr/bin/env python3
"""Writes couches.alea: the voices, the timing, the captions. The lines
are set by hand (the learning of a layered network is the next episode):
A fires above u - v + 0.3 = 0, B below u - v - 0.3 = 0, C where both say
yes: the band between them, which holds the two full corners and not the
two hollow ones.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a2"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。一つの秤で引けない線は、どうすれば引けますか。", 0, "The novice asked: the line 1 scale cannot draw, how is it drawn?"),
        ("m2", "M", "師は、秤をもう二つ持ってきて、三つ目の秤の皿に載せた。", 1.4, "Master Foo brought 2 more scales, and set them on the pans of a 3rd."),
    ], 0.6),
    ("problem", "1 / 4   the problem", [
        ("n1", "N", "Last time: one neuron is one straight line. It fires on one side, and stays quiet on the other.", 0, "Last time: 1 neuron is 1 straight line. It fires on 1 side, and stays quiet on the other."),
        ("n2", "N", "And this problem beat it: the full points in opposite corners. Whichever way the line turns, two points are on the wrong side.", 1.4, "And this problem beat it: the full points in opposite corners. Whichever way the line turns, 2 points are on the wrong side."),
        ("n3", "N", "The way out is not a better line. It is more neurons.", 1.4, ""),
    ], 1.0),
    ("lines", "2 / 4   two neurons", [
        ("n4", "N", "Take two neurons, each with its own weights. Each one draws its own line.", 0, "Take 2 neurons, each with its own weights. Each 1 draws its own line."),
        ("n5", "N", "Neuron A fires above its line.", 1.4, ""),
        ("n6", "N", "Neuron B fires below its own.", 1.4, ""),
        ("n7", "N", "Each one answers a single question: which side of my line are you on? Yes, or no.", 1.4, "Each 1 answers a single question: which side of my line are you on? Yes, or no."),
        ("n8", "N", "Now look at the full points. For both of them, A says yes, and B says yes.", 1.4, ""),
        ("n9", "N", "For the hollow ones, one of the two says no.", 1.4, "For the hollow ones, 1 of the 2 says no."),
    ], 1.0),
    ("band", "3 / 4   the third neuron", [
        ("n10", "N", "Add a third neuron, C. Its inputs are not the point. Its inputs are the answers of A and B.", 0, "Add a 3rd neuron, C. Its inputs are not the point. Its inputs are the answers of A and B."),
        ("n11", "N", "Give it a threshold that needs both answers to be yes. Then it fires only between the two lines.", 1.4, "Give it a threshold that needs both answers to be yes. Then it fires only between the 2 lines."),
        ("n12", "N", "Its decision is no longer a line. It is a band: two lines, joined. The full points inside, the hollow ones outside.", 1.4, "Its decision is no longer a line. It is a band: 2 lines, joined. The full points inside, the hollow ones outside."),
        ("n13", "N", "This is a layer: neurons working side by side, and feeding the next one. The problem that beat one neuron falls to three.", 1.4, "This is a layer: neurons working side by side, and feeding the next 1. The problem that beat 1 neuron falls to 3."),
    ], 1.0),
    ("shapes", "4 / 4   deeper", [
        ("n14", "N", "More neurons in the layer: more lines. And the shape they enclose can be any shape you like.", 0, ""),
        ("n15", "N", "More layers: shapes made of shapes. Edges, then corners, then faces.", 1.4, ""),
        ("n16", "N", "That is what deep means, in deep learning: many layers, one after the other.", 1.4, "That is what deep means, in deep learning: many layers, 1 after the other."),
        ("n17", "N", "One question remains. The three scales must learn their weights together. How does a mistake at the end reach the first scale? Next time.", 1.4, "1 question remains. The 3 scales must learn their weights together. How does a mistake at the end reach the first scale? Next time."),
    ], 1.0),
    ("end", "", [
        ("m3", "M", "弟子は見た。三つの秤が、曲がった線を一本引いた。", 0, "The novice looked: 3 scales had drawn 1 bent line."),
        ("m4", "M", "師は言った。秤の上に秤。それが、深さだ。", 1.4, "Master Foo said: scales upon scales. That is depth."),
        ("m5", "M", "その時、弟子は悟った。", 1.6, "And the novice was enlightened."),
    ], 1.0),
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
    w("""// Couches — Thus Spoke Master Foo, AI 02: layers. The line one scale
// cannot draw: Master Foo sets two scales on the pans of a third. One
// neuron is one line, and the opposite corners beat it; two neurons draw
// two lines and each answers one question; a third neuron takes their
// answers as its inputs and fires only between the lines: a band, two
// lines joined. A layer. More neurons, any shape; more layers, shapes of
// shapes: deep. Master Foo speaks Japanese, translated in the captions.
""")
    for f in ["koan", "problem", "lines", "band", "shapes"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Couches {")
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
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m2.end + 0.8", "koan")}, title: {lt("m2.end + 1.0", "koan")}, '
                          f'kana: ["レ", "イ", "ヤ", "ー"], episode: "AI 02  ·  layers", accent: {a})',
        "problem": lambda a: f'Problem(show: {lt("n1.start - 0.8", "problem")}, line0: {lt("n1.words[3]", "problem")}, turn0: {lt("n2.words[12]", "problem")}, wrong0: {lt("n2.words[17]", "problem")}, accent: {a})',
        "lines": lambda a: f'Lines(net0: {lt("n4.start - 0.8", "lines")}, a0: {lt("n5.words[1]", "lines")}, b0: {lt("n6.words[1]", "lines")}, each0: {lt("n7.words[6]", "lines")}, full0: {lt("n8.words[3]", "lines")}, hollow0: {lt("n9.words[2]", "lines")}, accent: {a})',
        "band": lambda a: f'Band(c0: {lt("n10.words[2]", "band")}, both0: {lt("n11.words[5]", "band")}, band0: {lt("n12.words[8]", "band")}, layer0: {lt("n13.words[3]", "band")}, accent: {a})',
        "shapes": lambda a: f'Shapes(lines0: {lt("n14.words[4]", "shapes")}, lines1: {lt("n14.words[9]", "shapes")}, fill0: {lt("n14.words[12]", "shapes")}, deep0: {lt("n15.words[1]", "shapes")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m3.start", "end")}, draw1: {lt("m5.end", "end")}, word: {lt("m5.start + 0.5", "end")}, title: {lt("m5.end + 0.6", "end")}, '
                         f'kana: ["レ", "イ", "ヤ", "ー"], episode: "AI 02  ·  layers", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 02", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the temple bell when the master speaks; the scales set on the pans
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m3.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern scales = repeat 3 event(t: (m2.start + 0.5 * m2.duration + 0.4 * i) / total, x: 0.4 + 0.1 * i, y: 0.5, size: 0.05, intensity: 0.7)
  // the problem: the line turning, the two wrong points
  pattern turning = repeat 1 event(t: n2.words[12] / total, x: 0.5, y: 0.5, size: 0.1, intensity: 0.5)
  pattern wrongs = repeat 2 event(t: (n2.words[17] + 0.3 * i) / total, x: 0.3 + 0.4 * i, y: 0.4, intensity: 0.6)
  // two lines, two neurons; the answers
  pattern linesAB = repeat 2 event(t: [n5.words[1], n6.words[1]][i] / total, x: 0.3 + 0.4 * i, y: 0.5, size: 0.08, intensity: 0.7)
  pattern answers = repeat 8 event(t: ([n8.words[3], n9.words[2]][floor(i / 4)] + 0.03 * {L["lines"]} + 0.25 * (i % 4)) / total, x: 0.3 + 0.1 * (i % 4), y: 0.5, intensity: 0.4 + 0.3 * ((i == 5) + (i == 6)))
  // the third neuron, the band
  pattern third = repeat 1 event(t: n10.words[2] / total, x: 0.8, y: 0.4, size: 0.08, intensity: 0.7)
  pattern bandin = repeat 3 event(t: n12.words[8] / total, x: 0.5, y: [0.5, 0.4, 0.3][i], size: 0.1, intensity: 0.7)
  // the lines around the shape, one by one; the layers, column by column
  pattern more = repeat 8 event(t: (n14.words[4] + (n14.words[9] - n14.words[4]) * i / 8) / total, x: 0.5 + 0.3 * cos(tau * i / 8), y: 0.6 + 0.3 * sin(tau * i / 8), intensity: 0.5)
  pattern deeper = repeat 5 event(t: (n15.words[1] + 0.08 * {L["shapes"]} * i) / total, x: 0.2 + 0.15 * i, y: 0.5, size: 0.05, intensity: 0.6)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(scales, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(turning, instrument: brush, scale: "chromatic", key: 100, gain: 0.4),
    notes(wrongs, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.45),
    notes(linesAB, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(answers, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.35),
    notes(third, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(bandin, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(more, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.4),
    notes(deeper, instrument: chord, scale: "major", key: 82, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['band'] + L['band'] * 0.75) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "couches.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
