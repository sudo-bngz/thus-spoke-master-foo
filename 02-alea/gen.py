#!/usr/bin/env python3
"""Writes alea.alea: the voices, the timing of the scenes, the captions.

Master Foo speaks Japanese (voices/kokoro-ja.py, jm_kumo); the captions
give his words in English, in vermilion, as he says them. The explanation
is in English (alea's Kokoro engine, af_heart), typed as it is said. Each
line is said once to measure it; the scenes take the time their lines need.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import io, os, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = "0xa161"                     # the edition published; shown in the film
EN_ENGINE = "../voices/kokoro.py"
JA_ENGINE = "../voices/kokoro-ja.py"
NARRATOR = ("af_heart", 0.95)
MASTER = ("jm_kumo", 0.85)

LEAD, GAP, HOLD = 1.4, 1.0, 2.0

# (name, header, lines, extra seconds); a line: (id, who, text, gap before it, English for the master)
SCENES = [
    ("koan", "", [
        ("m1", "M", "ある弟子が、フー師に乱数をひとつ求めた。", 0, "A novice asked Master Foo for a random number."),
        ("m2", "M", "師は答えた。七。", 1.0, "Master Foo answered: seven."),
        ("m3", "M", "弟子はもう一度たずねた。師は答えた。七。", 1.4, "The novice asked again. Master Foo answered: seven."),
    ], 1.5),
    ("machine", "1 / 4   a machine can't guess", [
        ("n1", "N", "A computer cannot roll a die.", 0, ""),
        ("n2", "N", "It only follows recipes, and the same recipe always gives the same answer.", 1.0, ""),
    ], 1.0),
    ("lfsr", "2 / 4   a fake die", [
        ("n3", "N", "So it fakes chance, with a recipe that scrambles bits.", 0, ""),
        ("n4", "N", "Fifteen bits slide to the right. The last two are mixed, and the result comes back at the start.", 1.0, ""),
        ("n5", "N", "Step after step, the bits that fall out look like chance.", 1.4, ""),
        ("n6", "N", "Played fast, they are noise: the very noise of an old game console.", 1.6, ""),
        ("n7", "N", "But after thirty-two thousand, seven hundred and sixty-seven steps, it all starts again.", 1.4, ""),
    ], 0.5),
    ("seed", "3 / 4   the seed", [
        ("n8", "N", "The bits it starts from are its seed.", 0, ""),
        ("n9", "N", "Same seed, same numbers. Every time.", 1.2, ""),
        ("n10", "N", "Change a single bit, and everything changes.", 1.2, ""),
        ("n11", "N", "This film, too, was drawn from a seed. Another seed, another film.", 1.6, ""),
    ], 1.0),
    ("entropy", "4 / 4   real chance", [
        ("n12", "N", "When chance must be real, for a password or a key, the machine listens to the world:", 0, ""),
        ("n13", "N", "the timing of your keys, the moves of your mouse, the noise in its own circuits.", 0.8, ""),
        ("n14", "N", "It stirs them into a seed that no one can guess.", 1.2, ""),
    ], 0.5),
    ("end", "", [
        ("m4", "M", "そして師は、弟子にたねを渡した。", 0, "Then Master Foo gave the novice the seed."),
        ("m5", "M", "その時、弟子は悟った。", 1.4, "And the novice was enlightened."),
    ], 2.5),
]
TRANSITIONS = ["wipe(0.8, angle: 0, softness: 0.12)", "glitch(0.6, amount: 0.5)", "wipe(0.7, angle: 90, softness: 0.1)",
               "morph(0.8, amount: 0.15)", "wipe(0.8, angle: 180, softness: 0.12)", "morph(1.2, amount: 0.2)"]


def measure(text, who):
    voice, speed = NARRATOR if who == "N" else MASTER
    engine = os.path.join(HERE, EN_ENGINE if who == "N" else JA_ENGINE)
    env = dict(os.environ, ALEA_LANG="en", ALEA_VOICE=voice, ALEA_SPEED=str(speed))
    wav = subprocess.run([sys.executable, engine], input=text.encode(), capture_output=True, env=env, check=True).stdout
    with wave.open(io.BytesIO(wav)) as w:
        return w.getnframes() / w.getframerate()


def wrap(text, width=33):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word) if cur else word
    lines.append(cur)
    return lines


def caption(vid, text, nxt, master):
    """The narrator's words typed as they are said; the master's English
    typed evenly while he speaks Japanese."""
    if master:
        typed = f"clamp((T - {vid}.start) / ({vid}.duration * 0.92), 0, 1) * {len(text)}"
    else:
        words = text.split()
        typed = " + ".join(f"clamp((T - {vid}.words[{k}]) / ({vid}.ends[{k}] - {vid}.words[{k}]), 0, 1) * {len(w) + (k < len(words) - 1)}"
                           for k, w in enumerate(words))
    parts, off = [], 0
    for r, ln in enumerate(wrap(text)):
        parts.append(f'text("{ln}", x: 0.06, y: {-0.060 + 0.052 * r:.3f}, size: 0.042, font: "mono", align: "left") '
                     f"* (x < 0.06 + clamp(({typed}) - {off}, 0, {len(ln)}) * adv)")
        off += len(ln) + 1
    body = parts[0] if len(parts) == 1 else "merge(" + ", ".join(parts) + ")"
    until = f"min({vid}.end + 1.5, {nxt}.start)" if nxt else f"{vid}.end + 3"
    return f"  let c_{vid} = {body} * (T >= {vid}.start) * (T < {until})"


def main():
    dur, at, starts, lengths = {}, {}, [], []
    clock = 0.0
    for name, _, lines, extra in SCENES:
        starts.append(clock)
        tt = clock + LEAD
        for k, (vid, who, text, gap, _) in enumerate(lines):
            dur[vid] = measure(text, who)
            tt += (gap or GAP) if k else 0
            at[vid] = tt
            tt += dur[vid]
            print(f"  {vid:4} {dur[vid]:5.2f} s  {text}", file=sys.stderr)
        length = round(tt + HOLD + extra - clock, 1)
        lengths.append(length)
        clock += length
    total = round(clock, 2)
    S = dict(zip([s[0] for s in SCENES], starts))
    L = dict(zip([s[0] for s in SCENES], lengths))
    print(f"total {total} s", file=sys.stderr)

    allines = [l for s in SCENES for l in s[2]]
    order = [l[0] for l in allines]
    who = {l[0]: l[1] for l in allines}
    text = {l[0]: l[2] for l in allines}
    gaps = {l[0]: l[3] for l in allines}
    english = {l[0]: (l[4] or l[2]) for l in allines}
    firsts = {s[2][0][0] for s in SCENES}

    out = []
    w = out.append
    w("""// Aléa — Thus Spoke Master Foo, 02: can a computer roll a die? A novice
