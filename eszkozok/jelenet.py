# -*- coding: utf-8 -*-
"""HyperFrames-jelenetek az időtervből: jelenetek/sX/index.html, a felhasználó stíluslapjával.

    python jelenet.py <epizód> [s0 s2 …] [--lint]

Bemenet:
  <epizód>/szoveg.json      – az ütemek "kep" mezője mondja meg, mi látszik (lásd videogyar-kep)
  <epizód>/audio/plan.json  – mikor hangzik el az ütem (ehhez időzít minden képi esemény)
  <munkamappa>/kozos/stilus.css   – a felhasználó stílusa (CSS-változók); ha nincs, semleges próbastílus
  <munkamappa>/kozos/fonts/       – betűfájlok (a jelenet mappájába másolódnak)
  <munkamappa>/kozos/vendor/gsap.min.js – ha megvan, beágyazva; ha nincs, a CDN-ről töltődik

Elemtípusok: cim, felirat, kartya, szam, kep. Ez kiindulás: a visszatérő elemeket a kozos/komponensek/
mappába érdemes kiemelni, és ezt a programot velük bővíteni.

A HyperFrames-szerződés, amit követ: a gyökér közvetlenül a <body>-ban, data-composition-id / -width /
-height / -duration; az időzített elemek data-start + data-duration + class="clip"; egyetlen megállított
GSAP-idővonal a window.__timelines["<id>"] alatt; a .clip elemet nem animálja, csak a belsejét; a kezdő
állapotot fromTo adja (nincs CSS-transform); minden fájl a jelenet saját mappájából töltődik.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kozos as K  # noqa: E402

# Semleges PRÓBAstílus, csak ha a felhasználónak még nincs stíluslapja (videogyar-stilus). Szándékosan egyszerű.
SEMLEGES = """:root {
  --hatter: #14171c; --felulet: #1f242c; --szoveg: #f4f6f8; --halvany: #9aa3ad;
  --kiemeles: #5ab0f0; --kiemeles2: #f0b45a;
  --betu-cim: system-ui, sans-serif; --betu-szoveg: system-ui, sans-serif;
  --lekerekites: 22px; --arnyek: 0 18px 50px rgba(0, 0, 0, 0.35);
}"""

ALAP = """html, body { margin: 0; background: var(--hatter); }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--hatter);
        color: var(--szoveg); font-family: var(--betu-szoveg); }
.hatter { position: absolute; inset: 0; background: var(--hatter); }
.clip { position: absolute; inset: 0; }
.kozep { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
         justify-content: center; text-align: center; padding: 0 160px; }
.cim { font-family: var(--betu-cim); font-size: 120px; font-weight: 800; line-height: 1.05; margin: 0; }
.alcim { font-size: 46px; color: var(--halvany); margin: 30px 0 0; }
.felirat-sav { position: absolute; left: 0; right: 0; bottom: 120px; display: flex; justify-content: center; }
.felirat { font-size: 64px; font-weight: 700; background: var(--felulet); padding: 24px 56px;
           border-radius: var(--lekerekites); box-shadow: var(--arnyek); border-left: 10px solid var(--kiemeles); }
.kartya { background: var(--felulet); border-radius: var(--lekerekites); box-shadow: var(--arnyek);
          padding: 64px 84px; min-width: 900px; text-align: left; }
