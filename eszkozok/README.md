# Eszközök

Kis, külön futtatható Python-programok, egy-egy lépéssel. Az AI a telepítéskor a felhasználó munkamappájába
másolja őket (`<munkamappa>/eszkozok/`), és ott igazítja, bővíti. Csak a numpy, a Pillow és (a
visszahallgatáshoz) a faster-whisper kell hozzájuk, plusz az FFmpeg; a renderhez a Node.js és a HyperFrames.

```
pip install -r requirements.txt
python onteszt.py            # a teljes lánc próbája hangmotor nélkül
```

| Program | Bemenet → kimenet |
|---|---|
| `gepfelmeres.py` | → `gep.json` (rendszer, processzor, memória, videókártyák, hely, eszközök) |
| `kiejtes.py <epizód>` | `szoveg.json` + `kozos/kiejtes.json` → gyanús szavak listája (kilépési kód 1, ha van) |
| `narracio.py <epizód>` | `szoveg.json` → `audio/utemek/*.wav` → `audio/sX.wav` + `audio/plan.json` → hangkapuk |
| `terv.py <epizód>` | `audio/utemek/*.wav` → `audio/sX.wav` + `audio/plan.json` (a `narracio.py` is hívja) |
| `hangkapu.py <wav…>` | elharapott mondatvég, kattanás, zúgás |
| `visszahallgat.py <epizód>` | Whisper-átirat vs. szöveg → `audio/whisper.json` |
| `jelenet.py <epizód>` | `plan.json` + `szoveg.json` + `kozos/stilus.css` → `jelenetek/sX/index.html` |
| `render.py <epizód>` | `jelenetek/sX/` → `render/sX.mp4` (Windowson láthatatlan asztalon) |
| `kontaktlap.py <epizód>` | `render/sX.mp4` → `_check/sX.jpg` |
| `keveres.py <epizód>` | `audio/sX.wav` + zene → `audio/mix_sX.wav` + `out/reszek/NN_sX_*.mp4` |
| `keveres.py <epizód> --osszefuz` | → `out/vegleges.mp4` (csak jóváhagyás után) |
| `leiras.py <epizód>` | → `out/leiras.txt` (fejezetek, megjelölések) |
| `gpu_zar.py` | egyszerre egy nagy GPU-s munka (a `narracio.py` és a `render.py` használja) |
| `tts_proba.py` | álhangmotor a próbákhoz (nem beszél) |
| `windows/rejtett_asztal.ps1` | Windows: parancsfájl futtatása láthatatlan asztalon |

Az FFmpeg helyét a `FFMPEG` és `FFPROBE` környezeti változóval is meg lehet adni, ha nincs a PATH-on.

## A hangmotor illesztése

A `narracio.py` a `gyar.json` `tts.modul` mezőjében megadott modult hívja (pl. `tts_piper` →
`eszkozok/tts_piper.py`). A szerződés: `szintetizal(szoveg, kimenet_wav, beallitas)`, opcionálisan
`betolt(beallitas)` és `lezar()`. Részletek és motorválasztás: `skills/videogyar-hang/SKILL.md`.
Minta: `tts_proba.py`.
