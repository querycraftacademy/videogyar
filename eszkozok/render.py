# -*- coding: utf-8 -*-
"""Jelenetek renderelése HyperFrames-szel: jelenetek/sX/index.html → render/sX.mp4 (néma).

    python render.py <epizód> [s0 s2 …] [--minoseg draft|looks|delivery] [--lathato]

- A sorrend a plan.json szerinti (vagy a megadott jelenetek).
- Windowson alapból láthatatlan asztalon fut (windows/rejtett_asztal.ps1), hogy semmi ne ugorjon fel;
  a gyar.json "render.rejtett": false vagy a --lathato kapcsoló kikapcsolja.
- A videókártyát a gpu_zar foglalja a futás idejére (a hanggenerálás addig vár).
- Jelenetenként napló: render/sX.log; a végén render/_kesz.txt az eredménnyel.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time

ITT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ITT)
import _kozos as K  # noqa: E402
from gpu_zar import gpu_zar  # noqa: E402

PS1 = os.path.join(ITT, "windows", "rejtett_asztal.ps1")


def egy_jelenet(mappa: str, kimenet: str, naplo: str, minoseg: str, rejtett: bool) -> int:
    npx = shutil.which("npx")
    if not npx:
        sys.exit("HIBA: nincs npx (Node.js 22+ kell, lásd videogyar-telepites).")
    if os.name == "nt" and rejtett:
        cmd = os.path.join(os.path.dirname(kimenet), f"_render_{os.path.basename(mappa)}.cmd")
        with open(cmd, "w", encoding="utf-8") as f:
            f.write("@echo off\r\nchcp 65001 >nul\r\n")
            f.write(f'cd /d "{mappa}"\r\n')
            f.write(f'call npx hyperframes render --quality {minoseg} --output "{kimenet}" > "{naplo}" 2>&1\r\n')
            f.write("exit /b %errorlevel%\r\n")
        kod = subprocess.call(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS1,
                               "-Fajl", cmd, "-Mappa", mappa])
        os.remove(cmd)
        return kod
    with open(naplo, "w", encoding="utf-8") as f:
        return subprocess.call([npx, "hyperframes", "render", "--quality", minoseg, "--output", kimenet],
                               cwd=mappa, stdout=f, stderr=subprocess.STDOUT)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="HyperFrames-render jelenetenként")
    ap.add_argument("epizod")
    ap.add_argument("jelenetek", nargs="*")
    ap.add_argument("--minoseg", choices=["draft", "looks", "delivery"])
    ap.add_argument("--lathato", action="store_true", help="ne láthatatlan asztalon fusson (Windows)")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    g = K.gyar(ep)
    p = K.terv(ep)
    minoseg = a.minoseg or g["render"].get("minoseg", "looks")
    rejtett = bool(g["render"].get("rejtett", True)) and not a.lathato
    kimappa = os.path.join(ep, "render")
    os.makedirs(kimappa, exist_ok=True)
    kesz_ut = os.path.join(kimappa, "_kesz.txt")
    if os.path.exists(kesz_ut):
        os.remove(kesz_ut)
    eredmeny = []
    with gpu_zar(f"render ({os.path.basename(ep)})"):
        for sid in (a.jelenetek or p["sorrend"]):
            mappa = os.path.join(ep, "jelenetek", sid)
            if not os.path.exists(os.path.join(mappa, "index.html")):
                eredmeny.append(f"{sid}: HIÁNYZIK az index.html (futtasd a jelenet.py-t)")
                print(eredmeny[-1])
                continue
            kimenet = os.path.join(kimappa, f"{sid}.mp4")
            naplo = os.path.join(kimappa, f"{sid}.log")
            t0 = time.time()
            print(f"  {sid}: render ({minoseg}) …", flush=True)
            kod = egy_jelenet(mappa, kimenet, naplo, minoseg, rejtett)
            mp = time.time() - t0
            if kod == 0 and os.path.exists(kimenet):
                d = K.hossz(kimenet)
                elvart = p["jelenetek"][sid]["duration"]
                jel = "" if abs(d - elvart) < 0.2 else f"  ← FIGYELEM: {elvart} mp-nek kellene lennie"
                eredmeny.append(f"{sid}: rendben, {d:.2f} mp videó, {mp:.0f} mp alatt{jel}")
            else:
                eredmeny.append(f"{sid}: HIBA (kód {kod}), napló: {naplo}")
            print("   ", eredmeny[-1], flush=True)
    with open(kesz_ut, "w", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n" + "\n".join(eredmeny) + "\n")
    return 0 if all("rendben" in s for s in eredmeny) else 1


if __name__ == "__main__":
    sys.exit(main())
