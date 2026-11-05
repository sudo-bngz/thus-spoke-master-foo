#!/bin/sh
# The explanation's voice. With $ELEVENLABS_API_KEY and $NARRATOR_VOICE set
# (an ElevenLabs voice id, given as `voice:` by gen.py): ElevenLabs, through
# alea's voices/elevenlabs.sh. Otherwise Kokoro (af_heart), through alea's
# own engine, kokoro.py next to this script. Text on stdin, WAV on stdout.
set -e
here=$(dirname "$0")
if [ -n "$ELEVENLABS_API_KEY" ] && [ -n "$NARRATOR_VOICE" ]; then
  home="${ALEA_HOME:-$(dirname "$(dirname "$(command -v alea)")")/..}"
  [ -f "$home/voices/elevenlabs.sh" ] || { echo "narrator.sh: set ALEA_HOME to your clone of alea" >&2; exit 1; }
  ELEVENLABS_MODEL="${ELEVENLABS_MODEL:-eleven_multilingual_v2}" exec sh "$home/voices/elevenlabs.sh"
fi
exec python3 "$here/kokoro.py"
