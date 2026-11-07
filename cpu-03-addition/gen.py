#!/usr/bin/env python3
"""Writes addition.alea: the voices, the timing, the captions. The
sums and carries are computed from the bits inside alea.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1b3"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、数を数えられるのですか。", 0, "The novice asked: can the machine count?"),
        ("m2", "M", "師は言った。1と1を足してみよ。", 1.4, "Master Foo said: add 1 and 1."),
        ("m3", "M", "弟子は答えた。2です。師は言った。機械には、2という数字はない。", 1.4, "The novice answered: 2. Master Foo said: the machine has no digit 2."),
    ], 0.6),
    ("half", "1 / 4   one plus one", [
        ("n1", "N", "In binary, one plus one is not two. There is no digit two. One plus one is one zero: zero, and carry one. Just like nine plus one is ten.", 0, "In binary, 1 + 1 is not 2. There is no digit 2. 1 + 1 is 10: 0, and carry 1. Just like 9 + 1 is 10."),
        ("n2", "N", "So adding two bits gives two answers: the sum, and the carry. Zero and zero. Zero and one. One and zero. One and one. The sum is on when exactly one input is on: exclusive or.", 1.4, "So adding 2 bits gives 2 answers: the sum, and the carry. 0 and 0. 0 and 1. 1 and 0. 1 and 1. The sum is on when exactly 1 input is on: exclusive or."),
        ("n3", "N", "The carry is on when both are on: AND. Two gates from last time, and we have a half adder.", 1.4, "The carry is on when both are on: AND. 2 gates from last time, and we have a half adder."),
    ], 1.0),
    ("full", "2 / 4   the carry", [
        ("n4", "N", "Half, because a real column has three things to add: the two bits, and the carry coming in from the right.", 0, "Half, because a real column has 3 things to add: the 2 bits, and the carry coming in from the right."),
        ("n5", "N", "Three inputs: eight cases. The sum is on when an odd number of them are on. The carry, when at least two are on.", 1.4, "3 inputs: 8 cases. The sum is on when an odd number of them are on. The carry, when at least 2 are on."),
        ("n6", "N", "Two half adders and an OR gate do it. That is a full adder: one column of an addition, in five gates.", 1.4, "2 half adders and an OR gate do it. That is a full adder: 1 column of an addition, in 5 gates."),
    ], 1.0),
    ("ripple", "3 / 4   four columns", [
        ("n7", "N", "Now chain four of them. Each column passes its carry to the next, right to left, like you learned at school.", 0, "Now chain 4 of them. Each column passes its carry to the next, right to left, like you learned at school."),
        ("n8", "N", "Five plus seven. Zero one zero one, plus zero one one one. Watch the carry ripple.", 1.4, "5 + 7. 0101 + 0111. Watch the carry ripple."),
        ("n9", "N", "Right column: one plus one, zero, carry one. Next: zero plus one plus the carry, zero, carry one. Next: one plus one plus one: one, carry one. Last: zero plus zero plus one: one.", 1.4, "Right column: 1 + 1, 0, carry 1. Next: 0 + 1 + the carry, 0, carry 1. Next: 1 + 1 + 1: 1, carry 1. Last: 0 + 0 + 1: 1."),
        ("n10", "N", "One one zero zero: twelve. That is a ripple adder. Twenty gates, and it adds. The first piece of our machine.", 1.4, "1100: 12. That is a ripple adder. 20 gates, and it adds. The first piece of our machine."),
    ], 1.0),
    ("minus", "4 / 4   subtraction", [
        ("n11", "N", "And subtracting? No new circuit. Seven minus five. Take five: zero one zero one. Flip every bit: one zero one zero. Add one: one zero one one.", 0, "And subtracting? No new circuit. 7 - 5. Take 5: 0101. Flip every bit: 1010. Add 1: 1011."),
        ("n12", "N", "Now add that to seven. Zero one one one plus one zero one one: one zero zero one zero. The fifth bit falls off the end. Zero zero one zero: two.", 1.4, "Now add that to 7. 0111 + 1011: 10010. The 5th bit falls off the end. 0010: 2."),
        ("n13", "N", "Two's complement: the same adder subtracts. Next time: how a wire remembers.", 1.4, "2's complement: the same adder subtracts. Next time: how a wire remembers."),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。1と1で、10。それだけを知る機械が、", 0, "Master Foo said: 1 and 1 make 10. A machine that knows only that"),
        ("m5", "M", "すべての数を足す。", 1.4, "adds every number there is."),
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
    w("""// Addition — Thus Spoke Master Foo, CPU 03: the first thing worth
