---
name: videogyar-kep
description: A videógyár képállomása — HyperFrames-jelenetek írása az időtervből (plan.json) a felhasználó stíluslapjával, újrahasznosítható jelenetelemek, képernyőfelvétel láthatatlan böngészőben, kivágás és elmosás, 3D és kameramozgás, borító. Használd, ha jelenetet kell készíteni vagy javítani, ha egy elem rossz időben jelenik meg, ha képernyőfelvétel kell egy programról vagy weboldalról, ha valamit el kell mosni a felvételen, vagy ha borítót kell rajzolni.
---

# Kép: minden jelenet egy weboldal

Nincs videószerkesztő program. Minden jelenet egy HTML-fájl (`jelenetek/sX/index.html`), az animációt
a GSAP mozgatja, és a [HyperFrames](https://github.com/heygen-com/hyperframes) képkockánként videót
készít belőle. A jelenet **az időtervhez igazodik**: a `plan.json` mondja meg, melyik ütem mikor
hangzik el, és a képi esemény ahhoz időzít.

## 1. Gyors út: jelenet.py

```
python eszkozok/jelenet.py epizodok/001_proba            # minden jelenet
python eszkozok/jelenet.py epizodok/001_proba s2         # csak egy
```

A `szoveg.json` ütemeinek `kep` mezőjéből és a `plan.json`-ból ír jelenetet, a `kozos/stilus.css`
változóival. Beépített elemtípusok:

| `tipus` | Mezők | Mit mutat |
|---|---|---|
| `cim` | `szoveg`, `alcim` | nagy cím középen |
| `felirat` | `szoveg` | rövid felirat alul |
| `kartya` | `cim`, `pontok` (lista) | kártya, a pontok egymás után beúsznak |
| `szam` | `ertek`, `egyseg`, `cimke` | nagy szám felpörgéssel |
| `kep` | `fajl`, `felirat` | kép (a jelenet mappájába másolva) |

Ez kiindulás. Ahogy a felhasználó videói gyűlnek, **a visszatérő elemeket emeld ki a
`kozos/komponensek/` mappába** (Python-függvény, ami HTML-t és GSAP-sort ad vissza), és a `jelenet.py`-t
bővítsd velük. Egy új epizód így egyre inkább kész elemekből épül.

## 2. A HyperFrames-szerződés (ha kézzel írsz vagy bővítesz)

A teljes leírás a HyperFrames saját skilljeiben van (`npx hyperframes skills`, majd `hyperframes-core`).
A legfontosabbak, amikbe az első próbálkozás biztosan belefut:

- A gyökér egy `<div>` közvetlenül a `<body>`-ban: `data-composition-id`, `data-width`, `data-height`,
  `data-duration` (a jelenet hossza a `plan.json`-ból). A gyökér mérete `width/height: 100%`, ne fix pixel.
- Időzített elem: `data-start` + `data-duration` + `class="clip"`. A láthatóság ablaka félig nyitott
  (`[start, start+duration)`): az animáció végállapota a jelenet vége **előtt** álljon be.
- **Egyetlen, megállított GSAP-idővonal:** `const tl = gsap.timeline({ paused: true })`, a végén
  `window.__timelines["<composition-id>"] = tl`.
- Ne legyen CSS-ben kezdő `transform` olyan elemen, amit a GSAP is mozgat (`fromTo`-val add meg a
  kezdőállapotot). `.clip` elemen ne animálj `visibility`-t vagy `autoAlpha`-t, a belső elemét animáld.
- Minden `<video>` és `<audio>` kapjon `id`-t; `crossorigin` ne legyen rajtuk.
- Megnevezett betűtípushoz `@font-face` kell, helyi fájllal.
- **Determinizmus:** nincs `Math.random()` mag nélkül, nincs `Date.now()`, nincs hálózati kérés render közben.
- **A jelenet csak a saját mappájából töltsön be fájlt.** A `../` útvonal nem megbízható: a képet,
  betűt, GSAP-ot másold a jelenet mappájába, vagy ágyazd be (a `jelenet.py` így csinálja).
- Render előtt: `npx hyperframes lint` (a jelenet mappájában), és ha hibát ad, azt javítsd először.
  Kétes időzítésnél: `npx hyperframes snapshot --at 1.5,4.2` és nézd meg a kockákat.

## 3. Időzítési szabályok

- Az elem az ütem kezdete után 0,1–0,3 mp-cel jelenjen meg (`at + 0.2`), ne előtte: a néző előbb
  hallja, aztán látja.
- Egy ütemre egy fő képi esemény. Ha egy mondatban három dolog van, bontsd három ütemre a szövegben.
- A jelenet utolsó másodpercében már ne induljon új elem.
- Nyugodt tempó: két esemény között legyen legalább 1 mp, hogy a néző követni tudja.

## 4. Képernyőfelvétel (ha valódi program vagy weboldal látszik)

- **Weboldal:** a Playwright láthatatlan (headless) böngészővel végigcsinálja a lépéseket, és videót vesz
  (`record_video_dir`). Így a felhasználó képernyőjén semmi nem jelenik meg, és a felvétel megismételhető.
  Fix ablakméret (pl. 1920×1080), nagyított tartalom (`device_scale_factor`), lassú, emberi tempó.
- **Asztali program:** ezt a felhasználó veszi fel (pl. OBS), vagy a rendszer saját képernyőfelvevője.
  Az AI megírhatja a lépéslistát, amit felvétel közben követ.
- A felvételt **ütemre vágd** (FFmpeg), és 16:9-es kivágással nagyítsd arra, ami fontos. A vágott klip
  a jelenet mappájába kerül, és `<video id="..." data-start=... muted>` elemként jön be.
- **Adatvédelem:** minden felvételhez legyen egy KIVÁGANDÓ és egy ELMOSANDÓ lista az epizód
  `FELADAT.md`-jében (nevek, e-mail-címek, telefonszámok, fiókadatok, mappanevek, böngésző-könyvjelzők,
  értesítések). Elmosás FFmpeg-gel:
  ```
  ffmpeg -i be.mp4 -filter_complex "[0:v]crop=400:60:1200:20,boxblur=20:2[b];[0:v][b]overlay=1200:20" -c:a copy ki.mp4
  ```
  (a `crop` szélesség:magasság:x:y, az `overlay` ugyanaz az x:y). A végén **a renderelt kockán**
  ellenőrizd, hogy tényleg nem látszik semmi (`videogyar-ellenorzes`).

## 5. 3D és kamera

- **2D kamera:** egy nagy „vászon” `<div>`, amit a GSAP mozgat és nagyít; így egy ábrán belül lehet
  ide-oda közelíteni. Lassú, puha mozgás (1,2–2 mp, `power2.inOut`).
- **3D:** Three.js a jeleneten belül; ilyenkor a gyökér `data-duration`-je kötelező, és a jelenetnek a
  HyperFrames Three.js-illesztését kell követnie (lásd a HyperFrames `hyperframes-animation` skilljét).
- A kiemelő keret (doboz egy gomb körül) mindig a **renderelt** kockán ellenőrizendő: egy elcsúszott
  keret a szomszédos elemet keretezi.

## 6. Borító

A borító is egy HTML-oldal (1280×720), ugyanazzal a stíluslappal, és egy HyperFrames-snapshot vagy egy
láthatatlan böngésző képernyőképe lesz belőle (`borito.jpg`).
- Egy fő tárgy nagyban, 2–4 szavas, nagyon jól olvasható kérdés vagy állítás, és ha a videó egy ismert
  eszközről szól, annak a neve.
- **Tévé- és telefonteszt:** készíts belőle 480×270-es és 246×138-as kicsinyítést; mindkettőn
  olvasható kell legyen a szöveg.
- Minden szám és állítás a borítón legyen igaz a videóra.

Kész az állomás, ha a próbajelenet a felhasználó stílusában, az időtervhez igazítva elkészült, és a
`lint` tiszta.
