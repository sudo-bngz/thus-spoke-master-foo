# Thus Spoke Master Foo

Two minutes, one idea of computing, explained in a Reel. Each episode opens
with a koan: a novice asks, Master Foo answers with something to do; then a
voice explains, step by step, with diagrams that move and sound; and the
koan closes it.

Every episode is a work written in [alea](https://github.com/sudo-bngz/alea),
the language whose output is an artwork rather than a program. Nothing is
drawn by hand: the diagrams, the music and the timing are code, and each
edition (each seed) draws its own variations.

Ink on paper, a vermilion accent; the master's words in vermilion, the
explanation in ink. From episode 02, Master Foo speaks Japanese and the
captions translate him.

## Episodes

| # | Episode | The idea | Length |
|---|---|---|---|
| 01 | [Algorithme](01-algorithme/) | What is an algorithm? A recipe: steps, in order, until the work is done. Two recipes sort the same sixteen cards (insertion, merging); a counter adds up their comparisons, and for a thousand cards the difference is a large square against a small one. | 1 min 40 |
| 02 | [Aléa](02-alea/) | Can a computer roll a die? It fakes chance: fifteen bits slide along a register, the last two mixed and fed back (an LFSR, the noise of old game consoles), grown step by step in alea from the edition's own seed. Same seed, same numbers; one bit changed, another tape. Real chance comes from the world. Master Foo speaks Japanese. | 1 min 47 |
| 03 | [Hachage](03-hachage/) | What is a hash? A fingerprint for data: any text in, 256 bits out, always the same for the same text; change one letter and half the bits flip; no way back. A password kept as its hash, a git commit named by it, a download checked by it. The fingerprints are real SHA-256 digests, to check with `sha256sum`. | 1 min 46 |

## Render

You need alea (a clone of `sudo-bngz/alea`, built with `cargo build
--release`), ffmpeg, and the Kokoro voice (`pip install sherpa-onnx numpy`;
the model, about 350 MB, is fetched once; `espeak-ng` for words it doesn't
know).

```sh
export ALEA_HOME=/path/to/alea                     # voices/kokoro.py is found there
export PATH=$ALEA_HOME/target/release:$PATH

cd 01-algorithme
python3 gen.py                                     # only after changing the script: writes algorithme.alea
alea algorithme.alea --seed 0xa160 -o out/         # the cover (png) and the 1080×1920 Reel (mp4)

cd ../02-alea
python3 gen.py
alea alea.alea --seed 0xa161 -o out/               # the seed shown in the film

cd ../03-hachage
python3 gen.py
alea hachage.alea --seed 0xa162 -o out/
```

Master Foo's Japanese needs misaki, Kokoro's pronunciation library:
`pip install "misaki[ja]"`.

Another seed, another deck: the cards, the counts and the music change.

The rendered videos are not kept in this repository: render them locally.

## Layout

```
voices/kokoro.py        the explanation's voice: runs alea's own Kokoro engine
voices/kokoro-ja.py     Master Foo's voice: Kokoro speaking Japanese, through misaki
fonts/                  Noto Sans JP (subset, OFL), for the katakana and the seal
01-algorithme/
  gen.py                the script, line by line; measures the voice and writes algorithme.alea
  algorithme.alea       the Reel: the deck, the voices, the timeline, the captions, the sound
  scenes/               one work per scene: koan, recipe, insertion, merge, cost
02-alea/
  gen.py                the script, Master Foo's lines in Japanese with their English
  alea.alea             the Reel, and the register: grown with `grow`, from the edition's seed
  scenes/               koan, machine, lfsr, seed, entropy
03-hachage/
  gen.py                the script, and the SHA-256 digests of the texts shown, as bits
  hachage.alea          the Reel; the edition chooses which letter the avalanche changes
  scenes/               koan, digest, fingerprint, avalanche, oneway, uses
lib/episode.py          what the generators share: the voice measured, the captions typed, the layout
```

## The voices

- Master Foo: `bm_george` in 01; from 02, `jm_kumo`, in Japanese.
- The explanation: `af_heart`.

The captions are typed as the words are said; `gen.py` writes them, since
they are long to write by hand.

## Licence

MIT. Noto Sans JP is under the SIL Open Font License 1.1 (`fonts/OFL.txt`).
