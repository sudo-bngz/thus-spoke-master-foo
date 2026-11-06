#!/usr/bin/env python3
"""Writes attention.alea: the voices, the timing, the captions. The
attention scores are illustrative (no model runs here).

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a5"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。文の中で、どの言葉を見ればよいのですか。", 0, "The novice asked: in a sentence, which words should I look at?"),
        ("m2", "M", "師は言った。猫は腹が減っていた。だから、それは魚を食べた。「それ」とは、何か。", 1.4, "Master Foo said: the cat was hungry, so it ate the fish. What is 'it'?"),
        ("m3", "M", "弟子は答えた。猫です。師は言った。どうして分かった。", 1.4, "The novice answered: the cat. Master Foo said: how did you know?"),
    ], 0.6),
    ("problem", "1 / 4   the word alone", [
        ("n1", "N", "A word alone means little. 'it' could be anything. Its meaning comes from the words around it.", 0, ""),
        ("n2", "N", "The cat was hungry, so it ate the fish. Here, 'it' is the cat. You knew that at once. The model has to work it out.", 1.4, ""),
        ("n3", "N", "Last time, each word became a point on the map. But that point is the same wherever the word appears. 'it' needs more than that.", 1.4, ""),
    ], 1.0),
    ("scores", "2 / 4   looking", [
        ("n4", "N", "So each word looks at every other word, and gives it a score: how much does that word matter to me, here?", 0, ""),
        ("n5", "N", "For 'it': cat, a lot. hungry, a little. fish and ate, a little. the and so, almost nothing.", 1.4, ""),
        ("n6", "N", "The scores add up to one. They are the attention of 'it'.", 1.4, "The scores add up to 1. They are the attention of 'it'."),
        ("n7", "N", "And every word does this at the same time. All of them, looking at all of them.", 1.4, ""),
    ], 1.0),
    ("keys", "3 / 4   the question and the label", [
        ("n8", "N", "Where do the scores come from? From the map.", 0, ""),
        ("n9", "N", "From its point, each word makes two small things: a question, and a label.", 1.4, "From its point, each word makes 2 small things: a question, and a label."),
        ("n10", "N", "'it' asks: what is a living thing, mentioned before me? The label of cat answers that well. The score is how well a question matches a label.", 1.4, ""),
        ("n11", "N", "Questions and labels are made with weights. And the weights are learned, like everything else, by the error flowing backward.", 1.4, ""),
    ], 1.0),
    ("blend", "4 / 4   the blend", [
        ("n12", "N", "Then each word takes a blend of the others, weighted by its scores. 'it' takes mostly cat.", 0, ""),
        ("n13", "N", "Its point on the map moves. 'it' now stands near cat. The word has absorbed its context.", 1.4, ""),
        ("n14", "N", "Do this in a layer, then again in the next, and again: dozens of times. Each time, every word looks at all the others.", 1.4, ""),
        ("n15", "N", "That is a transformer: the T in GPT. Next time: what it does with all this, one token at a time.", 1.4, "That is a transformer: the T in GPT. Next time: what it does with all this, 1 token at a time."),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "弟子は言った。「それ」は、猫を見ていました。", 0, "The novice said: 'it' was looking at the cat."),
        ("m5", "M", "師は言った。言葉は、互いを見る。それが、注意だ。", 1.4, "Master Foo said: words look at each other. That is attention."),
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
    w("""// Attention — Thus Spoke Master Foo, AI 05: the transformer's idea. The
// cat was hungry, so it ate the fish: what is "it"? A word alone means
// little; each word looks at every other and gives it a score (the
// attention, adding up to one); the scores come from a question and a
// label made from each word's point on the map; then each word becomes a
// blend of the others, weighted by its scores, and absorbs its context;
// layer after layer. The scores are illustrative. Master Foo speaks
// Japanese, translated in the captions.
""")
    for f in ["koan", "problem", "scores", "keys", "blend"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Attention {")
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
                          f'kana: ["チ", "ュ", "ウ", "イ"], episode: "AI 05  ·  attention", accent: {a})',
        "problem": lambda a: f'Problem(show: {lt("n2.words[0]", "problem")}, it0: {lt("n2.words[9]", "problem")}, ask0: {lt("n2.words[9]", "problem")}, same0: {lt("n3.words[11]", "problem")}, accent: {a})',
        "scores": lambda a: f'Scores(look0: {lt("n4.words[3]", "scores")}, scores0: {lt("n5.words[1]", "scores")}, sum0: {lt("n6.words[1]", "scores")}, all0: {lt("n7.words[1]", "scores")}, accent: {a})',
        "keys": lambda a: f'Keys(point0: {lt("n8.words[7]", "keys")}, cards0: {lt("n9.words[6]", "keys")}, labels0: {lt("n10.words[12]", "keys")}, match0: {lt("n10.words[17]", "keys")}, accent: {a})',
        "blend": lambda a: f'Blend(move0: {lt("n13.words[0]", "blend")}, moved0: {lt("n13.words[5]", "blend")}, layers0: {lt("n14.words[3]", "blend")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["チ", "ュ", "ウ", "イ"], episode: "AI 05  ·  attention", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 05", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the sentence placed; `it` lit; the same point
  pattern placed = repeat 9 event(t: (n2.words[0] + 0.04 * {L["problem"]} * (i / 9)) / total, x: 0.5 + 0.3 * cos(tau * i / 9), y: 0.5 + 0.3 * sin(tau * i / 9), intensity: 0.4)
  pattern itlit = repeat 1 event(t: n2.words[9] / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the chords of `it`, one by one, louder with the score; everyone looking
  pattern chords = repeat 8 event(t: (n4.words[3] + 0.025 * {L["scores"]} * i) / total, x: 0.5 + 0.3 * cos(tau * (i + 6) / 9), y: 0.5 + 0.3 * sin(tau * (i + 6) / 9), size: 0.03 + 0.1 * [0.1, 0.02, 0.08, 0.02, 0.03, 0.55, 0.03, 0.12][i], intensity: 0.3 + 0.6 * [0.1, 0.02, 0.08, 0.02, 0.03, 0.55, 0.03, 0.12][i])
  pattern everyone = repeat 24 event(t: (n7.words[1] + 0.08 * {L["scores"]} * (i / 24)) / total, x: ~between(0.2, 0.8), y: ~between(0.3, 0.8), intensity: 0.25)
  // the cards, the matches
  pattern cards = repeat 2 event(t: (n9.words[6] + 0.04 * {L["keys"]} * i) / total, x: 0.55, y: 0.4 + 0.2 * i, size: 0.04, intensity: 0.6)
  pattern matches = repeat 3 event(t: (n10.words[17] + 0.06 * {L["keys"]} * i + 0.1 * {L["keys"]}) / total, x: 0.6, y: 0.5 + 0.1 * i, size: 0.03 + 0.08 * [0.55, 0.12, 0.02][i], intensity: 0.3 + 0.6 * [0.55, 0.12, 0.02][i])
  // the move, the layers
  pattern moved = repeat 1 event(t: n13.words[5] / total, x: 0.4, y: 0.4, size: 0.1, intensity: 0.7)
  pattern layers = repeat 3 event(t: (n14.words[3] + 0.12 * {L["blend"]} * i) / total, x: 0.5, y: 0.7 - 0.2 * i, size: 0.06, intensity: 0.6)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(placed, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.35),
    notes(itlit, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(chords, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(everyone, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(cards, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(matches, instrument: "kalimba", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(moved, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(layers, instrument: chord, scale: "major", key: 82, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['scores'] + L['scores'] * 0.5) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "attention.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
