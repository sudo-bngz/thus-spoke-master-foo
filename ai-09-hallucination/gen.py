#!/usr/bin/env python3
"""Writes hallucination.alea: the voices, the timing, the captions. The
percentages and the invented paper are illustrative: no model runs here.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a9"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、嘘をつくのですか。", 0, "The novice asked: does the machine lie?"),
        ("m2", "M", "師は言った。嘘をつくには、まず真実を知らねばならぬ。", 1.4, "Master Foo said: to lie, one must first know the truth."),
        ("m3", "M", "弟子は、黙った。", 1.4, "The novice was silent."),
    ], 0.6),
    ("shape", "1 / 4   the shape", [
        ("n1", "N", "The machine was never asked to be right. Only to guess the next word. A sentence that sounds right is enough.", 0, ""),
        ("n2", "N", "The capital of Australia is: Sydney, forty percent. Canberra, thirty-five. Both are shaped like an answer. The die picks.", 1.4, "The capital of Australia is: Sydney, 40 %. Canberra, 35. Both are shaped like an answer. The die picks."),
        ("n3", "N", "It picks Sydney. Nothing inside protests. The grammar is perfect, the sentence is complete, and it is wrong.", 1.4, ""),
        ("n4", "N", "That is a hallucination: a sentence shaped like a fact, with no fact behind it.", 1.4, ""),
    ], 1.0),
    ("blur", "2 / 4   the blur", [
        ("n5", "N", "Why? The weights hold the internet, blurred. A fact seen a million times leaves a sharp peak: Paris.", 0, "Why? The weights hold the internet, blurred. A fact seen 1 000 000 times leaves a sharp peak: Paris."),
        ("n6", "N", "A fact seen twice, a small town, a paper from nineteen eighty-seven, leaves almost nothing. A flat spread.", 1.4, "A fact seen 2 times, a small town, a paper from 1987, leaves almost nothing. A flat spread."),
        ("n7", "N", "But the sentence must go on. So the machine fills the gap with the most plausible words. A name that sounds like a name. A date that sounds like a date.", 1.4, ""),
    ], 1.0),
    ("sure", "3 / 4   the voice", [
        ("n8", "N", "And it says it with the same voice. The tone does not come from the truth. It comes from the texts it learned from, and people write with confidence.", 0, ""),
        ("n9", "N", "Under each sentence there is a number: how sure the die was. Ninety-two percent. Thirty-one percent. You never see it. Only the words.", 1.4, "Under each sentence there is a number: how sure the die was. 92 %. 31 %. You never see it. Only the words."),
        ("n10", "N", "Same font, same voice, same calm. A fact and an invention look exactly alike from the outside.", 1.4, ""),
    ], 1.0),
    ("check", "4 / 4   what to do", [
        ("n11", "N", "So what can you do? Three things. One: give it the text. Put the document in the window, and it reads instead of guessing.", 0, "So what can you do? 3 things. 1: give it the text. Put the document in the window, and it reads instead of guessing."),
        ("n12", "N", "Two: ask twice. Two rolls of the die. If the answers disagree, the spread was flat.", 1.4, "2: ask twice. 2 rolls of the die. If the answers disagree, the spread was flat."),
        ("n13", "N", "Three: check what matters. A name, a date, a number, a law. The machine continues sentences. Whether they are true is your job.", 1.4, "3: check what matters. A name, a date, a number, a law. The machine continues sentences. Whether they are true is your job."),
        ("n14", "N", "This closes the series on AI. From the neuron to the next token, and back.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。機械は、ありそうな言葉を続けるだけだ。", 0, "Master Foo said: the machine only continues with the likeliest words."),
        ("m5", "M", "疑うのは、お前の仕事だ。", 1.4, "Doubting them is your job."),
        ("m6", "M", "その時、弟子は悟った。", 1.6, "And the novice was enlightened."),
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
    w("""// Hallucination — Thus Spoke Master Foo, AI 09: sure, and wrong. The
