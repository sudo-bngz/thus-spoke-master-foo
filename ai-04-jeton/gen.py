#!/usr/bin/env python3
"""Writes jeton.alea: the voices, the timing, the captions. The token
ids and the places on the map are illustrative (no tokenizer or model
runs here); the map is jittered by the edition.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a4"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、言葉をどう読むのですか。", 0, "The novice asked: how does a machine read words?"),
        ("m2", "M", "師は言った。機械は、言葉を読まない。数を読む。", 1.4, "Master Foo said: the machine does not read words. It reads numbers."),
        ("m3", "M", "そして師は、一枚の地図を広げた。", 1.4, "And Master Foo unrolled a map."),
    ], 0.6),
    ("pieces", "1 / 4   the pieces", [
        ("n1", "N", "A language model does not read letters. And not quite words, either. It reads tokens.", 0, ""),
        ("n2", "N", "A token is a piece of text: a short word, a part of a long one, a punctuation mark.", 1.4, ""),
        ("n3", "N", "This sentence is four tokens.", 1.4, "This sentence is 4 tokens."),
        ("n4", "N", "This long word is three.", 1.4, "This long word is 3."),
        ("n5", "N", "A model knows about fifty thousand tokens. That list is its vocabulary. Everything it ever reads or writes is made of them.", 1.4, "A model knows about 50 000 tokens. That list is its vocabulary. Everything it ever reads or writes is made of them."),
    ], 1.0),
    ("numbers", "2 / 4   the numbers", [
        ("n6", "N", "Each token has a place in the vocabulary: a number.", 0, ""),
        ("n7", "N", "So to the machine, a sentence is only a list of numbers.", 1.4, ""),
        ("n8", "N", "But a number says nothing about meaning. Four thousand nine hundred fifty-eight and fifty-nine are neighbours by chance, like two words on the same page of a dictionary.", 1.4, "But a number says nothing about meaning. 4958 and 4959 are neighbours by chance, like 2 words on the same page of a dictionary."),
    ], 1.0),
    ("map", "3 / 4   the map", [
        ("n9", "N", "So the model gives every token a second thing: a place on a map.", 0, ""),
        ("n10", "N", "A point, with coordinates. Hundreds of them, in a real model. Here, two, so that we can see it.", 1.4, "A point, with coordinates. Hundreds of them, in a real model. Here, 2, so that we can see it."),
        ("n11", "N", "Words used in the same ways end up close together: cat near dog, king near queen. Tuesday, far from both.", 1.4, ""),
        ("n12", "N", "This place is called an embedding. Nobody draws the map: the model learns it, like the weights of the last episode, by moving words until their neighbours make sense.", 1.4, ""),
    ], 1.0),
    ("arrows", "4 / 4   the directions", [
        ("n13", "N", "And on this map, directions mean something.", 0, ""),
        ("n14", "N", "From man to woman is an arrow. Start from king, follow the same arrow: you land near queen.", 1.4, ""),
        ("n15", "N", "Points that can be added and subtracted like this are called vectors. King, minus man, plus woman, is queen.", 1.4, ""),
        ("n16", "N", "This is what the model computes with: not words, but points on a map, where meaning is nearness. Next time: how it knows which words to look at.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "弟子は見た。地図の上で、王と女王は隣り合っていた。", 0, "The novice looked: on the map, the king and the queen stood side by side."),
        ("m5", "M", "師は言った。意味とは、近さだ。", 1.4, "Master Foo said: meaning is nearness."),
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
    w("""// Jeton — Thus Spoke Master Foo, AI 04: tokens, and the map of meaning.
// The machine does not read words; it reads numbers; Master Foo unrolls a
// map. A token is a piece of text (a sentence of four, a long word of
// three, a vocabulary of 50 000); each has a number, which says nothing
// about meaning; so each gets a place on a map, learned, where words used
// in the same ways sit close (an embedding); and directions mean
// something: king − man + woman ≈ queen. The ids and the places are
// illustrative; the edition jitters the map. Master Foo speaks Japanese,
// translated in the captions.
""")
    for f in ["koan", "pieces", "numbers", "atlas"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Jeton {")
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
    w("""  // ── the map, jittered by the edition ──
  let jx = [~between(-0.02, 0.02) for k in range(13)]
  let jy = [~between(-0.02, 0.02) for k in range(13)]