.kartya h2 { font-family: var(--betu-cim); font-size: 72px; margin: 0 0 30px; color: var(--kiemeles); }
.pont { font-size: 54px; margin: 18px 0; display: flex; align-items: center; gap: 28px; }
.pont::before { content: ""; width: 22px; height: 22px; border-radius: 50%; background: var(--kiemeles); flex: none; }
.szamsor { display: flex; align-items: baseline; }
.szam { font-family: var(--betu-cim); font-size: 260px; font-weight: 800; color: var(--kiemeles); line-height: 1; }
.egyseg { font-size: 76px; font-weight: 700; margin-left: 24px; }
.cimke { font-size: 50px; color: var(--halvany); margin-top: 26px; }
.kep { max-width: 1500px; max-height: 760px; border-radius: var(--lekerekites); box-shadow: var(--arnyek); }
"""

BE = 0.2        # ennyivel az ütem kezdete után jelenik meg az elem
ATTUNES = 0.35  # két egymást követő elem áttűnése
GSAP_CDN = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"


def e(s) -> str:
    return html.escape(str(s), quote=True)


def elem(tipus: str, kep: dict, eid: str, t: float, dur: float, jelenet_mappa: str) -> tuple[str, list[str]]:
    """(HTML, GSAP-sorok) egy képi elemhez; t = megjelenés ideje a jelenet elejétől."""
    js = []
    sel = f"#{eid}"
    if tipus == "cim":
        h = f'<div class="kozep"><h1 class="cim">{e(kep.get("szoveg", ""))}</h1>'
        if kep.get("alcim"):
            h += f'<p class="alcim">{e(kep["alcim"])}</p>'
        h += "</div>"
        js.append(f'tl.fromTo("{sel} .cim", {{y: 50, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.7, ease: "power3.out"}}, {t:.3f});')
        if kep.get("alcim"):
            js.append(f'tl.fromTo("{sel} .alcim", {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.6, ease: "power3.out"}}, {t + 0.25:.3f});')
    elif tipus == "felirat":
        h = f'<div class="felirat-sav"><div class="felirat">{e(kep.get("szoveg", ""))}</div></div>'
        js.append(f'tl.fromTo("{sel} .felirat", {{y: 80, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.6, ease: "power3.out"}}, {t:.3f});')
    elif tipus == "kartya":
        pontok = kep.get("pontok", [])
        h = '<div class="kozep"><div class="kartya">'
        if kep.get("cim"):
            h += f'<h2>{e(kep["cim"])}</h2>'
        h += "".join(f'<div class="pont" id="{eid}-p{k}">{e(p)}</div>' for k, p in enumerate(pontok))
        h += "</div></div>"
        js.append(f'tl.fromTo("{sel} .kartya", {{y: 60, opacity: 0, scale: 0.97}}, {{y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "power3.out"}}, {t:.3f});')
        lep = min(0.8, max(0.35, (dur - 0.8) / max(1, len(pontok))))
        for k in range(len(pontok)):
            js.append(f'tl.fromTo("#{eid}-p{k}", {{x: -40, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.5, ease: "power2.out"}}, {t + 0.45 + k * lep:.3f});')
    elif tipus == "szam":
        ertek = kep.get("ertek", 0)
        egesz = isinstance(ertek, int) or (isinstance(ertek, float) and ertek.is_integer())
        h = (f'<div class="kozep"><div class="szamsor"><span class="szam" id="{eid}-n">{e(ertek)}</span>'
             f'<span class="egyseg">{e(kep.get("egyseg", ""))}</span></div>')
        if kep.get("cimke"):
            h += f'<div class="cimke">{e(kep["cimke"])}</div>'
        h += "</div>"
        js.append(f'tl.fromTo("{sel} .szamsor", {{scale: 0.9, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.6)"}}, {t:.3f});')
        if egesz and int(ertek) > 1:
            js.append(f'tl.fromTo("#{eid}-n", {{textContent: 0}}, {{textContent: {int(ertek)}, duration: 1.2, ease: "power2.out", snap: {{textContent: 1}}}}, {t:.3f});')
        if kep.get("cimke"):
            js.append(f'tl.fromTo("{sel} .cimke", {{y: 24, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.5, ease: "power2.out"}}, {t + 0.5:.3f});')
    elif tipus == "kep":
        forras = kep.get("fajl", "")
        nev = os.path.basename(forras)
        if forras and os.path.exists(forras):
            os.makedirs(os.path.join(jelenet_mappa, "kepek"), exist_ok=True)
            shutil.copy2(forras, os.path.join(jelenet_mappa, "kepek", nev))
        else:
            print(f"  FIGYELEM: nincs meg a kép: {forras}")
        h = f'<div class="kozep"><img class="kep" src="kepek/{e(nev)}" alt=""></div>'
        js.append(f'tl.fromTo("{sel} .kep", {{scale: 1.04, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.8, ease: "power2.out"}}, {t:.3f});')
        if kep.get("felirat"):
            h += f'<div class="felirat-sav"><div class="felirat">{e(kep["felirat"])}</div></div>'
            js.append(f'tl.fromTo("{sel} .felirat", {{y: 80, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.6, ease: "power3.out"}}, {t + 0.4:.3f});')
    else:
        raise SystemExit(f"HIBA: ismeretlen képtípus: {tipus} (cim, felirat, kartya, szam, kep)")
    return h, js


def jelenet_html(sid: str, p: dict, j: dict, w: int, hgt: int, css: str, gsap: str, mappa: str) -> str:
    d = p["duration"]
    vis = []
    for b, u in zip(p["beats"], j["utemek"]):
        if isinstance(u, dict) and u.get("kep"):
            vis.append((b, u["kep"]))
    tartalom, js = [], []
    for n, (b, kep) in enumerate(vis):
        eid = f"{sid}-e{n}"
        t_be = 0.3 if n == 0 else b["at"] + BE
        start = 0.0 if n == 0 else b["at"]
        kov = vis[n + 1][0]["at"] + BE if n + 1 < len(vis) else None
        vege = min(d, kov + ATTUNES) if kov is not None else d
        h, sorok = elem(kep.get("tipus", "felirat"), kep, eid, t_be, (kov or d) - t_be, mappa)
        tartalom.append(f'<section id="{eid}" class="clip" data-start="{start:.3f}" data-duration="{vege - start:.3f}" '
                        f'data-track-index="1"><div class="belso" id="{eid}-b">{h}</div></section>')
        js += sorok
        if kov is not None:  # kiúszik, amikor a következő bejön (a .clip-et nem animáljuk, csak a belsejét)
            js.append(f'tl.to("#{eid}-b", {{opacity: 0, duration: {ATTUNES}, ease: "power1.inOut"}}, {kov:.3f});')
            js.append(f'tl.set("#{eid}-b", {{opacity: 0}}, {kov + ATTUNES:.3f});')
    return f"""<!doctype html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width={w}, height={hgt}">