// building. 1 + 1 = 10; the half adder, XOR for the sum and AND for the
// carry, its table computed; the full adder with the carry in, 8 cases
// computed, 2 half adders and an OR inside; 4 of them chained, the
// carries rippling right to left, 5 + 7 added column by column; and
// subtraction with the same adder, 2's complement. Master Foo speaks
// Japanese, translated in the captions.
""")
    for f in ["koan", "half", "full", "ripple", "minus"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Addition {")
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
                          f'kana: ["タ", "シ", "ザ", "ン"], episode: "CPU 03  ·  addition", accent: {a})',
        "half": lambda a: f'Half(big0: {lt("n1.words[9]", "half")}, table0: {lt("n2.words[2]", "half")}, rows: [{lt("n2.words[12]", "half")}, {lt("n2.words[15]", "half")}, {lt("n2.words[18]", "half")}, {lt("n2.words[21]", "half")}], gates0: {lt("n3.words[8]", "half")}, cycle: {6.0 / L["half"]:.4f}, accent: {a})',
        "full": lambda a: f'Full(box0: {lt("n4.words[5]", "full")}, cases0: {lt("n5.words[0]", "full")}, cycle: {9.0 / L["full"]:.4f}, inside0: {lt("n6.words[0]", "full")}, accent: {a})',
        "ripple": lambda a: f'Ripple(draw0: {lt("n7.words[2]", "ripple")}, nums0: {lt("n8.words[0]", "ripple")}, steps: [{lt("n9.words[0]", "ripple")}, {lt("n9.words[7]", "ripple")}, {lt("n9.words[16]", "ripple")}, {lt("n9.words[25]", "ripple")}], value0: {lt("n10.words[0]", "ripple")}, accent: {a})',
        "minus": lambda a: f'Minus(q0: {lt("n11.words[0]", "minus")}, five0: {lt("n11.words[8]", "minus")}, flip0: {lt("n11.words[14]", "minus")}, plus0: {lt("n11.words[22]", "minus")}, add0: {lt("n12.words[0]", "minus")}, drop0: {lt("n12.words[16]", "minus")}, result0: {lt("n12.words[25]", "minus")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["タ", "シ", "ザ", "ン"], episode: "CPU 03  ·  addition", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  CPU 03", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // 1 + 1; the rows; the 2 gates cycling
  pattern oneone = repeat 1 event(t: n1.words[9] / total, x: 0.5, y: 0.3, size: 0.1, intensity: 0.7)
  pattern hrows = repeat 4 event(t: [n2.words[12], n2.words[15], n2.words[18], n2.words[21]][i] / total, x: 0.4, y: 0.63 + 0.07 * i, size: 0.04, intensity: 0.5)
  pattern hcases = repeat 4 event(t: (n3.words[8] + 0.05 * {L["half"]} + 1.5 * i) / total, x: 0.14, y: 1.12, size: 0.03, intensity: 0.4)
  // the 8 cases of the full adder
  pattern fcases = repeat 8 event(t: (n5.words[0] + 9.0 * (i / 8)) / total, x: 0.2, y: 0.55, size: 0.03, intensity: 0.35)
  pattern inside = repeat 3 event(t: (n6.words[0] + 0.03 * {L["full"]} * i) / total, x: 0.3 + 0.22 * i, y: 1.05, size: 0.05, intensity: 0.5)
  // the 4 columns, right to left; the value
  pattern columns = repeat 4 event(t: [n9.words[0], n9.words[7], n9.words[16], n9.words[25]][i] / total, x: 0.8 - 0.2 * i, y: 0.66, size: 0.08, intensity: 0.6 + 0.1 * i)
  pattern carries = repeat 3 event(t: ([n9.words[0], n9.words[7], n9.words[16]][i] + 0.05 * {L["ripple"]}) / total, x: 0.7 - 0.2 * i, y: 0.66, size: 0.03, intensity: 0.5)
  pattern twelve = repeat 1 event(t: n10.words[0] / total, x: 0.5, y: 0.98, size: 0.1, intensity: 0.8)
  // the rows of the subtraction; the dropped bit; the result
  pattern mrows = repeat 5 event(t: [n11.words[8], n11.words[14], n11.words[22], n12.words[0], n12.words[0] + 0.06 * {L["minus"]}][i] / total, x: 0.6, y: 0.48 + 0.08 * i, size: 0.04, intensity: 0.45)
  pattern dropped = repeat 1 event(t: n12.words[16] / total, x: 0.45, y: 1.04, size: 0.04, intensity: 0.6)
  pattern two = repeat 1 event(t: n12.words[25] / total, x: 0.5, y: 1.22, size: 0.1, intensity: 0.8)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(oneone, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(hrows, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.45),
    notes(hcases, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(fcases, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(inside, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(columns, instrument: "kalimba", scale: "hirajoshi", key: 262, gain: 0.5),
    notes(carries, instrument: "glass", scale: "hirajoshi", key: 784, gain: 0.4),
    notes(twelve, instrument: chord, scale: "major", key: 110, gain: 0.45),
    notes(mrows, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.4),
    notes(dropped, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.6),
    notes(two, instrument: chord, scale: "major", key: 110, gain: 0.45),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['ripple'] + L['ripple'] * 0.85) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "addition.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
