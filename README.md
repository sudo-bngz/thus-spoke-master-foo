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
| 04 | [Clé](04-cle/) | How do two strangers agree on a secret in a square where everyone listens? Arithmetic on a clock of 23 hours, a prime; jumping by 5 visits every hour; forward is easy, backward is the discrete logarithm. Each keeps a secret number of jumps, says the result aloud, and both land on the same key (Diffie–Hellman, with the real numbers). The lock in the browser. | 2 min 10 |
| 05 | [Token](05-token/) | What is a language model? It reads tokens, pieces of words, each a number; its only job is a probability for every token that could come next; it picks one, adds it, asks again. It rolls a die weighted by the probabilities, and temperature shapes the die. The probabilities come from reading nearly everything, hundreds of billions of knobs turned until the guesses matched. The probabilities shown are illustrative. | 2 min 01 |

### AI, a sub-series

One idea per episode, in the order they build on each other: the neuron,
layers, how it learns, tokens, attention, the next token, training, the
context window, hallucination. Episode 05 above was the first attempt to
say it all in one; these take their time.

| # | Episode | The idea | Length |
|---|---|---|---|
| AI 01 | [Neurone](ai-01-neurone/) | The perceptron. Inputs on weighted wires, a sum, a threshold: it fires or not. With two inputs it is a line; the rule (show it a point; if wrong, move the weights toward the answer) swings the line until it is never wrong again. Then the limit: the opposite corners together, which no line separates. The edition draws the points, and the weights are grown by the rule itself, inside alea. | 2 min 59 |
| AI 02 | [Couches](ai-02-couches/) | Layers. The opposite corners beat one neuron; two neurons draw two lines and each answers one question; a third neuron takes their answers as its inputs and fires only between the lines: a band, two lines joined. More neurons, any shape; more layers, shapes of shapes: deep. | 2 min 31 |
| AI 03 | [Erreur](ai-03-erreur/) | How the scales learn. The error as one number (the gaps between answers and right answers, added up); the error as a landscape over the weights; the slope under one's feet and the walk down, step by step (gradient descent, grown by the slope itself, with steps too small and too big beside it); the blame sent backward along the wires (backpropagation). The landscape is the edition's. | 2 min 39 |
| AI 04 | [Jeton](ai-04-jeton/) | Tokens, and the map of meaning. A token is a piece of text (a sentence of 4, a long word of 3, a vocabulary of 50 000); each has a number, which says nothing about meaning; so each gets a place on a learned map where words used in the same ways sit close (an embedding); and directions mean something: king − man + woman ≈ queen. The ids and places are illustrative. | 2 min 30 |
| AI 05 | [Attention](ai-05-attention/) | The transformer's idea. The cat was hungry, so it ate the fish: what is "it"? A word alone means little; each word looks at every other and gives it a score (the attention, adding up to 1); the scores come from a question and a label made from each word's point on the map; then each word becomes a blend of the others and absorbs its context, layer after layer. The scores are illustrative. | 2 min 34 |
| AI 06 | [Suivant](ai-06-suivant/) | The next token. Once upon a: after all the layers, the last word's point becomes a score for every token the machine knows (50 000); squeezed, the scores are probabilities; the machine picks 1, adds it to the text, and starts over, 1 token at a time; which 1 it picks is a weighted die, shaped by the temperature and rolled with a seed; and the whole machine is a loop: text, tokens, map, layers, probabilities, die, and back into the text. The probabilities are illustrative; the die's temperatures are computed by gen.py. | 2 min 38 |
| AI 07 | [Entraînement](ai-07-entrainement/) | Where the weights come from. At first they are random; training is a game: a sentence from the internet, the next word hidden, the machine guesses; the error is how far the guess is from the truth; it flows backward and every weight moves a tiny step; done on everything ever written, on thousands of machines for months, the error goes down; and to guess the next word well the machine had to learn grammar, facts, styles, arithmetic. The numbers are illustrative. | 2 min 23 |
| AI 08 | [Mémoire](ai-08-memoire/) | The window. The weights never change once training is done; a conversation lives in the text, fed back in whole at every message; the text has a limit, the window (12 tokens here, 100 000 or more in real ones); why: every token looks at every other, so twice the text is 4 times the work; at the edge the oldest tokens fall out, never seen; and the machine's 2 memories, the weights and the window, with the trick: a note at the top of the window. | 2 min 27 |

## Render

