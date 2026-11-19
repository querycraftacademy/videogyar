# -*- coding: utf-8 -*-
"""Önteszt: a teljes lánc gyors próbája hangmotor nélkül, egy ideiglenes munkamappában.

    python onteszt.py              # kiejtés, narráció (álhanggal), időterv, hangkapuk, jelenet, keverés,
                                   # összefűzés, leírás – render helyett színes helykitöltő videóval
    python onteszt.py --lint       # + npx hyperframes lint a jeleneteken
    python onteszt.py --render     # + valódi HyperFrames-render (draft) és pillanatkép-lap
    python onteszt.py --megtart    # az ideiglenes munkamappa megmarad (kiírja, hol)

Kilépési kód: 0 = minden rendben, 1 = valami megbukott (a kimenet megmondja, mi).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave

ITT = os.path.dirname(os.path.abspath(__file__))
CSOMAG = os.path.dirname(ITT)
sys.path.insert(0, ITT)
import _kozos as K  # noqa: E402

EREDMENY: list[tuple[str, bool, str]] = []


def lepes(nev: str, ok: bool, megj: str = "") -> bool:
    EREDMENY.append((nev, ok, megj))
    print(f"[{'OK' if ok else 'HIBA'}] {nev}" + (f" – {megj}" if megj else ""), flush=True)
    return ok


def eszkoz(nev: str, *args: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(ITT, nev), *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def ir_wav(ut: str, jel, sr: int = 48000) -> None:
    import numpy as np
    with wave.open(ut, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(jel, -1, 1) * 32767).astype("<i2").tobytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A videógyár önteszte")
    ap.add_argument("--lint", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--megtart", action="store_true")
    a = ap.parse_args(argv)
    import numpy as np

    print(f"FFmpeg: {K.ffmpeg()}")
    mappa = tempfile.mkdtemp(prefix="videogyar_onteszt_")
    ep = os.path.join(mappa, "epizodok", "001_proba")
    os.makedirs(os.path.join(mappa, "kozos", "zene"))
    os.makedirs(ep)
    shutil.copy(os.path.join(CSOMAG, "sablonok", "gyar.json"), mappa)
    shutil.copy(os.path.join(CSOMAG, "sablonok", "kiejtes.json"), os.path.join(mappa, "kozos"))
    shutil.copy(os.path.join(CSOMAG, "sablonok", "epizod", "szoveg.json"), ep)
    g = json.load(open(os.path.join(mappa, "gyar.json"), encoding="utf-8"))
    g["render"]["minoseg"] = "draft"
    g["kreditek"] = ["Hang: próbamotor (önteszt)"]
    K.json_ir(os.path.join(mappa, "gyar.json"), g)
    # háttérzene: 40 mp-es akkord, hogy a keverés is kipróbálható legyen
    K.ff("-f", "lavfi", "-i", "sine=f=220:d=40", "-f", "lavfi", "-i", "sine=f=277:d=40", "-f", "lavfi", "-i",
         "sine=f=330:d=40", "-filter_complex", "amix=inputs=3,volume=0.5,aformat=channel_layouts=stereo",
         os.path.join(mappa, "kozos", "zene", "proba_zene.wav"))

    # 1. kiejtés: a sablon szövege átmegy, egy rossz mondat megbukik
    import kiejtes
    szotar, engedett = kiejtes.betolt(os.path.join(mappa, "kozos", "kiejtes.json"))
    jo = kiejtes.alkalmaz("A Claude és a ChatGPT is ért hozzá.", szotar)
    rossz = kiejtes.gyanus(kiejtes.alkalmaz("Nézzük meg a Sales_Total oszlopot a DAX-ban, Excelben.", szotar), engedett)
    lepes("kiejtés: szótár csere", "klód" in jo and not kiejtes.gyanus(jo, engedett), jo)
    lepes("kiejtés: gyanús szavak megfogva", len(rossz) == 3, ", ".join(s for s, _ in rossz))

    # 2. narráció álhanggal + időterv + hangkapuk
    r = eszkoz("narracio.py", ep, cwd=mappa)
    plan = K.json_olvas(os.path.join(ep, "audio", "plan.json"))
    ok = r.returncode == 0 and plan and plan["sorrend"] == ["s0", "s1"]
    lepes("narráció, időterv, hangkapuk", bool(ok), (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "")
    if not ok:
        print(r.stdout, r.stderr)
        return osszegzes(mappa, a.megtart)
    r2 = eszkoz("narracio.py", ep, cwd=mappa)
    lepes("gyorsítótár: másodszorra nem generál", "naprakész" in r2.stdout)
    hosszak = all(abs(K.hossz(os.path.join(ep, "audio", f"{s}.wav")) - plan["jelenetek"][s]["duration"]) < 0.05
                  for s in plan["sorrend"])
    lepes("jelenethang hossza = jelenet hossza", hosszak)

    # 3. hangkapuk negatív próba: levágott mondat, kattanás, zúgás
    import hangkapu
    sr = 48000
    t = np.arange(int(sr * 1.2)) / sr
    # szótagszerűen hullámzó hang, ami a végén TELJES hangerőn szakad meg (nem cseng le)
    burok = np.where(t < 0.9, 0.6 + 0.4 * np.sin(2 * np.pi * 4 * t), 1.0)
    beszed = (0.4 * np.sin(2 * np.pi * 150 * t) * burok).astype(np.float32)
    levagott = np.concatenate([beszed, np.zeros(sr // 2, np.float32)])
    katt = np.concatenate([np.zeros(sr // 2), 0.8 * np.sin(2 * np.pi * 900 * np.arange(int(sr * 0.015)) / sr),
                           np.zeros(sr // 2)]).astype(np.float32)
    zug = np.concatenate([(0.2 * np.sin(2 * np.pi * 120 * np.arange(int(sr * 1.3)) / sr)), np.zeros(sr // 3)]).astype(np.float32)
    proba = os.path.join(mappa, "_kapu")
    os.makedirs(proba)
    for nev, jel in (("levagott", levagott), ("katt", katt), ("zug", zug)):
        ir_wav(os.path.join(proba, nev + ".wav"), jel)
    j1, _ = K.wav_olvas(os.path.join(proba, "levagott.wav"))
    j2, _ = K.wav_olvas(os.path.join(proba, "katt.wav"))
    j3, _ = K.wav_olvas(os.path.join(proba, "zug.wav"))
    lepes("hangkapu: levágott mondatvég megfogva", bool(hangkapu.elharapott(j1, sr)))
    lepes("hangkapu: kattanás megfogva", bool(hangkapu.kattanasok(j2, sr)))
    lepes("hangkapu: zúgás megfogva", bool(hangkapu.zugasok(j3, sr)))

    # 4. jelenetek
    r = eszkoz("jelenet.py", ep, *(["--lint"] if a.lint else []), cwd=mappa)
    html0 = os.path.join(ep, "jelenetek", "s0", "index.html")
    tart = open(html0, encoding="utf-8").read() if os.path.exists(html0) else ""
    ok = r.returncode == 0 and 'data-composition-id="s0"' in tart and 'window.__timelines["s0"]' in tart
    lepes("jelenetek" + (" + lint" if a.lint else ""), ok, "" if ok else (r.stdout + r.stderr)[-800:])

    # 5. render (vagy helykitöltő videó)
    w, h = g["felbontas"]
    if a.render:
        r = eszkoz("render.py", ep, cwd=mappa)
        lepes("render (HyperFrames, draft)", r.returncode == 0, (r.stdout + r.stderr).strip()[-400:])
        r = eszkoz("kontaktlap.py", ep, cwd=mappa)
        lepes("pillanatkép-lap", r.returncode == 0 and os.path.exists(os.path.join(ep, "_check", "s0.jpg")))
    else:
        os.makedirs(os.path.join(ep, "render"), exist_ok=True)
        for s, szin in zip(plan["sorrend"], ("0x203040", "0x402030")):
            K.ff("-f", "lavfi", "-i", f"color=c={szin}:s={w}x{h}:r={g['fps']}:d={plan['jelenetek'][s]['duration']}",
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(ep, "render", f"{s}.mp4"))
        r = eszkoz("kontaktlap.py", ep, cwd=mappa)
        lepes("pillanatkép-lap (helykitöltőn)", r.returncode == 0 and os.path.exists(os.path.join(ep, "_check", "s0.jpg")),
              "" if r.returncode == 0 else r.stderr[-400:])

    # 6. keverés + átnéző fájlok
    r = eszkoz("keveres.py", ep, cwd=mappa)
    reszek = sorted(os.listdir(os.path.join(ep, "out", "reszek"))) if os.path.isdir(os.path.join(ep, "out", "reszek")) else []
    cel = g["hangero_lufs"]
    mert = [K.lufs(os.path.join(ep, "audio", f"mix_{s}.wav")) for s in plan["sorrend"]] if r.returncode == 0 else []
    ok = r.returncode == 0 and len(reszek) == 2 and all(abs(x - cel) < 1.0 for x in mert)
    lepes("keverés + átnéző fájlok", ok, ", ".join(f"{x:.1f} LUFS" for x in mert) or r.stderr[-600:])

    # 7. összefűzés + leírás
    r = eszkoz("keveres.py", ep, "--osszefuz", cwd=mappa)
    vegleges = os.path.join(ep, "out", "vegleges.mp4")
    if r.returncode == 0 and os.path.exists(vegleges):
        elvart = sum(plan["jelenetek"][s]["duration"] for s in plan["sorrend"])
        d = K.hossz(vegleges)
        lepes("összefűzés", abs(d - elvart) < 0.3, f"{d:.2f} mp (várt {elvart}), {K.lufs(vegleges):.1f} LUFS")
    else:
        lepes("összefűzés", False, r.stderr[-600:])
    r = eszkoz("leiras.py", ep, cwd=mappa)
    lepes("leírás", r.returncode == 0 and "Fejezetek:" in r.stdout)
    return osszegzes(mappa, a.megtart)


def osszegzes(mappa: str, megtart: bool) -> int:
    hibak = [n for n, ok, _ in EREDMENY if not ok]
    print("\n" + ("MINDEN RENDBEN" if not hibak else f"{len(hibak)} HIBA: " + "; ".join(hibak)))
    if megtart or hibak:
        print(f"a próbamappa: {mappa}")
    else:
        shutil.rmtree(mappa, ignore_errors=True)
    return 1 if hibak else 0


if __name__ == "__main__":
    sys.exit(main())
