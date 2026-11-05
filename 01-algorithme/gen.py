#!/usr/bin/env python3
"""Writes algorithme.alea: the voice, the timing of the scenes, the captions.

The script lives here, line by line. Each line is said once by the voice
engine to measure it (alea caches what it says, so the render says it
again only if the text changes); the scenes take the time their lines need:
a moment of picture alone before the voice, a breath between sentences, a
hold before the cut. The captions are typed as the words are said, so they
are long to write by hand: this writes them.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import io, os, shutil, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = "../voices/narrator.sh"
NARRATOR = (os.environ.get("NARRATOR_VOICE", "af_heart"), 0.95)       # voice, speed
MASTER = ("bm_george", 0.88)

LEAD, GAP, HOLD = 1.4, 1.0, 2.0     # seconds: picture alone, between sentences, before the cut

# (name, header, lines, extra seconds at the end); a line: (id, who, text, gap before it)
SCENES = [
    ("koan", "", [
        ("m1", "M", "A novice asked Master Foo: what is an algorithm?", 0),
        ("m2", "M", "Master Foo shuffled sixteen cards, and said: sort them.", 1.2, "Master Foo shuffled 16 cards, and said: sort them."),
    ], 1.0),
    ("recipe", "1 / 4   the recipe", [
        ("n1", "N", "An algorithm is a recipe.", 0),
        ("n2", "N", "Precise steps, followed in order, until the work is done.", 0.8),
        ("n3", "N", "A computer does not understand them. It only follows them, very fast.", 1.0),
    ], 2.5),
    ("insertion", "2 / 4   sorting by insertion", [
        ("n4", "N", "Here is one, for the cards: take the next card, and slide it left, past every bigger one.", 0),
        ("n5", "N", "Each card is compared with the ones before it. Again, and again.", 1.0),
        ("n6", "N", "Sorted. Count the comparisons.", 2.6),
    ], 0.5),
    ("merge", "3 / 4   sorting by merging", [
        ("n7", "N", "A second recipe: cut the deck in pairs, and sort each pair.", 0),
        ("n8", "N", "Then merge two sorted piles into one: only their top cards need comparing.", 1.2),
        ("n9", "N", "Fours make eights, eights make sixteen. Sorted, with fewer comparisons.", 1.2),
    ], 0.5),
    ("cost", "4 / 4   the cost", [
        ("n10", "N", "With sixteen cards, the difference is small.", 0, "With 16 cards, the difference is small."),
        ("n11", "N", "With a thousand, the first recipe needs about a quarter of a million comparisons.", 1.2, "With 1 000, the first recipe needs about 250 000 comparisons."),
        ("n12", "N", "The second, fewer than ten thousand.", 0.8, "The second, fewer than 10 000."),
        ("n13", "N", "An algorithm is a way. Some ways are shorter.", 1.6),
    ], 0.5),
    ("end", "", [
        ("m3", "M", "Then Master Foo shuffled a thousand cards.", 0, "Then Master Foo shuffled 1 000 cards."),
        ("m4", "M", "And the novice was enlightened.", 1.4),
    ], 2.0),
]
TRANSITIONS = ["wipe(0.8, angle: 0, softness: 0.12)", "morph(0.8, amount: 0.15)", "wipe(0.7, angle: 90, softness: 0.1)",
               "morph(0.8, amount: 0.15)", "wipe(0.8, angle: 180, softness: 0.12)", "morph(1.2, amount: 0.2)"]


def measure(text, who):
    voice, speed = NARRATOR if who == "N" else MASTER
    engine = os.path.join(HERE, ENGINE)
    env = dict(os.environ, ALEA_LANG="en", ALEA_VOICE=voice, ALEA_SPEED=str(speed))
    wav = subprocess.run([engine], input=text.encode(), capture_output=True, env=env, check=True).stdout
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


def caption(vid, text, nxt, even=False):
    """The text typed as it is said: each word's letters appear while it is spoken;
    typed evenly when the shown text is not the spoken one (numbers in digits)."""
    words = text.split()
    typed = f"clamp((T - {vid}.start) / ({vid}.duration * 0.92), 0, 1) * {len(text)}" if even else " + ".join(f"clamp((T - {vid}.words[{k}]) / ({vid}.ends[{k}] - {vid}.words[{k}]), 0, 1) * {len(w) + (k < len(words) - 1)}"
                       for k, w in enumerate(words))
    parts, off = [], 0
    for r, ln in enumerate(wrap(text)):
        parts.append(f'text("{ln}", x: 0.06, y: {-0.060 + 0.052 * r:.3f}, size: 0.042, font: "mono", align: "left") '
                     f"* (x < 0.06 + clamp(({typed}) - {off}, 0, {len(ln)}) * adv)")
        off += len(ln) + 1
    body = parts[0] if len(parts) == 1 else "merge(" + ", ".join(parts) + ")"
    until = f"min({vid}.end + 1.5, {nxt}.start)" if nxt else f"{vid}.end + 2.5"
    return f"  let c_{vid} = {body} * (T >= {vid}.start) * (T < {until})"


def main():
    # measure, and lay the scenes out
    dur, at, starts, lengths = {}, {}, [], []
    clock = 0.0
    for name, _, lines, extra in SCENES:
        starts.append(clock)
        tt = clock + LEAD
        for k, line in enumerate(lines):
            vid, who, text, gap = line[:4]
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

    order = [l[0] for s in SCENES for l in s[2]]
    who = {l[0]: l[1] for s in SCENES for l in s[2]}
    text = {l[0]: l[2] for s in SCENES for l in s[2]}
    gaps = {l[0]: l[3] for s in SCENES for l in s[2]}
    shown = {l[0]: (l[4] if len(l) > 4 else l[2]) for s in SCENES for l in s[2]}

    out = []
    w = out.append
    w("""// Algorithme — Thus Spoke Master Foo, 01: what is an algorithm? A novice
