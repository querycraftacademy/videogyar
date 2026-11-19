# -*- coding: utf-8 -*-
"""Pillanatkép-lap jelenetenként: minden ütemből egy kocka + a jelenet utolsó másodperce, az ütem szövegével.

    python kontaktlap.py <epizód> [s0 s2 …] [--f 0.85] [--video render|reszek]

A kockát az ütem `f` arányánál veszi (alapból 0,85: addigra minden kint van, ami az ütemhez tartozik).
Kimenet: <epizód>/_check/sX.jpg. Nézd meg, mielőtt a felhasználónak átnézésre adod.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

BETUK = ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"]


def betu(meret: int):
    from PIL import ImageFont
    for b in BETUK:
        try:
            return ImageFont.truetype(b, meret)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=meret)
    except TypeError:
        return ImageFont.load_default()


def kocka(video: str, t: float, ki: str, szel: int = 480) -> bool:
    r = subprocess.run([K.ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                        "-vf", f"scale={szel}:-2", ki], capture_output=True)
    return r.returncode == 0 and os.path.exists(ki)


def lap(ep: str, sid: str, p: dict, f: float, video: str) -> str:
    from PIL import Image, ImageDraw
    j = p["jelenetek"][sid]
    idok = [(b["at"] + f * b["dur"], b["text"]) for b in j["beats"]]
    idok.append((max(0.0, j["duration"] - 0.5), "a jelenet vége"))
    szel, oszlop = 480, 3
    kepek = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, (t, szoveg) in enumerate(idok):
            ut = os.path.join(tmp, f"{n}.png")
            if kocka(video, t, ut, szel):
                kepek.append((Image.open(ut).convert("RGB").copy(), t, szoveg))
    if not kepek:
        sys.exit(f"HIBA: nem sikerült kockát venni: {video}")
    mag = kepek[0][0].height
    felirat = 64
    sorok = (len(kepek) + oszlop - 1) // oszlop
    vaszon = Image.new("RGB", (oszlop * (szel + 10) + 10, sorok * (mag + felirat + 10) + 10), (24, 24, 28))
    rajz = ImageDraw.Draw(vaszon)
    b1, b2 = betu(18), betu(15)
    for n, (kep, t, szoveg) in enumerate(kepek):
        x = 10 + (n % oszlop) * (szel + 10)
        y = 10 + (n // oszlop) * (mag + felirat + 10)
        vaszon.paste(kep, (x, y))
        rajz.text((x, y + mag + 4), f"{sid}  {t:5.2f} mp", fill=(120, 200, 255), font=b1)
        rov = szoveg if len(szoveg) <= 58 else szoveg[:56] + "…"
        rajz.text((x, y + mag + 28), rov, fill=(220, 220, 220), font=b2)
    ki = os.path.join(ep, "_check", f"{sid}.jpg")
    os.makedirs(os.path.dirname(ki), exist_ok=True)
    vaszon.save(ki, quality=88)
    return ki


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pillanatkép-lap a renderelt jelenetekből")
    ap.add_argument("epizod")
    ap.add_argument("jelenetek", nargs="*")
    ap.add_argument("--f", type=float, default=0.85)
    ap.add_argument("--video", choices=["render", "reszek"], default="render")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    p = K.terv(ep)
    for sid in (a.jelenetek or p["sorrend"]):
        if a.video == "render":
            video = os.path.join(ep, "render", f"{sid}.mp4")
        else:
            talalat = glob.glob(os.path.join(ep, "out", "reszek", f"*_{sid}_*.mp4"))
            video = talalat[0] if talalat else ""
        if not video or not os.path.exists(video):
            print(f"  {sid}: nincs videó ({a.video}), kihagyva")
            continue
        print(f"  {sid}: {lap(ep, sid, p, a.f, video)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
