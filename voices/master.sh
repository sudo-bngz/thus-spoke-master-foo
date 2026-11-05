#!/bin/sh
# Master Foo's voice. With $ELEVENLABS_API_KEY set: ElevenLabs, through alea's
# voices/elevenlabs.sh (model eleven_multilingual_v2, which speaks Japanese),
# the voice being the id given as `voice:` ($MASTER_VOICE in gen.py). Without
# the key: Kokoro's Japanese voice, kokoro-ja.py next to this script.
# Text on stdin, WAV on stdout, as alea expects.
set -e
here=$(dirname "$0")
if [ -n "$ELEVENLABS_API_KEY" ]; then
  home="${ALEA_HOME:-$(dirname "$(dirname "$(command -v alea)")")/..}"
  [ -f "$home/voices/elevenlabs.sh" ] || { echo "master.sh: set ALEA_HOME to your clone of alea" >&2; exit 1; }
  ELEVENLABS_MODEL="${ELEVENLABS_MODEL:-eleven_multilingual_v2}" exec sh "$home/voices/elevenlabs.sh"
fi
exec python3 "$here/kokoro-ja.py"
