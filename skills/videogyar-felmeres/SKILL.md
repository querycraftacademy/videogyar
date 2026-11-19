---
name: videogyar-felmeres
description: A videógyár építésének KÖTELEZŐ első lépése. Felméri a felhasználó gépét (rendszer, processzor, memória, videókártya márkája és memóriája, szabad hely, meglévő eszközök), kikérdezi az igényeiről, és ezekből megírja a gep.json-t és a gyar.json-t, amiből minden további telepítési és motorválasztási döntés dolgozik. Használd, ha a videógyárat most kezditek, ha új gépre költöztök, ha a felhasználó új videókártyát vett, vagy ha egy motorválasztás előtt nem tudod, milyen gépen dolgozol.
---

# Felmérés: milyen gépen, mire, kinek

**Amíg ez nincs kész, semmit ne telepíts, és semmilyen motort ne ajánlj.** A felhasználó gépe bármilyen
lehet, és ami az egyiken jó választás, a másikon el sem indul. Ne a saját feltételezésedből, és ne a
csomag példáiból indulj ki, hanem a mért adatokból.

## 1. A gép felmérése

```
python eszkozok/gepfelmeres.py --ki gep.json
```

A program kiírja és elmenti: operációs rendszer és verzió, processzor (típus, magok, szálak), memória,
videókártyák (gyártó, típus, videómemória, ha kiolvasható), szabad hely a munkamappa meghajtóján, és
hogy telepítve van-e: Python, Node.js, FFmpeg, ffprobe, git, nvidia-smi.

Ha nincs Python, kérdezd le kézzel:

| Rendszer | Parancsok |
|---|---|
| Windows (PowerShell) | `Get-CimInstance Win32_OperatingSystem`, `Get-CimInstance Win32_Processor`, `Get-CimInstance Win32_VideoController`, `Get-PSDrive`, `nvidia-smi` |
| macOS | `sw_vers`, `sysctl -n machdep.cpu.brand_string hw.memsize hw.ncpu`, `system_profiler SPDisplaysDataType`, `df -h .` |
| Linux | `cat /etc/os-release`, `lscpu`, `free -g`, `lspci \| grep -iE "vga\|3d"`, `nvidia-smi`, `rocm-smi`, `df -h .` |

A Windows `Win32_VideoController.AdapterRAM` 4 GB fölött hibás értéket ad; a `gepfelmeres.py` ezért a
regisztrációs adatbázisból (és NVIDIA-nál az `nvidia-smi`-ből) olvas. Ha a videómemória ismeretlen,
kérdezd meg a felhasználót, vagy nézd meg a kártya típusából.

## 2. Mit jelent a mért gép

Ebből a táblából döntsd el, melyik úton induljatok. Ez irányt ad, nem végleges ítélet: a konkrét motor
követelményeit mindig nézd meg a saját oldalán, a telepítés napján.

| Amit találtál | Helyi hangmotor | Render | Megjegyzés |
|---|---|---|---|
| **NVIDIA**, 8 GB+ videómemória | a legtöbb nyílt motor fut (PyTorch + CUDA) | gyors | a legszélesebb választék |
| **NVIDIA**, 4–6 GB | kisebb modellek, vagy processzoros motor | jó | nagy modellnél kevés lehet a memória |
| **AMD** Radeon | Linuxon PyTorch + ROCm (újabb kártyák); Windowson szűkebb: Vulkan- vagy DirectML-alapú motorok, vagy processzor | jó | mindig nézd meg, hogy a motor támogatja-e |
| **Intel** Arc / Iris Xe | PyTorch XPU-val, vagy Vulkan-alapú (pl. llama.cpp-szerű) motorok | jó | kevesebb motor támogatja, mint az NVIDIA-t |
| **Apple Silicon** (M1–M4) | PyTorch MPS vagy MLX; a közös memória miatt nagyobb modell is elfér | jó | CUDA-only motor itt nem fut |
| **Nincs videókártya** vagy nagyon kevés memória | processzoros motor (pl. Piper) vagy felhős hang | lassabb, de megy | a felhős hang itt gyakran a jobb élmény |
| Memória (RAM) 8 GB | csak könnyű motorok | `--quality draft`, kevesebb szál | |
| Szabad hely < 20 GB | inkább felhős vagy kicsi motor | | a modellek 1–10 GB-osak |

