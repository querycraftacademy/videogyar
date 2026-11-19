---
name: videogyar-ellenorzes
description: A videógyár ellenőrző állomása — három réteg: gépi hangellenőrzés (kiejtés, hangkapuk, Whisper), gépi képellenőrzés (pillanatkép-lap, kiemelő keretek a renderen, adatvédelmi kockák), és a felhasználó átnézése jelenetenként, képkockára tűzött hibajegyzetekkel, javítási körrel és jóváhagyással. Használd minden render után, ha a felhasználó hibát jelez egy videóban, ha átnézésre adsz át valamit, vagy ha egy javítás után újra át kell nézni.
---

# Ellenőrzés: előbb a gép néz, aztán az ember

A minőség nem szerencse kérdése. Három réteg van, és **a felhasználó csak azt kapja meg átnézésre, ami
az első kettőn átment.**

## 1. réteg: a hang (gépi)

A `videogyar-hang` állomás kapui, röviden:
- `kiejtes.py`: ottfelejtett angol szó (a generálás előtt);
- `hangkapu.py`: elharapott mondatvég, kattanás, zúgás (a generálás után);
- `visszahallgat.py`: Whisper-átirat összevetve a szöveggel (0,86 alatti egyezés gyanús);
- `kiejtes.py --szamok`: hosszú számnevek.

## 2. réteg: a kép (gépi)

- **Pillanatkép-lap:** `python eszkozok/kontaktlap.py epizodok/001_proba [s2]` → `_check/sX.jpg`.
  Minden ütemből egy kocka (az ütem 85%-ánál, amikor már minden kint van, ami hozzá tartozik), az ütem
  szövegével. Nézd meg te magad (ha az AI-eszközöd lát képet), mielőtt a felhasználónak adod: kilóg-e
  szöveg, takar-e valami valamit, jó-e a sorrend, olvasható-e minden.
- **Kiemelő keretek:** minden keretről (doboz egy gomb vagy szám körül) egy kivágás a **renderelt**
  kockáról, a keret megjelenése után ~1,2 mp-cel, egy kis ráhagyással. A tervben a koordináta jó lehet,
  a renderen mégis a szomszédos elemre ül. Ha a jelenetekben sok keret van, írj rá egy kis szkriptet,
  ami a jelenet HTML-jéből kiolvassa a keretek helyét és idejét, és kontaktlapot készít.
- **Adatvédelem:** az epizód `FELADAT.md`-jének KIVÁGANDÓ és ELMOSANDÓ listája alapján nézd meg azokat a
  kockákat, ahol érzékeny adat lehetett. Ami látszik, az javítandó, nem „majd senki nem veszi észre”.
- `npx hyperframes lint` minden jeleneten, a render előtt.

## 3. réteg: a felhasználó

- Átnézésre a **jelenetenkénti fájlokat** add (`out/reszek/`), ne a teljes videót: így egy hiba egy
  jelenet újrarenderelése, és a felhasználó pontosan meg tudja mondani, hol van.
- A fájlok helyét mindig **teljes, abszolút útvonallal** add meg, hogy egy kattintással megnyíljon.
- Írj mellé egy rövid átnézési listát (`ATNEZESRE.md` az epizód mappájában): mi változott, mire figyeljen,
  mi bizonytalan.

### Hogyan jelezze a hibát

A legrosszabb a szóbeli leírás („a harmadik jelenetben a kijelölés nem pontos”): az AI-nak keresgélnie
kell, melyik kockáról van szó, és diktálva még félre is érthető. Jobb sorrendben:

1. **Fájlnév + időpont + egy mondat** („03_s2: 0:04, a nyíl rossz gombra mutat”). Ez mindig működik.
2. **Képernyőkép a hibás kockáról**, rajta bekarikázva a hiba.
3. **Saját hibajegyzet-eszköz** (ha sokat dolgoztok együtt, megéri megépíteni):
   - helyi weboldal (pl. egy kis Python-szerver a `127.0.0.1`-en), ami listázza az `out/reszek/` videóit;
   - a felhasználó megállítja a videót, a kockára egy átlátszó rajzrétegen (canvas) karikát vagy nyilat
     rajzol, és ír mellé egy mondatot;
   - a jegyzet a videó mellé kerül JSON-ban: fájl, időpont, képkocka sorszáma, a rajz koordinátái
     (a videó méretéhez viszonyítva), a szöveg, az állapot (`nyitott` / `javitva` / `jo` / `meg_rossz`);
   - egy parancssori `lista` parancs, amivel az AI kiolvassa a nyitott jegyzeteket, és FFmpeg-gel kivágja
     a kockát és a bekarikázott részt, hogy lássa, mire gondolt a felhasználó;
   - a javítás után az AI `javitva` jelölést tesz rá egy mondattal, a felhasználó pedig a lapon eldönti:
     jó lett, vagy még rossz. Új render ugyanazon a néven: a jegyzet a fájlnévhez kötődik.

### A javítási kör

1. Olvasd ki az összes jegyzetet, csoportosítsd jelenetenként.
2. Javíts (szöveg → hang → időterv → jelenet, ha a szöveg változott; különben csak a jelenet).
3. Rendereld újra és keverd újra **csak az érintett jeleneteket**, ugyanazon a néven.
4. Ellenőrizd a javított kockát te is (kontaktlap vagy kivágás), mielőtt visszaadod.
5. Írd meg röviden, mit javítottál, jegyzetenként.
6. Ami tanulság, az a „minden hiba csak egyszer” szabály szerint a házirendbe vagy a skillbe kerül.

### Jóváhagyás

Összefűzés, feltöltés, ütemezés, borító- vagy címcsere **csak a felhasználó kimondott jóváhagyása után**
(„mehet”, „jóváhagyom”). A hallgatás nem jóváhagyás, és egy korábbi jóváhagyás nem vonatkozik a következő
lépésre.
