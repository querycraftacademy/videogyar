---
name: videogyar-ai-beallitas
description: Az AI munkaterületének beállítása a videógyárhoz — házirend (CLAUDE.md / AGENTS.md / GEMINI.md), állapotnapló (ALLAPOT.md), tanulságok rögzítése, skillek, MCP-kapcsolatok, engedélyek, titkok (.env, .gitignore) és verziókövetés. Használd a telepítés után, ha az AI új munkamenetben nem tudja, hol tartotok, ha egy hiba másodszor fordul elő, vagy ha új kapcsolatot (pl. YouTube) kell bekötni.
---

# Az AI munkaterülete: hogy ne kelljen mindent kétszer elmondani

Egy AI minden munkamenetet tiszta lappal kezd. Amit nem írtatok le, azt nem tudja. Ez az állomás azt
állítja be, hogy a rendszer tudása fájlokban éljen, ne a beszélgetésben.

## 1. Házirend

Hozd létre a munkamappa gyökerében a felhasználó saját házirendjét a `sablonok/HAZIREND.md` alapján,
azon a néven, amit az AI-eszköze magától olvas:

| Eszköz | Fájlnév |
|---|---|
| Claude Code | `CLAUDE.md` |
| Codex, Cursor és a legtöbb ügynök | `AGENTS.md` |
| Gemini CLI | `GEMINI.md` |

Ha több eszközt is használ, egy fájl legyen a valódi (pl. `AGENTS.md`), a többi csak hivatkozzon rá.

Mi kerüljön bele (a sablon ezt követi):
- **Térkép:** mi melyik mappában van, és mi az epizódok szerkezete.
- **A gyártás sorrendje** a pontos parancsokkal (amit a felhasználó gépén kipróbáltál).
- **Kötelező szabályok:** pl. a hang megy elöl; kifelé ható lépés csak jóváhagyással; titok csak a
  `.env`-ben; a GPU-n egyszerre egy nagy munka.
- **Gépspecifikus tudnivalók:** melyik Python, melyik hangmotor, hol van az FFmpeg, mi a videókártya.
- **Tanulságok:** rövid szabályok a már megtörtént hibákból (lásd a 3. pontot).

Rövid, tömör mondatok. A házirendet az AI minden munkamenet elején elolvassa, ezért ne nőjön végtelenre:
ami csak egy feladathoz kell, az skillbe való.

## 2. Állapotnapló

Az `ALLAPOT.md` (sablon: `sablonok/ALLAPOT.md`) mondja meg, hol tartotok: melyik állomás kész, mi van
folyamatban, mi a következő lépés, melyik epizód hol tart. Minden munkamenet végén frissítsd.

## 3. Minden hiba csak egyszer

Ez a rendszer legfontosabb szokása. Ha a felhasználó hibát talál, vagy egy kapu megbukik:
1. Javítsd ki a hibát.
2. Gondold végig, mitől fordulhat elő újra.
3. Írd be a megelőzést oda, ahol a következő munkamenet megtalálja:
   - ha általános szabály → házirend, *Tanulságok* rész, egy mondatban, okkal együtt;
   - ha egy állomáshoz tartozik → a munkamappában lévő skill-példányba;
   - ha mérhető → gépi kapu vagy önteszt-eset (a legjobb, mert nem lehet elfelejteni).
4. Mondd meg a felhasználónak, mit írtál be és hova.

Ha az AI-eszközödnek van saját memóriája (pl. a Claude Code automatikus memóriája), használhatod, de a
gyártáshoz szükséges szabály a házirendbe vagy a skillbe kerüljön: az a munkamappával együtt költözik.

## 4. Skillek

Másold a csomag skilljeit a munkamappába, és **a felhasználó példányát igazítsd** (a csomag példányát
ne). Claude Code-ban: `<munkamappa>/.claude/skills/<név>/SKILL.md`. Más eszköznél egy `skills/` mappa is
jó; a házirendben írd le, melyik skillt mikor kell elolvasni.

Új skill akkor kell, ha egy feladat ismétlődik, és több lépésből áll (pl. „borító készítése”, „Shorts
kivágása”). Egy skill: rövid leírás arról, mikor kell használni, utána a lépések, a parancsok és a
buktatók.

## 5. Kapcsolatok (MCP) – csak ha kell

Az MCP-szerver egy kis program, amin keresztül az AI külső szolgáltatást ér el (pl. YouTube, böngésző).
- Ha a felhasználó kéri a YouTube-feltöltést, lásd `videogyar-kozzetetel`. Egyszerű szkript is elég;
  MCP-szerver akkor éri meg, ha az AI gyakran kérdez le adatot (lista, statisztika).
- Egy kapcsolat egy fiókhoz tartozzon. Ha több csatorna van, külön kapcsolat, külön `.env`, beszédes
  névvel, és a házirendben le van írva, melyik melyik.
- Idegen MCP-szervert csak megbízható forrásból telepíts, és mondd meg a felhasználónak, mihez fér hozzá.

## 6. Engedélyek

- Olvasó és helyi parancsoknál (fájl olvasása, FFmpeg, a gyártósor szkriptjei) kevesebb rákérdezés is elég.
- Kifelé ható lépéshez (feltöltés, törlés, komment, e-mail, publikálás, fizetős API első használata)
  mindig kérj jóváhagyást, akkor is, ha az eszközöd engedné. Ezt a házirendbe is írd be.
- Rendszerszintű változtatás (illesztőprogram, rendszerbeállítás) előtt mondd meg, mit csinálsz és miért.

## 7. Titkok és verziókövetés

- API-kulcs, token, jelszó: csak a munkamappa `.env` fájljába. Soha ne írd ki a beszélgetésbe, és ne
  tedd szkriptbe.
- Hozd létre a `.gitignore`-t: `.env`, `.venv/`, `**/audio/`, `**/render/`, `**/out/`, `**/_check/`,
  `**/rec/`, `*.mp4`, `*.wav`, `*.mkv`. A média nagy és gyakran személyes; a szkriptek, a szövegek és a
  házirend viszont menjenek verziókövetésbe (`git init`), mert így minden változás visszakövethető.
- Ha a felhasználó valaha nyilvánossá teszi a munkamappáját vagy egy részét: előtte keress kulcsokat,
  e-mail-címeket, neveket, gépspecifikus útvonalakat.

## 8. Kényelmi extrák (opcionális)

- **Diktálás:** sokan gyorsabban beszélnek, mint gépelnek. Bármilyen diktálóprogram jó; ingyenes, helyi
  változat például a [querycraftacademy/diktalo](https://github.com/querycraftacademy/diktalo).
- **Felolvasás:** az AI válaszait egy helyi hang fel is olvashatja; ez a hangmotorral megoldható, de
  ne fusson egyszerre a narrációval vagy a renderrel a videókártyán.

Kész, ha megvan a házirend, az `ALLAPOT.md`, a `.env`, a `.gitignore`, és a felhasználó tudja, hol
találja őket. Írd be az `ALLAPOT.md`-be, hogy a 2. állomás kész.
