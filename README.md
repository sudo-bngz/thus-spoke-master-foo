# Thus Spoke Master Foo

Two minutes, one idea of computing, explained in a Reel. Each episode opens
with a koan: a novice asks, Master Foo answers with something to do; then a
voice explains, step by step, with diagrams that move and sound; and the
koan closes it.

Every episode is a work written in [alea](https://github.com/sudo-bngz/alea),
the language whose output is an artwork rather than a program. Nothing is
drawn by hand: the diagrams, the music and the timing are code, and each
edition (each seed) draws its own variations.

Ink on paper, a vermilion accent; the master speaks in vermilion, the
explanation in ink.

## Episodes

| # | Episode | The idea | Length |
|---|---|---|---|
| 01 | [Algorithme](01-algorithme/) | What is an algorithm? A recipe: steps, in order, until the work is done. Two recipes sort the same sixteen cards (insertion, merging); a counter adds up their comparisons, and for a thousand cards the difference is a large square against a small one. | 1 min 40 |

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
```

Another seed, another deck: the cards, the counts and the music change.

The rendered videos are not kept in this repository: render them locally.

## Layout

```
voices/kokoro.py        the series' voice: runs alea's own Kokoro engine
fonts/                  Noto Sans JP (subset, OFL), for the katakana and the seal
01-algorithme/
  gen.py                the script, line by line; measures the voice and writes algorithme.alea
  algorithme.alea       the Reel: the deck, the voices, the timeline, the captions, the sound
  scenes/               one work per scene: koan, recipe, insertion, merge, cost
```

## The voices

- Master Foo: `bm_george`, a little slower.
- The explanation: `af_heart`.

The captions are typed as the words are said; `gen.py` writes them, since
they are long to write by hand.

## Licence

MIT. Noto Sans JP is under the SIL Open Font License 1.1 (`fonts/OFL.txt`).
