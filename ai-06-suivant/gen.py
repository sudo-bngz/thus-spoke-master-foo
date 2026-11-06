#!/usr/bin/env python3
"""Writes suivant.alea: the voices, the timing, the captions. The
probabilities are illustrative (no model runs here); the die's three
temperatures are computed here (p^(1/T), normalised).

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a6"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

CAND = ["time", "midnight", "the", "dragon"]
PROB = [62, 8, 5, 1]
TEMPS = [0, 0.7, 1.5]


def reshaped(T):
    if T == 0:
        return [100 if k == PROB.index(max(PROB)) else 0 for k in range(4)]
    w = [p ** (1 / T) for p in PROB]
    return [round(100 * x / sum(w)) for x in w]


TPROBS = [v for T in TEMPS for v in reshaped(T)]
PICKS = [0, 0, 3]

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、どうやって話すのですか。", 0, "The novice asked: how does the machine speak?"),
        ("m2", "M", "師は言った。むかしむかし、あるところに。次の言葉は？", 1.4, "Master Foo said: once upon a time, in a certain place. The next word?"),
        ("m3", "M", "弟子は答えた。おじいさん。", 1.4, "The novice answered: an old man."),
    ], 0.6),
    ("job", "1 / 4   the job", [
        ("n1", "N", "Last time, every word looked at every other, layer after layer. At the end, the last word's point holds the whole sentence so far.", 0, ""),
        ("n2", "N", "One more layer turns that point into a score for every token the machine knows. Fifty thousand scores, one per token.", 1.4, "1 more layer turns that point into a score for every token the machine knows. 50 000 scores, 1 per token."),
        ("n3", "N", "The scores are squeezed so that they add up to one. Now they are probabilities: how likely each token is to come next.", 1.4, "The scores are squeezed so that they add up to 1. Now they are probabilities: how likely each token is to come next."),
        ("n4", "N", "Once upon a: time, sixty-two percent. midnight, eight. the, five. dragon, one. And forty-nine thousand nine hundred ninety-six others, sharing the rest.", 1.4, "Once upon a: time, 62 %. midnight, 8. the, 5. dragon, 1. And 49 996 others, sharing the rest."),
    ], 1.0),
    ("next", "2 / 4   the pick", [
        ("n5", "N", "The machine picks one, adds it to the text, and starts over. The new text goes through all the layers again.", 0, "The machine picks 1, adds it to the text, and starts over. The new text goes through all the layers again."),
        ("n6", "N", "Once upon a time. It asks again, and picks: there. It asks again: was. One token at a time, each one chosen after the whole text so far.", 1.4, "Once upon a time. It asks again, and picks: there. It asks again: was. 1 token at a time, each 1 chosen after the whole text so far."),
        ("n7", "N", "That is all the machine does. A paragraph is a few hundred rounds. A long answer, a few thousand.", 1.4, ""),
    ], 1.0),
    ("dice", "3 / 4   the die", [
        ("n8", "N", "Which one does it pick? Not always the top one. It rolls a die, weighted by the probabilities.", 0, "Which 1 does it pick? Not always the top 1. It rolls a die, weighted by the probabilities."),
        ("n9", "N", "A setting called temperature shapes the die. At zero, it always takes the top token: the same text every time.", 1.4, "A setting called temperature shapes the die. At 0, it always takes the top token: the same text every time."),
        ("n10", "N", "Higher, and the rare ones get their chance: dragon, sometimes. Same question, different answers. That is why the machine never says the same thing twice.", 1.4, ""),
        ("n11", "N", "And the die is rolled with a seed, like in the episode on chance. Same seed, same rolls, same text.", 1.4, ""),
    ], 1.0),
    ("loop", "4 / 4   the loop", [
        ("n12", "N", "Put it together. Text. Tokens. The map. The layers. Probabilities. The die. And the chosen token goes back into the text.", 0, ""),
        ("n13", "N", "Round and round, billions of times. That is a language model. Nothing else is inside: no dictionary, no rules, no plan. Only the next token.", 1.4, ""),
        ("n14", "N", "Next time: where the weights come from. Training.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。それが、機械のすることのすべてだ。", 0, "Master Foo said: that is all the machine does."),
        ("m5", "M", "一語ずつ。何十億回も。", 1.4, "1 word at a time. Billions of times."),
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
    w("""// Suivant — Thus Spoke Master Foo, AI 06: the next token. Once upon a:
// the last word's point, after all the layers, becomes a score for every
// token the machine knows; squeezed, the scores are probabilities; the
// machine picks one, adds it to the text, and starts over, one token at a
// time; which one it picks is a weighted die, shaped by the temperature
// and rolled with a seed; and the whole machine is a loop: text, tokens,
// map, layers, probabilities, die, and back into the text. The
// probabilities are illustrative; the die's temperatures are computed by
// gen.py. Master Foo speaks Japanese, translated in the captions.
""")
    for f in ["koan", "job", "next", "dice", "loop"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Suivant {")
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
    w("  // ── the candidates and their probabilities (illustrative), and the die's three temperatures (gen.py) ──")
    w("  let cand = [" + ", ".join(f'"{c}"' for c in CAND) + "]")
    w(f"  let tprobs = {alist(TPROBS)}")
    w(f"  let picks = {alist(PICKS)}")
    w("")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ツ", "ギ"], episode: "AI 06  ·  next", accent: {a})',
        "job": lambda a: f'Job(point0: {lt("n1.words[14]", "job")}, layer0: {lt("n2.words[0]", "job")}, column0: {lt("n2.words[8]", "job")}, squeeze0: {lt("n3.words[3]", "job")}, '
                         f'top: [{lt("n4.words[3]", "job")}, {lt("n4.words[6]", "job")}, {lt("n4.words[8]", "job")}, {lt("n4.words[10]", "job")}], rest0: {lt("n4.words[12]", "job")}, accent: {a})',
        "next": lambda a: f'Next(cand: ["time", "midnight", "the", "dragon", "there", "a", "in", "the", "was", "lived", "were", "is"], starts: [{lt("n5.start - 1.2", "next")}, {lt("n5.words[8]", "next")}, {lt("n6.words[11] + 0.3", "next")}], taken: [{lt("n5.words[2]", "next")}, {lt("n6.words[9]", "next")}, {lt("n6.words[13]", "next")}], accent: {a})',
        "dice": lambda a: f'Dice(cand: cand, probs: tprobs, picks: picks, at: [{lt("n9.words[7]", "dice")}, {lt("n8.words[11]", "dice")}, {lt("n10.words[0]", "dice")}], accent: {a})',
        "loop": lambda a: f'Loop(when: [{lt("n12.words[3]", "loop")}, {lt("n12.words[4]", "loop")}, {lt("n12.words[6]", "loop")}, {lt("n12.words[8]", "loop")}, {lt("n12.words[9]", "loop")}, {lt("n12.words[11]", "loop")}], back0: {lt("n12.words[12]", "loop")}, round0: {lt("n13.words[0]", "loop")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ツ", "ギ"], episode: "AI 06  ·  next", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 06", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the point; the column pouring; the four bars, and the rest
  pattern point = repeat 1 event(t: n1.words[14] / total, x: 0.16, y: 0.5, size: 0.05, intensity: 0.7)
  pattern pour = repeat 24 event(t: (n2.words[8] + 0.06 * {L["job"]} * (i / 24)) / total, x: 0.72, y: 0.3 + 0.4 * i / 24, intensity: 0.3)
  pattern four = repeat 4 event(t: [n4.words[3], n4.words[6], n4.words[8], n4.words[10]][i] / total, x: 0.5, y: 0.98 + 0.08 * i, size: 0.03 + 0.1 * [0.62, 0.08, 0.05, 0.01][i], intensity: 0.3 + 0.6 * [0.62, 0.08, 0.05, 0.01][i])
  // the three picks
  pattern picked = repeat 3 event(t: [n5.words[2], n6.words[9], n6.words[13]][i] / total, x: 0.5, y: 0.3, size: 0.06, intensity: 0.8)
  // the die landing, three times
  pattern lands = repeat 3 event(t: ([n9.words[7], n8.words[11], n10.words[0]][i] + 0.17 * {L["dice"]}) / total, x: 0.84, y: 0.35 + 0.3 * i, size: 0.05, intensity: 0.7)
  // the six stations, then the light going round
  pattern stations = repeat 6 event(t: [n12.words[3], n12.words[4], n12.words[6], n12.words[8], n12.words[9], n12.words[11]][i] / total, x: 0.5 + 0.3 * cos(-tau / 4 + tau * i / 6), y: 0.78 + 0.3 * sin(-tau / 4 + tau * i / 6), size: 0.05, intensity: 0.6)
  pattern round = repeat 12 event(t: (n13.words[0] + {L["loop"]} * 0.45 * ((i / 12) ^ (1 / 1.5))) / total, x: 0.5 + 0.3 * cos(-tau / 4 + tau * 2.2 * i / 12), y: 0.78 + 0.3 * sin(-tau / 4 + tau * 2.2 * i / 12), intensity: 0.35)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(point, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(pour, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(four, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(picked, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(lands, instrument: knock, scale: "hirajoshi", key: 220, gain: 0.6),
    notes(stations, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.45),
    notes(round, instrument: tick, scale: "hirajoshi", key: 660, gain: 0.3),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['dice'] + L['dice'] * 0.75) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "suivant.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
