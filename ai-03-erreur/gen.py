#!/usr/bin/env python3
"""Writes erreur.alea: the voices, the timing, the captions. The error
landscape is drawn by the edition (a bowl with hills), and the walk down
it is grown step by step by the slope itself (gradient descent in alea's
`grow`): three walkers, with small, right and too-big steps. Needs alea
with PR #39 (a grown field held at a moment).

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import episode
from episode import GAP, caption, layout, measure
episode.LEAD, episode.HOLD = 1.5, 1.8     # a lesson: more picture alone before the voice, a longer hold

SEED = "0xa1a3"
EN_ENGINE = "../voices/narrator.sh"
JA_ENGINE = "../voices/master.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 1.0)
MASTER = (os.environ.get("MASTER_VOICE", "jm_kumo"), 0.82)   # an ElevenLabs voice id, with ELEVENLABS_API_KEY

SCENES = [
    ("koan", "", [
        ("m1", "M", "弟子は尋ねた。三つの秤は、どうやって一緒に学ぶのですか。", 0, "The novice asked: how do 3 scales learn together?"),
        ("m2", "M", "師は言った。終わりの皿を見よ。どれだけ傾いたか。それが、間違いだ。", 1.4, "Master Foo said: look at the last pan. How far it tipped: that is the mistake."),
        ("m3", "M", "その間違いを、来た道を逆に、秤から秤へ戻せ。", 1.4, "Send that mistake back the way it came, scale to scale."),
    ], 0.6),
    ("error", "1 / 4   the error", [
        ("n1", "N", "Last time, three scales drew a bent line. But their weights were set by hand. Now they must find the weights themselves.", 0, "Last time, 3 scales drew a bent line. But their weights were set by hand. Now they must find the weights themselves."),
        ("n2", "N", "For that, the network first needs a way to know how wrong it is. One number.", 1.4, "For that, the network first needs a way to know how wrong it is. 1 number."),
        ("n3", "N", "Show it an example. It answers with a number between zero and one. Compare with the right answer: the gap is its mistake.", 1.4, "Show it an example. It answers with a number between 0 and 1. Compare with the right answer: the gap is its mistake."),
        ("n4", "N", "Do this for every example, and add the gaps up. That total is the error. Zero would be perfect.", 1.4, "Do this for every example, and add the gaps up. That total is the error. 0 would be perfect."),
    ], 1.0),
    ("landscape", "2 / 4   the landscape", [
        ("n5", "N", "Now imagine turning one weight slowly, from low to high, and writing down the error each time. You get a curve: high here, low there.", 0, "Now imagine turning 1 weight slowly, from low to high, and writing down the error each time. You get a curve: high here, low there."),
        ("n6", "N", "With two weights, you get a landscape: hills where the error is high, valleys where it is low.", 1.4, "With 2 weights, you get a landscape: hills where the error is high, valleys where it is low."),
        ("n7", "N", "Learning is nothing more than this: finding the bottom of a valley.", 1.4, ""),
        ("n8", "N", "But the network cannot see the landscape. It only knows where it stands.", 1.4, ""),
    ], 1.0),
    ("descent", "3 / 4   the slope", [
        ("n9", "N", "What it can feel is the slope under its feet: which way is down, and how steep. That is called the gradient.", 0, ""),
        ("n10", "N", "So it takes one small step downhill. Then feels the slope again. Then steps again.", 1.4, "So it takes 1 small step downhill. Then feels the slope again. Then steps again."),
        ("n11", "N", "Step by step, it walks down into the valley. This is gradient descent.", 1.4, ""),
        ("n12", "N", "The size of the step matters. Too small, and it takes forever. Too big, and it jumps over the valley, and bounces.", 1.4, ""),
    ], 1.0),
    ("backward", "4 / 4   backward", [
        ("n13", "N", "One thing left. With many weights, in many layers, which weights are to blame for the error?", 0, "1 thing left. With many weights, in many layers, which weights are to blame for the error?"),
        ("n14", "N", "The error is measured at the end. So it is sent backward, layer by layer, along the same wires the answer came through.", 1.4, ""),
        ("n15", "N", "Each wire receives its share of the blame, and moves its weight by that much.", 1.4, ""),
        ("n16", "N", "Forward to answer. Backward to blame. This is backpropagation, and every network learns this way.", 1.4, ""),
    ], 1.0),
    ("end", "", [
        ("m4", "M", "弟子は、谷を下る水のように、重りを動かした。", 0, "The novice moved the weights like water going down a valley."),
        ("m5", "M", "師は言った。一歩ずつ。急げば、谷を跳び越える。", 1.4, "Master Foo said: 1 step at a time. Hurry, and you jump over the valley."),
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
    w("""// Erreur — Thus Spoke Master Foo, AI 03: how the scales learn. Look at
