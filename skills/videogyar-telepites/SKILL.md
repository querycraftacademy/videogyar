---
name: videogyar-telepites
description: A videógyár eszközeinek telepítése a felmérés (gep.json, gyar.json) alapján, a felhasználó rendszeréhez és videókártyájához igazítva — Python-környezet, Node.js, FFmpeg, HyperFrames, GSAP, a csomag segédprogramjai, és csak a választott hangmotorhoz szükséges GPU-s csomagok. Használd a felmérés után, ha valami hiányzik vagy elromlott a telepítésben, ha a hangmotort cserélitek, vagy ha az önteszt megbukik.
---

# Telepítés: csak ami kell, a gépnek megfelelő változatban

**Előfeltétel:** kész a `gep.json` és a `gyar.json` (`videogyar-felmeres`), és a felhasználó jóváhagyta
a tervet. Ha nincs meg, előbb azt csináld.

Elvek:
- Ami már telepítve van és elég új, azt ne telepítsd újra.
- Rendszerszintű telepítés (winget, brew, apt) előtt mondd meg, mit telepítesz. Ha rendszergazdai jog
  kell, a felhasználó futtassa.
- A Python-csomagok a munkamappa saját környezetébe (`.venv`) mennek, ne a rendszer Pythonjába.
- **Rövid, ékezet és szóköz nélküli munkamappa-útvonal** (pl. `C:\videogyar`, `~/videogyar`). Néhány
  eszköz ékezetes vagy szóközös útvonalon hibázik.

## 1. Alapeszközök

| Eszköz | Windows | macOS | Linux (Debian/Ubuntu) |
|---|---|---|---|
| Python 3.10+ | `winget install Python.Python.3.12` | `brew install python@3.12` | `sudo apt install python3 python3-venv` |
| Node.js 22+ | `winget install OpenJS.NodeJS.LTS` | `brew install node` | a nodejs.org leírása szerint (az apt csomagja gyakran régi) |
| FFmpeg | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| git (ajánlott) | `winget install Git.Git` | `xcode-select --install` | `sudo apt install git` |

Telepítés után nyiss új terminált (a PATH frissül), és ellenőrizd: `python --version`, `node --version`,
`ffmpeg -version`, `ffprobe -version`.

## 2. A munkamappa és a Python-környezet

```
cd <munkamappa>
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r <csomag>/eszkozok/requirements.txt
```

Másold át a csomag `eszkozok/` mappáját a munkamappába (`<munkamappa>/eszkozok/`), és hozd létre a
mappaszerkezetet az `AGENTS.md` szerint (`kozos/`, `kozos/zene/`, `kozos/vendor/`, `epizodok/`).

## 3. HyperFrames és GSAP

```
npx hyperframes doctor            # Node, FFmpeg, Chrome, erőforrások
npx hyperframes browser ensure    # a renderhez használt Chrome letöltése, ha hiányzik
```

- Ha az AI-eszközöd ismeri a skilleket, a HyperFrames saját skilljei is hasznosak: `npx hyperframes skills`.
- A GSAP-ot töltsd le helyben, hogy a render ne függjön az internettől:
  ```
  curl -L -o kozos/vendor/gsap.min.js https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js
  ```
  (Windows PowerShellben a `curl.exe` nevet használd.) A `jelenet.py` ezt beágyazza a jelenetbe; ha nincs
  meg, a CDN-ről tölti be.
- A HyperFrames névtelen használati statisztikát küld. Ha a felhasználó nem szeretné, mondd meg neki,
  hogy kikapcsolható (`npx hyperframes telemetry --help`).

## 4. A hangmotor csomagjai (csak a választotthoz)

A választott motor saját telepítési leírását kövesd (`gyar.json` → `tts.motor`). Ha PyTorch kell, a
videókártyának megfelelő változat kell; a pontos parancsot mindig a pytorch.org *Get Started* oldaláról
vedd, mert a verziók változnak:

| `tts.eszkoz` | PyTorch-változat |
|---|---|
| `cuda` (NVIDIA) | CUDA-s kerék a pytorch.org index-URL-jével |
| `rocm` (AMD, Linux) | ROCm-os kerék |
| `xpu` (Intel Arc) | XPU-s kerék (Intel GPU-illesztő kell hozzá) |
| `mps` (Apple Silicon) | a sima `pip install torch` (MPS benne van) |
| `cpu` | CPU-s kerék (kisebb letöltés) |
| `felho` | nem kell PyTorch; csak az API kliense és a kulcs a `.env`-ben |

Telepítés után egy háromsoros próbával ellenőrizd, hogy a motor tényleg a videókártyát használja-e
(pl. `torch.cuda.is_available()`, `torch.xpu.is_available()`, `torch.backends.mps.is_available()`).
Ha nem, ne lépj tovább: derítsd ki, miért (illesztőprogram, rossz kerék), vagy beszéljétek meg a
processzoros vagy felhős utat.

## 5. Whisper (visszahallgatáshoz)

A `requirements.txt` telepíti a `faster-whisper`-t. Processzoron is jól fut (`int8`); a `small` modell
jó kompromisszum, a `medium` pontosabb, de lassabb. Az első futás letölti a modellt.

## 6. Önteszt

```
python eszkozok/onteszt.py
```

Hangmotor nélkül, egy álhanggal végigpróbálja a láncot: időterv, hangkapuk, kiejtés, jelenetírás,
keverés, kontaktlap. Ha a `--render` kapcsolóval is lefut, a HyperFrames-render is működik.

Ha valami megbukik, javítsd, és csak hibátlan önteszt után lépj tovább. Írd be az `ALLAPOT.md`-be, mit
telepítettél (verziókkal), és hogy az 1. állomás kész.
