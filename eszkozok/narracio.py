# -*- coding: utf-8 -*-
"""Narráció: szoveg.json → kiejtés-ellenőrzés → hang ütemenként (gyorsítótárral) → időterv → hangkapuk.

    python narracio.py <epizód>                 # a hiányzó vagy megváltozott ütemek
    python narracio.py <epizód> --csak s1 s2    # csak ezek a jelenetek (az időterv mindig teljes)
    python narracio.py <epizód> --ujra          # minden ütem újra
    python narracio.py <epizód> --replan        # hangmotor nélkül: csak időterv és kapuk
    python narracio.py <epizód> --motor tts_proba

A hangmotort a gyar.json "tts.modul" mezője adja (pl. "tts_piper" → eszkozok/tts_piper.py). Az illesztő
szerződése a videogyar-hang skillben van: szintetizal(szoveg, kimenet_wav, beallitas), opcionálisan
betolt(beallitas) és lezar().

Gyorsítótár: minden ütemhang mellett egy .txt őrzi, milyen (kiejtés szerint átírt) szövegből készült.
Ha a szöveg nem változott, a hang nem készül újra, így egy mondat javítása egy ütem újragenerálása.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import os
import sys

ITT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ITT)
import _kozos as K  # noqa: E402
import hangkapu  # noqa: E402
import kiejtes  # noqa: E402
import terv  # noqa: E402
from gpu_zar import gpu_zar  # noqa: E402

TUL_GYORS = 0.035   # mp/karakter alatt gyanúsan rövid (szavak maradhattak ki)
TUL_LASSU = 0.16    # mp/karakter fölött gyanúsan hosszú (nyújtott vagy zagyva hang)


def motor_betoltes(nev: str, munkamappa: str):
    for ut in (os.path.join(munkamappa, "eszkozok"), ITT):
        if ut not in sys.path:
            sys.path.insert(0, ut)
    try:
        return importlib.import_module(nev)
    except ImportError as e:
        sys.exit(f"HIBA: nem tudom betölteni a hangmotor illesztőjét: {nev} ({e}).\n"
                 f"Írd meg: eszkozok/{nev}.py (lásd videogyar-hang, 3. pont), vagy javítsd a gyar.json tts.modul mezőjét.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Narráció generálása és ellenőrzése")
    ap.add_argument("epizod")
    ap.add_argument("--csak", nargs="*", default=None)
    ap.add_argument("--ujra", action="store_true")
    ap.add_argument("--replan", action="store_true")
    ap.add_argument("--motor")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    g = K.gyar(ep)
    root = K.munkamappa(ep)
    szotar, engedett = kiejtes.betolt(os.path.join(root, "kozos", "kiejtes.json"))
    sz = K.szoveg(ep)
    maxk = int(g["tts"].get("max_karakter", 250))
    utemdir = os.path.join(ep, "audio", "utemek")
    os.makedirs(utemdir, exist_ok=True)

    # 1. kiejtés és hossz
    feladat, hibak = [], []
    for j in sz["jelenetek"]:
        if a.csak and j["id"] not in a.csak:
            continue
        for i, u in enumerate(j["utemek"]):
            mondat = K.utem_mondat(u)
            tts = kiejtes.alkalmaz(mondat, szotar)
            nev = f"{j['id']}/{i:02d}"
            for szo, ok in kiejtes.gyanus(tts, engedett):
                hibak.append(f"{nev}  gyanús szó: {szo} ({ok}) → vedd fel a kozos/kiejtes.json-ba")
            if len(tts) > maxk:
                hibak.append(f"{nev}  túl hosszú ütem ({len(tts)} > {maxk} karakter) → bontsd két ütemre")
            if len(mondat.split()) < 2:
                hibak.append(f"{nev}  egyszavas ütem → vond össze a szomszédjával")
            feladat.append((j["id"], i, tts))
    if hibak:
        print("\n".join(hibak))
        print("\nA szöveg nem ment át az ellenőrzésen; hang nem készült.")
        return 1

    # 2. hang ütemenként
    if not a.replan:
        kell = []
        for sid, i, tts in feladat:
            wav = os.path.join(utemdir, f"{sid}_{i:02d}.wav")
            txt = os.path.join(utemdir, f"{sid}_{i:02d}.txt")
            regi = open(txt, encoding="utf-8").read() if os.path.exists(txt) else None
            if a.ujra or not os.path.exists(wav) or regi != tts:
                kell.append((sid, i, tts, wav, txt))
        if kell:
            nev = a.motor or g["tts"]["modul"]
            motor = motor_betoltes(nev, root)
            helyi = g["tts"].get("eszkoz", "cpu") not in ("cpu", "felho")
            zar = gpu_zar(f"narráció ({nev})") if helyi else contextlib.nullcontext()
            print(f"hang: {len(kell)} ütem a(z) {nev} motorral", flush=True)
            with zar:
                if hasattr(motor, "betolt"):
                    motor.betolt(g["tts"])
                try:
                    for sid, i, tts, wav, txt in kell:
                        nyers = wav + ".nyers.wav"
                        motor.szintetizal(tts, nyers, g["tts"])
                        K.ff("-i", nyers, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav)
                        os.remove(nyers)
                        with open(txt, "w", encoding="utf-8") as f:
                            f.write(tts)
                        d = K.hossz(wav)
                        jel = ""
                        if d < TUL_GYORS * len(tts):
                            jel = "  ← GYANÚSAN RÖVID: hallgasd meg, kimaradhatott valami"
                        elif d > TUL_LASSU * len(tts) + 1.0:
                            jel = "  ← GYANÚSAN HOSSZÚ: hallgasd meg"
                        print(f"  {sid}/{i:02d}  {d:5.2f} mp  {tts[:60]}{jel}", flush=True)
                finally:
                    if hasattr(motor, "lezar"):
                        motor.lezar()
        else:
            print("hang: minden ütem naprakész (nincs mit generálni)")

    # 3. időterv
    plan = terv.epit(ep)
    terv.kiir(plan)

    # 4. hangkapuk
    utak = [os.path.join(utemdir, f"{sid}_{i:02d}.wav") for sid, i, _ in feladat]
    rossz = hangkapu.ellenoriz(utak)
    if rossz:
        print("\n".join(rossz))
        print("\nHANGKAPU MEGBUKOTT: írd át a mondatot (a kockázatos szó ne a végén álljon), "
              "töröld az ütem .wav-ját, és futtasd újra.")
        return 1
    print("hangkapuk: rendben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
