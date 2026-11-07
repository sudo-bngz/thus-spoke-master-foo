#!/usr/bin/env python3
"""Writes logique.alea: the voices, the timing, the captions. The
gate answers are computed from the inputs inside alea.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1b2"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。スイッチに、何を聞けるのですか。", 0, "The novice asked: what can you ask a switch?"),
        ("m2", "M", "師は言った。両方か。どちらかか。それとも、逆か。", 1.4, "Master Foo said: both? Either? Or the opposite?"),
        ("m3", "M", "弟子は言った。それだけ？ 師は言った。それだけで、すべてだ。", 1.4, "The novice said: only that? Master Foo said: only that, and everything."),
    ], 0.6),
    ("gates", "1 / 4   three questions", [
        ("n1", "N", "A switch answers one question: is it on? George Boole, eighteen fifty-four, asked what can be done with yes and no alone. Three things.", 0, "A switch answers 1 question: is it on? George Boole, 1854, asked what can be done with yes and no alone. 3 things."),
        ("n2", "N", "AND: are both on? Yes, only if the first is on and the second is on.", 1.4, ""),
        ("n3", "N", "OR: is at least one on? Yes if either is on, or both.", 1.4, "OR: is at least 1 on? Yes if either is on, or both."),
        ("n4", "N", "NOT: the opposite. On becomes off, off becomes on. A gate is a small circuit that answers one of these questions.", 1.4, "NOT: the opposite. On becomes off, off becomes on. A gate is a small circuit that answers 1 of these questions."),
    ], 1.0),
    ("table", "2 / 4   the table", [
        ("n5", "N", "Two inputs, each zero or one: four cases, no more. Write the answer for each. That is a truth table.", 0, "2 inputs, each 0 or 1: 4 cases, no more. Write the answer for each. That is a truth table."),
        ("n6", "N", "AND. Zero and zero: zero. Zero and one: zero. One and zero: zero. One and one: one. Four lines, and the gate is completely described.", 1.4, "AND. 0 and 0: 0. 0 and 1: 0. 1 and 0: 0. 1 and 1: 1. 4 lines, and the gate is completely described."),
        ("n7", "N", "Nothing is hidden. Whatever the gate does, it does one of these four things. A table is the whole truth.", 1.4, "Nothing is hidden. Whatever the gate does, it does 1 of these 4 things. A table is the whole truth."),
    ], 1.0),
    ("xor", "3 / 4   building", [
        ("n8", "N", "Gates can be wired together: the answer of one is the question of the next. Let us build one that no single gate gives: exclusive or, on if exactly one input is on.", 0, "Gates can be wired together: the answer of 1 is the question of the next. Let us build 1 that no single gate gives: exclusive or, on if exactly 1 input is on."),
        ("n9", "N", "Four gates. An OR: at least one. An AND then a NOT: not both. And an AND on their two answers: at least one, and not both.", 1.4, "4 gates. An OR: at least 1. An AND then a NOT: not both. And an AND on their 2 answers: at least 1, and not both."),
        ("n10", "N", "Watch the four cases flow through. Zero zero: off. Zero one: on. One zero: on. One one: off. The line that no neuron could draw, in the first AI episode, is four gates.", 1.4, "Watch the 4 cases flow through. 0 0: off. 0 1: on. 1 0: on. 1 1: off. The line that no neuron could draw, in the first AI episode, is 4 gates."),
    ], 1.0),
    ("any", "4 / 4   anything", [
        ("n11", "N", "Here is the big idea. Any truth table at all, any number of inputs, any answers you choose, can be built from these gates.", 0, ""),
        ("n12", "N", "A comparison, an addition, a decision in a program: all of them are tables, and all tables are gates. Billions of gates, and the only question each one answers is: are both on?", 1.4, "A comparison, an addition, a decision in a program: all of them are tables, and all tables are gates. Billions of gates, and the only question each 1 answers is: are both on?"),
        ("n13", "N", "Next time: the first thing worth building. Adding.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。問いは3つ。答えは、はいか、いいえ。", 0, "Master Foo said: 3 questions. The answers: yes, or no."),
        ("m5", "M", "それを何十億も重ねれば、機械が考える。", 1.4, "Pile up billions of them, and the machine thinks."),
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
    w("""// Logique — Thus Spoke Master Foo, CPU 02: what you can ask a switch.