// asks; Master Foo hands him sixteen cards. An algorithm is a recipe: steps,
// in order, until the work is done. Two recipes sort the same cards: by
// insertion (each card slides left past the bigger ones) and by merging
// (pairs, then fours, eights, the whole deck); a counter adds up their
// comparisons, and for a thousand cards the difference is a large square
// against a small one. Every edition draws its own deck, so the cards, the
// counts and the music change: each card sounds its value, the comparisons
// tick down the cards they pass, and the merges sweep up in scales.
// Written by gen.py (the script and the timing); the scenes are in scenes/.
""")
    for f in ["koan", "recipe", "insertion", "merge", "cost"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Algorithme {")
    w(f"  let total = {total}")
    w("  let T = t * total")
    w(f'  let ENGINE = "{ENGINE}"')
    w("")
    w("  // ── the deck: sixteen cards, a value each, shuffled by the edition ──")
    w("  let N = 16")
    w("  let u = [~between(0, 1) for k in range(N)]")
    w("  let h = [(sum([u[j] < u[k] for j in range(N)]) + 1) / N for k in range(N)]")
    w("")
    w("  // ── the voices: the master, and the one who explains ──")
    prev = None
    for vid in order:
        voice, speed = NARRATOR if who[vid] == "N" else MASTER
        first = prev is None or [s for s in SCENES if vid in [l[0] for l in s[2]]][0][2][0][0] == vid
        when = f"{at[vid]:.2f}" if first else f"{prev}.end + {gaps[vid] or GAP}"
        w(f'  let {vid} = say("{text[vid]}", at: {when}, engine: ENGINE, voice: "{voice}", speed: {speed}, gain: 2.3)')
        prev = vid
    w("")
    w("  // ── the moments the pictures and the sounds follow ──")
    w("  // insertion: card k is taken from \"take\" until the end of the second sentence")
    w("  let ins0 = n4.words[6]")
    w("  let ins1 = n5.end - 0.4")
    w("  let insmove = (ins1 - ins0) / (N - 1) * 0.75")
    w("  let insat = [ins0 + (ins1 - ins0) * (k - 1) / (N - 2) for k in range(1, N)]")
    w("  // merging: the pairs on \"sort\", the piles on \"merge\", the eights and the deck on their words")
    w("  let mat = [n7.words[9], n8.words[1], n9.words[2], n9.words[5]]")
    w("  let mmove = 0.9")
    w("")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')
    names = [s[0] for s in SCENES]
    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda acc: f"Koan(draw0: {lt('m1.words[0]', 'koan')}, draw1: {lt('m1.end', 'koan')}, word: {lt('m1.words[6]', 'koan')}, title: {lt('m2.words[0]', 'koan')}, accent: {acc})",
        "recipe": lambda acc: f"Recipe(show: [{lt('n2.words[0]', 'recipe')}, {lt('n2.words[1]', 'recipe')}, {lt('n2.words[3]', 'recipe')}, {lt('n2.words[5]', 'recipe')}], run0: {lt('n3.words[6]', 'recipe')}, run1: {lt('n3.end + 2.2', 'recipe')}, accent: {acc})",
        "insertion": lambda acc: f"Insertion(h: h, starts: [{lt('s', 'insertion')} for s in insat], move: insmove / {L['insertion']}, accent: {acc})",
        "merge": lambda acc: f"Merge(h: h, at: [{lt('s', 'merge')} for s in mat], split: {lt('n7.words[3]', 'merge')}, move: mmove / {L['merge']}, accent: {acc})",
        "cost": lambda acc: f"Cost(counts: [inscount, mcount], show16: {lt('n10.words[1]', 'cost')}, grow1: {lt('n11.words[2]', 'cost')}, grow2: {lt('n12.words[1]', 'cost')}, span: 3.5 / {L['cost']}, accent: {acc})",
        "end": lambda acc: f"Koan(draw0: {lt('m3.words[0]', 'end')}, draw1: {lt('m4.end', 'end')}, word: {lt('m3.words[2]', 'end')}, title: {lt('m4.end + 0.6', 'end')}, accent: {acc})",
    }
    w("  // the counts, for the cost scene: the same sums the scenes make")
    w("  let bigger(k) = sum([(j < k) * (h[j] > h[k]) for j in range(N)])")
    w("  let inscount = sum([bigger(k) + (bigger(k) < k) for k in range(1, N)])")
    w("  let inb(j, B, b) = (floor(j / B) == b)")
    w("  let top(B, b) = maximum([h[j] * inb(j, B, b) for j in range(N)])")
    w("  let mcost(Lv) = sum([2 ^ Lv - sum([inb(j, 2 ^ Lv, b) * (h[j] > min(top(2 ^ (Lv - 1), 2 * b), top(2 ^ (Lv - 1), 2 * b + 1))) for j in range(N)]) for b in range(N / 2 ^ Lv)])")
    w("  let mcount = sum([mcost(Lv) for Lv in range(1, 5)])")
    w("  let reel = timeline([")
    for k, sc in enumerate(names):
        piece = args[sc]
        w(f"      scene(ink({piece(0)}, {piece(1)}), {L[sc]}),  {TRANSITIONS[k]},")
    w("  ], loop: 1)")
    w("")
    w("  // ── over it: the series, the step, the captions (the master's in vermilion) ──")
    w("  let adv = 0.021722")
    heads = []
    for k, (name, header, _, _) in enumerate(SCENES):
        if header:
            heads.append(f'text("{header}", x: 0.06, y: -0.15, size: 0.03, font: "mono", align: "left") * (reel.index > {k} - 0.5) * (reel.index < {k} + 0.5)')
    w("  let header = merge(" + ", ".join(heads) + ") * 0.7")
    w('  let series = text("thus spoke master foo  ·  01", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
    for k, vid in enumerate(order):
        nxt = order[k + 1] if k + 1 < len(order) else None
        w(caption(vid, shown[vid], nxt, shown[vid] != text[vid]))
    w("  let said = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "N") + ")")
    w("  let spoken = merge(" + ", ".join(f"c_{v}" for v in order if who[v] == "M") + ")")
    w("  let dark = paint(merge(header, series, said), palette: [\"#000000\", \"#1a1712\"], range: [0, 1], alpha: merge(header, series, said))")
    w("  let red  = paint(spoken, palette: [\"#000000\", \"#b8361f\"], range: [0, 1], alpha: spoken)")
    w("  let look = film(vignette(overlay(reel, dark, red), amount: 0.06), amount: 0.035)")
    w("")
    w("""  // ── the sound ──
  // a card is a plucked string as high as its value; a comparison a knock of
  // wood at the pitch of the card passed; the merges ring like a kalimba
  let pitch(v) = 0.97 - v * 0.9
  let brush = synth { bandpass(noise(), cutoff: 1400, resonance: 0.3) * adsr(attack: 0.12, decay: 0.3, sustain: 0.3, release: 0.5) * note.velocity }
  let pad = synth {
    let env = adsr(attack: 3, decay: 1, sustain: 0.9, release: 4)
    lowpass(saw(note.freq) + saw(note.freq * 1.003) + sine(note.freq * 0.5), cutoff: 260 + 300 * note.level, resonance: 0.2) * env
  }
  // the temple bell, when the master speaks
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m3.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  // the recipe: a knock for every line the cursor reads
  pattern written = repeat 4 event(t: [n2.words[0], n2.words[1], n2.words[3], n2.words[5]][i] / total, x: 0.4, y: 0.6 - 0.08 * i, intensity: 0.6)""")
    # the cursor steps, as in the scene
    w(f"  let rs0 = n3.words[6]")
    w(f"  let rs1 = n3.end + 2.2")
    w(f"  pattern reads = repeat 63 event(t: (rs0 + (rs1 - rs0) * (i / 63) ^ 0.55) / total, x: 0.3 + 0.4 * (i % 2), y: [0.7, 0.6, 0.5, 0.4][[0, 1, 2, 1, 3, 0, 1, 3, 0, 1, 2, 1, 2, 1, 3, 0, 1, 2, 1, 3, 0, 1, 3, 0, 1, 2, 1, 2, 1, 2, 1, 3, 0, 1, 2, 1, 3, 0, 1, 3, 0, 1, 2, 1, 2, 1, 3, 0, 1, 2, 1, 3, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 3][i]], intensity: 0.45)")
    w("""  // insertion: the card taken, then a knock for each card it passes
  let posI(q, k) = (q < k) * sum([(j < k) * (h[j] < h[q]) for j in range(N)]) + (q >= k) * q
  let comps = [bigger(k) + (bigger(k) < k) for k in range(1, N)]
  pattern taken = repeat 15 event(t: insat[i] / total, x: 0.2 + 0.6 * (i + 1) / N, y: pitch(h[i + 1]), size: 0.04, intensity: 0.85)
  pattern passed = repeat 225 event(t: (insat[floor(i / 15)] + insmove * ((i % 15) + 1) / (comps[floor(i / 15)] + 1)) / total,
                                    x: 0.2 + 0.6 * (floor(i / 15) - (i % 15)) / N,
                                    y: pitch(sum([(q <= floor(i / 15)) * (posI(q, floor(i / 15) + 1) == floor(i / 15) - (i % 15)) * h[q] for q in range(N)])),
                                    intensity: ((i % 15) < comps[floor(i / 15)]) * 0.5)
  // merging: each level, every card rings as it lands, left to right: the
  // runs climb, and the last level is one scale
  let posM(q, Lv) = floor(q / 2 ^ Lv) * 2 ^ Lv + sum([(floor(j / 2 ^ Lv) == floor(q / 2 ^ Lv)) * (h[j] < h[q]) for j in range(N)])
  pattern landed = repeat 64 event(t: (mat[floor(i / 16)] + 0.25 + 0.05 * posM(i % 16, floor(i / 16) + 1)) / total,
                                   x: 0.15 + 0.7 * posM(i % 16, floor(i / 16) + 1) / N, y: pitch(h[i % 16]), size: 0.03, intensity: 0.5 + 0.2 * (floor(i / 16) == 3))
  // the cost: the big square fills with a rain of ticks, the small one with a few
  pattern rainA = repeat 120 event(t: (n11.words[2] + 3.5 * i / 120) / total, x: ~between(0.1, 0.6), y: ~between(0.3, 0.7), intensity: ~between(0.2, 0.5))
  pattern rainB = repeat 6 event(t: (n12.words[1] + 1.05 * i / 6) / total, x: ~between(0.7, 0.9), y: ~between(0.3, 0.7), intensity: 0.5)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.35 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.5),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(written, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.35),
    notes(reads, instrument: "wood", scale: "hirajoshi", key: 440, gain: 0.25),
    notes(taken, instrument: "pluck", scale: "hirajoshi", key: 196, gain: 0.55),
    notes(passed, instrument: "wood", scale: "hirajoshi", key: 196, gain: 0.3),
    notes(landed, instrument: "kalimba", scale: "hirajoshi", key: 196, gain: 0.45),
    notes(rainA, instrument: "tick", gain: 0.25),
    notes(rainB, instrument: "kalimba", scale: "hirajoshi", key: 784, gain: 0.3),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['insertion'] + L['insertion'] * 0.62) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "algorithme.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
