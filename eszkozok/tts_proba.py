# -*- coding: utf-8 -*-
"""Álhangmotor a lánc kipróbálásához. NEM beszél: szótagszerű, lecsengő zajt ad a szöveg hosszával arányosan.

Arra jó, hogy a narráció → időterv → jelenet → render → keverés lánc hangmotor nélkül is kipróbálható
legyen (önteszt, új gép). Valódi videóhoz a felhasználó által választott motor illesztője kell
(lásd videogyar-hang, 3. pont). Ugyanazt a szerződést követi, mint egy valódi illesztő.
"""
from __future__ import annotations

import hashlib
import wave

import numpy as np

SR = 48000


def betolt(beallitas: dict) -> None:  # noqa: ARG001 – a szerződés része
    pass


def szintetizal(szoveg: str, kimenet_wav: str, beallitas: dict | None = None) -> None:
    mag = int(hashlib.sha1(szoveg.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(mag)
    darabok = []
    szavak = szoveg.split()
    for n, szo in enumerate(szavak):
        maganhangzok = max(1, sum(c in "aáeéiíoóöőuúüű" for c in szo.lower()))
        for _ in range(maganhangzok):
            hossz = rng.uniform(0.11, 0.2)
            t = np.arange(int(SR * hossz)) / SR
            burok = np.sin(np.pi * t / hossz) ** 1.5 * rng.uniform(0.25, 0.6)
            alap = rng.uniform(110, 170)
            jel = (0.6 * np.sin(2 * np.pi * alap * t) + 0.3 * np.sin(2 * np.pi * 2 * alap * t)
                   + 0.25 * rng.standard_normal(t.size))
            darabok.append((jel * burok).astype(np.float32))
        szunet = 0.06
        if szo.endswith((",", ";", "–")):
            szunet = 0.18
        elif szo.endswith((".", "!", "?", ":")) and n < len(szavak) - 1:
            szunet = 0.32
        darabok.append(np.zeros(int(SR * szunet), dtype=np.float32))
    jel = np.concatenate(darabok) if darabok else np.zeros(SR, dtype=np.float32)
    # a vége biztosan lecsengjen, utána rövid csend (ahogy egy jó hangmotor is adja)
    lecs = min(int(SR * 0.12), jel.size)
    jel[-lecs:] *= np.linspace(1, 0, lecs, dtype=np.float32)
    jel = np.concatenate([jel, np.zeros(int(SR * 0.1), dtype=np.float32)])
    jel = jel / max(1e-6, np.abs(jel).max()) * 0.5
    with wave.open(kimenet_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((jel * 32767).astype("<i2").tobytes())


def lezar() -> None:
    pass
