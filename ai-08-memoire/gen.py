#!/usr/bin/env python3
"""Writes memoire.alea: the voices, the timing, the captions. The
window of 12 tokens is illustrative; the counts of looks (n squared) are real.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a8"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。機械は、私のことを覚えていますか。", 0, "The novice asked: does the machine remember me?"),
        ("m2", "M", "師は言った。昨日、機械と何を話した？", 1.4, "Master Foo said: what did you say to it yesterday?"),
        ("m3", "M", "弟子は答えた。覚えていません。師は言った。機械も同じだ。", 1.4, "The novice answered: I don't remember. Master Foo said: neither does the machine."),
    ], 0.6),
    ("window", "1 / 4   the window", [
        ("n1", "N", "Last time, the weights. Once training is done, they never change. Ask the machine a question today, or next year: the same weights answer.", 0, ""),
        ("n2", "N", "So where does a conversation live? Not in the weights. In the text. Every time you send a message, the whole conversation is fed back in, from the start.", 1.4, ""),
        ("n3", "N", "That text has a limit: the window. Here, a window of twelve tokens. Real ones hold a hundred thousand, or more.", 1.4, "That text has a limit: the window. Here, a window of 12 tokens. Real ones hold 100 000, or more."),
        ("n4", "N", "Everything inside the window, the machine sees. Outside it, nothing. It has no other memory of you.", 1.4, ""),
    ], 1.0),
    ("cost", "2 / 4   the cost", [
        ("n5", "N", "Why a limit? Attention. Every token looks at every other token. Four tokens: sixteen looks.", 0, "Why a limit? Attention. Every token looks at every other token. 4 tokens: 16 looks."),
        ("n6", "N", "Twice the text, four times the looks. Eight tokens: sixty-four. Forty tokens: one thousand six hundred. A long conversation is expensive, and slow.", 1.4, "Twice the text, 4 times the looks. 8 tokens: 64. 40 tokens: 1 600. A long conversation is expensive, and slow."),
        ("n7", "N", "That is why the window is a window, and not a wall of everything you ever said.", 1.4, ""),
    ], 1.0),
    ("edge", "3 / 4   the edge", [
        ("n8", "N", "What happens at the edge? When the conversation grows past the window, the oldest tokens fall out.", 0, ""),
        ("n9", "N", "The machine answers as if they were never said. It did not forget them: it never saw them.", 1.4, ""),
        ("n10", "N", "A long chat that goes strange halfway through? Often, the beginning fell out of the window.", 1.4, ""),
    ], 1.0),
    ("two", "4 / 4   two memories", [
        ("n11", "N", "So the machine has two memories. The weights: slow, learned once, from everything ever written. And the window: fast, this conversation, gone when it closes.", 0, ""),
        ("n12", "N", "To make it remember, write it down. A note at the top of the window, put back in every time. That is all a memory feature is: text.", 1.4, ""),
        ("n13", "N", "Next time: when the machine is sure, and wrong. Hallucination.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "師は言った。機械は、目の前にあるものだけを見ている。", 0, "Master Foo said: the machine sees only what is in front of it."),
        ("m5", "M", "覚えていてほしければ、書いておけ。", 1.4, "If you want it to remember, write it down."),
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
    w("""// Mémoire — Thus Spoke Master Foo, AI 08: the window. The weights never
// change once training is done; a conversation lives in the text, fed
// back in whole at every message; the text has a limit, the window;
// why: every token looks at every other, so twice the text is 4 times
// the work; at the edge the oldest tokens fall out, never seen; and the
// machine's two memories, the weights and the window, with the trick: a
// note at the top of the window. The window of 12 is illustrative.
// Master Foo speaks Japanese, translated in the captions.
""")
    for f in ["koan", "window", "cost", "edge", "two"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Memoire {")
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
                          f'kana: ["キ", "オ", "ク"], episode: "AI 08  ·  memory", accent: {a})',
        "window": lambda a: f'Window(weights0: {lt("n1.words[2]", "window")}, text0: {lt("n2.words[9]", "window")}, frame0: {lt("n3.words[5]", "window")}, outside0: {lt("n4.words[7]", "window")}, accent: {a})',
        "cost": lambda a: f'Cost(at: [{lt("n5.words[9]", "cost")}, {lt("n6.words[6]", "cost")}, {lt("n6.words[9]", "cost")}], wall0: {lt("n7.words[9]", "cost")}, accent: {a})',
        "edge": lambda a: f'Edge(slide0: {lt("n8.words[6]", "edge")}, slide1: {lt("n9.words[0]", "edge")}, never0: {lt("n9.words[9]", "edge")}, accent: {a})',
        "two": lambda a: f'Two(weights0: {lt("n11.words[6]", "two")}, window0: {lt("n11.words[20]", "two")}, note0: {lt("n12.words[6]", "two")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["キ", "オ", "ク"], episode: "AI 08  ·  memory", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 08", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the weights; the tokens arriving; the frame; outside
  pattern weights = repeat 1 event(t: n1.words[2] / total, x: 0.5, y: 0.3, size: 0.2, intensity: 0.5)
  pattern tokens = repeat 20 event(t: (n2.words[9] + {L["window"]} * (0.07 * floor(i / 7) + 0.006 * (i % 7))) / total, x: 0.08 + 0.84 * i / 19, y: 0.72, intensity: 0.3)
  pattern frame = repeat 1 event(t: n3.words[5] / total, x: 0.7, y: 0.72, size: 0.15, intensity: 0.8)
  // the three grids
  pattern grids = repeat 3 event(t: [n5.words[9], n6.words[6], n6.words[9]][i] / total, x: 0.5, y: 0.62, size: 0.1 + 0.1 * i, intensity: 0.5 + 0.2 * i)
  pattern looks = repeat 16 event(t: (n6.words[9] + 0.05 * {L["cost"]} * (i / 16)) / total, x: 0.2 + 0.6 * i / 16, y: 0.62, intensity: 0.2)
  // the tokens falling out
  pattern falling = repeat 12 event(t: (n8.words[6] + (n9.words[0] - n8.words[6]) * ((i + 0.5) / 12)) / total, x: 0.2, y: 0.8, size: 0.05, intensity: 0.5)
  // the two memories; the note
  pattern memories = repeat 2 event(t: [n11.words[6], n11.words[20]][i] / total, x: 0.5, y: 0.36 + 0.42 * i, size: 0.3, intensity: 0.6)
  pattern note = repeat 1 event(t: (n12.words[6] + 0.03 * {L["two"]}) / total, x: 0.3, y: 0.9, size: 0.06, intensity: 0.7)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(asked, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(weights, instrument: chord, scale: "major", key: 82, gain: 0.4),
    notes(tokens, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(frame, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(grids, instrument: "kalimba", scale: "hirajoshi", key: 262, gain: 0.5),
    notes(looks, instrument: tick, scale: "hirajoshi", key: 1320, gain: 0.2),
    notes(falling, instrument: "wood", scale: "hirajoshi", key: 220, gain: 0.45),
    notes(memories, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(note, instrument: "glass", scale: "hirajoshi", key: 659, gain: 0.5),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['edge'] + L['edge'] * 0.5) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "memoire.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
