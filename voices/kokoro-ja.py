#!/usr/bin/env python3
"""Master Foo's voice: Kokoro speaking Japanese (jm_kumo by default).

alea's Kokoro engine knows English and Chinese; this one reads Japanese.
misaki, Kokoro's own pronunciation library, turns the text (kanji, kana)
into the model's phonemes; each word is handed to the model through a
lexicon of its own, so nothing is guessed from spelling.

    pip install sherpa-onnx numpy "misaki[ja]"
    say("師は答えた。七。", engine: "../voices/kokoro-ja.py", voice: "jm_kumo")

The model is alea's (fetched once by its voices/kokoro.py, into the cache,
or $KOKORO_DIR). Text on stdin, WAV on stdout, as alea expects.
"""
import os, re, sys, tempfile, wave

MODEL = "kokoro-multi-lang-v1_0"
SPEAKERS = ("af_alloy af_aoede af_bella af_heart af_jessica af_kore af_nicole af_nova af_river af_sarah af_sky "
            "am_adam am_echo am_eric am_fenrir am_liam am_michael am_onyx am_puck am_santa bf_alice bf_emma bf_isabella "
            "bf_lily bm_daniel bm_fable bm_george bm_lewis ef_dora em_alex ff_siwis hf_alpha hf_beta hm_omega hm_psi "
            "if_sara im_nicola jf_alpha jf_gongitsune jf_nezumi jf_tebukuro jm_kumo pf_dora pm_alex pm_santa zf_xiaobei "
            "zf_xiaoni zf_xiaoxiao zf_xiaoyi zm_yunjian zm_yunxi zm_yunxia zm_yunyang em_santa").split()


def model_dir():
    d = os.environ.get("KOKORO_DIR")
    if d:
        return d
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    d = os.path.join(cache, "alea", MODEL)
    if not os.path.exists(os.path.join(d, "model.onnx")):
        sys.exit(f"kokoro-ja: no model in {d}; say something once with alea's voices/kokoro.py to fetch it")
    return d


def name(k):
    """A made-up word, letters only, for the k-th Japanese word: qzja, qzjb…"""
    s = ""
    k += 26
    while k:
        k, r = divmod(k, 26)
        s = chr(97 + r) + s
    return "qzj" + s


def main():
    import numpy as np
    import sherpa_onnx
    from misaki import ja
    text = sys.stdin.read().strip()
    voice = os.environ.get("ALEA_VOICE") or "jm_kumo"
    if voice not in SPEAKERS:
        sys.exit(f"kokoro-ja: no voice `{voice}`")
    speed = float(os.environ.get("ALEA_SPEED", "1"))
    d = model_dir()
    phones = ja.JAG2P()(text)
    phones = phones[0] if isinstance(phones, tuple) else phones
    tokens = {l.split()[0] for l in open(os.path.join(d, "tokens.txt"), encoding="utf-8") if l.split()}
    # each run of phonemes becomes a word of the lexicon; punctuation stays, for the pauses
    lexicon, words = [], []
    for k, (run, punct) in enumerate(re.findall(r"([^\s.,!?。、！？]+)|([.,!?。、！？])", phones)):
        if punct:
            words.append({"。": ".", "、": ",", "！": "!", "？": "?"}.get(punct, punct))
            continue
        w = name(len(lexicon))
        lexicon.append(w + " " + " ".join(c for c in run if c in tokens))
        words.append(" " + w)
    path = os.path.join(tempfile.gettempdir(), f"kokoro-ja-{os.getpid()}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lexicon) + "\n")
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=os.path.join(d, "model.onnx"), voices=os.path.join(d, "voices.bin"), tokens=os.path.join(d, "tokens.txt"),
                data_dir=os.path.join(d, "espeak-ng-data"), dict_dir=os.path.join(d, "dict"),
                lexicon=",".join([path, os.path.join(d, "lexicon-us-en.txt")])),
            num_threads=os.cpu_count() or 2),
        max_num_sentences=1)
    tts = sherpa_onnx.OfflineTts(cfg)
    audio = tts.generate("".join(words).strip(), sid=SPEAKERS.index(voice), speed=speed)
    out = wave.open(sys.stdout.buffer, "wb")
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(audio.sample_rate)
    out.writeframes((np.clip(np.array(audio.samples), -1, 1) * 32767).astype(np.int16).tobytes())
    out.close()
    os.remove(path)


if __name__ == "__main__":
    main()