// Boole's 3 questions, AND, OR, NOT, each a gate with inputs and a lamp,
// the answers computed; the truth table, 4 cases and nothing hidden;
// exclusive or built from 4 gates, the 4 cases flowing through the
// wires, the answer computed from the gates; and the big idea: any table
// can be built from gates. Master Foo speaks Japanese, translated in the
// captions.
""")
    for f in ["koan", "gates", "table", "xor", "any"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Logique {")
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
                          f'kana: ["ロ", "ン", "リ"], episode: "CPU 02  ·  logic", accent: {a})',
        "gates": lambda a: f'Gates(at: [{lt("n2.words[0]", "gates")}, {lt("n3.words[0]", "gates")}, {lt("n4.words[0]", "gates")}], cycle: {6.0 / L["gates"]:.4f}, accent: {a})',
        "table": lambda a: f'Table(head0: {lt("n5.words[0]", "table")}, rows: [{lt("n6.words[1]", "table")}, {lt("n6.words[5]", "table")}, {lt("n6.words[9]", "table")}, {lt("n6.words[13]", "table")}], whole0: {lt("n6.words[17]", "table")}, accent: {a})',
        "xor": lambda a: f'Xor(draw0: {lt("n8.words[0]", "xor")}, cases: [{lt("n10.words[5]", "xor")}, {lt("n10.words[8]", "xor")}, {lt("n10.words[11]", "xor")}, {lt("n10.words[14]", "xor")}], hold: {2.4 / L["xor"]:.4f}, neuron0: {lt("n10.words[17]", "xor")}, accent: {a})',
        "any": lambda a: f'Any(tables0: {lt("n11.words[5]", "any")}, arrow0: {lt("n11.words[17]", "any")}, gates0: {lt("n11.words[20]", "any")}, billions0: {lt("n12.words[18]", "any")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ロ", "ン", "リ"], episode: "CPU 02  ·  logic", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  CPU 02", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the three gates, each running its 4 cases
  pattern gate = repeat 3 event(t: [n2.words[0], n3.words[0], n4.words[0]][i] / total, x: 0.5, y: 0.36 + 0.3 * i, size: 0.1, intensity: 0.6)
  pattern cases = repeat 12 event(t: ([n2.words[0], n3.words[0], n4.words[0]][floor(i / 4)] + 0.05 * {L["gates"]} + 1.5 * (i % 4)) / total, x: 0.22, y: 0.36 + 0.3 * floor(i / 4), size: 0.03, intensity: 0.4)
  // the rows of the table
  pattern rows = repeat 4 event(t: [n6.words[1], n6.words[5], n6.words[9], n6.words[13]][i] / total, x: 0.4, y: 0.52 + 0.09 * i, size: 0.04, intensity: 0.5)
  pattern answers = repeat 4 event(t: ([n6.words[1], n6.words[5], n6.words[9], n6.words[13]][i] + 0.03 * {L["table"]}) / total, x: 0.68, y: 0.52 + 0.09 * i, size: 0.04, intensity: 0.4 + 0.5 * (i == 3))
  // the 4 cases through the xor; the lamp
  pattern flow = repeat 4 event(t: [n10.words[5], n10.words[8], n10.words[11], n10.words[14]][i] / total, x: 0.12, y: 0.62, size: 0.05, intensity: 0.5)
  pattern xlamp = repeat 2 event(t: ([n10.words[8], n10.words[11]][i] + 0.3) / total, x: 0.9, y: 0.62, size: 0.09, intensity: 0.8)
  // the tables; the arrow; the gates growing
  pattern tbls = repeat 3 event(t: (n11.words[5] + 0.05 * {L["any"]} * i) / total, x: 0.16, y: 0.4 + 0.24 * i, size: 0.05, intensity: 0.4)
  pattern mesh = repeat 24 event(t: (n12.words[18] + 0.2 * {L["any"]} * (i / 24)) / total, x: ~between(0.2, 0.8), y: ~between(0.3, 0.9), intensity: 0.15 + 0.01 * i)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(gate, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(cases, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(rows, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.45),
    notes(answers, instrument: "glass", scale: "hirajoshi", key: 659, gain: 0.45),
    notes(flow, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(xlamp, instrument: "glass", scale: "hirajoshi", key: 784, gain: 0.5),
    notes(tbls, instrument: "wood", scale: "hirajoshi", key: 262, gain: 0.4),
    notes(mesh, instrument: tick, scale: "hirajoshi", key: 1320, gain: 0.15),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['xor'] + L['xor'] * 0.8) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "logique.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