// the last pan: how far it tipped is the mistake; send it back the way it
// came. The error as one number (the gaps between answers and right
// answers, added up); the error as a landscape over the weights, hills and
// valleys; the slope under one's feet, and the walk down, step by step
// (gradient descent, grown here by the slope itself, with steps too small
// and too big beside it); the blame sent backward along the wires
// (backpropagation). The landscape is the edition's. Master Foo speaks
// Japanese, translated in the captions.
""")
    for f in ["koan", "error", "landscape", "descent", "backward"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Erreur {")
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
    w("""  // ── the landscape: the error over the two weights (u, v in 0..1), a bowl with hills, the edition's ──
  let cu = ~between(0.5, 0.75)
  let cv = ~between(0.3, 0.6)
  let bump = ~between(3, 9)
  let E = 2.2 * ((x - cu) ^ 2 + (y - cv) ^ 2) + 0.28 * noise(x * 3.5, y * 3.5, bump) + 0.3
  // ── the walk down, grown: at each step, the slope under the ball, and a step against it;
  // three walkers from the same start: the right step, one too small, one too big ──
  let S = 120
  let h = 0.01
  let x0 = 0.12 + ~between(0, 0.08)
  let y0 = 0.82 + ~between(0, 0.08)
  let slopex(px, py) = (move(E, x: x - px - h, y: y - py) - move(E, x: x - px + h, y: y - py)) / (2 * h)
  let slopey(px, py) = (move(E, x: x - px, y: y - py - h) - move(E, x: x - px, y: y - py + h)) / (2 * h)
  grow over 64 for 120 {
    bx = x0
      then bx + x * 0 - 0.03 * slopex(bx, by)
    by = y0
      then by + x * 0 - 0.03 * slopey(bx, by)
    sx = x0
      then sx + x * 0 - 0.004 * slopex(sx, sy)
    sy = y0
      then sy + x * 0 - 0.004 * slopey(sx, sy)
    gx = x0
      then clamp(gx + x * 0 - 0.2 * slopex(gx, gy), 0.03, 0.97)
    gy = y0
      then clamp(gy + x * 0 - 0.2 * slopey(gx, gy), 0.03, 0.97)
    // the trails: a dot stamped where each walker stands, kept
    tb = 0
      then max(tb, exp(-((x - bx) ^ 2 + (y - by) ^ 2) / 0.00005))
    ts = 0
      then max(ts, exp(-((x - sx) ^ 2 + (y - sy) ^ 2) / 0.00003))
    tg = 0
      then max(tg, exp(-((x - gx) ^ 2 + (y - gy) ^ 2) / 0.00005))
  }