// asks Master Foo for a random number; twice, the master says seven. A
// computer only follows recipes, so it fakes chance: fifteen bits slide
// along a register, the last two are mixed and come back at the start (a
// linear-feedback shift register, the noise of old game consoles), grown
// here step by step from the edition's own seed. Same seed, same numbers;
// one bit changed, another tape. Real chance comes from the world: keys,
// mouse, the noise of circuits. Master Foo speaks Japanese, translated in
// the captions. Written by gen.py; the scenes are in scenes/.
""")
    for f in ["koan", "machine", "lfsr", "seed", "entropy"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Alea {")
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
    w("""
  // ── the register: fifteen bits from the edition's seed; at each generation
  // they slide right and the last two, mixed, come back at the start. Each row
  // of the grid is a register: row 7 (y = 0.5) is the one shown; row 8 starts
  // from the same bits but one, cell 3, changed (its twin). ──
  let seedbits = ~~uniform(0, 1) < 0.5
  let first = move(seedbits, x: 0, y: y - 0.5)
  grow over 15 for 575 {
    reg = abs(first - (y > 8 / 15) * (y < 9 / 15) * (x > 3 / 15) * (x < 4 / 15))
      then (x < 1 / 15) * abs(move(reg, x: -13 / 15, y: 0) - move(reg, x: -14 / 15, y: 0)) + (x >= 1 / 15) * move(reg, x: 1 / 15, y: 0)
  }
  // the steps: slowly, then faster and faster, from "Fifteen" to the end of the noise
  let s0 = n4.words[0]
  let s1 = n6.end
  let stepat(k) = s0 + (s1 - s0) * (k / 575) ^ (1 / 3)
