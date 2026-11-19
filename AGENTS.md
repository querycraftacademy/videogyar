# Videógyár – utasítás az AI-nak

Ezt a fájlt egy AI-ügynöknek írtuk (Claude Code, Codex, Gemini CLI, Cursor vagy bármelyik, amelyik fájlt
olvas és parancsot futtat). A feladatod: **a felhasználó gépén, az ő igényei szerint felépíteni egy
videógyártó rendszert**, ami szövegből narrált, animált magyarázó videót készít. A csomag egy tervrajz,
nem kész program: a `skills/` mappa receptjeiből és az `eszkozok/` kipróbált segédprogramjaiból te
állítod össze a felhasználó saját rendszerét.

A felhasználóval az ő nyelvén beszélj (a csomag magyar, a felhasználó valószínűleg magyar). Ne feltételezd,
hogy programozó: magyarázd el röviden, mit miért csinálsz, és kérdezz, ha az ő döntése kell.

## Az első lépés mindig a felmérés

**Semmit ne telepíts, és semmilyen motort ne ajánlj, amíg nem mérted fel a gépet.** A felhasználó gépe
bármilyen lehet: Windows, macOS vagy Linux; NVIDIA, AMD, Intel vagy Apple grafikus processzor, vagy
egyáltalán nincs videókártya; 8 GB vagy 64 GB memória. Ami az egyik gépen jó választás, a másikon el sem
indul.

1. Olvasd el: [`skills/videogyar-felmeres/SKILL.md`](skills/videogyar-felmeres/SKILL.md).
2. Futtasd: `python eszkozok/gepfelmeres.py --ki gep.json` (ha nincs Python, a skill leírja a kézi utat).
3. Kérdezd ki a felhasználót a skill kérdései szerint.
4. Írd meg a `gyar.json`-t: a gép adatai és a választott motorok. **Minden további lépés ebből dolgozik.**

## A sorrend

Állomásonként haladj, és minden állomás végén próbáld ki, amit építettél. A következőbe csak akkor
kezdj bele, ha az előző működik. A haladást az `ALLAPOT.md`-ben vezeted (sablon: `sablonok/ALLAPOT.md`),
így egy új munkamenetben is tudod, hol tartotok.

| # | Állomás | Skill | Kész, ha |
|---|---|---|---|
| 0 | Felmérés és kikérdezés | `videogyar-felmeres` | megvan a `gep.json` és a `gyar.json` |
| 1 | Telepítés | `videogyar-telepites` | az `eszkozok/onteszt.py` hibátlanul lefut |
| 2 | Az AI munkaterülete | `videogyar-ai-beallitas` | megvan a házirend, az `ALLAPOT.md`, a `.env` és a `.gitignore` |
| 3 | Stílus | `videogyar-stilus` | megvan a `kozos/stilus.md` és a `kozos/stilus.css`, a felhasználó jóváhagyta |
| 4 | Hang | `videogyar-hang` | egy kétmondatos próbaszöveg hangja átmegy a kapukon, és a felhasználó meghallgatta |
| 5 | Kép | `videogyar-kep` | a próbajelenet a felhasználó stílusában, az időtervhez igazítva |
| 6 | Render | `videogyar-render` | a próbajelenetből MP4 lett, a felhasználó képernyőjét nem zavarta |
| 7 | Keverés és összefűzés | `videogyar-keveres` | kész a 10 másodperces **próbavideó**, hanggal, zenével |
| 8 | Ellenőrzés | `videogyar-ellenorzes` | a kapuk, a pillanatkép-lap és az átnézési kör működik |
| 9 | Közzététel (ha kéri) | `videogyar-kozzetetel` | leírás, cím, borító; feltöltés csak jóváhagyással |
| 10 | Kamerás videó (ha kéri) | `videogyar-kamera` | egy rövid saját felvétel szövegből vágva |

Ha a rendszer kész, a további videók a `videogyar-uj-epizod` skill menetrendje szerint készülnek.

A skillek a `skills/<név>/SKILL.md` fájlokban vannak. Ha az eszközöd ismeri a skilleket (pl. Claude
Code: `.claude/skills/`), telepítsd őket oda; ha nem, olvasd el a fájlt, amikor az állomáshoz érsz.

## Az aranyszabályok

1. **A hang megy elöl, a kép igazodik hozzá.** Előbb a narráció készül el, a mért hosszából lesz az
   időterv (`audio/plan.json`), és a jelenetek ehhez animálnak. Ha a szöveg változik, a hang, az
   időterv és a jelenet is újra készül.
2. **Minden lépés egy kis, külön program**, ami fájlt olvas és fájlt ír. Nem egy nagy, mindent tudó
   alkalmazás. Ha valami elromlik, csak azt az egy lépést kell újrafuttatni.
3. **Minden hiba csak egyszer fordulhat elő.** Ha a felhasználó hibát talál, vagy egy kapu megbukik,
   a javítás mellett a tanulság is kerüljön be a házirendbe vagy a megfelelő skillbe (a felhasználó
   munkamappájában lévő példányba). A következő munkamenet így már tudja.
