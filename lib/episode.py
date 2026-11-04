"""What the episodes' generators share: the voice measured, captions typed
as the words are said, and the layout of the scenes from their lines."""
import io, os, subprocess, sys, wave

LEAD, GAP, HOLD = 1.4, 1.0, 2.0     # seconds: picture alone, between sentences, before the cut


def measure(text, who, here, narrator, master, en_engine, ja_engine):
    voice, speed = narrator if who == "N" else master
    engine = os.path.join(here, en_engine if who == "N" else ja_engine)
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



def layout(scenes, measure):
    """Lays the scenes out in time from their lines; gives (total, starts,
    lengths, at) with at[vid] the second each line starts."""
    dur, at, starts, lengths = {}, {}, [], []
    clock = 0.0
    for name, _, lines, extra in scenes:
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
    print(f"total {total} s", file=sys.stderr)
    return total, starts, lengths, at
