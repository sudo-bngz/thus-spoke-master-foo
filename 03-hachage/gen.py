#!/usr/bin/env python3
"""Writes hachage.alea: the voices, the timing, the captions, and the
fingerprints: real SHA-256 digests of the texts shown, so anyone can check
them (`printf 'thus spoke master foo' | sha256sum`). The edition chooses
which letter of the sentence is changed for the avalanche, among a few.

    ALEA_HOME=/path/to/alea python3 gen.py
"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from episode import GAP, caption, layout, measure

SEED = "0xa162"
EN_ENGINE = "../voices/kokoro.py"
JA_ENGINE = "../voices/kokoro-ja.py"
NARRATOR = ("af_heart", 0.95)
MASTER = ("jm_kumo", 0.82)

SENTENCE = "thus spoke master foo"
# the letter changed, for the edition to choose from: (index, new sentence)
VARIANTS = [(20, "thus spoke master fou"), (19, "thus spoke master fao"), (2, "this spoke master foo"),
            (11, "thus spoke faster foo"), (5, "thus spike master foo"), (14, "thus spoke mister foo")]
BOOK = ("Thus spoke Master Foo. A novice asks; the master answers with something to do; "
        "a voice explains, step by step, with diagrams that move and sound; and the koan closes it. "
        "Every episode is a work written in alea, the language whose output is an artwork rather than a program. "
        "Nothing is drawn by hand: the diagrams, the music and the timing are code, and each edition draws its own variations.")
PASSWORD = "correct horse battery"

SCENES = [
    ("koan", "", [
        ("m1", "M", "ある弟子が、フー師に手紙を託した。", 0, "A novice entrusted Master Foo with a letter."),
        ("m2", "M", "途中で誰かが書き換えたら、どう分かりますか。", 1.0, "If someone changes it on the way, how will I know?"),
        ("m3", "M", "師は手紙を読み、封筒にひとつの言葉を書いた。", 1.4, "Master Foo read the letter, and wrote one word on the envelope."),
    ], 1.5),
    ("fingerprint", "1 / 4   the fingerprint", [
        ("n1", "N", "A hash is a fingerprint for data.", 0, ""),
        ("n2", "N", "Any text goes in: a word, a sentence, a whole book.", 1.0, ""),
        ("n3", "N", "Out comes a code, always the same size: two hundred and fifty-six bits.", 1.0, ""),
        ("n4", "N", "The same text always gives the same fingerprint.", 1.6, ""),
    ], 0.5),
    ("avalanche", "2 / 4   the avalanche", [
        ("n5", "N", "Change a single letter, and the fingerprint changes completely.", 0, ""),
        ("n6", "N", "About half of the bits flip, as if by chance. This is called the avalanche.", 1.2, ""),
    ], 1.0),
    ("oneway", "3 / 4   no way back", [
        ("n7", "N", "And there is no way back: from the fingerprint, you cannot find the text.", 0, ""),
        ("n8", "N", "Only by trying every text there is, which would take longer than the universe has existed.", 1.2, ""),
    ], 1.0),
    ("uses", "4 / 4   the seal", [
        ("n9", "N", "That is why a website keeps only the hash of your password, never the password.", 0, ""),
        ("n10", "N", "Why every commit in git is named by its hash.", 1.0, ""),
        ("n11", "N", "And why a file's fingerprint tells you it was not changed on the way.", 1.0, ""),
        ("n12", "N", "A hash is a seal. Change one letter, and the seal breaks.", 1.6, ""),
    ], 0.5),
    ("end", "", [
        ("m4", "M", "手紙は戻ってきた。一文字だけ、変わっていた。", 0, "The letter came back. One letter had changed."),
        ("m5", "M", "封筒の言葉は、もう合わなかった。", 1.2, "The word on the envelope no longer matched."),
        ("m6", "M", "その時、弟子は悟った。", 1.4, "And the novice was enlightened."),
    ], 2.5),
]
TRANSITIONS = ["wipe(0.8, angle: 0, softness: 0.12)", "pixels(0.6, size: 0.05)", "wipe(0.7, angle: 90, softness: 0.1)",
               "morph(0.8, amount: 0.15)", "wipe(0.8, angle: 180, softness: 0.12)", "morph(1.2, amount: 0.2)"]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def bits(hexa):
    return [int(c) for c in bin(int(hexa, 16))[2:].zfill(256)]


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

    h1, hb = sha(SENTENCE), sha(BOOK)
    b1 = bits(h1)
    variants = [(pos, s2, bits(sha(s2))) for pos, s2 in VARIANTS]
    changed = [sum(x != y for x, y in zip(b1, vb)) for _, _, vb in variants]
    print(f"sha256({SENTENCE!r}) = {h1}", file=sys.stderr)
    for (pos, s2, _), c in zip(variants, changed):
        print(f"  {s2!r}: {c} bits changed", file=sys.stderr)

    out = []
    w = out.append
    w("""// Hachage — Thus Spoke Master Foo, 03: what is a hash? A novice entrusts