4. **Amit lehet, ellenőrizzen a gép; a végső szó a felhasználóé.** A gépi kapu jelez, a fül és a szem dönt.
5. **Kifelé ható lépés csak kimondott jóváhagyással:** feltöltés, ütemezés, publikálás, törlés,
   komment, e-mail, fizetős szolgáltatás első használata. Addig minden a gépen marad.
6. **Titok soha nem kerülhet fájlba, amit megosztanak:** API-kulcs, jelszó, token csak a `.env`-be,
   és a `.env` a `.gitignore`-ba. Képernyőfelvételen, kontaktlapon se látszódjon.
7. **Licenc.** Hangmotor, zene, betűtípus, kép: mielőtt a felhasználó bevételszerző csatornán használja,
   nézd meg a licencét, és mondd meg neki, mit enged és mit nem. Ha nem egyértelmű, mondd ki, hogy nem az.
8. **Ne zavard a felhasználó képernyőjét.** A render és a böngészős felvétel láthatatlanul fusson
   (lásd `videogyar-render`). Ha valami mégis ablakot nyit, az hiba, nem szépséghiba.
9. **Egy videókártya, egy nagy munka.** A hanggenerálás és a render ne fusson egyszerre ugyanazon a
   kártyán (lásd `eszkozok/gpu_zar.py`). Ha más program is használja a kártyát, előbb nézd meg a szabad
   memóriát.
10. **A kész epizódhoz ne nyúlj**, ha nem az a feladat. Ha egy közös modult módosítasz, előtte készíts
    róla másolatot (`fajl.bak_<ÓÓPP>`), és a régi epizódok működjenek tovább.

## A munkamappa szerkezete (amit felépítesz)

```
<munkamappa>/
  AGENTS.md vagy CLAUDE.md  ← a felhasználó saját házirendje (sablon: sablonok/HAZIREND.md)
  ALLAPOT.md                ← hol tartunk (sablon: sablonok/ALLAPOT.md)
  gep.json, gyar.json       ← a gép adatai és a választott motorok
  .env, .gitignore          ← titkok (soha nem kerül megosztásra)
  eszkozok/                 ← a csomag eszközei + amit hozzáírsz (pl. tts_<motor>.py)
  kozos/
    stilus.md, stilus.css   ← a felhasználó stílusa (videogyar-stilus)
    komponensek/            ← újrahasznosítható jelenetelemek, ahogy gyűlnek
    kiejtes.json            ← kiejtési szótár
    zene/                   ← jóváhagyott háttérzenék
    vendor/gsap.min.js      ← a GSAP helyi példánya
  epizodok/
    001_proba/
      szoveg.json           ← a narráció: jelenetek és ütemek (sablon: sablonok/epizod/)
      FELADAT.md            ← mi a videó célja, KIVÁGANDÓ és ELMOSANDÓ lista
      audio/                ← ütemhangok, plan.json, whisper.json, keverések
      jelenetek/s0/index.html …
      render/s0.mp4 …       ← néma jelenetvideók
      _check/               ← kontaktlapok, kapuk eredménye
      out/reszek/           ← jelenetenkénti átnéző fájlok (hanggal)
      out/vegleges.mp4      ← csak jóváhagyás után
```

## Az eszközök (eszkozok/)

Kipróbált, processzoron futó Python-segédprogramok. Másold át őket a munkamappába, és ha kell,
igazítsd. Részletek: [`eszkozok/README.md`](eszkozok/README.md).

| Program | Mit csinál |
|---|---|
| `gepfelmeres.py` | rendszer, processzor, memória, videókártya(k), meglévő eszközök → `gep.json` |
| `kiejtes.py` | kiejtési szótár alkalmazása + ottfelejtett angol szavak keresése |
| `narracio.py` | a `szoveg.json`-ból ütemenként hangot kér a választott motortól, gyorsítótárral |
| `terv.py` | a kész ütemhangokból jelenethangot és időtervet (`plan.json`) készít |
| `hangkapu.py` | elharapott mondatvég, kattanás, zúgás keresése |
| `visszahallgat.py` | Whisperrel visszahallgatja a narrációt, és összeveti a szöveggel |
| `jelenet.py` | az időtervből HyperFrames-jelenetet ír, a felhasználó stíluslapjával |
| `render.py` | a jelenetek renderelése (Windowson láthatatlan asztalon) |
| `keveres.py` | jelenetenkénti keverés (narráció, zene, hangerő), átnéző fájlok, összefűzés |
| `kontaktlap.py` | pillanatkép-lap: minden ütemből egy kocka |
| `leiras.py` | YouTube-leírás fejezetekkel és a kötelező megjelölésekkel |
| `gpu_zar.py` | egyszerre csak egy nagy GPU-s munka fusson |
| `tts_proba.py` | álhangmotor a lánc kipróbálásához (nem beszél, csak hangot ad) |
| `onteszt.py` | a teljes lánc gyors próbája, hangmotor nélkül |

## Ha elakadsz

- Mondd meg a felhasználónak őszintén, mi nem működik, mit próbáltál, és mi a javaslatod.
- Ne gyengíts egy ellenőrzést csak azért, hogy átmenjen. Ha egy kapu téves riasztást ad, azt mérd
  meg, és a kivételt dokumentáld.
- Ne mondd, hogy valami kész, ha nem próbáltad ki.