""")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["エ", "ラ", "ー"], episode: "AI 03  ·  error", accent: {a})',
        "error": lambda a: f'Error(first0: {lt("n3.words[0]", "error")}, gap0: {lt("n3.words[17]", "error")}, rest0: {lt("n4.words[0]", "error")}, total0: {lt("n4.words[12]", "error")}, accent: {a})',
        "landscape": lambda a: f'Landscape(E: E, bx: x0, by: y0, cu: cu, cv: cv, curve0: {lt("n5.words[1]", "landscape")}, map0: {lt("n6.words[0]", "landscape")}, valley0: {lt("n6.words[6]", "landscape")}, here0: {lt("n8.words[9]", "landscape")}, accent: {a})',
        "descent": lambda a: f'Descent(E: E, bx: bx, by: by, sx: sx, sy: sy, gx: gx, gy: gy, tb: tb, ts: ts, tg: tg, S: S, arrow0: {lt("n9.words[5]", "descent")}, l0: {lt("n10.words[3]", "descent")}, l1: {lt("n11.end + 0.8", "descent")}, size0: {lt("n12.words[6]", "descent")}, accent: {a})',
        "backward": lambda a: f'Backward(fwd0: {lt("n13.start - 0.9", "backward")}, gap0: {lt("n14.words[4]", "backward")}, back0: {lt("n14.words[8]", "backward")}, move0: {lt("n15.words[8]", "backward")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["エ", "ラ", "ー"], episode: "AI 03  ·  error", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  AI 03", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
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
  // the temple bell when the master speaks; the last pan tipping
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern tipped = repeat 1 event(t: (m2.start + 0.45 * m2.duration) / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the error: the answers, the gaps, the total
  pattern answers = repeat 4 event(t: ([n3.words[0], n4.words[0], n4.words[0] + 0.05 * {L["error"]}, n4.words[0] + 0.1 * {L["error"]}][i] + 0.06 * {L["error"]}) / total, x: 0.3 + 0.1 * i, y: 0.5, size: 0.04, intensity: 0.5)
  pattern gaps = repeat 4 event(t: ([n3.words[17], n4.words[0] + 0.14 * {L["error"]}, n4.words[0] + 0.19 * {L["error"]}, n4.words[0] + 0.24 * {L["error"]}][i]) / total, x: 0.6, y: 0.5 + 0.1 * i, intensity: 0.6)
  pattern totalled = repeat 1 event(t: n4.words[12] / total, x: 0.5, y: 0.8, size: 0.08, intensity: 0.7)
  // the landscape: the curve drawn, the map, the ball placed
  pattern curve = repeat 1 event(t: n5.words[1] / total, x: 0.5, y: 0.5, size: 0.08, intensity: 0.5)
  pattern mapped = repeat 3 event(t: (n6.words[0] + 0.3 * i) / total, x: 0.4 + 0.1 * i, y: 0.6, intensity: 0.5)
  pattern placed = repeat 1 event(t: n8.words[9] / total, x: 0.2, y: 0.3, size: 0.05, intensity: 0.7)
  // the steps: a tick at each, slowly then faster; the valley reached; the big steps bouncing
  pattern steps = repeat 120 event(t: (n10.words[3] + (n11.end + 0.8 - n10.words[3]) * ((i + 1) / 120) ^ (1 / 1.6)) / total, x: 0.3 + 0.4 * (i % 2), y: 0.7 - 0.5 * i / 120, intensity: 0.35)
  pattern bottom = repeat 3 event(t: (n11.end + 0.8) / total, x: 0.5, y: [0.5, 0.4, 0.3][i], size: 0.1, intensity: 0.7)
  pattern bounces = repeat 8 event(t: (n12.words[6] + 0.3 * i) / total, x: 0.3 + 0.4 * (i % 2), y: 0.3 + 0.4 * (i % 2), size: 0.04, intensity: 0.6)
  // forward, the gap, backward, the weights moving
  pattern forward = repeat 1 event(t: (n13.start - 0.9) / total, x: 0.2, y: 0.5, size: 0.1, intensity: 0.6)
  pattern gapend = repeat 1 event(t: n14.words[4] / total, x: 0.85, y: 0.5, size: 0.05, intensity: 0.8)
  pattern back = repeat 1 event(t: n14.words[8] / total, x: 0.8, y: 0.5, size: 0.14, intensity: 0.8)
  pattern moving = repeat 9 event(t: (n15.words[8] + 0.12 * i) / total, x: 0.2 + 0.07 * i, y: 0.6, intensity: 0.4)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(tipped, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(answers, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.4),
    notes(gaps, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.45),
    notes(totalled, instrument: chord, scale: "minor", key: 110, gain: 0.4),
    notes(curve, instrument: brush, scale: "chromatic", key: 100, gain: 0.4),
    notes(mapped, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.4),
    notes(placed, instrument: "glass", scale: "hirajoshi", key: 523, gain: 0.5),
    notes(steps, instrument: tick, scale: "hirajoshi", key: 880, gain: 0.3),
    notes(bottom, instrument: chord, scale: "major", key: 110, gain: 0.4),
    notes(bounces, instrument: knock, scale: "hirajoshi", key: 220, gain: 0.4),
    notes(forward, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(gapend, instrument: knock, scale: "hirajoshi", key: 165, gain: 0.5),
    notes(back, instrument: brush, scale: "chromatic", key: 100, gain: 0.5),
    notes(moving, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['descent'] + L['descent'] * 0.5) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "erreur.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
