#!/usr/bin/env python3
"""Writes token.alea: the voices, the timing, the captions, and the
probabilities of the next-token scenes (illustrative, not a real model's;
the temperature rows are computed from them: p^(1/T), normalised).

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from episode import GAP, caption, layout, measure

SEED = "0xa164"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 0.95)
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
        ("m1", "M", "弟子は尋ねた。機械は、どうやって話すのですか。", 0, "The novice asked: how does a machine speak?"),
        ("m2", "M", "師は言った。むかしむかし、あるところに。次の言葉は？", 1.2, "Master Foo said: once upon a time, in a certain place… The next word?"),
        ("m3", "M", "弟子は答えた。おじいさん。", 1.4, "The novice answered: an old man."),
    ], 1.0),
    ("tokens", "1 / 4   tokens", [
        ("n1", "N", "A language model does not read letters, nor words. It reads tokens: pieces of words, each one a number.", 0, ""),
        ("n2", "N", "A long word can be three tokens.", 1.2, "A long word can be 3 tokens."),
    ], 1.5),
    ("next", "2 / 4   the next token", [
        ("n3", "N", "Its only job: given the tokens so far, a probability for every token that could come next.", 0, ""),
        ("n4", "N", "Once upon a: time, sixty-two percent. Midnight, eight. The, five. And fifty thousand others.", 1.2, "Once upon a: time, 62 %. Midnight, 8. The, 5. And 50 000 others."),
        ("n5", "N", "It picks one, adds it to the text, and asks again. One token at a time.", 1.2, "It picks 1, adds it to the text, and asks again. 1 token at a time."),
        ("n6", "N", "That is the whole machine. Everything it writes is this, repeated.", 1.2, ""),
    ], 1.0),
    ("dice", "3 / 4   the die", [
        ("n7", "N", "It does not always take the most likely one. It rolls a die, weighted by the probabilities.", 0, ""),
        ("n8", "N", "Temperature shapes the die: at zero, always the top. Higher, and the rare words come out.", 1.2, "Temperature shapes the die: at 0, always the top. Higher, and the rare words come out."),
        ("n9", "N", "The same question, different answers: a die, with a very good memory.", 1.4, ""),
    ], 0.8),
    ("knobs", "4 / 4   the knobs", [
        ("n10", "N", "Where do the probabilities come from? From reading nearly everything ever written.", 0, ""),
        ("n11", "N", "Hundreds of billions of knobs, turned a little at each sentence, until the guesses matched the text.", 1.2, ""),
        ("n12", "N", "It does not know. It predicts. And at this scale, predicting looks a lot like knowing.", 1.6, ""),
    ], 0.8),
    ("end", "", [
        ("m4", "M", "師は言った。それが、機械のすることのすべてだ。", 0, "Master Foo said: that is all the machine does."),
        ("m5", "M", "一語ずつ。何十億回も。", 1.2, "1 word at a time. Billions of times."),
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
    w("""// Token — Thus Spoke Master Foo, 05: what is a language model? A novice
