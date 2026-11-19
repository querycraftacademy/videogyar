---
name: videogyar-render
description: A videógyár renderállomása — a HyperFrames-jelenetekből néma MP4 jelenetenként (render.py), minőségi fokozatok, videókártya vagy processzor, a felhasználó képernyőjének zavarása nélkül (Windowson láthatatlan asztal), hosszú render háttérben, a GPU megosztása a hangmotorral. Használd, ha jelenetet kell renderelni, ha a render elszáll vagy lassú, ha render közben ablakok ugranak fel, vagy ha a render és a hanggenerálás ütközik.
---

# Render: jelenetből videó, észrevétlenül

## 1. Parancs

```
python eszkozok/render.py epizodok/001_proba                  # minden jelenet a plan.json sorrendjében
python eszkozok/render.py epizodok/001_proba s2 s3            # csak ezek
python eszkozok/render.py epizodok/001_proba --minoseg draft  # gyors próba
```

Jelenetenként ezt futtatja a jelenet mappájában:
`npx hyperframes render --quality <minőség> --output ../../render/sX.mp4`

Az eredmény: `render/sX.mp4` (néma), és a végén `render/_kesz.txt` (mikor, mi sikerült, mi nem).
A hang a keverésnél kerül alá.

| Minőség | Mikor |
|---|---|
| `draft` | iterálás közben, gyors |
| `looks` | az első valódi render, átnézésre (a `gyar.json` alapértéke) |
| `delivery` | a végleges változat, ha a `looks` nem elég éles |

## 2. Ne zavard a felhasználót

A HyperFrames egy fej nélküli Chrome-ot indít. **Windowson** előfordulhat, hogy közben konzolablakok
ugranak fel és elveszik a fókuszt (főleg, ha a Windows Terminal az alapértelmezett terminál). Ez hiba,
nem szépséghiba: a felhasználó közben dolgozni szeretne.

- A `render.py` Windowson alapból egy **külön, láthatatlan Windows-asztalon** futtatja a rendert
  (`eszkozok/windows/rejtett_asztal.ps1`). Minden ablak oda kerül, a felhasználó képernyőjén semmi nem
  jelenik meg. A futás idejére a konzolok gazdáját a klasszikus konzolra állítja, utána visszaállítja.
  Kikapcsolni a `gyar.json` `render.rejtett: false` értékével lehet.
- Ha egy render félbeszakad, és a terminálbeállítás nem állt vissza: `rejtett_asztal.ps1 -Vissza`.
- **macOS és Linux:** a fej nélküli Chrome nem nyit ablakot, külön teendő nincs. Linux-szerveren
  kijelző sem kell.
- A böngészős képernyőfelvétel (Playwright) ugyanígy fej nélkül fusson.

## 3. Videókártya és erőforrás

- A render Chrome-ot és FFmpeg-et használ; videókártyával gyorsabb, processzoron is megy. A
  `npx hyperframes render` összegzésének második sora megmondja, milyen módban futott.
- **Egyszerre egy nagy GPU-s munka.** A `render.py` és a `narracio.py` a `gpu_zar.py`-on keresztül
  egymásra vár. Ha a felhasználó gépén más is használja a kártyát (`gyar.json` → `gpu_megosztott`),
  előtte nézd meg a szabad memóriát.
- Kevés memóriánál: `--minoseg draft`, vagy kevesebb párhuzamos szál (`npx hyperframes render --help`).
- **Render közben ne generáld újra ugyanannak az epizódnak a jeleneteit:** a generátor felülírja az
  `index.html`-t, amit a render éppen olvas.

## 4. Hosszú render

- Több jelenetnél futtasd háttérben, naplóval, és a `render/_kesz.txt` megjelenését figyeld, ne a
  terminált.
- macOS/Linux alatt, ha az AI-eszköz a parancs végén leállítja a folyamatcsoportot:
  `HYPERFRAMES_RENDER_DETACHED=1` (lásd a HyperFrames dokumentációját).

## 5. Ha elszáll

1. `npx hyperframes doctor` — Node, FFmpeg, Chrome rendben van-e.
2. `npx hyperframes lint` a jelenet mappájában — szerkezeti hiba.
3. Egyetlen jelenet `--minoseg draft`-tal, a hibaüzenet teljes szövegével.
4. Memória: zárd be a többi Chrome-ot, vagy csökkentsd a párhuzamos szálakat.

Kész az állomás, ha a próbajelenetből MP4 lett, és a felhasználó képernyőjén közben semmi nem ugrott fel.
