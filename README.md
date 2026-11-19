# Videógyár – saját, AI-vezérelt videógyártó rendszer, a te gépedre szabva

Ez **nem egy kész program**, hanem egy tervrajz: egy skillcsomag és egy leírás, amit odaadsz egy
mesterséges intelligenciának. Az AI ebből **a te gépeden** építi fel a videógyártó rendszert, lépésről
lépésre, a te hardveredhez, a te stílusodhoz és a te igényeidhez igazítva.

Bármelyik AI-ügynökkel működik, amelyik fájlokat tud olvasni és parancsokat futtatni:
**Claude Code**, **OpenAI Codex**, **Gemini CLI**, **Cursor** vagy hasonló.

## Mit tud a kész rendszer?

Szövegből narrált, animált magyarázó videót készít:

```
1. szöveg  →  2. hang  →  3. kép  →  4. render  →  5. keverés  →  6. gépi ellenőrzés  →  7. átnézés (te)  →  8. feltöltés
```

- **Hang:** a narrációt egy hangmotor (TTS) mondja fel. Te választod ki, melyiket: helyi és ingyenes,
  vagy felhős és fizetős, akár a saját klónozott hangodon.
- **Kép:** minden jelenet egy weboldal (HTML, CSS, animáció), amiből a [HyperFrames](https://github.com/heygen-com/hyperframes)
  képkockánként videót készít. Videószerkesztő program nem kell.
- **Az aranyszabály:** a hang megy elöl, a kép igazodik hozzá. Előbb elkészül a narráció, a program
  megméri minden mondat hosszát, és a jelenetek ehhez az időtervhez animálnak.
- **Ellenőrzés:** gépi kapuk (elharapott mondatvég, kattanás, ottfelejtett angol szó, visszahallgatás
  Whisperrel, pillanatkép-lap), utána a te átnézésed. Feltöltés csak a te jóváhagyásod után.
- **Opcionális:** feltöltés és ütemezés a YouTube-ra, kamerás (beszélő fejes) felvételek vágása szövegből.

## Mit csinál az AI, amikor megkapja?

1. **Felméri a gépedet.** Milyen rendszer (Windows, macOS, Linux), milyen processzor, mennyi memória,
   van-e videókártya, és ha igen, milyen márkájú és mennyi memóriája van (NVIDIA, AMD, Intel, Apple).
   Ami telepítve van, azt nem telepíti újra. **Minden további döntés ehhez igazodik.**
2. **Kikérdez:** milyen videókat akarsz, milyen nyelven, milyen hangon, mennyit fizetnél felhős
   szolgáltatásért, kell-e YouTube-feltöltés, és **milyen legyen a videóid stílusa** (színek, betűk,
   hangulat, minták). A stílust te határozod meg, a csomag nem ír elő semmilyen dizájnt.
3. **Telepít:** csak azt, ami kell, a te gépedhez választott változatban.
4. **Beállítja magát:** házirendet ír a munkamappába (mi hol van, mit szabad, mit nem), hogy a
   következő munkamenetben is tudja, hol tartotok.
5. **Próbavideó:** először egy kb. 10 másodperces, egyjelenetes videó készül, végig a teljes láncon.
6. **Bővít:** ha a próba jó, jöhetnek a további állomások, egyenként, mindegyik után kipróbálva.

## Indítás három lépésben

1. Töltsd le ezt a repót (zöld **Code** gomb → *Download ZIP*, majd csomagold ki), vagy:
   ```
   git clone https://github.com/querycraftacademy/videogyar.git
   ```
2. Hozz létre egy üres munkamappát a videóidnak (pl. `C:\videogyar` vagy `~/videogyar`), és nyisd meg
   az AI-eszközödben. A letöltött csomag lehet benne vagy mellette.
3. Másold be az AI-nak az [INDITAS.md](INDITAS.md) indító szövegét. Onnantól ő vezet, és megkérdez,
   amikor a te döntésed kell.

## Mi kell hozzá?

| | Kötelező | Megjegyzés |
|---|---|---|
| Rendszer | Windows 10/11, macOS vagy Linux | |
| AI-ügynök | igen | olyan, amelyik parancsot tud futtatni (lásd fent) |
| Python 3.10+, Node.js 22+, FFmpeg | igen | ha hiányzik, az AI telepíti vagy megmondja, hogyan |
| Szabad hely | kb. 10–30 GB | a hangmotortól függ |
| Videókártya | nem | helyi hangmotorhoz ajánlott; nélküle felhős hang vagy processzoros motor |
| Programozás | nem | de türelem igen: ez egy műhely, nem egy gomb |

## A csomag tartalma

| Hely | Mi van benne |
|---|---|
| [`AGENTS.md`](AGENTS.md) | az AI fő utasítása: a sorrend, a szabályok, melyik skillt mikor kell elolvasni |
| [`CLAUDE.md`](CLAUDE.md), [`GEMINI.md`](GEMINI.md) | ugyanoda mutatnak (a Claude Code és a Gemini CLI ezeket olvassa) |
| [`INDITAS.md`](INDITAS.md) | az indító szöveg, amit bemásolsz |
| [`skills/`](skills/) | a receptkönyv: állomásonként egy skill (felmérés, telepítés, AI-beállítás, stílus, hang, kép, render, keverés, ellenőrzés, közzététel, kamerás videó) |
| [`sablonok/`](sablonok/) | házirend-sablon, epizódsablon, kiejtési szótár, stíluslap-sablon |
| [`eszkozok/`](eszkozok/) | kipróbált segédprogramok (Python): gépfelmérés, kiejtés-ellenőrzés, narráció, időterv, hangkapuk, visszahallgatás, jelenetgenerátor, render, keverés, kontaktlap, önteszt |

## Ami szándékosan nincs benne

- **Hang.** Nincs benne hangmotor és nincs benne senkinek a hangja. A felmérés után az AI ajánl
  néhányat, a döntés a tiéd.
- **Dizájn.** Nincs kötelező stílus. Az AI kikérdez, és a te ízlésed szerint írja meg a stíluslapot.
- **Kulcsok, fiókok.** API-kulcs, jelszó, YouTube-hozzáférés soha nem kerülhet a csomagba vagy a
  repódba. Az AI ezeket egy `.env` fájlba teszi, ami nem megy fel sehova.

## Licencek: erre figyelj

A csomag MIT licencű, szabadon használhatod. **A motoroknak viszont saját licencük van.** Sok nyílt
hang- és zenemodell csak nem kereskedelmi célra használható, és ide számít a bevételszerző
YouTube-csatorna is. Mielőtt bekapcsolod a bevételszerzést, olvasd el a hangmotor és a zene licencét.
Az AI ebben segít, de a döntés és a felelősség a tiéd.

## Kipróbálva

Őszintén: amit ki tudtunk próbálni, és amit nem.

| Mit | Hol | Eredmény |
|---|---|---|
| `onteszt.py`: kiejtés, narráció álhanggal, időterv, hangkapuk, jelenet, keverés, összefűzés, leírás, kontaktlap | Windows 11, Python 3.12, csak processzor | 13/13 rendben |
| A generált jelenetek HyperFrames-ellenőrzése (`npx hyperframes lint`) | Windows 11, HyperFrames 0.9.58 | 0 hiba |
| `hangkapu.py` valódi, gépi narráción (123 ütem) | Windows 11 | 0 téves riasztás; a mesterségesen elvágott mondatot, kattanást és zúgást megfogja |
| `visszahallgat.py` valódi narráción | Windows 11, processzor, `small` modell | működik (egy téves gyanú: két szó egybeírva) |
| `gepfelmeres.py` | Windows 11, AMD Ryzen + Intel Arc | a videómemóriát is helyesen olvassa |
| `render.py` (HyperFrames-render, Windowson láthatatlan asztalon) + `onteszt.py --render` | Windows 11, Intel Arc videókártya | rendben: egy 9 mp-es jelenet `draft` minőségben kb. 28 mp alatt, semmi nem ugrott fel a képernyőn |
| A teljes felépítés egy AI-val, a nulláról | | még nem próbáltuk |
| macOS, Linux, NVIDIA, AMD | | nem próbáltuk; a kód hordozhatónak készült |

## Ha elakadsz

A videó, amiben bemutatjuk: [Query Craft Academy a YouTube-on](https://www.youtube.com/@querycraftacademy).
Hibát a GitHubon, az *Issues* fülön jelezhetsz.

Ha szeretnéd, hogy megépítsük neked, vagy a cégednek kell ilyen rendszer: [adatpulzus.hu](https://adatpulzus.hu)
(fizetős szolgáltatás).

## Licenc

MIT, lásd [LICENSE](LICENSE).