// asks how a machine speaks; Master Foo says "once upon a time, in a
// certain place…" and asks for the next word. A model reads tokens, pieces
// of words, each a number; its only job is a probability for every token
// that could come next; it picks one, adds it, asks again. It rolls a die
// weighted by the probabilities, and temperature shapes the die. The
// probabilities come from reading nearly everything, hundreds of billions
// of knobs turned until the guesses matched. The probabilities shown are
// illustrative (gen.py). Master Foo speaks Japanese, translated in the
// captions.
""")
    for f in ["koan", "tokens", "next", "dice", "knobs"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Token {")
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
                          f'kana: ["ト", "ー", "ク", "ン"], episode: "05  ·  token", big: "?", bigsize: 0.2, bigat: [{lt("m2.end - 0.3", "koan")}, {lt("m3.end + 5", "koan")}], bigoff: {lt("m3.start + 0.6 * m3.duration", "koan")}, accent: {a})',
        "tokens": lambda a: f'Tokens(cut0: {lt("n1.words[11]", "tokens")}, cut1: {lt("n1.words[14]", "tokens")}, word0: {lt("n2.words[1]", "tokens")}, accent: {a})',
        "next": lambda a: f'Next(cand: ["time", "midnight", "the", "dragon", "there", "a", "in", "the", "was", "lived", "were", "is"], starts: [{lt("n4.words[0]", "next")}, {lt("n5.words[9]", "next")}, {lt("n6.words[0]", "next")}], pick: (n5.words[1] - n4.words[0]) / {L["next"]}, accent: {a})',
        "dice": lambda a: f'Dice(cand: cand, probs: tprobs, picks: picks, at: [{lt("n8.words[4]", "dice")}, {lt("n7.words[8]", "dice")}, {lt("n8.words[9]", "dice")}], accent: {a})',
        "knobs": lambda a: f'Knobs(read0: {lt("n10.words[6]", "knobs")}, settle: {lt("n11.end", "knobs")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ト", "ー", "ク", "ン"], episode: "05  ·  token", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  05", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  let snip = synth {{ highpass(noise(), cutoff: 3000, resonance: 0.3) * perc(attack: 0.001, release: 0.04) * note.velocity }}
  let sweep = synth {{ lowpass(saw(note.freq * (1 + 0.5 * note.time)), cutoff: 800 + 2000 * note.time, resonance: 0.3) * adsr(attack: 0.02, decay: 0.3, sustain: 0.5, release: 0.2) * 0.5 }}
  let tumble = synth {{ bandpass(noise(), cutoff: 1200, resonance: 0.6) * perc(release: 0.03) * note.velocity + sine(note.freq) * perc(release: 0.04) * 0.3 }}
  // the temple bell when the master speaks; the question, and the answer
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern asked = repeat 1 event(t: (m2.end - 0.3) / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the cuts between tokens, the numbers; the long word cut
  pattern cuts = repeat 3 event(t: (n1.words[11] + (n1.words[14] - n1.words[11]) * (i + 1) / 3) / total, x: 0.3 + 0.2 * i, y: 0.5, intensity: 0.7)
  pattern ids = repeat 4 event(t: (n1.words[11] + (n1.words[14] - n1.words[11]) * i / 3 + 0.4) / total, x: 0.3 + 0.15 * i, y: 0.4 + 0.1 * (i % 2), intensity: 0.4)
  pattern wcuts = repeat 2 event(t: (n2.words[1] + {L["tokens"]} * (0.1 + 0.08 * i)) / total, x: 0.4 + 0.2 * i, y: 0.6, intensity: 0.7)
  // the bars growing, the pick, three rounds
  pattern grows = repeat 3 event(t: ([n4.words[0], n5.words[9], n6.words[0]][i] + 0.02 * {L["next"]}) / total, x: 0.5, y: 0.6, size: 0.05, intensity: 0.5)
  pattern picked = repeat 3 event(t: ([n4.words[0], n5.words[9], n6.words[0]][i] + n5.words[1] - n4.words[0]) / total, x: 0.5, y: 0.35, size: 0.05, intensity: 0.8)
  // the die tumbling, three times, and landing
  pattern tumbles = repeat 30 event(t: ([n8.words[4], n7.words[8], n8.words[9]][floor(i / 10)] + {L["dice"]} * (0.12 + 0.05 * (i % 10) / 10)) / total, x: ~between(0.3, 0.7), y: ~between(0.4, 0.7), intensity: 0.4)
  pattern lands = repeat 3 event(t: ([n8.words[4], n7.words[8], n8.words[9]][i] + {L["dice"]} * 0.17) / total, x: 0.8, y: [0.5, 0.5, 0.3][i], size: 0.05, intensity: 0.8)
  // the reading: a crackle of knobs turning, fading as they settle
  let turning = (T > n10.words[6]) * (1 - smoothstep(n11.end - 3, n11.end, T)) + x * 0
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(cuts, instrument: snip, gain: 0.5),
    notes(ids, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.3),
    notes(wcuts, instrument: snip, gain: 0.5),
    notes(grows, instrument: sweep, scale: "hirajoshi", key: 110, gain: 0.35),
    notes(picked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.55),
    notes(tumbles, instrument: tumble, scale: "chromatic", key: 600, gain: 0.3),
    notes(lands, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.5),
    texture(turning, kind: "crackle", gain: 0.5),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['next'] + L['next'] * 0.3) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "token.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
