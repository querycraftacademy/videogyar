# -*- coding: utf-8 -*-
"""Gépi hangkapuk a kész narrációra: elharapott mondatvég, darabhatár-kattanás, egyenletes zúgás.

Elharapott mondatvég
    Egy rendesen befejezett mondat LECSENG: az utolsó 40 ms-a halk (jellemzően −40 dB körül), és
    érezhetően halkabb az előtte lévő 40 ms-nál. Egy levágott mondat magas szinten szakad meg (pl. −15 dB).
    A különbség tíz decibelekben mérhető, ezért ez kapu, nem ízlés kérdése. Mondatvégnek számít minden
    hely, ahol a beszéd után legalább 0,15 mp csend jön, és a fájl vége (a záró digitális csend levágva).
Kattanás
    Rövid (≤ 40 ms), nagyon hangos felpattanás, két oldalról digitális csenddel – tipikusan két
    hangdarab illesztésénél. Valódi beszédben ilyen nincs.
Zúgás
    Legalább 0,8 mp hallható, de szinte egyenletes szintű hang (a szint szórása 1,5 dB alatt). A beszéd
    szintje szótagonként hullámzik, a zúgásé nem.

Téves riasztás lehetséges (pl. zárhangra végződő szó). Ilyenkor hallgasd meg; ha jó, a kivételt írd fel,
de a küszöböt ne lazítsd vakon.

    python hangkapu.py <wav …> | <epizód-mappa>
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

VEG_KUSZOB_DB = -30.0   # e fölött gyanús az utolsó 40 ms
LECSENGES_DB = 6.0      # ennyivel legyen halkabb az előző 40 ms-nál
ABLAK = 0.04
CSEND_DB = -40.0        # mondathatár-kereséshez
CSEND_MIN = 0.25        # ennél rövidebb szünet szavak közötti, nem mondatvég
ZAR_DB = -40.0          # zárhang: a zárás ennél halkabb ...
ZAR_ABLAK = 0.10        # ... a mondatvég előtti ennyi időben ...
ZAR_ZC = 0.15           # ... és utána zajos (nullátmenetes) felpattanás jön
PARNA_DB = -70.0        # digitális csend
KATT_SZINT = -14.0
KATT_MAX = 0.04
ZUGAS_SZINT = -25.0
ZUGAS_SZORAS = 1.5
ZUGAS_MIN = 0.8


def _db(x: np.ndarray) -> float:
    if not x.size:
        return -120.0
    return max(-120.0, float(20 * np.log10(np.sqrt(np.mean(np.square(x, dtype=np.float64))) + 1e-12)))


def _keretek_db(jel: np.ndarray, sr: int, lep: float) -> np.ndarray:
    n = int(sr * lep)
    db = len(jel) // n
    if db == 0:
        return np.array([])
    k = jel[: db * n].reshape(db, n).astype(np.float64)
    return 20 * np.log10(np.sqrt(np.mean(k * k, axis=1)) + 1e-12)


def mondatvegek(jel: np.ndarray, sr: int) -> list[float]:
    """A mondatvégek időpontjai (mp): csend kezdete beszéd után, és a hangos rész vége."""
    lep = 0.01
    db = _keretek_db(jel, sr, lep)
    if db.size == 0:
        return []
    hangos = np.where(db > PARNA_DB)[0]
    if hangos.size == 0:
        return []
    vege = (hangos[-1] + 1) * lep
    vegek = []
    # a csendet a keret CSÚCSA dönti el (mint az FFmpeg silencedetect), nem az átlaga: így a mondatvég a
    # lecsengés végére esik, nem a közepére
    n = int(sr * lep)
    keretek = len(jel) // n
    csucs = np.abs(jel[: keretek * n].reshape(keretek, n)).max(axis=1)
    csendes = 20 * np.log10(csucs + 1e-12) < CSEND_DB
    i, n = 0, len(db)
    while i < n:
        if csendes[i] and i > 0 and not csendes[i - 1]:
            j = i
            while j < n and csendes[j]:
                j += 1
            if (j - i) * lep >= CSEND_MIN or j >= n:
                vegek.append(i * lep)
            i = j
        else:
            i += 1
    # a fájl végén rendszerint csend van; ha az utolsó csend nem ér el a hangos rész végéig,
    # akkor az utolsó mondat a hangos rész végén ér véget (a záró digitális csend nélkül)
    if not vegek or vege - vegek[-1] > 0.6:
        vegek.append(vege)
    return vegek


def zarhang_vegu(jel: np.ndarray, sr: int, t: float) -> bool:
    """Igaz, ha a mondat zárhang-felpattanással ér véget (pl. „…százalék.”): rövid zárás, utána zajos kitörés.
    Ilyenkor a 40 ms-os ablak a zárást az előző ablakba sorolja, és a kapu tévesen levágottnak hinné."""
    lep = 0.01
    k = int(sr * lep)
    darab = jel[max(0, int((t - ZAR_ABLAK) * sr)): int(t * sr)]
    kf = []
    for i in range(0, len(darab) - k + 1, k):
        s = darab[i:i + k]
        zc = float(np.mean(np.signbit(s[1:]) != np.signbit(s[:-1]))) if s.size > 1 else 0.0
        kf.append((_db(s), zc))
    for j, (szint, _zc) in enumerate(kf):
        if szint < ZAR_DB:
            utana = kf[j + 1:]
            while utana and utana[0][0] < ZAR_DB:
                utana = utana[1:]
            if utana and len(utana) * lep <= 0.06:
                return sum(z for _d, z in utana) / len(utana) > ZAR_ZC
    return False


def veg_profil(jel: np.ndarray, sr: int, t: float) -> tuple[float, float]:
    """(az utolsó 40 ms szintje dB-ben, lecsengés dB-ben – pozitív, ha halkul)."""
    a = int(sr * ABLAK)
    v = int(sr * t)
    utolso = _db(jel[max(0, v - a): v])
    elozo = _db(jel[max(0, v - 2 * a): max(0, v - a)])
    return utolso, elozo - utolso


def elharapott(jel: np.ndarray, sr: int) -> list[tuple[float, float, float]]:
    ki = []
    for t in mondatvegek(jel, sr):
        szint, lecs = veg_profil(jel, sr, t)
        if szint > VEG_KUSZOB_DB and lecs < LECSENGES_DB and not zarhang_vegu(jel, sr, t):
            ki.append((round(t, 2), round(szint, 1), round(lecs, 1)))
    return ki


def kattanasok(jel: np.ndarray, sr: int) -> list[tuple[float, float]]:
    lep = 0.005
    n = int(sr * lep)
    db = _keretek_db(jel, sr, lep)
    ki = []
    i = 0
    while i < len(db):
        if db[i] > PARNA_DB and (i == 0 or db[i - 1] <= PARNA_DB):
            j = i
            while j < len(db) and db[j] > PARNA_DB:
                j += 1
            hossz = (j - i) * lep
            utana_csend = j < len(db) and db[j] <= PARNA_DB
            elotte_csend = i > 0
            if hossz <= KATT_MAX and elotte_csend and utana_csend:
                csucs = float(20 * np.log10(np.abs(jel[i * n: j * n]).max() + 1e-12))
                if csucs > KATT_SZINT:
                    ki.append((round(i * lep, 3), round(csucs, 1)))
            i = j
        else:
            i += 1
    return ki


def zugasok(jel: np.ndarray, sr: int) -> list[tuple[float, float, float]]:
    lep = 0.04
    db = _keretek_db(jel, sr, lep)
    w = int(ZUGAS_MIN / lep)
    ki = []
    i = 0
    while i + w <= len(db):
        ablak = db[i: i + w]
        if ablak.min() > ZUGAS_SZINT and ablak.std() < ZUGAS_SZORAS:
            j = i + w
            while j < len(db) and db[j] > ZUGAS_SZINT and db[i:j + 1].std() < ZUGAS_SZORAS:
                j += 1
            ki.append((round(i * lep, 2), round((j - i) * lep, 2), round(float(db[i:j].mean()), 1)))
            i = j
        else:
            i += 1
    return ki


def ellenoriz(utak: list[str]) -> list[str]:
    """Az összes hiba szövegesen; üres lista = rendben."""
    hibak = []
    for ut in utak:
        jel, sr = K.wav_olvas(ut)
        nev = os.path.basename(ut)
        for t, szint, lecs in elharapott(jel, sr):
            hibak.append(f"{nev} @ {t:6.2f} mp  ELHARAPOTT MONDATVÉG  utolsó 40 ms {szint} dB, lecsengés {lecs:+} dB")
        for t, csucs in kattanasok(jel, sr):
            hibak.append(f"{nev} @ {t:6.2f} mp  KATTANÁS  csúcs {csucs} dB")
        for t, h, szint in zugasok(jel, sr):
            hibak.append(f"{nev} @ {t:6.2f} mp  ZÚGÁS  {h} mp, {szint} dB")
    return hibak


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print(__doc__)
        return 2
    utak = []
    for x in a:
        if os.path.isdir(x):
            utak += sorted(glob.glob(os.path.join(x, "audio", "utemek", "*.wav")))
        else:
            utak.append(x)
    hibak = ellenoriz(utak)
    for h in hibak:
        print(h)
    if hibak:
        print("\nHANGKAPU MEGBUKOTT: írd át a mondatot (a kockázatos szó ne a végén álljon), "
              "töröld az ütem hangját, és generáld újra.")
        return 1
    print(f"hangkapuk: rendben ({len(utak)} fájl)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
