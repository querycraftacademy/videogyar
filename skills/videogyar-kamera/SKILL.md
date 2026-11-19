---
name: videogyar-kamera
description: Kamerás (beszélő fejes) videók vágása a videógyárban — felvételi tanácsok, átirat szavankénti időbélyeggel, vágás a szövegből (csendek, töltelékszavak, újramondások ki), zajszűrés, egységes hangerő, háttér cseréje (zöld háttér FFmpeg-gel vagy gépi kivágás), grafikák a kimondott szóra időzítve, kompozit. Használd, ha a felhasználó saját felvételt hoz (telefon, kamera, OBS), ha „vágd meg”, „vedd ki az ő-ket”, „cseréld le a hátteret”, vagy ha egy videóban ő maga is szerepel.
---

# Kamerás videó: vágás a szövegből

Itt nem a hang megy elöl, hanem a felvétel: a felhasználó beszél, és a kép a beszédhez igazodik. A lánc:
**átirat → vágás a szövegből → hang → háttér → grafika → kompozit**. A nyers felvételt soha ne írd felül;
minden lépés új fájlt ír.

## 1. Felvételi tanácsok (felvétel előtt add át)

- Telefon vagy kamera fekvő helyzetben, 1080p vagy 4K, állandó képkockasebesség, ha a készülék engedi.
- Fény elölről (ablak vagy lámpa), egyenletes háttér; zöld háttérnél a vászon legyen ráncmentes és
  egyenletesen megvilágított, és a felhasználó álljon tőle legalább egy méterre.
- Külső mikrofon sokat javít; ha nincs, a telefon legyen közel, és a szoba ne visszhangozzon.
- Rontás után nyugodtan mondja újra a mondatot: a vágás az utolsó jó változatot tartja meg.
- Ha a felvétel szöveg alapján készül, írjátok meg előre (vázlat vagy teljes szöveg), jelenetenként:
  mit mond, és mi látszik közben.

## 2. Átirat

Szavankénti időbélyeg kell.
- **Helyben, ingyen:** `faster-whisper` `word_timestamps=True` beállítással (a `large-v3` modell
  pontosabb, de lassabb; processzoron is megy).
- **Felhőben:** fizetős beszédfelismerő, ami szavanként ad időt (pontosabb lehet magyarul). Az első
  használat előtt kérdezd meg a felhasználót, mert pénzbe kerül.

A telefonok gyakran változó képkockasebességgel vesznek fel. Vágás előtt alakítsd állandóra
(`ffmpeg -i be.mov -vf fps=30 -c:v libx264 -crf 14 -c:a copy cfr.mp4`), különben a vágások elcsúsznak.

## 3. Vágás a szövegből

1. Az átiratból szólista: `index: kezdet–vég szó`.
2. Döntsd el, mi marad (`keep.json`: megtartott szótartományok, megjegyzéssel):
   - csendek: 0,4 mp fölött rövidítsd;
   - töltelékszavak („ő”, „öö”, „hát” mondat elején): ki, de vigyázz, hogy az „ő” névmás nem töltelék;
   - újramondás: **mindig az utolsó, jó változat marad**, a félbehagyott mondat egészében kiesik;
   - elszólás, „ezt majd vágjuk ki”: ki. Az önironikus megjegyzések maradnak, azok a hangulat.
3. A vágás FFmpeg-gel, a szóhatárokon egy kis ráhagyással (40–80 ms), és rövid hangáttűnéssel
   (10–20 ms), hogy ne kattanjon. A szó végét a hangerőgörbéből vedd, ne csak az átiratból.
4. A videó utolsó szava után hagyj 0,5–0,7 mp csendet, hogy a búcsú ne harapódjon el.
5. Mutasd meg a felhasználónak a vágott változatot, mielőtt a többi lépéshez fogsz.

## 4. Hang

- Zajszűrés: DeepFilterNet (processzoron is fut), vagy FFmpeg `afftdn` / `arnndn`. Óvatosan: a túl erős
  zajszűrés gépies hangot ad. Készíts 2–3 változatot, és a felhasználó válasszon.
- Előtte a bemenet csúcsa legyen kb. −6 dBFS (ne vágjon), utána egységes hangerő a `gyar.json` szerint.

## 5. Háttér

- **Zöld háttér:** FFmpeg `chromakey` (vagy különbségkulcs egy üres háttérképpel), és egy rögzített maszk,
  ami kívül mindent levág. Szélekre kis elmosás, a zöld visszaverődésre színkorrekció.
- **Zöld háttér nélkül:** gépi kivágás (videós „matting” modellek). Videókártyát igényel és lassú;
  csak akkor ajánld, ha a felmérés szerint a gép elbírja.
- Az új háttér lehet egy HyperFrames-jelenet a felhasználó stílusában (lásd `videogyar-stilus`),
  egyszer renderelve, hosszra ismételve. Több változatot mutass, a felhasználó választ.

## 6. Grafika és elrendezés

- A grafikák (kártya, szám, kép) **a kimondott szóra** időzítve jönnek: az átiratból tudod, mikor hangzik el.
- Elrendezés (teljes kép, oldalt, sarokban) csak témaváltáskor változzon, különben ugrál a kép.
- A grafikát átlátszó háttérrel rendereld (pl. ProRes 4444 vagy WebM alfával), és FFmpeg `overlay`-jel
  tedd rá; vagy a felhasználót és a grafikát egy HyperFrames-kompozícióban rakd össze.

## 7. Kompozit és átnézés

Háttér + kivágott felhasználó + grafika + hang (+ zene halkan, + hangeffekt) → átnézés a
`videogyar-ellenorzes` szerint → összefűzés és közzététel csak jóváhagyás után.
