#!/usr/bin/env python3
"""Writes entrainement.alea: the voices, the timing, the captions. The
numbers (3 %, 97, 4 %, the curve) are illustrative: no model is trained here.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a7"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、どこで言葉を学んだのですか。", 0, "The novice asked: where did the machine learn its words?"),
        ("m2", "M", "師は言った。書かれたものを、すべて読んだ。そして、1語ずつ、間違えた。", 1.4, "Master Foo said: it read everything ever written. And, 1 word at a time, it was wrong."),
        ("m3", "M", "弟子は尋ねた。間違えて、どうなるのですか。", 1.4, "The novice asked: and what comes of being wrong?"),
    ], 0.6),
    ("guess", "1 / 4   the guess", [
        ("n1", "N", "Where do the weights come from? At first, they are random. The machine knows nothing: every token is as likely as any other.", 0, ""),
        ("n2", "N", "Training is a game. Take a sentence from the internet. Hide the next word. Let the machine guess.", 1.4, ""),
        ("n3", "N", "Once upon a: the machine gives time three percent. The truth is time, one hundred percent. The error is how far three is from one hundred.", 1.4, "Once upon a: the machine gives time 3 %. The truth is time, 100 %. The error is how far 3 is from 100."),
        ("n4", "N", "One sentence, one error. That number is all the machine learns from.", 1.4, "1 sentence, 1 error. That number is all the machine learns from."),
    ], 1.0),
    ("nudge", "2 / 4   the nudge", [
        ("n5", "N", "The error flows backward through the layers, like in the episode on error. Every weight learns which way to move.", 0, ""),
        ("n6", "N", "Each weight moves a tiny step. Billions of weights, all at once.", 1.4, ""),
        ("n7", "N", "Next time, on the same sentence, time gets four percent. A little better. Then the next sentence.", 1.4, "Next time, on the same sentence, time gets 4 %. A little better. Then the next sentence."),
    ], 1.0),
    ("scale", "3 / 4   the scale", [
        ("n8", "N", "Now do it on everything ever written. Trillions of words. Thousands of machines, for months.", 0, ""),
        ("n9", "N", "The error goes down. Fast at first, then slower. Each step is tiny, but there are billions of them.", 1.4, ""),
        ("n10", "N", "Nobody writes a rule. Nobody tells it what a noun is, or what the capital of France is. Only: guess the next word.", 1.4, ""),
    ], 1.0),
    ("learned", "4 / 4   what it learned", [
        ("n11", "N", "To guess the next word well, the machine had to learn grammar. Facts. Styles. Arithmetic. Everything the next word depends on.", 0, ""),
        ("n12", "N", "The capital of France is: Paris. Two plus two equals: four. Dear Sir: I hope this. The weights hold it all.", 1.4, "The capital of France is: Paris. 2 + 2 =: 4. Dear Sir: I hope this. The weights hold it all."),
        ("n13", "N", "It learned the internet: the true and the false alike. Next time: how much it can hold in mind at once. Memory.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。間違えるたびに、少し変わる。", 0, "Master Foo said: each time it is wrong, it changes a little."),
        ("m5", "M", "何十億回も。それが、学ぶということだ。", 1.4, "Billions of times. That is what learning is."),
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
    w("""// Entraînement — Thus Spoke Master Foo, AI 07: where the weights come
