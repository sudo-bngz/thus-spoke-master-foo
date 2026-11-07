#!/usr/bin/env python3
"""Writes bit.alea: the voices, the timing, the captions. The
4-bit values are computed from the bits inside alea.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1b1"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、どれだけのことを知っているのですか。", 0, "The novice asked: how much does the machine know?"),
        ("m2", "M", "師は言った。2つだけだ。入か、切か。", 1.4, "Master Foo said: 2 things only. On, or off."),
        ("m3", "M", "弟子は言った。たった2つ？ 師は言った。では、2つ同時に聞け。", 1.4, "The novice said: only 2? Master Foo said: then ask it 2 things at a time."),
    ], 0.6),
    ("switch", "1 / 4   the switch", [
        ("n1", "N", "A computer is made of switches. A switch has two positions: open, or closed. Current flows, or it does not.", 0, "A computer is made of switches. A switch has 2 positions: open, or closed. Current flows, or it does not."),
        ("n2", "N", "Call them zero and one. Nothing in between. A half-open switch does not exist.", 1.4, "Call them 0 and 1. Nothing in between. A half-open switch does not exist."),
        ("n3", "N", "That is a bit: the smallest thing a computer can hold. One switch, one bit, two possibilities.", 1.4, "That is a bit: the smallest thing a computer can hold. 1 switch, 1 bit, 2 possibilities."),
    ], 1.0),
    ("two", "2 / 4   why two", [
        ("n4", "N", "Why not ten, like our fingers? Ten positions would need a switch that is a little open, more open, almost closed.", 0, "Why not 10, like our fingers? 10 positions would need a switch that is a little open, more open, almost closed."),
        ("n5", "N", "A little open and more open are hard to tell apart, especially when the signal is weak, or noisy. Open or closed is never ambiguous.", 1.4, ""),
        ("n6", "N", "So the machine uses the dumbest switch there is, and asks it many times. Billions of switches, each one certain.", 1.4, ""),
    ], 1.0),
    ("count", "3 / 4   counting", [
        ("n7", "N", "How do you count with switches? Line up four. Each one is a bit. Read them together, as a number.", 0, "How do you count with switches? Line up 4. Each one is a bit. Read them together, as a number."),
        ("n8", "N", "The rightmost bit counts one. The next, two. Then four. Then eight. Each bit is worth twice the one before.", 1.4, "The rightmost bit counts 1. The next, 2. Then 4. Then 8. Each bit is worth twice the one before."),
        ("n9", "N", "Zero zero zero zero is zero. Zero zero zero one is one. Zero zero one zero is two. One zero one one: eight plus two plus one, eleven.", 1.4, "0000 is 0. 0001 is 1. 0010 is 2. 1011: 8 + 2 + 1, 11."),
        ("n10", "N", "Four bits: sixteen numbers, zero to fifteen. Watch them all.", 1.4, "4 bits: 16 numbers, 0 to 15. Watch them all."),
    ], 1.0),
    ("byte", "4 / 4   the byte", [
        ("n11", "N", "Eight bits: two hundred fifty-six numbers. That is a byte. One letter, one small number, one shade of grey.", 0, "8 bits: 256 numbers. That is a byte. 1 letter, 1 small number, 1 shade of grey."),
        ("n12", "N", "A word today is sixty-four bits. That is eighteen billion billion possibilities, in one row of switches.", 1.4, "A word today is 64 bits. That is 18 000 000 000 000 000 000 possibilities, in 1 row of switches."),
        ("n13", "N", "Everything else in this series is built from this: a switch, a bit, a row of bits. Next time: asking a switch a question. Logic.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。1つのスイッチは、2つを知る。", 0, "Master Foo said: 1 switch knows 2 things."),
        ("m5", "M", "64のスイッチは、世界を知る。", 1.4, "64 switches know the world."),
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
    w("""// Bit — Thus Spoke Master Foo, CPU 01: what a computer is made of. A