## 3. Kikérdezés

Egyszerre legfeljebb 3–4 kérdést tegyél fel, és ajánlj alapértéket, hogy a felhasználó egy szóval
válaszolhasson. A válaszokat írd be a `gyar.json`-ba.

**A videókról**
- Mire kellenek? (YouTube-csatorna, cégen belüli oktatás, ügyfélnek) Lesz-e bevételszerzés?
  *Ez dönti el, melyik hangmotor és zene licence fér bele.*
- Milyen nyelven? Milyen hosszúak, és milyen gyakran készülnek?
- Milyen típusúak? Animált magyarázó, képernyős programbemutató, kamerás (a felhasználó a képen), vagy vegyes.

**A hangról**
- Kinek a hangján szóljon? Saját, klónozott hang (csak saját vagy írásban hozzájáruló ember hangja),
  egy kész hang a motor kínálatából, vagy mindegy.
- Helyben, ingyen (lassabb lehet, a géptől függ), vagy felhőben, fizetősen (gyors, jó minőség)? Mennyi
  a havi keret?

**A működésről**
- Kell-e YouTube-feltöltés és ütemezés a rendszerből, vagy kézzel tölti fel?
- Használja-e más program a videókártyát rendszeresen (játék, más AI)? *Ha igen, a nagy GPU-s munkák
  előtt várni kell (`eszkozok/gpu_zar.py`).*
- Mennyire szereti a technikai részleteket? *Ehhez igazítsd a magyarázataidat.*

A **stílusról** (színek, betűk, hangulat) a `videogyar-stilus` skill kérdez, külön állomáson.

## 4. A gyar.json

Írd meg a munkamappa gyökerébe. Minden további eszköz és skill ebből olvas.

```json
{
  "nyelv": "hu",
  "felbontas": [1920, 1080],
  "fps": 30,
  "bevetel": true,
  "tts": {
    "motor": "a választott motor neve",
    "modul": "tts_motornev",
    "eszkoz": "cuda | rocm | xpu | mps | cpu | felho",
    "hang": "hangazonosító vagy referenciafájl",
    "licenc": "a licenc neve és a lényeg egy mondatban",
    "bevetel_engedett": "igen | nem | nem egyértelmű",
    "max_karakter": 250
  },
  "whisper": { "modell": "small", "eszkoz": "cpu" },
  "render": { "minoseg": "looks", "rejtett": true },
  "hangero_lufs": -14,
  "zene": { "mappa": "kozos/zene", "hangero": 0.11 },
  "gpu_megosztott": false,
  "youtube": false,
  "kamera": false
}
```

A `hangero_lufs` alapértéke −14: a YouTube nagyjából erre normalizál. Ha a felhasználónak már van
csatornája, igazodj a meglévő videóihoz.

## 5. Visszajelzés a felhasználónak

Mielőtt telepítesz, foglald össze 5–8 sorban:
- mit találtál a gépen (egyszerű szavakkal: „NVIDIA-kártya 8 GB-tal, ez helyi hanghoz elég”);
- melyik utat javaslod és miért (hangmotor, render), és mi kerül pénzbe;
- mit fogsz telepíteni, kb. mennyi helyet foglal;
- ami bizonytalan (pl. „ezt a kártyát a motor hivatalosan nem támogatja, kipróbáljuk, és ha nem megy,
  processzorra váltunk”).

Csak a jóváhagyása után kezdj a telepítésbe (`videogyar-telepites`). Írd be az `ALLAPOT.md`-be, hogy a
0. állomás kész.