""")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ト", "ー", "ク", "ン"], episode: "AI 04  ·  token", accent: {a})',
        "pieces": lambda a: f'Pieces(sentence0: {lt("n3.words[0]", "pieces")}, cut0: {lt("n3.words[2]", "pieces")}, cut1: {lt("n3.words[3]", "pieces")}, word0: {lt("n4.words[0]", "pieces")}, vocab0: {lt("n5.words[4]", "pieces")}, accent: {a})',
        "numbers": lambda a: f'Numbers(ids0: {lt("n6.words[6]", "numbers")}, list0: {lt("n7.words[6]", "numbers")}, dict0: {lt("n8.words[8]", "numbers")}, accent: {a})',
        "map": lambda a: f'Atlas(jx: jx, jy: jy, axes0: {lt("n9.words[9]", "map")}, first0: {lt("n10.words[0]", "map")}, cluster0: {lt("n11.words[0]", "map")}, far0: {lt("n11.words[15]", "map")}, arrow0: 5, same0: 5, land0: 5, accent: {a})',
        "arrows": lambda a: f'Atlas(jx: jx, jy: jy, axes0: -1, first0: -1, cluster0: -1, far0: -1, arrow0: {lt("n14.words[0]", "arrows")}, same0: {lt("n14.words[6]", "arrows")}, land0: {lt("n14.words[13]", "arrows")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ト", "ー", "ク", "ン"], episode: "AI 04  ·  token", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 04", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the temple bell when the master speaks; the map unrolled
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern unrolled = repeat 1 event(t: (m3.start + 0.5 * m3.duration) / total, x: 0.5, y: 0.5, size: 0.08, intensity: 0.7)
  // the cuts, the long word, the vocabulary scrolling
  pattern cuts = repeat 3 event(t: (n3.words[2] + (n3.words[3] - n3.words[2]) * i / 3) / total, x: 0.3 + 0.2 * i, y: 0.5, intensity: 0.7)
  pattern wcuts = repeat 2 event(t: (n4.words[0] + {L["pieces"]} * (0.08 + 0.06 * i)) / total, x: 0.4 + 0.2 * i, y: 0.6, intensity: 0.7)
  pattern vocab = repeat 12 event(t: (n5.words[4] + 0.12 * i) / total, x: 0.3, y: 0.9 - 0.05 * i, intensity: 0.3)
  // the numbers, the list, the neighbour
  pattern numbers = repeat 4 event(t: (n6.words[6] + 0.05 * {L["numbers"]} * i) / total, x: 0.3 + 0.13 * i, y: 0.5, intensity: 0.5)
  pattern listed = repeat 1 event(t: n7.words[6] / total, x: 0.5, y: 0.6, size: 0.06, intensity: 0.6)
  pattern neighbour = repeat 1 event(t: (n8.words[8] + 0.1 * {L["numbers"]}) / total, x: 0.45, y: 0.8, size: 0.04, intensity: 0.7)
  // the map: the words placed, one by one
  pattern placed = repeat 13 event(t: ([n10.words[0], n10.words[0], n11.words[0], n11.words[0] + 0.025 * {L["map"]}, n11.words[0] + 0.05 * {L["map"]}, n11.words[0] + 0.075 * {L["map"]}, n11.words[0] + 0.1 * {L["map"]}, n11.words[0] + 0.125 * {L["map"]}, n11.words[0] + 0.15 * {L["map"]}, n11.words[0] + 0.175 * {L["map"]}, n11.words[15], n11.words[15] + 0.03 * {L["map"]}, n11.words[15] + 0.06 * {L["map"]}][i]) / total, x: 0.2 + 0.6 * fract(i * 0.37), y: 0.3 + 0.5 * fract(i * 0.61), intensity: 0.5)
  // the arrows, the landing
  pattern arrows = repeat 2 event(t: [n14.words[0], n14.words[6]][i] / total, x: 0.8, y: 0.5, size: 0.08, intensity: 0.6)
  pattern landed = repeat 3 event(t: n14.words[13] / total, x: 0.7, y: [0.5, 0.4, 0.3][i], size: 0.1, intensity: 0.7)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(unrolled, instrument: brush, scale: "chromatic", key: 100, gain: 0.5),
    notes(cuts, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.5),
    notes(wcuts, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.5),
    notes(vocab, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.25),
    notes(numbers, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.4),
    notes(listed, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(neighbour, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.5),
    notes(placed, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(arrows, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(landed, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['arrows'] + L['arrows'] * 0.7) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "jeton.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
