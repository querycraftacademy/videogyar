# Házirend – <a felhasználó neve vagy a csatorna> videógyára

<!-- Sablon. Az AI tölti ki a felmérés és a telepítés után, a felhasználó gépén kipróbált parancsokkal.
     A fájl neve az AI-eszköztől függ: CLAUDE.md (Claude Code), AGENTS.md (Codex, Cursor), GEMINI.md (Gemini CLI). -->

Ez a munkamappa egy videógyártó rendszer. A videók szövegből készülnek: hang → időterv → HTML-jelenetek
(HyperFrames) → render → keverés → ellenőrzés → átnézés → közzététel. A felhasználóval magyarul beszélj.

## Térkép

| Mappa | Tartalom |
|---|---|
| `eszkozok/` | a gyártósor programjai (Python) |
| `kozos/` | stíluslap, komponensek, kiejtési szótár, zenék, GSAP |
| `epizodok/NNN_nev/` | egy-egy videó: `szoveg.json`, `FELADAT.md`, `audio/`, `jelenetek/`, `render/`, `out/` |
| `.claude/skills/` vagy `skills/` | a receptek állomásonként |

## A gép

- Rendszer: <…>, processzor: <…>, memória: <…>, videókártya: <…> (lásd `gep.json`)
- Python: `<.venv útvonala>`; FFmpeg: `<útvonal vagy PATH>`; Node: <verzió>
- Hangmotor: <név> (`eszkozok/<tts_modul>.py`), fut: <cuda / cpu / felhő>; licenc: <röviden>
- Whisper: <modell>, <cpu/gpu>

## A gyártás sorrendje

```
python eszkozok/narracio.py epizodok/NNN      # hang + időterv + hangkapuk
python eszkozok/visszahallgat.py epizodok/NNN # Whisper-visszahallgatás
python eszkozok/jelenet.py epizodok/NNN       # jelenetek
python eszkozok/render.py epizodok/NNN        # render
python eszkozok/kontaktlap.py epizodok/NNN    # pillanatkép-lap
python eszkozok/keveres.py epizodok/NNN       # átnéző fájlok: out/reszek/
python eszkozok/keveres.py epizodok/NNN --osszefuz   # CSAK jóváhagyás után
python eszkozok/leiras.py epizodok/NNN        # leírás
```

## Kötelező szabályok

- **A hang megy elöl, a kép igazodik hozzá.** Ha a szöveg változik: hang, időterv, jelenet, render, keverés újra.
- **Kifelé ható lépés csak a felhasználó kimondott jóváhagyása után:** összefűzés, feltöltés, ütemezés,
  cím- vagy borítócsere, komment, fizetős szolgáltatás első használata.
- **Titok** (kulcs, token, jelszó) csak a `.env`-be; soha ne írd ki, és ne kerüljön szkriptbe vagy képre.
- **Egyszerre egy nagy GPU-s munka** (hang vagy render).
- **Angol szó a narrációban csak a kiejtési szótáron át** (`kozos/kiejtes.json`). Ha a kiejtés-ellenőrzés
  megbukik, a szótár bővül, nem a detektor gyengül.
- **Számok:** a narráció kerekít, a pontos szám a képernyőre kerül.
- **Kész epizódhoz ne nyúlj**, ha nem az a feladat; közös modul módosítása előtt másolat (`.bak_ÓÓPP`).
- **Átnézésre** a jelenetenkénti fájlokat add (`out/reszek/`), teljes útvonallal.
- A stílus a `kozos/stilus.md` szerint; változtatás a stíluslapon, nem jelenetenként.

## Tanulságok

<!-- Minden hiba csak egyszer: ide kerül egy-egy mondat arról, mi romlott el, és mit csinálunk azóta másképp.
     Példa: "A zene elnyomta a beszédet a halk mondatoknál → zene.hangero 0,11 helyett 0,08 (2026-12-03)." -->