You need alea (a clone of `sudo-bngz/alea`, built with `cargo build
--release`; from AI 01 on, with [PR #39](https://github.com/sudo-bngz/alea/pull/39),
which lets a grown field be read at a given moment), ffmpeg, and the Kokoro voice (`pip install sherpa-onnx numpy`;
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

cd ../04-cle
python3 gen.py
alea cle.alea --seed 0xa163 -o out/

cd ../05-token
python3 gen.py
alea token.alea --seed 0xa164 -o out/

cd ../ai-01-neurone
python3 gen.py
alea neurone.alea --seed 0xa1a1 -o out/

cd ../ai-02-couches
python3 gen.py
alea couches.alea --seed 0xa1a2 -o out/

cd ../ai-03-erreur
python3 gen.py
alea erreur.alea --seed 0xa1a3 -o out/               # needs alea with PR #39 (a grown field held at a moment)

cd ../ai-04-jeton
python3 gen.py
alea jeton.alea --seed 0xa1a4 -o out/

cd ../ai-05-attention
python3 gen.py
alea attention.alea --seed 0xa1a5 -o out/

cd ../ai-06-suivant
python3 gen.py
alea suivant.alea --seed 0xa1a6 -o out/

cd ../ai-07-entrainement
python3 gen.py
alea entrainement.alea --seed 0xa1a7 -o out/

cd ../ai-08-memoire
python3 gen.py
alea memoire.alea --seed 0xa1a8 -o out/
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
04-cle/
  gen.py                the script, and the numbers of the exchange, checked (23, 5, 6, 15 → 8, 19 → 2)
  cle.alea              the Reel
  scenes/               koan, clock, oneway, exchange, lock
05-token/
  gen.py                the script, the candidates' probabilities (illustrative) and the die's temperatures
  token.alea            the Reel
  scenes/               koan, tokens, next, dice, knobs
ai-01-neurone/
  gen.py                the script; the points and the perceptron rule, grown with `grow`
  neurone.alea          the Reel
  scenes/               koan, cell, line, learn (also the XOR corners)
ai-02-couches/
  gen.py                the script
  couches.alea          the Reel
  scenes/               koan, plane, half, net, problem, lines, band, shapes
ai-03-erreur/
  gen.py                the script; the landscape, and the three walkers grown by the slope
  erreur.alea           the Reel
  scenes/               koan, error, map, landscape, descent, backward, net
ai-04-jeton/
  gen.py                the script
  jeton.alea            the Reel
  scenes/               koan, pieces, numbers, atlas
ai-05-attention/
  gen.py                the script
  attention.alea        the Reel
  scenes/               koan, words, problem, scores, keys, blend
ai-06-suivant/
  gen.py                the script
  suivant.alea          the Reel
  scenes/               koan, job, next, dice, loop
ai-07-entrainement/
  gen.py                the script
  entrainement.alea     the Reel
  scenes/               koan, guess, nudge, scale, learned
ai-08-memoire/
  gen.py                the script
  memoire.alea          the Reel
  scenes/               koan, window, cost, edge, two
lib/episode.py          what the generators share: the voice measured, the captions typed, the layout
```

## The voices

Two engines, in `voices/`, each a small program that reads the text on its
standard input and writes a WAV, as alea expects:

- `master.sh`, Master Foo: with `ELEVENLABS_API_KEY` set, ElevenLabs (model
  `eleven_multilingual_v2`, which speaks Japanese), the voice being the id
  in `MASTER_VOICE`; without the key, Kokoro's Japanese voice (`jm_kumo`),
  through `kokoro-ja.py` and misaki.
- `narrator.sh`, the explanation: ElevenLabs too when `NARRATOR_VOICE` is
  set as well; otherwise Kokoro (`af_heart`), through alea's own engine.

```sh
export ELEVENLABS_API_KEY=…
export MASTER_VOICE=<an ElevenLabs voice id, Japanese>     # and NARRATOR_VOICE=<id>, if wanted
cd 04-cle && python3 gen.py && alea cle.alea --seed 0xa163 -o out/

cd ../05-token
python3 gen.py
alea token.alea --seed 0xa164 -o out/

cd ../ai-01-neurone
python3 gen.py
alea neurone.alea --seed 0xa1a1 -o out/

cd ../ai-02-couches
python3 gen.py
alea couches.alea --seed 0xa1a2 -o out/

cd ../ai-03-erreur
python3 gen.py
alea erreur.alea --seed 0xa1a3 -o out/               # needs alea with PR #39 (a grown field held at a moment)

cd ../ai-04-jeton
python3 gen.py
alea jeton.alea --seed 0xa1a4 -o out/

cd ../ai-05-attention
python3 gen.py
alea attention.alea --seed 0xa1a5 -o out/

cd ../ai-06-suivant
python3 gen.py
alea suivant.alea --seed 0xa1a6 -o out/

cd ../ai-07-entrainement
python3 gen.py
alea entrainement.alea --seed 0xa1a7 -o out/

cd ../ai-08-memoire
python3 gen.py
alea memoire.alea --seed 0xa1a8 -o out/
```

Run `gen.py` and `alea` with the same variables: `gen.py` measures each
line with the engine to lay the scenes out, and alea says each line once and
keeps it (`~/.cache/alea/voices/`), so a voice change needs both. In 01 the
master is `bm_george`, in English. The mix keeps a small room (`room: 0.12`)
and no echo, so the voices stay clear.

The captions are typed as the words are said; `gen.py` writes them. Numbers
are always shown in digits (the voice is given them in words, which the
engines read better); a caption whose text differs from the spoken one is
typed evenly over the line.

## Licence

MIT. Noto Sans JP is under the SIL Open Font License 1.1 (`fonts/OFL.txt`).
