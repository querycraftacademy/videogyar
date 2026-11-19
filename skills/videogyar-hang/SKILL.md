---
name: videogyar-hang
description: A videógyár hangállomása — narrációs szöveg írása hangmotorra (szoveg.json), hangmotor választása a gép, a költségkeret és a licenc alapján, a motor illesztése (eszkozok/tts_<motor>.py), kiejtési szótár, gyorsítótáras generálás (narracio.py), időterv (plan.json), gépi hangkapuk és visszahallgatás Whisperrel. Használd, ha narrációt kell írni vagy generálni, hangmotort választani vagy cserélni, ha a hang rossz (elharapott szó, angol szó magyarul betűzve, összemosott szám, zúgás), vagy ha a szöveg változott és újra kell időzíteni.
---

# Hang: a szövegtől az időtervig

**A hang megy elöl, a kép igazodik hozzá.** Ez az állomás állítja elő az időtervet (`audio/plan.json`),
amihez minden jelenet animál. Ha a szöveg változik, ez az állomás újra fut, és utána a jelenetek is.

## 1. A szöveg (szoveg.json)

Minden epizódnak egy `szoveg.json`-ja van (sablon: `sablonok/epizod/szoveg.json`): jelenetek, azokon
belül ütemek. Egy ütem egy-két mondat, és egy képi esemény tartozik hozzá (opcionális `kep` mező, lásd
`videogyar-kep`).

```json
{
  "cim": "Próbavideó",
  "jelenetek": [
    { "id": "s0", "cim": "nyitas", "utemek": [
      { "mondat": "Ez a videó magától készült.", "kep": { "tipus": "cim", "szoveg": "Magától készült" } },
      { "mondat": "Megmutatom, hogyan.", "kep": { "tipus": "felirat", "szoveg": "Hogyan?" } }
    ] }
  ]
}
```

A szöveget előbb mutasd meg a felhasználónak; **hangot csak a jóváhagyott szövegből generálj.**

### Írási szabályok hangmotorra

- **Ütemenként egy-két mondat**, legfeljebb a `gyar.json` `tts.max_karakter` értéke (alapból 250).
  Egyszavas ütem ne legyen: a hang úgy darabos lesz.
- **Angol szó csak a kiejtési szótáron át.** A magyar hangmotor az angol szavakat magyarul olvassa
  („Claude” helyett „kla-u-de”). A `kozos/kiejtes.json` kiejtés szerint írja át őket („klód”).
  A `kiejtes.py` megbuktatja a szöveget, ha benne maradt egy gyanús szó: ilyenkor **a szótár bővül, a
  detektor nem lesz engedékenyebb.**
- **Számok:** a hosszú összetett számneveket sok motor összemossa. A narráció kerekítsen („több mint
  negyven százalék”), a pontos szám a képernyőre kerüljön. Évszámot, dátumot, időt úgy írj, ahogy kimondjuk.
- **Rövidítést írj ki** úgy, ahogy kimondjuk (pl. „em-í” vagy „mesterséges intelligencia”).
- **Mondatvég:** a halk, gyenge zárószótagot a motor néha elharapja. Ha a hangkapu jelez, írd át a
  mondatot úgy, hogy egy erősebb szó kerüljön a végére.
- Zárójel, perjel, emoji, felsorolásjel ne legyen a narrációban. A szünetet az írásjelek adják.

## 2. A hangmotor kiválasztása

A felmérés (`gep.json`, `gyar.json`) és a felhasználó válaszai alapján ajánlj 2–3 motort, és **a döntést
hagyd rá**. Mondd meg mindegyiknél: hol fut, mennyibe kerül, tud-e magyarul, és mit enged a licence.

Kiindulásnak (az állapot változik: **a licencet és a magyar támogatást a választás napján ellenőrizd**
a motor saját oldalán):

| Motor | Hol fut | Klónozás | Licenc, röviden |
|---|---|---|---|
| ElevenLabs | felhő | igen | fizetős csomagban kereskedelmi használat |
| Azure AI Speech | felhő (kész magyar hangok) | egyedi hang külön engedéllyel | fizetős |
| Google Cloud TTS | felhő (kész magyar hangok) | korlátozott | fizetős |
| OpenAI TTS | felhő | nem, kész hangok | fizetős; a magyar kiejtése nem mindig természetes |
| Piper | helyben, processzoron is gyors | nem | a motor nyílt; minden hangnak saját licence van (nézd meg a hang leírását) |
| XTTS-v2 (Coqui) | helyben, videókártya ajánlott | igen, rövid mintából | Coqui Public Model License: nem kereskedelmi |
| OmniVoice | helyben, videókártya | igen | a modell licence nem kereskedelmi |
| Higgs TTS 3 (Boson AI) | helyben, videókártya (kb. 5 GB+) | igen | alapból nem kereskedelmi; saját csatornán bevételszerzés megjelöléssel engedett, a pontos feltételeket olvasd el |

Szempontok:
- **Bevételszerző csatornához** csak olyan motor jó, aminek a licence ezt kifejezetten engedi. Ha nem
  egyértelmű, mondd ki, és a felhasználó döntsön. Írd be a `gyar.json`-ba (`tts.licenc`,
  `tts.bevetel_engedett`), és ha a licenc megjelölést kér, az a leírásba kerül (`videogyar-kozzetetel`).
- **Hangklónozás** csak a felhasználó saját hangjáról, vagy olyan ember hangjáról, aki írásban
  hozzájárult. A hozzájárulást őrizd meg. A YouTube a valósághű, módosított vagy gépi tartalom
  jelölését kérheti; lásd `videogyar-kozzetetel`.
- Nincs videókártya, vagy kevés a memória: processzoros motor vagy felhő.

