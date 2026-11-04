#!/usr/bin/env python3
"""The voice of the series: alea's Kokoro engine, found where alea lives.

The works say `engine: "../voices/kokoro.py"`; this runs alea's own
voices/kokoro.py, from $ALEA_HOME (a clone of github.com/sudo-bngz/alea), or
else from the clone the `alea` on the PATH was built in. Text on stdin, WAV
on stdout, as alea expects.
"""
import os, runpy, shutil, sys


def find():
    home = os.environ.get("ALEA_HOME")
    if home:
        return os.path.join(home, "voices", "kokoro.py")
    exe = shutil.which("alea")
    if exe:
        d = os.path.dirname(os.path.realpath(exe))
        for up in range(4):
            p = os.path.join(d, "voices", "kokoro.py")
            if os.path.exists(p):
                return p
            d = os.path.dirname(d)
    sys.exit("kokoro: set ALEA_HOME to your clone of alea (it has voices/kokoro.py)")


engine = find()
sys.argv[0] = engine
runpy.run_path(engine, run_name="__main__")
