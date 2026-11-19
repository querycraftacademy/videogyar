# -*- coding: utf-8 -*-
"""A videógyár eszközeinek közös segédfüggvényei: FFmpeg keresése, futtatás, JSON, beállítások, hangbeolvasás.

Minden eszköz innen importál. Csak a standard könyvtárat és (a hangos részeknél) a numpy-t használja.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unicodedata

ESZKOZOK = os.path.dirname(os.path.abspath(__file__))

ALAP_GYAR = {
    "nyelv": "hu",
    "felbontas": [1920, 1080],
    "fps": 30,
    "tts": {"motor": "proba", "modul": "tts_proba", "eszkoz": "cpu", "max_karakter": 250},
    "whisper": {"modell": "small", "eszkoz": "cpu"},
    "render": {"minoseg": "looks", "rejtett": True},
    "hangero_lufs": -14,
    "zene": {"mappa": "kozos/zene", "fajl": "", "hangero": 0.11},
    "kreditek": [],
    "gpu_megosztott": False,
}


def _keres(nev: str, kornyezeti: str) -> str:
    ut = os.environ.get(kornyezeti)
    if ut and os.path.exists(ut):
        return ut
    talalt = shutil.which(nev)
    if talalt:
        return talalt
    sys.exit(f"HIBA: nem találom a(z) {nev} programot. Telepítsd (lásd videogyar-telepites), "
             f"vagy add meg az útját a {kornyezeti} környezeti változóban.")


def ffmpeg() -> str:
    return _keres("ffmpeg", "FFMPEG")


def ffprobe() -> str:
    ut = os.environ.get("FFPROBE")
    if ut and os.path.exists(ut):
        return ut
    talalt = shutil.which("ffprobe")
    if talalt:
        return talalt
    # az ffmpeg mellett szokott lenni
    ff = ffmpeg()
    melle = os.path.join(os.path.dirname(ff), "ffprobe" + (".exe" if os.name == "nt" else ""))
    if os.path.exists(melle):
        return melle
    sys.exit("HIBA: nem találom az ffprobe programot (az FFmpeg része).")


def futtat(args: list, csendes: bool = True, **kw) -> subprocess.CompletedProcess:
    """Parancs futtatása; hiba esetén kiírja a parancs kimenetét és kilép."""
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        print("HIBA a parancsban:", " ".join(str(a) for a in args[:6]), "...", file=sys.stderr)
        print((r.stderr or r.stdout)[-3000:], file=sys.stderr)
        sys.exit(r.returncode)
    if not csendes and r.stdout:
        print(r.stdout)
    return r


def ff(*args: str) -> subprocess.CompletedProcess:
    """FFmpeg-hívás a szokásos csendes kapcsolókkal."""
    return futtat([ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", *args])


def hossz(ut: str) -> float:
    """Médiafájl hossza másodpercben."""
    r = futtat([ffprobe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", ut])
    return float(r.stdout.strip())


def van_hangja(ut: str) -> bool:
    r = futtat([ffprobe(), "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                "-of", "csv=p=0", ut])
    return bool(r.stdout.strip())


def lufs(ut: str) -> float:
    """Integrált hangerő (EBU R128) LUFS-ben."""
    r = subprocess.run([ffmpeg(), "-hide_banner", "-nostats", "-i", ut, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    sorok = [s for s in r.stderr.splitlines() if s.strip().startswith("I:") and "LUFS" in s]
    if not sorok:
        return float("-inf")
    return float(sorok[-1].split("I:")[1].split("LUFS")[0].strip())


def json_olvas(ut: str, alap=None):
    if not os.path.exists(ut):
        return alap
    with open(ut, encoding="utf-8") as f:
        return json.load(f)


def json_ir(ut: str, adat) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(ut)), exist_ok=True)
    with open(ut, "w", encoding="utf-8") as f:
        json.dump(adat, f, ensure_ascii=False, indent=1)


def munkamappa(epizod: str) -> str:
    """A gyar.json-t tartalmazó mappa felfelé keresve; ha nincs, az epizód szülőjének szülője."""
    ut = os.path.abspath(epizod)
    while True:
        if os.path.exists(os.path.join(ut, "gyar.json")):
            return ut
        fel = os.path.dirname(ut)
        if fel == ut:
            return os.path.dirname(os.path.dirname(os.path.abspath(epizod)))
        ut = fel


def gyar(epizod: str) -> dict:
    """A gyar.json beállításai az alapértékekkel kiegészítve."""
    g = json.loads(json.dumps(ALAP_GYAR))
    sajat = json_olvas(os.path.join(munkamappa(epizod), "gyar.json"), {}) or {}
    for k, v in sajat.items():
        if isinstance(v, dict) and isinstance(g.get(k), dict):
            g[k].update(v)
        else:
            g[k] = v
    return g


def szoveg(epizod: str) -> dict:
    sz = json_olvas(os.path.join(epizod, "szoveg.json"))
    if not sz:
        sys.exit(f"HIBA: nincs szoveg.json ebben az epizódban: {epizod}")
    return sz


def utem_mondat(utem) -> str:
    return utem if isinstance(utem, str) else utem.get("mondat", "")


def terv(epizod: str) -> dict:
    p = json_olvas(os.path.join(epizod, "audio", "plan.json"))
    if not p:
        sys.exit("HIBA: nincs audio/plan.json. Előbb a narráció kell (narracio.py vagy terv.py).")
    return p


def ekezet_nelkul(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def rovid_nev(s: str, max_hossz: int = 24) -> str:
    s = ekezet_nelkul(s).lower()
    s = "".join(c if c.isalnum() else "_" for c in s)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")[:max_hossz] or "jelenet"


def wav_olvas(ut: str, sr: int = 48000):
    """Bármilyen hangfájl mono float32 numpy-tömbként (FFmpeg dekódolja)."""
    import numpy as np
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", ut, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"HIBA: nem tudom beolvasni: {ut}\n{r.stderr.decode(errors='replace')[-1000:]}")
    return np.frombuffer(r.stdout, dtype=np.float32), sr


def ido(mp: float) -> str:
    """Másodperc → p:mm formátum."""
    mp = int(round(mp))
    return f"{mp // 60}:{mp % 60:02d}"