## 3. A motor illesztése (eszkozok/tts_<motor>.py)

A `narracio.py` nem ismer egyetlen motort sem; a választottat egy kis illesztőmodulon át hívja, amit
te írsz meg a motor dokumentációja alapján. A modul neve a `gyar.json` `tts.modul` mezőjében van.

```python
# eszkozok/tts_motornev.py — a szerződés
def betolt(beallitas: dict) -> None:
    """Opcionális. Egyszer hívódik a generálás elején (modell betöltése, kliens létrehozása)."""

def szintetizal(szoveg: str, kimenet_wav: str, beallitas: dict) -> None:
    """Kötelező. Egy ütem szövegéből WAV-fájlt ír. A mintavétel mindegy, a narracio.py átalakítja."""

def lezar() -> None:
    """Opcionális. A végén hívódik (videómemória felszabadítása)."""
```

A `beallitas` a `gyar.json` `tts` része. Kulcsot soha ne írj a modulba: a `.env`-ből olvasd
(`os.environ`). Minta álmotorhoz: `eszkozok/tts_proba.py`.

Buktatók, amiket mérés igazolt:
- **Hosszú darab:** egyes motorok a túl hosszú bemenetből hibaüzenet nélkül kihagynak szavakat. Ezért
  rövid az ütem, és a `narracio.py` figyelmeztet, ha egy ütem hangja gyanúsan rövid a szöveghez képest.
- **Halk referenciahang klónozásnál:** a modell elakadhat. A minta másolatát normalizáld (−1 dB csúcs),
  az eredetit ne írd felül.
- **Videómemória:** a hanggenerálás és a render ne fusson egyszerre ugyanazon a kártyán. A `narracio.py`
  a `gpu_zar.py`-t használja, ha a motor nem felhős.

## 4. Generálás

```
python eszkozok/narracio.py epizodok/001_proba            # a hiányzó vagy megváltozott ütemek
python eszkozok/narracio.py epizodok/001_proba --csak s2  # csak egy jelenet
python eszkozok/narracio.py epizodok/001_proba --replan   # hangmotor nélkül, csak újraidőzítés
```

Mit csinál, sorban:
1. A kiejtési szótárral átírja az ütemeket, és a `kiejtes.py`-jal ellenőrzi: ha marad gyanús szó, megáll.
2. Ütemenként hangot kér a motortól, **csak ha a hang hiányzik vagy a szöveg változott** (a hang mellett
   egy `.txt` őrzi, milyen szövegből készült). Így egy mondat javítása egy ütem újragenerálása.
3. Minden ütemhangot 48 kHz-es sztereó WAV-ra alakít (`audio/utemek/`).
4. A `terv.py`-jal jelenethangot fűz (`audio/s0.wav` …), és megírja az időtervet (`audio/plan.json`).
5. Lefuttatja a hangkapukat (`hangkapu.py`). Ha megbukik, kiírja, melyik ütem, és mi a teendő.

### Az időterv (plan.json)

```json
{
  "lead": 0.9, "gap": 0.35, "tail": 1.0,
  "sorrend": ["s0", "s1"],
  "jelenetek": {
    "s0": { "audio": 4.12, "duration": 7,
            "beats": [ { "at": 0.9, "dur": 1.8, "text": "Ez a videó magától készült." },
                       { "at": 3.05, "dur": 1.97, "text": "Megmutatom, hogyan." } ] }
  }
}
```

- `at`: hányadik másodpercben kezdődik az ütem a **jelenet elejétől** (a `lead` már benne van).
- `lead`: ennyi csend van a jelenet elején, mielőtt a narráció indul (a képnek idő kell beúszni).
- `duration`: a jelenet hossza egész másodpercre kerekítve felfelé (az összefűzés így nem gyűjt tört
  képkockákat).

## 5. Ellenőrzés

- **Hangkapuk** (automatikusan, a generálás végén): elharapott mondatvég (a rendes mondat utolsó 40 ms-a
  −40 dB körül van és lecseng; a levágott −30 dB fölött szakad meg), darabhatár-kattanás, egyenletes
  zúgás. **Ha megbukik, a mondatot írd át**, töröld az ütem hangját, és generáld újra. Ne a hangot foltozd.
- **Visszahallgatás:** `python eszkozok/visszahallgat.py epizodok/001_proba` — a Whisper leírja, amit
  hall, és ütemenként összeveti a szöveggel. 0,86 alatti egyezésnél jelez. **A végső szó a fülé:** a
  márkaneveket a Whisper gyakran félrehallja, pedig jól hangzanak el. A gyanús ütemeket a felhasználó
  hallgassa meg. A `small` modell gyors, de több téves riasztást ad (pl. két szót egybeír); ha zavaróan
  sok, állítsd a `gyar.json` `whisper.modell` értékét `medium`-ra.
- **Számnevek:** a `kiejtes.py --szamok` kilistázza a hosszú számneveket; ezeket kerekítsd, vagy hallgasd meg.
- Az első epizódnál a felhasználó hallgassa végig az egészet. Amit talál, az a „minden hiba csak
  egyszer” szabály szerint kerüljön a szótárba, a házirendbe vagy egy kapuba.

## 6. Zene

A zenét a keverés állomás teszi alá (`videogyar-keveres`). Forrás: saját zene, licencelt zenetár, a
YouTube Hangtára, vagy helyben generált zene. Mindegyiknél nézd meg, mit enged a licenc (bevételszerzés,
megjelölés). A jóváhagyott zenék a `kozos/zene/` mappába kerülnek; ha több van, váltogasd őket, hogy két
egymást követő videóban ne ugyanaz szóljon.

Kész az állomás, ha egy kétmondatos próbaszöveg hangja átment a kapukon, és a felhasználó meghallgatta.
