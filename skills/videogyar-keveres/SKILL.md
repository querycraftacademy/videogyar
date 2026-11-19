---
name: videogyar-keveres
description: A videógyár keverő- és összefűző állomása — jelenetenkénti hangkeverés (narráció késleltetéssel, folytonos háttérzene lehalkítással, hangeffektek, egységes hangerő LUFS-ben), jelenetenkénti átnéző fájlok, és a végleges összefűzés intróval vagy outróval, csak jóváhagyás után. Használd, ha a renderelt jelenetekhez hangot kell tenni, ha túl hangos vagy halk a zene, ha két jelenet között ugrik a zene, vagy ha kész a videó és össze kell fűzni.
---

# Keverés és összefűzés

## 1. Jelenetenkénti keverés és átnéző fájlok

```
python eszkozok/keveres.py epizodok/001_proba            # minden jelenet
python eszkozok/keveres.py epizodok/001_proba s2         # csak egy (javítás után)
```

Jelenetenként:
- **Narráció** a `plan.json` szerint: a jelenethang (`audio/sX.wav`) már tartalmazza a `lead` csendet,
  így a hang a képpel együtt indul.
- **Háttérzene** a `gyar.json` `zene` beállításával (vagy `--zene fajl.mp3`). **A zene folytonos:** minden
  jelenet ott folytatja, ahol az előző abbahagyta (a jelenet kezdőidejétől olvas), így az összefűzött
  videóban nem ugrik. A narráció alatt lehalkul (oldalláncos kompresszor), a szünetekben visszajön.
- **Hangeffekt** (opcionális): `jelenetek/sX/sfx.json` → `[[idő_mp, "fajl.wav", hangerő_dB], …]`.
- **Hangerő:** a kész keverést statikus erősítéssel a célértékre állítja (`gyar.json` → `hangero_lufs`,
  alapból −14), és egy határoló gondoskodik róla, hogy ne torzítson.

Kimenet: `audio/mix_sX.wav` és az átnéző fájl `out/reszek/NN_sX_<cím>.mp4` (a néma render + a keverés).
**Ezeket nézi át a felhasználó**, jelenetenként (`videogyar-ellenorzes`). Egy javítás után csak az
érintett jelenetet kell újrarenderelni és újrakeverni, ugyanazon a néven.

## 2. Összefűzés – csak jóváhagyás után

```
python eszkozok/keveres.py epizodok/001_proba --osszefuz [--intro intro.mp4] [--outro outro.mp4]
```

- A jelenetek videója és a keverések külön-külön fűződnek össze (a hang veszteségmentesen), és egyszer
  kódolódik AAC-re. Így a jelenethatárokon nincs kattanás vagy csúszás.
- Az intró és az outró ugyanolyan felbontású, képkockasebességű legyen, mint a jelenetek; ha nem, a
  program átkódolja őket.
- Kimenet: `out/vegleges.mp4`, és kiírja a teljes hosszt és a mért hangerőt.

**Az összefűzést csak a felhasználó kimondott jóváhagyása után futtasd.** Előtte a jelenetenkénti
átnéző fájlok a mérvadók.

## 3. Hasznos tudnivalók

- A YouTube a hangosabb videókat nagyjából −14 LUFS-re halkítja. Ha a felhasználó csatornáján már van
  megszokott hangerő, igazodj ahhoz, hogy a videók egymás után egyformán szóljanak.
- A zene hangereje (`zene.hangero`, alapból 0,11) a narráció alatti szintet adja; ha a felhasználó
  szerint elnyomja a beszédet, csökkentsd, és írd be a házirendbe.
- A videó végén a zene ússzon ki (az utolsó 1,5 mp-ben), a beszéd ne.
- Ha a felhasználó végefőcímet tesz a YouTube-on a videó végére, a videó utolsó 5–20 másodperce legyen
  nyugodt háttér (pl. outró), szöveg nélkül.

Kész az állomás, ha elkészült a 10 másodperces próbavideó hanggal és zenével, és a felhasználó
megnézte.
