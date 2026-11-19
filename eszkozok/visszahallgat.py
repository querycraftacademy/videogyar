# -*- coding: utf-8 -*-
"""Visszahallgatás Whisperrel: minden ütemhangot átír, és összeveti a szöveggel.

A hangkapuk a hang fizikáját nézik (elharapott vég, zúgás, kattanás). Azt nem látják, ha a hangmotor
félreolvas, elnyel vagy összemos egy szót. Ezt a Whisper látja.

    python visszahallgat.py <epizód> [s0 s2 …] [--modell small] [--kuszob 0.86]

Jelzi:  egyezés < küszöb  → valószínűleg félreolvasott vagy kimaradt szó
        karakter/mp kilóg → elnyújtott vagy elsietett, darabos beszéd
Kimenet: audio/whisper.json + a gyanús ütemek listája. A VÉGSŐ SZÓ A FÜLÉ: a márkaneveket és idegen
szavakat a Whisper gyakran félrehallja, pedig jól hangzanak el.

Kell hozzá: pip install faster-whisper (processzoron is fut; az első futás letölti a modellt).
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import statistics
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402


def norm(s: str) -> list[str]:
    s = unicodedata.normalize("NFC", s.lower())
    s = re.sub(r"[^\w\s]", " ", s)
    return s.split()


def egyezes(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Narráció visszahallgatása Whisperrel")
    ap.add_argument("epizod")
    ap.add_argument("jelenetek", nargs="*")
    ap.add_argument("--modell")
    ap.add_argument("--kuszob", type=float, default=0.86)
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    g = K.gyar(ep)
    p = K.terv(ep)
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("HIBA: nincs telepítve a faster-whisper (pip install faster-whisper).")
    w = g.get("whisper", {})
    modell = a.modell or w.get("modell", "small")
    eszkoz = w.get("eszkoz", "cpu")
    print(f"Whisper: {modell}, {eszkoz} …", flush=True)
    m = WhisperModel(modell, device=eszkoz, compute_type="int8" if eszkoz == "cpu" else "default")
    eredmeny, gyanus = {}, []
    cps = []
    for sid in (a.jelenetek or p["sorrend"]):
        for i, b in enumerate(p["jelenetek"][sid]["beats"]):
            wav = os.path.join(ep, "audio", "utemek", f"{sid}_{i:02d}.wav")
            szegmensek, _ = m.transcribe(wav, language=g.get("nyelv", "hu"), beam_size=5, vad_filter=False)
            hallott = " ".join(s.text.strip() for s in szegmensek).strip()
            arany = max(egyezes(b["text"], hallott), egyezes(b.get("tts") or b["text"], hallott))
            c = len(b["text"]) / max(0.1, b["dur"])
            cps.append(c)
            eredmeny[f"{sid}/{i:02d}"] = {"szoveg": b["text"], "hallott": hallott, "egyezes": round(arany, 3),
                                          "kar_per_mp": round(c, 1)}
            jel = "" if arany >= a.kuszob else "  ← GYANÚS"
            print(f"  {sid}/{i:02d}  {arany:.2f}  {hallott[:70]}{jel}", flush=True)
            if jel:
                gyanus.append(f"{sid}/{i:02d}")
    if len(cps) >= 4:
        med = statistics.median(cps)
        for k, v in eredmeny.items():
            if v["kar_per_mp"] > med * 1.45 or v["kar_per_mp"] < med * 0.6:
                v["tempo_gyanus"] = True
                if k not in gyanus:
                    gyanus.append(k)
                print(f"  {k}  tempó kilóg: {v['kar_per_mp']} kar/mp (medián {med:.1f})")
    K.json_ir(os.path.join(ep, "audio", "whisper.json"), eredmeny)
    if gyanus:
        print(f"\nHallgasd meg ezeket: {', '.join(gyanus)}  (a Whisper téved is; a fül dönt)")
        return 1
    print("\nvisszahallgatás: rendben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
