# -*- coding: utf-8 -*-
"""YouTube-leírás: cím, bevezető, kötelező megjelölések, fejezetek a jelenetek hosszából → out/leiras.txt.

    python leiras.py <epizód> [--intro <mp>]

Forrás: szoveg.json ("cim", "leiras", a jelenetek "cim" mezője), audio/plan.json (hosszak),
gyar.json "kreditek" listája (pl. a hangmotor vagy a zene licence által kért megjelölés).
A YouTube akkor mutat fejezeteket, ha az első 0:00-nál van, legalább három van, és mindegyik ≥ 10 mp.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Leírás fejezetekkel")
    ap.add_argument("epizod")
    ap.add_argument("--intro", type=float, default=0.0, help="az elején lévő intró hossza (mp)")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    g = K.gyar(ep)
    sz = K.szoveg(ep)
    p = K.terv(ep)
    cimek = {j["id"]: j.get("cim", j["id"]) for j in sz["jelenetek"]}
    fejezetek, t = [], a.intro
    if a.intro:
        fejezetek.append((0.0, "Intró"))
    for sid in p["sorrend"]:
        fejezetek.append((t, cimek.get(sid, sid)))
        t += p["jelenetek"][sid]["duration"]
    # az azonos című, egymást követő jelenetek egy fejezetbe
    osszevont = []
    for f in fejezetek:
        if not osszevont or osszevont[-1][1] != f[1]:
            osszevont.append(f)
    sorok = [sz.get("cim", ""), "", sz.get("leiras", "")]
    if g.get("kreditek"):
        sorok += [""] + list(g["kreditek"])
    sorok += ["", "Fejezetek:"] + [f"{K.ido(t0)} {c}" for t0, c in osszevont]
    ki = os.path.join(ep, "out", "leiras.txt")
    os.makedirs(os.path.dirname(ki), exist_ok=True)
    with open(ki, "w", encoding="utf-8") as f:
        f.write("\n".join(sorok).strip() + "\n")
    print(open(ki, encoding="utf-8").read())
    hossz = [(osszevont[i + 1][0] if i + 1 < len(osszevont) else t) - osszevont[i][0] for i in range(len(osszevont))]
    if len(osszevont) < 3 or min(hossz) < 10:
        print("FIGYELEM: a YouTube így nem mutat fejezeteket (legalább 3 kell, mindegyik legalább 10 mp).")
    print(f"kiírva: {ki}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
