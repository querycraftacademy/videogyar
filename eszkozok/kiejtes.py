# -*- coding: utf-8 -*-
"""Kiejtési szótár + őrszem az ottfelejtett angol (vagy más idegen) szavakra.

Miért kell: a magyar hangmotor az angol szavakat magyarul olvassa ki ("Claude" → "kla-u-de"). Ezért a
narráció minden ütemét a szótár kiejtés szerint átírja ("klód"), és utána ez a modul megbuktatja a
szöveget, ha maradt benne gyanús szó. A javítás mindig a szótár bővítése, nem az őrszem gyengítése.

Gyanús (a csere UTÁN):
  - aláhúzásos szó                       → Sales_Total
  - legalább két betűs, csupa nagybetűs   → DAX, PDF
  - mondat KÖZBEN nagybetűvel kezdődő     → Excel, Python (magyarban a mondatközi nagybetű tulajdonnév,
                                            és egy technikai videóban az többnyire idegen szó)
A szótár "_engedett" listája kivétel (pl. magyar személynevek). Toldalékos alakot ("Pythonban") vegyél
fel külön, vagy írd kötőjellel ("Python-ban" → a szótár a "Python" részt cseréli).

    python kiejtes.py <epizód-mappa | szoveg.json> [--szotar kozos/kiejtes.json] [--szamok]
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

SZO = re.compile(r"[^\W\d][\w'’-]*")
MONDATVEG = re.compile(r"[.!?…:]\s*$")


def betolt(ut: str | None) -> tuple[dict, set]:
    """(szótár, engedett szavak) – a "_" kezdetű kulcsok nem szótárelemek."""
    if not ut or not os.path.exists(ut):
        return {}, set()
    d = K.json_olvas(ut, {})
    szotar = {k: v for k, v in d.items() if not k.startswith("_")}
    return szotar, set(d.get("_engedett", []))


def alkalmaz(szoveg: str, szotar: dict) -> str:
    """A szótár cseréi, a leghosszabb kulccsal kezdve, egész szóra, kis- és nagybetűtől függetlenül."""
    for kulcs in sorted(szotar, key=len, reverse=True):
        minta = re.compile(r"(?<!\w)" + re.escape(kulcs) + r"(?!\w)", re.IGNORECASE)
        szoveg = minta.sub(lambda _m, v=szotar[kulcs]: v, szoveg)
    return szoveg


def gyanus(szoveg: str, engedett: set | None = None) -> list[tuple[str, str]]:
    """A gyanús szavak listája: (szó, ok)."""
    engedett = engedett or set()
    talalat = []
    elozo_vege = 0
    for m in SZO.finditer(szoveg):
        szo = m.group(0).strip("-'’")
        if not szo or szo in engedett:
            elozo_vege = m.end()
            continue
        elotte = szoveg[:m.start()]
        mondat_eleje = not elotte.strip() or bool(MONDATVEG.search(elotte)) or elotte.rstrip().endswith(("„", '"', "(", "–"))
        betuk = [c for c in szo if c.isalpha()]
        if "_" in szo:
            talalat.append((szo, "aláhúzás"))
        elif len(betuk) >= 2 and all(c.isupper() for c in betuk):
            talalat.append((szo, "csupa nagybetű"))
        elif szo[0].isupper() and not mondat_eleje:
            talalat.append((szo, "nagybetű mondat közben"))
        elozo_vege = m.end()
    return talalat


SZAMRESZ = ("egy", "kettő", "két", "három", "négy", "öt", "hat", "hét", "nyolc", "kilenc", "tíz", "tizen",
            "húsz", "huszon", "harminc", "negyven", "ötven", "hatvan", "hetven", "nyolcvan", "kilencven",
            "száz", "ezer", "millió", "milliárd")


def szamnevek(szoveg: str) -> list[str]:
    """Hosszú összetett számnevek (figyelmeztetés: ezeket sok hangmotor összemossa)."""
    ki = []
    for m in SZO.finditer(szoveg.lower()):
        szo = m.group(0)
        darab = sum(szo.count(r) for r in SZAMRESZ)
        if len(szo) >= 11 and darab >= 2:
            ki.append(szo)
    return ki


def szamjegyek(szoveg: str) -> list[str]:
    return re.findall(r"\d[\d.,:/%]*", szoveg)


def utemek(ut: str):
    """(jelenet-id, ütemindex, mondat) hármasok egy epizódból vagy szoveg.json-ból."""
    f = ut if ut.endswith(".json") else os.path.join(ut, "szoveg.json")
    sz = K.json_olvas(f)
    if not sz:
        sys.exit(f"HIBA: nem találom: {f}")
    for j in sz["jelenetek"]:
        for i, u in enumerate(j["utemek"]):
            yield j["id"], i, K.utem_mondat(u)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiejtési szótár és gyanús szavak ellenőrzése")
    ap.add_argument("ut", help="epizód-mappa vagy szoveg.json")
    ap.add_argument("--szotar", help="kiejtési szótár (alapból <munkamappa>/kozos/kiejtes.json)")
    ap.add_argument("--szamok", action="store_true", help="hosszú számnevek és számjegyek listája is")
    a = ap.parse_args(argv)
    szotar_ut = a.szotar or os.path.join(K.munkamappa(a.ut if os.path.isdir(a.ut) else os.path.dirname(a.ut)),
                                         "kozos", "kiejtes.json")
    szotar, engedett = betolt(szotar_ut)
    hibas = 0
    for sid, i, mondat in utemek(a.ut):
        uj = alkalmaz(mondat, szotar)
        gy = gyanus(uj, engedett)
        if gy:
            hibas += 1
            print(f"{sid}/{i:02d}  GYANÚS: " + ", ".join(f"{s} ({ok})" for s, ok in gy))
            print(f"        {uj}")
        if a.szamok:
            for s in szamnevek(uj):
                print(f"{sid}/{i:02d}  számnév: {s} (kerekítsd, vagy hallgasd meg)")
            for s in szamjegyek(uj):
                print(f"{sid}/{i:02d}  számjegy: {s} (írd ki betűvel, ahogy kimondjuk)")
    if hibas:
        print(f"\n{hibas} ütemben maradt gyanús szó. Bővítsd a szótárt: {szotar_ut}")
        return 1
    print("kiejtés: rendben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
