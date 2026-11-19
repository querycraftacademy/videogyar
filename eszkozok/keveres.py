# -*- coding: utf-8 -*-
"""Keverés jelenetenként + átnéző fájlok, és (csak jóváhagyás után) a végleges összefűzés.

    python keveres.py <epizód> [s0 s2 …] [--zene fajl.mp3]
    python keveres.py <epizód> --osszefuz [--intro intro.mp4] [--outro outro.mp4]

Jelenetenként (audio/mix_sX.wav):
  - narráció: audio/sX.wav (a terv.py írja; a lead csend már benne van, a hossza = a jelenet hossza)
  - háttérzene: FOLYTONOS – minden jelenet onnan folytatja, ahol az előző abbahagyta; a narráció alatt
    lehalkul (oldalláncos kompresszor); az utolsó jelenet végén kiúszik
  - hangeffektek (opcionális): jelenetek/sX/sfx.json → [[idő_mp, "fajl.wav", hangerő_dB], …]
  - statikus erősítés a gyar.json "hangero_lufs" célértékére (alapból −14), határolóval
Ha van render/sX.mp4, elkészül az átnéző fájl is: out/reszek/NN_sX_<cím>.mp4.

Összefűzés: a jelenetvideók és a keverések külön fűződnek (a hang veszteségmentesen), és egyszer
kódolódnak. Intró/outró esetén minden egységes formátumra kódolódik. Kimenet: out/vegleges.mp4.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

ZENE_KIT = (".mp3", ".wav", ".m4a", ".ogg", ".flac")


def zene_fajl(ep: str, g: dict, kert: str | None) -> str | None:
    if kert:
        return kert
    z = g.get("zene", {})
    root = K.munkamappa(ep)
    if z.get("fajl"):
        f = z["fajl"] if os.path.isabs(z["fajl"]) else os.path.join(root, z["fajl"])
        return f if os.path.exists(f) else None
    mappa = os.path.join(root, z.get("mappa", "kozos/zene"))
    lista = sorted(f for f in glob.glob(os.path.join(mappa, "*")) if f.lower().endswith(ZENE_KIT))
    return lista[0] if lista else None


def kezdetek(p: dict) -> dict:
    t, ki = 0.0, {}
    for sid in p["sorrend"]:
        ki[sid] = t
        t += p["jelenetek"][sid]["duration"]
    return ki


def kever(ep: str, sid: str, p: dict, g: dict, zene: str | None) -> str:
    aud = os.path.join(ep, "audio")
    d = p["jelenetek"][sid]["duration"]
    utolso = sid == p["sorrend"][-1]
    narr = os.path.join(aud, f"{sid}.wav")
    if not os.path.exists(narr):
        sys.exit(f"HIBA: hiányzik a jelenethang: {narr} (narracio.py / terv.py)")
    be = ["-i", narr]
    reszek = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:{d},asplit=2[nk][nv]"]
    keveredo = ["[nv]"]
    k = 1
    if zene:
        be += ["-stream_loop", "-1", "-ss", f"{kezdetek(p)[sid]:.3f}", "-i", zene]
        hangero = float(g.get("zene", {}).get("hangero", 0.11))
        kius = f",afade=t=out:st={max(0, d - 1.5)}:d=1.5" if utolso else ""
        reszek.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{d},asetpts=N/SR/TB,"
                      f"volume={hangero}{kius}[m]")
        reszek.append("[m][nk]sidechaincompress=threshold=0.02:ratio=10:attack=60:release=500[md]")
        keveredo.append("[md]")
        k += 1
    else:
        reszek.append("[nk]anullsink")
    sfx_ut = os.path.join(ep, "jelenetek", sid, "sfx.json")
    for n, (t, fajl, db) in enumerate(K.json_olvas(sfx_ut, []) or []):
        f = fajl if os.path.isabs(fajl) else os.path.join(os.path.dirname(sfx_ut), fajl)
        be += ["-i", f]
        ms = int(round(float(t) * 1000))
        reszek.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB,"
                      f"adelay={ms}|{ms},apad,atrim=0:{d}[x{n}]")
        keveredo.append(f"[x{n}]")
        k += 1
    if len(keveredo) == 1:
        reszek.append(f"{keveredo[0]}anull[ki]")
    else:
        reszek.append("".join(keveredo) + f"amix=inputs={len(keveredo)}:duration=first:normalize=0[ki]")
    nyers = os.path.join(aud, f"_mix_{sid}_nyers.wav")
    K.ff(*be, "-filter_complex", ";".join(reszek), "-map", "[ki]", "-t", str(d), "-c:a", "pcm_s24le", nyers)
    cel = float(g.get("hangero_lufs", -14))
    mert = K.lufs(nyers)
    erosites = 0.0 if mert == float("-inf") else cel - mert
    ki = os.path.join(aud, f"mix_{sid}.wav")
    K.ff("-i", nyers, "-af", f"volume={erosites:.2f}dB,alimiter=limit=0.95:level=false", "-c:a", "pcm_s24le", ki)
    os.remove(nyers)
    return ki


def atnezo(ep: str, sid: str, n: int, cim: str, mix: str) -> str | None:
    video = os.path.join(ep, "render", f"{sid}.mp4")
    if not os.path.exists(video):
        return None
    ki = os.path.join(ep, "out", "reszek", f"{n:02d}_{sid}_{K.rovid_nev(cim)}.mp4")
    os.makedirs(os.path.dirname(ki), exist_ok=True)
    K.ff("-i", video, "-i", mix, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", ki)
    return ki


def _lista(utak: list[str], ut: str) -> str:
    with open(ut, "w", encoding="utf-8") as f:
        for u in utak:
            f.write("file '" + os.path.abspath(u).replace("\\", "/").replace("'", "'\\''") + "'\n")
    return ut


def osszefuz(ep: str, p: dict, g: dict, intro: str | None, outro: str | None) -> str:
    videok = [os.path.join(ep, "render", f"{s}.mp4") for s in p["sorrend"]]
    mixek = [os.path.join(ep, "audio", f"mix_{s}.wav") for s in p["sorrend"]]
    hiany = [u for u in videok + mixek if not os.path.exists(u)]
    if hiany:
        sys.exit("HIBA: hiányzik:\n  " + "\n  ".join(hiany) + "\n(render.py és keveres.py előbb)")
    ki_mappa = os.path.join(ep, "out")
    os.makedirs(ki_mappa, exist_ok=True)
    tv = os.path.join(ki_mappa, "_fo_video.mp4")
    ta = os.path.join(ki_mappa, "_fo_hang.wav")
    K.ff("-f", "concat", "-safe", "0", "-i", _lista(videok, tv + ".txt"), "-c", "copy", tv)
    K.ff("-f", "concat", "-safe", "0", "-i", _lista(mixek, ta + ".txt"), "-c", "copy", ta)
    ki = os.path.join(ki_mappa, "vegleges.mp4")
    if not intro and not outro:
        K.ff("-i", tv, "-i", ta, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", "-movflags", "+faststart", ki)
    else:
        w, h = g["felbontas"]
        fps = g["fps"]
        be, szuro, n = [], [], 0
        for x in (intro, "FO", outro):
            if x is None:
                continue
            if x == "FO":
                be += ["-i", tv, "-i", ta]
                v, a = f"{n}:v", f"{n + 1}:a"
                n += 2
            else:
                be += ["-i", x]
                v = f"{n}:v"
                if K.van_hangja(x):
                    a = f"{n}:a"
                    n += 1
                else:
                    be += ["-f", "lavfi", "-t", f"{K.hossz(x):.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
                    a = f"{n + 1}:a"
                    n += 2
            i = len(szuro)
            szuro.append(f"[{v}]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                         f"fps={fps},format=yuv420p,setsar=1[v{i}];[{a}]aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
        db = len(szuro)
        szuro.append("".join(f"[v{i}][a{i}]" for i in range(db)) + f"concat=n={db}:v=1:a=1[v][a]")
        K.ff(*be, "-filter_complex", ";".join(szuro), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
             "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", ki)
    for f in (tv, ta, tv + ".txt", ta + ".txt"):
        if os.path.exists(f):
            os.remove(f)
    return ki


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Keverés, átnéző fájlok, összefűzés")
    ap.add_argument("epizod")
    ap.add_argument("jelenetek", nargs="*")
    ap.add_argument("--zene")
    ap.add_argument("--osszefuz", action="store_true", help="CSAK a felhasználó jóváhagyása után")
    ap.add_argument("--intro")
    ap.add_argument("--outro")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    g = K.gyar(ep)
    p = K.terv(ep)
    if a.osszefuz:
        ki = osszefuz(ep, p, g, a.intro, a.outro)
        print(f"kész: {ki}  ({K.ido(K.hossz(ki))}, {K.lufs(ki):.1f} LUFS)")
        return 0
    zene = zene_fajl(ep, g, a.zene)
    print(f"zene: {zene or 'nincs (csak narráció)'}")
    cimek = {j["id"]: j.get("cim", j["id"]) for j in K.szoveg(ep)["jelenetek"]}
    for n, sid in enumerate(p["sorrend"]):
        if a.jelenetek and sid not in a.jelenetek:
            continue
        mix = kever(ep, sid, p, g, zene)
        atn = atnezo(ep, sid, n, cimek.get(sid, sid), mix)
        print(f"  {sid}: {os.path.basename(mix)} {K.lufs(mix):.1f} LUFS" + (f" → {atn}" if atn else " (nincs render, csak hang)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
