---
name: videogyar-stilus
description: A felhasználó SAJÁT vizuális stílusának kialakítása a videógyárhoz — kikérdezés (hangulat, színek, betűk, mozgás, minták, logó), 2–3 stílusjelölt próbakockával, a választottból stíluslap (kozos/stilus.md + kozos/stilus.css), amit a jelenetgenerátor és a borító használ. A csomag nem ír elő dizájnt. Használd a 3. állomáson, ha a felhasználó új stílust szeretne, ha azt mondja, hogy „nem tetszik, ahogy kinéz”, „legyen modernebb / vidámabb / komolyabb”, vagy ha új sorozatot indít.
---

# Stílus: a felhasználó ízlése szerint, nem a csomag szerint

A csomag szándékosan nem tartalmaz kész dizájnt. Minden csatorna más, és egy átvett stílus mindenhol
ugyanúgy néz ki. A feladatod: kikérdezni a felhasználót, jelölteket mutatni, és a választásából
stíluslapot írni.

**Más csatorna, márka vagy film jellegzetes arculatát (logó, karakter, betűtípus-kombináció, színvilág,
grafikai elemek) ne másold le**, akkor sem, ha a felhasználó azt kéri, hogy „olyan legyen, mint X”.
Ilyenkor kérdezd meg, mi tetszik benne (pl. „nyugodt”, „sok fehér tér”, „nagy számok”), és abból
építs saját stílust.

## 1. Kikérdezés

Egyszerre 3–4 kérdés, alapértékekkel. Ha a felhasználó azt mondja, „mindegy”, ajánlj egy semleges,
jól olvasható kiindulást, és jelezd, hogy később bármikor cserélhető.

1. **Kinek szól, milyen hangulatú legyen?** Mondjon három szót (pl. „nyugodt, tiszta, barátságos” vagy
   „energikus, merész, tech”).
2. **Sötét vagy világos háttér?** (Tévén és telefonon mindkettő működik, a sötétnél a kiemelés
   látványosabb, a világos papírszerű, nyugodtabb.)
3. **Vannak-e kötött színek?** (céges szín, logó) Ha nincs: egy alapszín, egy kiemelőszín, és a
   semlegesek.
4. **Betűk:** modern és egyszerű, barátságos és kerek, vagy komoly és klasszikus? Csak olyan betűtípust
   javasolj, amit szabadon lehet használni videóban (pl. a Google Fonts OFL-licencű betűi), és amit
   letöltve a jelenet mellé lehet tenni.
5. **Mozgás:** nyugodt és lassú, vagy pörgős? Rugós, játékos mozdulatok, vagy egyenletes, visszafogott
   beúszások?
6. **Mennyi szöveg legyen a képen?** Csak kulcsszavak és nagy számok, vagy teljes mondatok, feliratok?
7. **Van-e logó, arculati elem, karakter, amit használni kell?** Kérd el a fájlt.

## 2. Jelöltek

Készíts 2–3 stílusjelöltet, ugyanarra a próbajelenetre (egy cím, egy kártya három ponttal, egy nagy
szám). Mindegyikből egy állókép (a HyperFrames `snapshot` parancsával vagy egy rövid renderből), és
mutasd meg őket egymás mellett. A jelöltek érdemben különbözzenek (háttér, szín, betű, elrendezés), ne
csak árnyalatban.

A felhasználó választ, vagy kever („az elsőnek a színei, a másodiknak a betűi”). Addig iterálj, amíg
azt nem mondja, hogy jó.

## 3. Stíluslap

A választásból két fájl készül:

**`kozos/stilus.css`** — CSS-változók; a `jelenet.py` ezt ágyazza be minden jelenetbe:

```css
:root {
  --hatter: #0f172a;        /* a jelenet háttere */
  --felulet: #1e293b;       /* kártyák, dobozok */
  --szoveg: #f8fafc;        /* fő szövegszín */
  --halvany: #94a3b8;       /* másodlagos szöveg */
  --kiemeles: #38bdf8;      /* a kiemelőszín */
  --kiemeles2: #f59e0b;     /* második kiemelés (ritkán) */
  --betu-cim: "Valami Sans", system-ui, sans-serif;
  --betu-szoveg: "Valami Sans", system-ui, sans-serif;
  --lekerekites: 24px;
  --arnyek: 0 20px 60px rgba(0, 0, 0, 0.35);
}
@font-face { font-family: "Valami Sans"; src: url("fonts/ValamiSans.woff2") format("woff2"); }
```

A fenti értékek csak a formát mutatják, nem javaslatok. A betűfájlokat a `kozos/fonts/` mappába tedd;
a `jelenet.py` a jelenet mappájába másolja őket, mert a HyperFrames csak a jelenet saját mappájából
tölt be biztonságosan, és megnevezett betűtípushoz `@font-face` kell.

**`kozos/stilus.md`** — a szabályok szövegesen, hogy a következő munkamenet is ugyanígy dolgozzon:
- a három hangulatszó és a választás oka;
- színek szerepe (mire való a kiemelőszín, és mire nem);
- betűméretek 1920×1080-on (cím, szöveg, felirat); tévén is olvasható legyen, a szöveg legalább ~36 px;
- mozgás: tipikus időtartamok és gyorsulási görbék (pl. beúszás 0,5–0,7 mp, `power3.out`), mennyi idő
  maradjon két elem között;
- elrendezés: margók, mennyi elem lehet egyszerre a képen;
- a borító szabályai (lásd `videogyar-kozzetetel`): ugyanaz a színvilág, nagy, rövid szöveg;
- tilos: amit a felhasználó kifejezetten nem kért (pl. villogás, túl sok effekt).

## 4. Utána

- A közös jelenetelemeket (kártya, nyíl, kiemelés, számláló) a stíluslap változóival építsd, a
  `kozos/komponensek/` mappába. Így a stílus egy helyen változtatható.
- Ha a felhasználó később változtatni akar, a stíluslapot módosítsd, ne az egyes jeleneteket. A régi,
  kész epizódokat ne generáld újra, hacsak nem kéri.

Kész, ha megvan a két fájl, és a felhasználó jóváhagyta a próbaképet. Írd be az `ALLAPOT.md`-be.