// from. At first they are random; training is a game: a sentence from the
// internet, the next word hidden, the machine guesses; the error is how
// far the guess is from the truth; it flows backward and every weight
// moves a tiny step; done on everything ever written, on thousands of
// machines for months, the error goes down; and to guess the next word
// well the machine had to learn grammar, facts, styles, arithmetic. The
// numbers are illustrative. Master Foo speaks Japanese, translated in the
// captions.
""")
    for f in ["koan", "guess", "nudge", "scale", "learned"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Entrainement {")
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
                          f'kana: ["ガ", "ク", "シ", "ュ", "ウ"], episode: "AI 07  ·  training", accent: {a})',
        "guess": lambda a: f'Guess(flat0: {lt("n1.words[7]", "guess")}, sentence0: {lt("n2.words[4]", "guess")}, hide0: {lt("n2.words[10]", "guess")}, guess0: {lt("n3.words[3]", "guess")}, truth0: {lt("n3.words[8]", "guess")}, error0: {lt("n3.words[14]", "guess")}, accent: {a})',
        "nudge": lambda a: f'Nudge(layers0: {lt("n5.start - 1.2", "nudge")}, back0: {lt("n5.words[2]", "nudge")}, step0: {lt("n6.words[3]", "nudge")}, again0: {lt("n7.words[0]", "nudge")}, accent: {a})',
        "scale": lambda a: f'Scale(machines0: {lt("n8.words[8]", "scale")}, curve0: {lt("n9.words[0]", "scale")}, curve1: {lt("n10.end + 1.0", "scale")}, rule0: {lt("n10.words[0]", "scale")}, accent: {a})',
        "learned": lambda a: f'Learned(at: [{lt("n12.words[0]", "learned")}, {lt("n12.words[6]", "learned")}, {lt("n12.words[11]", "learned")}], all0: {lt("n12.words[16]", "learned")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ガ", "ク", "シ", "ュ", "ウ"], episode: "AI 07  ·  training", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 07", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the flat row; the word hidden; the guess, the truth, the error
  pattern flat = repeat 20 event(t: (n1.words[7] + 0.05 * {L["guess"]} * (i / 20)) / total, x: 0.1 + 0.8 * i / 20, y: 0.55, intensity: 0.25)
  pattern hidden = repeat 1 event(t: n2.words[10] / total, x: 0.5, y: 0.3, size: 0.06, intensity: 0.7)
  pattern guessed = repeat 4 event(t: (n3.words[3] + 0.015 * {L["guess"]} * i) / total, x: 0.4, y: 0.52 + 0.08 * i, size: 0.04, intensity: 0.5)
  pattern truth = repeat 1 event(t: n3.words[8] / total, x: 0.6, y: 0.5, size: 0.1, intensity: 0.8)
  pattern error = repeat 1 event(t: n3.words[14] / total, x: 0.5, y: 1.07, size: 0.12, intensity: 0.9)
  // the error flowing back; the step; again
  pattern flowing = repeat 12 event(t: (n5.words[2] + 0.12 * {L["nudge"]} * (i / 12)) / total, x: 0.92 - 0.84 * i / 12, y: 0.3, intensity: 0.3 + 0.03 * i)
  pattern stepped = repeat 1 event(t: n6.words[3] / total, x: 0.5, y: 0.5, size: 0.3, intensity: 0.9)
  pattern again = repeat 1 event(t: n7.words[0] / total, x: 0.5, y: 1.08, size: 0.06, intensity: 0.6)
  // the machines; the curve going down
  pattern machines = repeat 48 event(t: (n8.words[8] + 0.08 * {L["scale"]} * (i / 48)) / total, x: 0.12 + 0.76 * (i % 16) / 15, y: 0.22 + 0.06 * floor(i / 16), intensity: 0.25)
  pattern down = repeat 24 event(t: (n9.words[0] + ({L["scale"]} - (n9.words[0] - {S["scale"]:.2f}) - 1.0) * (i / 24)) / total, x: 0.12 + 0.76 * i / 24, y: 1.1 - 0.44 / (1 + 14 * i / 24) ^ 0.6, intensity: 0.2 + 0.3 * (1 - i / 24))
  // the answers
  pattern answers = repeat 3 event(t: ([n12.words[0], n12.words[6], n12.words[11]][i] + 0.05 * {L["learned"]}) / total, x: 0.55, y: 0.42 + 0.18 * i, size: 0.05, intensity: 0.7)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(flat, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(hidden, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(guessed, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(truth, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(error, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.7),
    notes(flowing, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.35),
    notes(stepped, instrument: chord, scale: "major", key: 82, gain: 0.45),
    notes(again, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(machines, instrument: tick, scale: "hirajoshi", key: 660, gain: 0.25),
    notes(down, instrument: "kalimba", scale: "hirajoshi", key: 262, gain: 0.4),
    notes(answers, instrument: "glass", scale: "hirajoshi", key: 659, gain: 0.5),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['scale'] + L['scale'] * 0.8) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "entrainement.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
