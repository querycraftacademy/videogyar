# -*- coding: utf-8 -*-
"""Időterv: a kész ütemhangokból jelenethang (audio/sX.wav) és audio/plan.json.

A hang megy elöl, a kép igazodik hozzá: a jelenetek hossza és minden képi esemény időpontja INNEN jön.

    python terv.py <epizód> [--lead 0.9] [--gap 0.35] [--tail 1.0]

Bemenet: <epizód>/szoveg.json és <epizód>/audio/utemek/sX_NN.wav (48 kHz, sztereó; a narracio.py írja).
Kimenet:
  audio/sX.wav   – a jelenet teljes hangja: elején `lead` csend, az ütemek `gap` szünettel, a végén csend
                   a jelenet egész másodpercre kerekített hosszáig
  audio/plan.json – {"lead", "gap", "tail", "sorrend", "jelenetek": {sX: {"audio", "duration", "beats"}}}
                   a beats elemei: {"at": kezdet a jelenet elejétől (mp), "dur", "text", "tts"}
"""
from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

LEAD, GAP, TAIL = 0.9, 0.35, 1.0


def _csend(ut: str, mp: float) -> str:
    if not os.path.exists(ut):
        K.ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{mp:.3f}", "-c:a", "pcm_s16le", ut)
    return ut


def epit(epizod: str, lead: float = LEAD, gap: float = GAP, tail: float = TAIL) -> dict:
    sz = K.szoveg(epizod)
    aud = os.path.join(epizod, "audio")
    utemek = os.path.join(aud, "utemek")
    csend_lead = _csend(os.path.join(aud, f"_csend_{int(lead * 1000)}.wav"), lead)
    csend_gap = _csend(os.path.join(aud, f"_csend_{int(gap * 1000)}.wav"), gap)
    jelenetek, sorrend = {}, []
    for j in sz["jelenetek"]:
        sid = j["id"]
        sorrend.append(sid)
        beats, reszek, t = [], [csend_lead], lead
        for i, u in enumerate(j["utemek"]):
            wav = os.path.join(utemek, f"{sid}_{i:02d}.wav")
            if not os.path.exists(wav):
                sys.exit(f"HIBA: hiányzik az ütem hangja: {wav} (futtasd a narracio.py-t)")
            d = K.hossz(wav)
            txt = os.path.splitext(wav)[0] + ".txt"
            tts = open(txt, encoding="utf-8").read() if os.path.exists(txt) else ""
            beats.append({"at": round(t, 3), "dur": round(d, 3), "text": K.utem_mondat(u), "tts": tts})
            if i:
                reszek.append(csend_gap)
            reszek.append(wav)
            t += d + gap
        hang = t - gap - lead if beats else 0.0
        hossz = int(math.ceil(lead + hang + tail))
        lista = os.path.join(aud, f"_{sid}_lista.txt")
        with open(lista, "w", encoding="utf-8") as f:
            for r in reszek:
                f.write("file '" + os.path.abspath(r).replace("\\", "/").replace("'", "'\\''") + "'\n")
        K.ff("-f", "concat", "-safe", "0", "-i", lista, "-af", "apad", "-t", str(hossz),
             "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(aud, f"{sid}.wav"))
        os.remove(lista)
        jelenetek[sid] = {"audio": round(hang, 3), "duration": hossz, "beats": beats}
    plan = {"lead": lead, "gap": gap, "tail": tail, "sorrend": sorrend, "jelenetek": jelenetek}
    K.json_ir(os.path.join(aud, "plan.json"), plan)
    return plan


def kiir(plan: dict) -> None:
    ossz = 0
    for sid in plan["sorrend"]:
        p = plan["jelenetek"][sid]
        ossz += p["duration"]
        print(f"  {sid}: {len(p['beats'])} ütem, hang {p['audio']:.2f} mp, jelenet {p['duration']} mp")
    print(f"  összesen {ossz} mp ({K.ido(ossz)})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Időterv és jelenethangok a kész ütemhangokból")
    ap.add_argument("epizod")
    ap.add_argument("--lead", type=float, default=LEAD)
    ap.add_argument("--gap", type=float, default=GAP)
    ap.add_argument("--tail", type=float, default=TAIL)
    a = ap.parse_args(argv)
    kiir(epit(a.epizod, a.lead, a.gap, a.tail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
