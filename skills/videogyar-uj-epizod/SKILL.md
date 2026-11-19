---
name: videogyar-uj-epizod
description: Egy új videó legyártása a már felépített videógyárral, elejétől a végéig — téma és szöveg, jóváhagyás, hang és kapuk, jelenetek, pillanatkép-lap, render, keverés, átnézés, javítási kör, összefűzés, leírás, közzététel. Használd, ha a rendszer kész (az ALLAPOT.md szerint a próbavideó megvan), és a felhasználó új videót kér: „csináljunk egy videót erről”, „új rész”, „következő epizód”.
---

# Új epizód: a gyártósor egy menetben

Előfeltétel: az `ALLAPOT.md` szerint a 0–8. állomás kész (van próbavideó). Ha nem, előbb azt fejezzétek be.

## A menet

| # | Lépés | Parancs / teendő | Megállj és kérdezz? |
|---|---|---|---|
| 1 | Új epizódmappa | másold a `sablonok/epizod/` tartalmát `epizodok/NNN_rovid_nev/`-be | |
| 2 | Cél és terv | `FELADAT.md`: kinek, mit tanul belőle, hossz, jelenetlista, KIVÁGANDÓ/ELMOSANDÓ | |
| 3 | Szöveg | `szoveg.json`: jelenetek, ütemek, `kep` mezők; a nyitás legfeljebb 15 mp, és az első mondat a lényeg | **igen: a szöveget hagyja jóvá** |
| 4 | Hang | `python eszkozok/narracio.py <epizód>` → kapuk; `visszahallgat.py` | ha kapu bukik: javítsd a szöveget, és mondd meg, mit változtattál |
| 5 | Felvételek (ha kellenek) | képernyőfelvétel, vágás ütemre, elmosás | |
| 6 | Jelenetek | `python eszkozok/jelenet.py <epizód>` + bővítés a komponensekkel; `npx hyperframes lint` | |
| 7 | Render | `python eszkozok/render.py <epizód>` | |
| 8 | Gépi képellenőrzés | `python eszkozok/kontaktlap.py <epizód>`, nézd meg a lapokat; keretek, adatvédelem | |
| 9 | Keverés | `python eszkozok/keveres.py <epizód>` → `out/reszek/` | |
| 10 | Átnézés | add át az `out/reszek/` teljes útvonalát + `ATNEZESRE.md` | **igen: a felhasználó nézi át** |
| 11 | Javítási kör | csak az érintett jelenetek, ugyanazon a néven; tanulság a házirendbe | ismételd, amíg „jó” |
| 12 | Összefűzés | `python eszkozok/keveres.py <epizód> --osszefuz [--outro ...]` | **csak kimondott jóváhagyás után** |
| 13 | Leírás, cím, borító | `python eszkozok/leiras.py <epizód>`, borító a stíluslappal, tévéteszt | **igen: cím és borító jóváhagyása** |
| 14 | Közzététel | kézzel, vagy a `videogyar-kozzetetel` szerint | **csak kimondott jóváhagyás után** |
| 15 | Napló | `ALLAPOT.md`: mi készült, mi ment fel, mi van hátra | |

## Szabályok menet közben

- Ha a szöveg változik a 4. lépés után: hang → időterv → jelenet → render → keverés, mind újra az
  érintett jelenetekre (az időterv miatt a jelenet magától nem igazodik).
- Ha a felhasználónál korlátos a gépidő, a hosszú lépéseket (hang, render) egyben futtasd, és közben ne
  állj meg állapotjelentéssel; egy-két mondatot írhatsz két lépés között.
- Ne mondd, hogy kész, amíg nem nézted meg a kontaktlapot, és nem hallgattad vissza a kapukkal.
- Minden, amit a felhasználó az átnézéskor kifogásolt, és nem egyszeri, kerüljön be a házirendbe vagy
  a stíluslapba, hogy a következő epizódban már ne forduljon elő.