""")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ラ", "ン", "ダ", "ム"], episode: "02  ·  chance", big: "7", bigat: [{lt("m2.end - 0.5", "koan")}, {lt("m3.end - 0.5", "koan")}], bigoff: {lt("m3.end + 0.5", "koan")}, accent: {a})',
        "machine": lambda a: f'Machine(die: {lt("n1.words[3]", "machine")}, strike: {lt("n1.end", "machine")}, box: {lt("n2.words[3]", "machine")}, '
                             f'runs: [{lt("n2.words[7]", "machine")}, {lt("n2.words[9]", "machine")}, {lt("n2.words[12]", "machine")}], accent: {a})',
        "lfsr": lambda a: f'Lfsr(reg: reg, s0: {lt("s0", "lfsr")}, s1: {lt("s1", "lfsr")}, mix: {lt("n4.words[10]", "lfsr")}, period: {lt("n7.words[2]", "lfsr")}, accent: {a})',
        "seed": lambda a: f'Seed(r: reg, flip: 3, show: [{lt("n8.words[7]", "seed")}, {lt("n9.words[0]", "seed")}, {lt("n10.words[3]", "seed")}], fill: 1.6 / {L["seed"]}, '
                          f'cmd: "$ alea alea.alea --seed {SEED}", typed: [{lt("n11.words[8]", "seed")}, {lt("n11.end", "seed")}], accent: {a})',
        "entropy": lambda a: f'Entropy(when: [{lt("n13.words[4]", "entropy")}, {lt("n13.words[9]", "entropy")}, {lt("n13.words[15]", "entropy")}], stir: {lt("n14.words[1]", "entropy")}, seed: {lt("n14.words[5]", "entropy")}, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m5.end", "end")}, word: {lt("m4.start + 1.0", "end")}, title: {lt("m5.end + 0.6", "end")}, '
                         f'kana: ["ラ", "ン", "ダ", "ム"], episode: "02  ·  chance", accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  02", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
    for k, vid in enumerate(order):
        nxt = order[k + 1] if k + 1 < len(order) else None
        w(caption(vid, english[vid], nxt, who[vid] == "M"))
    w("  let said = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "N") + ")")
    w("  let spoken = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "M") + ")")
    w('  let dark = paint(merge(header, series, said), palette: ["#000000", "#1a1712"], range: [0, 1], alpha: merge(header, series, said))')
    w('  let red  = paint(spoken, palette: ["#000000", "#b8361f"], range: [0, 1], alpha: spoken)')
    w("  let look = film(vignette(overlay(reel, dark, red), amount: 0.06), amount: 0.035)")
    w("""
  // ── the sound ──
  let pad = synth {
    let env = adsr(attack: 3, decay: 1, sustain: 0.9, release: 4)
    lowpass(saw(note.freq) + saw(note.freq * 1.003) + sine(note.freq * 0.5), cutoff: 260 + 300 * note.level, resonance: 0.2) * env
  }
  let brush = synth { bandpass(noise(), cutoff: 1400, resonance: 0.3) * adsr(attack: 0.12, decay: 0.3, sustain: 0.3, release: 0.5) * note.velocity }
  // the register's voice: a square wave, on while the bit that falls out is 1
  let chip = synth { lowpass(square(note.freq), cutoff: 3000) * 0.5 }
  // the console's noise, two bursts, the second lower
  let console = synth { lowpass(noise(), cutoff: note.freq, resonance: 0.3) * perc(attack: 0.002, release: 0.9) * note.velocity }
  let click = synth { highpass(noise(), cutoff: 4000, resonance: 0.2) * perc(release: 0.012) * note.velocity }
  // the bit falling out of the register, step by step, as a field of t
  let gnow = floor(575 * clamp((T - s0) / (s1 - s0), 0, 1) ^ 3)
  let outbit = at(move(reg, x: x - 14.5 / 15, y: y - 0.5), time: gnow / 575) * (T > s0) * (T < s1)
  // the temple bell, when the master speaks; a chime on each seven, the same
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern sevens = repeat 2 event(t: [m2.end - 0.5, m3.end - 0.5][i] / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.8)
  // the recipe, three times, and three times the same answer
  pattern knocks = repeat 3 event(t: [n2.words[7], n2.words[9], n2.words[12]][i] / total, x: 0.3, y: 0.6, intensity: 0.6)
  pattern answers = repeat 3 event(t: ([n2.words[7], n2.words[9], n2.words[12]][i] + 0.6) / total, x: 0.7, y: 0.5, size: 0.04, intensity: 0.7)
  // a click at every step, while they can still be told apart
  pattern steps = repeat 160 event(t: stepat(i + 1) / total, x: 0.4 + 0.2 * (i % 2), y: 0.5, intensity: 0.5)
  pattern noisy = repeat 2 event(t: (n6.words[4] + 1.1 * i) / total, x: 0.35 + 0.3 * i, y: 0.3 + 0.3 * i, size: 0.05, intensity: 0.9)
  // the seeds: a chime for each tape, the same twice, a stranger one for the third
  pattern tapes = repeat 3 event(t: [n8.words[7], n9.words[0], n10.words[3]][i] / total, x: 0.2 + 0.3 * i, y: [0.5, 0.5, 0.42][i], size: 0.05, intensity: 0.7)
  // the world: taps of keys, the seed's bits coming out
  pattern taps = repeat 14 event(t: (n13.words[4] + ~between(0, 2.2)) / total, x: ~between(0.2, 0.5), y: 0.5, intensity: ~between(0.3, 0.7))
  pattern seedbits_out = repeat 15 event(t: (n14.words[5] + 0.12 * i) / total, x: 0.2 + 0.04 * i, y: 0.8 - 0.04 * i, intensity: 0.5)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    drone(outbit, voices: 1, instrument: chip, scale: "chromatic", key: 880, gain: 0.35),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(sevens, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.6),
    notes(knocks, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.4),
    notes(answers, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(steps, instrument: click, gain: 0.3),
    notes(noisy, instrument: console, scale: "chromatic", key: 2400, gain: 0.5),
    notes(tapes, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(taps, instrument: "tick", gain: 0.35),
    notes(seedbits_out, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.35),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['lfsr'] + L['lfsr'] * 0.75) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.45, echo: 0.12)")
    w("}")
    with open(os.path.join(HERE, "alea.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