// machine was never asked to be right, only to continue; a sentence
// shaped like a fact, with no fact behind it; why: the weights hold the
// internet blurred, a sharp peak for what was seen a million times, a
// flat spread for what was seen twice, and the gap filled anyway; the
// same voice for a fact and an invention, the number under the words
// never shown; and what to do: give it the text, ask twice, check what
// matters. The percentages and the paper are illustrative. Master Foo
// speaks Japanese, translated in the captions.
""")
    for f in ["koan", "shape", "blur", "sure", "check"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Hallucination {")
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
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ゲ", "ン", "カ", "ク"], episode: "AI 09  ·  hallucination", accent: {a})',
        "shape": lambda a: f'Shape(prompt0: {lt("n2.words[0]", "shape")}, bars0: {lt("n2.words[5]", "shape")}, pick0: {lt("n3.words[2]", "shape")}, wrong0: {lt("n3.words[6]", "shape")}, shaped0: {lt("n4.words[4]", "shape")}, accent: {a})',
        "blur": lambda a: f'Blur(sharp0: {lt("n5.words[9]", "blur")}, flat0: {lt("n6.words[0]", "blur")}, fill0: {lt("n7.words[7]", "blur")}, accent: {a})',
        "sure": lambda a: f'Sure(s0: {lt("n8.words[2]", "sure")}, s1: {lt("n8.words[8]", "sure")}, reveal0: {lt("n9.words[13]", "sure")}, same0: {lt("n10.words[0]", "sure")}, accent: {a})',
        "check": lambda a: f'Check(at: [{lt("n11.words[6]", "check")}, {lt("n12.words[0]", "check")}, {lt("n13.words[0]", "check")}], end0: {lt("n14.words[2]", "check")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ゲ", "ン", "カ", "ク"], episode: "AI 09  ·  hallucination", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 09", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the temple bell when the master speaks; the question
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern asked = repeat 1 event(t: (m2.start + 0.85 * m2.duration) / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the two bars; the pick; wrong
  pattern bars = repeat 2 event(t: (n2.words[5] + 0.03 * {L["shape"]} * i) / total, x: 0.5, y: 0.58 + 0.1 * i, size: 0.05, intensity: 0.5)
  pattern picked = repeat 1 event(t: n3.words[2] / total, x: 0.5, y: 0.43, size: 0.06, intensity: 0.8)
  pattern wrong = repeat 1 event(t: (n3.words[6] + 0.1 * {L["shape"]}) / total, x: 0.5, y: 1.0, size: 0.08, intensity: 0.9)
  // the sharp peak; the flat spread; the gap filled
  pattern peak = repeat 1 event(t: n5.words[9] / total, x: 0.5, y: 0.42, size: 0.05, intensity: 0.7)
  pattern spread = repeat 12 event(t: (n6.words[0] + 0.08 * {L["blur"]} * (i / 12)) / total, x: 0.12 + 0.76 * i / 12, y: 0.8, intensity: 0.25)
  pattern filled = repeat 8 event(t: (n7.words[7] + 0.03 * {L["blur"]} + 0.14 * {L["blur"]} * (i / 8)) / total, x: 0.2 + 0.6 * i / 8, y: 1.0, intensity: 0.3)
  // the two sentences; the numbers revealed
  pattern said = repeat 2 event(t: [n8.words[2], n8.words[8]][i] / total, x: 0.5, y: 0.42 + 0.3 * i, size: 0.1, intensity: 0.5)
  pattern revealed = repeat 2 event(t: (n9.words[13] + 0.06 * {L["sure"]}) / total, x: 0.5, y: 0.49 + 0.3 * i, size: 0.05, intensity: 0.6)
  // the three things; the series closed
  pattern things = repeat 3 event(t: [n11.words[6], n12.words[0], n13.words[0]][i] / total, x: 0.12, y: 0.38 + 0.22 * i, size: 0.06, intensity: 0.7)
  pattern series = repeat 9 event(t: (n14.words[2] + 0.05 * {L["check"]} * i) / total, x: 0.1 + 0.8 * i / 8, y: 1.12, intensity: 0.4)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(bars, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(picked, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(wrong, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.7),
    notes(peak, instrument: "glass", scale: "hirajoshi", key: 659, gain: 0.5),
    notes(spread, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.25),
    notes(filled, instrument: tick, scale: "hirajoshi", key: 1100, gain: 0.25),
    notes(said, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(revealed, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.5),
    notes(things, instrument: "kalimba", scale: "hirajoshi", key: 262, gain: 0.5),
    notes(series, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['sure'] + L['sure'] * 0.75) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "hallucination.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