<title>{e(sid)}</title>
{gsap}
<style>
{css}
{ALAP}
</style>
</head>
<body>
<div id="root" data-composition-id="{sid}" data-start="0" data-width="{w}" data-height="{hgt}" data-duration="{d}">
<div class="hatter"></div>
{chr(10).join(tartalom)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["{sid}"] = tl;
</script>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="HyperFrames-jelenetek írása az időtervből")
    ap.add_argument("epizod")
    ap.add_argument("jelenetek", nargs="*")
    ap.add_argument("--lint", action="store_true", help="utána npx hyperframes lint minden jeleneten")
    a = ap.parse_args(argv)
    ep = os.path.abspath(a.epizod)
    root = K.munkamappa(ep)
    g = K.gyar(ep)
    w, hgt = g["felbontas"]
    sz = K.szoveg(ep)
    p = K.terv(ep)
    stilus = os.path.join(root, "kozos", "stilus.css")
    if os.path.exists(stilus):
        css = open(stilus, encoding="utf-8").read()
    else:
        css = SEMLEGES
        print("FIGYELEM: nincs kozos/stilus.css, semleges próbastílussal dolgozom (lásd videogyar-stilus).")
    gsap_ut = os.path.join(root, "kozos", "vendor", "gsap.min.js")
    if os.path.exists(gsap_ut):
        gsap = "<script>\n" + open(gsap_ut, encoding="utf-8").read() + "\n</script>"
    else:
        gsap = f'<script src="{GSAP_CDN}"></script>'
        print("FIGYELEM: nincs kozos/vendor/gsap.min.js, a GSAP a CDN-ről töltődik (internet kell a renderhez).")
    fonts = os.path.join(root, "kozos", "fonts")
    jelek = {j["id"]: j for j in sz["jelenetek"]}
    kesz = []
    for sid in (a.jelenetek or p["sorrend"]):
        if sid not in p["jelenetek"] or sid not in jelek:
            print(f"  kihagyva: {sid} (nincs az időtervben vagy a szövegben)")
            continue
        mappa = os.path.join(ep, "jelenetek", sid)
        os.makedirs(mappa, exist_ok=True)
        if os.path.isdir(fonts):
            shutil.copytree(fonts, os.path.join(mappa, "fonts"), dirs_exist_ok=True)
        with open(os.path.join(mappa, "index.html"), "w", encoding="utf-8") as f:
            f.write(jelenet_html(sid, p["jelenetek"][sid], jelek[sid], w, hgt, css, gsap, mappa))
        kesz.append(mappa)
        print(f"  {sid}: {p['jelenetek'][sid]['duration']} mp → {os.path.join(mappa, 'index.html')}")
    if a.lint:
        npx = shutil.which("npx")
        if not npx:
            sys.exit("HIBA: nincs npx (Node.js), a lint nem futtatható.")
        hibas = 0
        for mappa in kesz:
            r = subprocess.run([npx, "hyperframes", "lint", "--json"], cwd=mappa, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            try:
                eredm = json.loads(r.stdout[r.stdout.index("{"):])
                hibak = [x for x in eredm.get("findings", []) if x.get("severity") == "error"]
            except ValueError:
                hibak = [] if r.returncode == 0 else [{"message": (r.stderr or r.stdout)[-500:]}]
            if hibak:
                hibas += 1
                print(f"  lint HIBA ({os.path.basename(mappa)}):")
                for x in hibak:
                    print("    ", x.get("code", ""), x.get("message", ""))
            else:
                print(f"  lint rendben: {os.path.basename(mappa)}")
        return 1 if hibas else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