// Master Foo with a letter: how will he know if someone changes it on the
// way? The master writes one word on the envelope. A hash is a fingerprint
// for data: any text in, 256 bits out, always the same for the same text;
// change one letter and about half the bits flip (the avalanche); and there
// is no way back. So a website keeps only the hash of a password, git names
// every commit by its hash, a download is checked by its fingerprint. The
// fingerprints are real SHA-256 digests of the texts shown (gen.py), to be
// checked with sha256sum; the edition chooses which letter is changed.
// Master Foo speaks Japanese, translated in the captions.
""")
    for f in ["koan", "fingerprint", "avalanche", "oneway", "uses"]:
        w(f'use "scenes/{f}.alea"')
    w("")
    w("work Hachage {")
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
    w("  // ── the fingerprints: SHA-256, computed by gen.py, as bits ──")
    w(f'  let SENTENCE = "{SENTENCE}"')
    w(f'  let HEX1 = "{h1}"')
    w(f'  let HEXB = "{hb}"')
    w(f"  let bits1 = {alist(b1)}")
    w(f"  let bitsb = {alist(bits(hb))}")
    w("  // the letter the edition changes, and the fingerprint that follows")
    w("  let v = choose { " + " | ".join(str(k) for k in range(len(variants))) + " }")
    w(f"  let positions = {alist(p for p, _, _ in variants)}")
    w("  let sentences = [" + ", ".join(f'"{s2}"' for _, s2, _ in variants) + "]")
    w("  let bitsv = [" + ", ".join(alist(vb) for _, _, vb in variants) + "]")
    w(f"  let changed = {alist(changed)}")
    w("  let hexv = [" + ", ".join(f'"{sha(s2)[:4]}"' for _, s2, _ in variants) + "]")
    w(f'  let PWHEX = "{sha(PASSWORD)[:12]}"')
    w(f'  let GITHEX = "{sha("feat(exhibition): hachage")[:12]}"')
    w(f'  let FILEHEX = "{hb[:16]}"')
    w("")
    w("  // ── the scenes: ink on paper, a vermilion accent, under the captions ──")
    w('  let PAPER = ["#efe9dc", "#d3c9b4", "#3b352c", "#17140f"]')
    w('  let fit(piece) = zoom(piece, by: 0.82, x: 0.5, y: 0.66)')
    w('  let ink(piece, accent) = overlay(paint(fit(piece), palette: PAPER, range: [0, 1]), paint(fit(accent), palette: ["#000000", "#c23b22"], range: [0, 1], alpha: fit(accent)))')

    def lt(expr, sc):
        return f"(({expr}) - {S[sc]:.2f}) / {L[sc]}"
    args = {
        "koan": lambda a: f'Koan(draw0: {lt("m1.start", "koan")}, draw1: {lt("m1.end", "koan")}, word: {lt("m3.end + 0.8", "koan")}, title: {lt("m3.end + 1.0", "koan")}, '
                          f'kana: ["ハ", "ッ", "シ", "ュ"], episode: "03  ·  hash", big: "{h1[:4]}", bigsize: 0.13, bigat: [{lt("m3.start + 0.72 * m3.duration", "koan")}, {lt("m3.end + 5", "koan")}], bigoff: {lt("m3.end + 0.5", "koan")}, accent: {a})',
        "fingerprint": lambda a: f'Fingerprint(sentence: SENTENCE, hex1: HEX1, hex2: HEXB, short: bits1, long: bitsb, type0: {lt("n2.words[0]", "fingerprint")}, type1: {lt("n2.words[3]", "fingerprint")}, '
                                 f'in1: {lt("n2.words[6]", "fingerprint")}, out1: {lt("n2.words[6] + 0.6", "fingerprint")}, book: {lt("n2.words[9]", "fingerprint")}, in2: {lt("n2.end + 0.4", "fingerprint")}, out2: {lt("n3.words[1]", "fingerprint")}, '
                                 f'size: {lt("n3.words[8]", "fingerprint")}, again: {lt("n4.words[1]", "fingerprint")}, in3: {lt("n4.words[3]", "fingerprint")}, out3: {lt("n4.words[6]", "fingerprint")}, accent: {a})',
        "avalanche": lambda a: f'Avalanche(s1: SENTENCE, s2: sentences[v], pos: positions[v], a: bits1, b: bitsv[v], changed: changed[v], show1: {lt("n5.start - 0.8", "avalanche")}, show2: {lt("n5.words[3]", "avalanche")}, '
                               f'flip: {lt("n6.words[0]", "avalanche")}, tally: {lt("n6.words[8]", "avalanche")}, accent: {a})',
        "oneway": lambda a: f'Oneway(bits: bits1, back: {lt("n7.words[6]", "oneway")}, strike: {lt("n7.words[11]", "oneway")}, trying: {lt("n8.words[2]", "oneway")}, accent: {a})',
        "uses": lambda a: f'Uses(when: [{lt("n9.words[4]", "uses")}, {lt("n10.words[1]", "uses")}, {lt("n11.words[2]", "uses")}], pwhex: PWHEX, githex: GITHEX, filehex: FILEHEX, accent: {a})',
        "end": lambda a: f'Koan(draw0: {lt("m4.start", "end")}, draw1: {lt("m6.end", "end")}, word: {lt("m6.start + 0.5", "end")}, title: {lt("m6.end + 0.6", "end")}, '
                         f'kana: ["ハ", "ッ", "シ", "ュ"], episode: "03  ·  hash", big: "{h1[:4]}", big2: hexv[v], swap: 1, bigsize: 0.13, bigat: [{lt("m4.start + 0.3", "end")}, {lt("m5.start + 0.5", "end")}], bigoff: {lt("m5.end + 0.3", "end")}, accent: {a})',
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
    w('  let series = text("thus spoke master foo  ·  03", x: 0.94, y: -0.3, size: 0.024, font: "mono", align: "right") * 0.45')
    for k, vid in enumerate(order):
        nxt = order[k + 1] if k + 1 < len(order) else None
        w(caption(vid, english[vid], nxt, who[vid] == "M"))
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
  let stamp = synth {{ lowpass(noise(), cutoff: 600, resonance: 0.4) * perc(attack: 0.002, release: 0.25) * note.velocity + sine(70) * perc(release: 0.15) * 0.8 }}
  let grind = synth {{ bandpass(noise(), cutoff: 900 + 1400 * note.time, resonance: 0.5) * adsr(attack: 0.05, decay: 0.3, sustain: 0.6, release: 0.3) * 0.7 }}
  let click = synth {{ highpass(noise(), cutoff: 4000, resonance: 0.2) * perc(release: 0.012) * note.velocity }}
  // the temple bell when the master speaks; the seal stamped on the envelope, twice
  pattern bells = repeat 2 event(t: [m1.start - 1.0, m4.start - 1.0][i] / total, x: 0.5, y: 0.95, size: 0.12, intensity: 0.9)
  pattern seals = repeat 2 event(t: [m3.start + 0.72 * m3.duration, m4.start + 0.3][i] / total, x: 0.5, y: 0.5, size: 0.06, intensity: 0.9)
  pattern broken = repeat 1 event(t: (m5.start + 0.5) / total, x: 0.5, y: 0.2, size: 0.08, intensity: 1)
  // the box working, twice; a cell of the fingerprint drawn, one by one
  pattern works = repeat 3 event(t: [n2.words[6], n2.end + 0.4, n4.words[3]][i] / total, x: 0.5, y: 0.5, size: 0.04, intensity: 0.8)
  pattern cells1 = repeat 64 event(t: (n2.words[6] + 0.6 + 0.08 * {L["fingerprint"]} * i / 64) / total, x: 0.3 + 0.4 * (i % 2), y: ~between(0.3, 0.8), intensity: 0.3)
  pattern cells2 = repeat 64 event(t: (n3.words[1] + 0.08 * {L["fingerprint"]} * i / 64) / total, x: 0.3 + 0.4 * (i % 2), y: ~between(0.3, 0.8), intensity: 0.3)
  pattern cells3 = repeat 64 event(t: (n4.words[6] + 0.08 * {L["fingerprint"]} * i / 64) / total, x: 0.3 + 0.4 * (i % 2), y: ~between(0.3, 0.8), intensity: 0.3)
  // the avalanche: a cascade of clicks, as many as bits changed, and the changed letter
  pattern letter = repeat 1 event(t: n5.words[3] / total, x: 0.73, y: 0.7, size: 0.05, intensity: 0.8)
  pattern cascade = repeat 128 event(t: (n6.words[0] + 0.1 * {L["avalanche"]} * (i / 128)) / total, x: 0.6 + 0.3 * fract(i * 0.618), y: ~between(0.2, 0.9), intensity: 0.5)
  // the strike through the way back; the trying, faster and faster
  pattern strike = repeat 1 event(t: n7.words[11] / total, x: 0.6, y: 0.3, size: 0.05, intensity: 1)
  pattern tries = repeat 24 event(t: (n8.words[2] + 0.4 * {L["oneway"]} * (i / 24) ^ 0.6) / total, x: 0.5, y: 0.6 + 0.2 * (i % 2), intensity: 0.5)
  // the three uses: a lock, a commit, a match
  pattern uses = repeat 3 event(t: [n9.words[4], n10.words[1], n11.words[2]][i] / total, x: 0.3 + 0.2 * i, y: [0.6, 0.5, 0.4][i], size: 0.05, intensity: 0.7)
  pattern match = repeat 1 event(t: (n11.words[2] + 0.14 * {L["uses"]}) / total, x: 0.8, y: 0.3, size: 0.08, intensity: 0.8)
""")
    w("  let music = [")
    w("    " + ", ".join(order) + ",")
    w("""    drone(0.45 + 0.15 * lfo(3) + x * 0, voices: 2, instrument: pad, scale: "hirajoshi", key: 55, gain: 0.9),
    notes(bells, instrument: "bell", scale: "hirajoshi", key: 110, gain: 0.7),
    notes(seals, instrument: stamp, gain: 0.7),
    notes(broken, instrument: brush, scale: "chromatic", key: 100, gain: 0.7),
    notes(works, instrument: grind, scale: "chromatic", key: 200, gain: 0.4),
    notes(cells1, instrument: click, gain: 0.3),
    notes(cells2, instrument: click, gain: 0.3),
    notes(cells3, instrument: click, gain: 0.3),
    notes(letter, instrument: "kalimba", scale: "hirajoshi", key: 392, gain: 0.5),
    notes(cascade, instrument: "wood", scale: "hirajoshi", key: 330, gain: 0.3),
    notes(strike, instrument: brush, scale: "chromatic", key: 100, gain: 0.6),
    notes(tries, instrument: "wood", scale: "hirajoshi", key: 440, gain: 0.3),
    notes(uses, instrument: "glass", scale: "hirajoshi", key: 392, gain: 0.45),
    notes(match, instrument: "kalimba", scale: "hirajoshi", key: 784, gain: 0.5),
    notes(reel.cues, instrument: brush, scale: "chromatic", key: 100, gain: 0.3),
  ]
""")
    w(f"  render image(look, width: 1080, height: 1920, at: {(S['avalanche'] + L['avalanche'] * 0.85) / total:.4f})")
    w("  render video(look, fps: 30, width: 1080, height: 1920, sound: music, room: 0.12, echo: 0)")
    w("}")
    with open(os.path.join(HERE, "hachage.alea"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