// switch, open or closed, 0 or 1, nothing in between: a bit. Why 2 and
// not 10: a dial with 10 positions and a trembling needle, a switch that
// is never ambiguous. Counting with 4 switches, each worth twice the one
// before, the 16 numbers computed from the bits. The byte, the 64-bit
// word, and the row of bits everything else is built from. Master Foo
// speaks Japanese, translated in the captions.
""")
    for f in ["koan", "switch", "two", "count", "byte"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Bit {")
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
                          f'kana: ["ビ", "ッ", "ト"], episode: "CPU 01  ·  bit", accent: {a})',
        "switch": lambda a: f'Switch(draw0: {lt("n1.words[6]", "switch")}, close0: {lt("n1.words[13]", "switch")}, open0: {lt("n1.words[16]", "switch")}, close1: {lt("n2.words[4]", "switch")}, names0: {lt("n2.words[2]", "switch")}, bit0: {lt("n3.words[9]", "switch")}, accent: {a})',
        "two": lambda a: f'Two(dial0: {lt("n4.words[6]", "two")}, noise0: {lt("n5.words[7]", "two")}, switch0: {lt("n5.words[19]", "two")}, many0: {lt("n6.words[13]", "two")}, accent: {a})',
        "count": lambda a: f'Count(line0: {lt("n7.words[6]", "count")}, worth0: {lt("n8.words[3]", "count")}, showat: [{lt("n9.words[0]", "count")}, {lt("n9.words[6]", "count")}, {lt("n9.words[12]", "count")}, {lt("n9.words[18]", "count")}], run0: {lt("n10.words[7]", "count")}, run1: {lt("n10.words[7] + 6.4", "count")}, accent: {a})',
        "byte": lambda a: f'Byte(byte0: {lt("n11.words[0]", "byte")}, word0: {lt("n12.words[0]", "byte")}, built0: {lt("n13.words[7]", "byte")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ビ", "ッ", "ト"], episode: "CPU 01  ·  bit", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  CPU 01", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the switch closing, opening, closing; the lamp
  pattern clicks = repeat 3 event(t: [n1.words[13], n1.words[16], n2.words[4]][i] / total, x: 0.5, y: 0.42, size: 0.04, intensity: 0.8)
  pattern lamp = repeat 2 event(t: ([n1.words[13], n2.words[4]][i] + 0.04 * {L["switch"]}) / total, x: 0.8, y: 0.78, size: 0.1, intensity: 0.5)
  // the dial marks; the needle trembling; the switch
  pattern marks = repeat 10 event(t: (n4.words[6] + 0.06 * {L["two"]} * (i / 10)) / total, x: 0.3 + 0.04 * i, y: 0.4, intensity: 0.3)
  pattern tremble = repeat 16 event(t: (n5.words[7] + 0.3 * {L["two"]} * (i / 16)) / total, x: ~between(0.4, 0.6), y: 0.45, size: 0.02, intensity: 0.2)
  pattern certain = repeat 1 event(t: n5.words[19] / total, x: 0.5, y: 0.93, size: 0.06, intensity: 0.8)
  // the 4 squares; the worths; the examples; the run of 16
  pattern squares = repeat 4 event(t: (n7.words[6] + 0.01 * {L["count"]} * i) / total, x: 0.26 + 0.16 * i, y: 0.58, size: 0.05, intensity: 0.5)
  pattern worths = repeat 4 event(t: (n8.words[3] + 0.04 * {L["count"]} * i) / total, x: 0.74 - 0.16 * i, y: 0.46, size: 0.04, intensity: 0.5 + 0.1 * i)
  pattern examples = repeat 4 event(t: [n9.words[0], n9.words[6], n9.words[12], n9.words[18]][i] / total, x: 0.5, y: 0.84, size: 0.06, intensity: 0.6)
  pattern sixteen = repeat 16 event(t: (n10.words[7] + 6.4 * (i / 16)) / total, x: 0.26 + 0.48 * (i % 4) / 3, y: 0.58, size: 0.03, intensity: 0.3 + 0.4 * (i / 16))
  // the byte; the word
  pattern eight = repeat 8 event(t: (n11.words[0] + 0.01 * {L["byte"]} * i) / total, x: 0.18 + 0.09 * i, y: 0.42, intensity: 0.3)
  pattern sixtyfour = repeat 64 event(t: (n12.words[0] + 0.003 * {L["byte"]} * i) / total, x: 0.12 + 0.76 * (i % 32) / 31, y: 0.76 + 0.035 * floor(i / 32), intensity: 0.15)
  pattern big = repeat 1 event(t: (n12.words[0] + 0.26 * {L["byte"]}) / total, x: 0.5, y: 0.92, size: 0.2, intensity: 0.6)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(clicks, instrument: knock, scale: "hirajoshi", key: 220, gain: 0.7),
    notes(lamp, instrument: "glass", scale: "hirajoshi", key: 659, gain: 0.5),
    notes(marks, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(tremble, instrument: tick, scale: "hirajoshi", key: 1320, gain: 0.15),
    notes(certain, instrument: knock, scale: "hirajoshi", key: 220, gain: 0.7),
    notes(squares, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.45),
    notes(worths, instrument: "kalimba", scale: "hirajoshi", key: 262, gain: 0.5),
    notes(examples, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(sixteen, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.4),
    notes(eight, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(sixtyfour, instrument: tick, scale: "hirajoshi", key: 1320, gain: 0.15),
    notes(big, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['count'] + L['count'] * 0.9) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "bit.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
