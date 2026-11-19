# -*- coding: utf-8 -*-
"""Gépfelmérés: rendszer, processzor, memória, videókártyák, szabad hely, meglévő eszközök → gep.json.

    python gepfelmeres.py [--ki gep.json] [--mappa <munkamappa>]

Csak a standard könyvtárat használja, és semmit nem telepít. Windowson, macOS-en és Linuxon is fut;
amit nem tud kiolvasni, azt "ismeretlen"-nek írja, és a felhasználótól kell megkérdezni.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys


def _parancs(args: list, ido: int = 20) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=ido)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _ps(script: str) -> str:
    return _parancs(["powershell", "-NoProfile", "-Command", script], 40)


def gyarto(nev: str) -> str:
    n = nev.lower()
    if any(k in n for k in ("nvidia", "geforce", "rtx", "quadro", "tesla")):
        return "nvidia"
    if any(k in n for k in ("amd", "radeon", "ati ")):
        return "amd"
    if any(k in n for k in ("intel", "arc", "iris", "uhd graphics")):
        return "intel"
    if "apple" in n or re.search(r"\bm[1-9]\b", n):
        return "apple"
    return "egyeb"


VIRTUALIS = ("microsoft basic", "remote display", "virtual", "vmware", "parsec", "citrix", "hyper-v")


# --- processzor és memória ------------------------------------------------------------------------
def processzor() -> dict:
    rendszer = platform.system()
    nev, magok = platform.processor() or "ismeretlen", None
    if rendszer == "Windows":
        ki = _ps("Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores | ConvertTo-Json")
        try:
            d = json.loads(ki)
            d = d[0] if isinstance(d, list) else d
            nev, magok = d.get("Name", nev).strip(), d.get("NumberOfCores")
        except (ValueError, AttributeError):
            pass
    elif rendszer == "Darwin":
        nev = _parancs(["sysctl", "-n", "machdep.cpu.brand_string"]) or nev
        m = _parancs(["sysctl", "-n", "hw.physicalcpu"])
        magok = int(m) if m.isdigit() else None
    elif rendszer == "Linux":
        try:
            info = open("/proc/cpuinfo", encoding="utf-8").read()
            m = re.search(r"model name\s*:\s*(.+)", info)
            nev = m.group(1).strip() if m else nev
            magok = len({(a, b) for a, b in re.findall(r"physical id\s*:\s*(\d+).*?core id\s*:\s*(\d+)", info, re.S)}) or None
        except OSError:
            pass
    return {"nev": nev, "magok": magok, "szalak": os.cpu_count(), "architektura": platform.machine()}


def memoria_gb() -> float | None:
    rendszer = platform.system()
    try:
        if rendszer == "Windows":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 2**30, 1)
        if rendszer == "Darwin":
            return round(int(_parancs(["sysctl", "-n", "hw.memsize"])) / 2**30, 1)
        if rendszer == "Linux":
            for sor in open("/proc/meminfo", encoding="utf-8"):
                if sor.startswith("MemTotal:"):
                    return round(int(sor.split()[1]) / 2**20, 1)
    except (OSError, ValueError, AttributeError):
        pass
    return None


# --- videókártyák ---------------------------------------------------------------------------------
def _nvidia_smi() -> list[dict]:
    ki = _parancs(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"])
    lista = []
    for sor in ki.splitlines():
        reszek = [r.strip() for r in sor.split(",")]
        if len(reszek) >= 2:
            try:
                vram = round(float(reszek[1]) / 1024, 1)
            except ValueError:
                vram = None
            lista.append({"nev": reszek[0], "gyarto": "nvidia", "vram_gb": vram,
                          "illeszto": reszek[2] if len(reszek) > 2 else None, "forras": "nvidia-smi"})
    return lista


def _windows_gpu() -> list[dict]:
    lista = []
    # A Win32_VideoController.AdapterRAM 4 GB fölött hibás, ezért a regisztrációs adatbázisból olvasunk.
    try:
        import winreg
        kulcs = r"SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, kulcs) as k:
            i = 0
            while True:
                try:
                    al = winreg.EnumKey(k, i)
                except OSError:
                    break
                i += 1
                if not al.isdigit():
                    continue
                try:
                    with winreg.OpenKey(k, al) as a:
                        nev = winreg.QueryValueEx(a, "DriverDesc")[0]
                        try:
                            mem = winreg.QueryValueEx(a, "HardwareInformation.qwMemorySize")[0]
                        except OSError:
                            mem = None
                        try:
                            illeszto = winreg.QueryValueEx(a, "DriverVersion")[0]
                        except OSError:
                            illeszto = None
                except OSError:
                    continue
                if isinstance(mem, bytes):
                    mem = int.from_bytes(mem[:8], "little")
                lista.append({"nev": nev, "gyarto": gyarto(nev),
                              "vram_gb": round(mem / 2**30, 1) if isinstance(mem, int) and mem > 0 else None,
                              "illeszto": illeszto, "forras": "registry"})
    except ImportError:
        pass
    if not lista:
        ki = _ps("Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion | ConvertTo-Json")
        try:
            d = json.loads(ki)
            for g in (d if isinstance(d, list) else [d]):
                ram = g.get("AdapterRAM") or 0
                lista.append({"nev": g.get("Name", "?"), "gyarto": gyarto(g.get("Name", "")),
                              "vram_gb": round(ram / 2**30, 1) if ram else None,
                              "illeszto": g.get("DriverVersion"), "forras": "wmi (4 GB fölött pontatlan)"})
        except ValueError:
            pass
    return lista


def _mac_gpu() -> list[dict]:
    ki = _parancs(["system_profiler", "SPDisplaysDataType", "-json"], 40)
    lista = []
    try:
        for g in json.loads(ki).get("SPDisplaysDataType", []):
            nev = g.get("sppci_model") or g.get("_name", "?")
            vram = g.get("spdisplays_vram") or g.get("spdisplays_vram_shared") or ""
            m = re.search(r"(\d+)\s*(GB|MB)", str(vram))
            gb = (int(m.group(1)) / (1024 if m.group(2) == "MB" else 1)) if m else None
            lista.append({"nev": nev, "gyarto": gyarto(nev), "vram_gb": gb, "illeszto": None,
                          "forras": "system_profiler"})
    except ValueError:
        pass
    return lista


def _linux_gpu() -> list[dict]:
    lista = []
    for sor in _parancs(["lspci"]).splitlines():
        if re.search(r"vga|3d|display", sor, re.I):
            nev = sor.split(": ", 1)[-1]
            lista.append({"nev": nev, "gyarto": gyarto(nev), "vram_gb": None, "illeszto": None, "forras": "lspci"})
    # AMD: a kernel kiírja a videómemória méretét
    for kartya in sorted(os.listdir("/sys/class/drm")) if os.path.isdir("/sys/class/drm") else []:
        f = os.path.join("/sys/class/drm", kartya, "device", "mem_info_vram_total")
        if re.fullmatch(r"card\d+", kartya) and os.path.exists(f):
            try:
                gb = round(int(open(f).read()) / 2**30, 1)
                for g in lista:
                    if g["gyarto"] == "amd" and g["vram_gb"] is None:
                        g["vram_gb"], g["forras"] = gb, "lspci + sysfs"
                        break
            except (OSError, ValueError):
                pass
    return lista


def videokartyak() -> list[dict]:
    rendszer = platform.system()
    nv = _nvidia_smi()
    if rendszer == "Windows":
        egyeb = _windows_gpu()
    elif rendszer == "Darwin":
        egyeb = _mac_gpu()
    else:
        egyeb = _linux_gpu()
    # az nvidia-smi adata a pontosabb; a többiből az NVIDIA-sorokat kihagyjuk, ha az nvidia-smi futott
    lista = nv + [g for g in egyeb if not (nv and g["gyarto"] == "nvidia")]
    return [g for g in lista if not any(v in g["nev"].lower() for v in VIRTUALIS)]


# --- eszközök és hely -----------------------------------------------------------------------------
def _verzio(args: list, minta: str = r"(\d+\.\d+(\.\d+)?)") -> str | None:
    if not shutil.which(args[0]):
        return None
    ki = _parancs(args)
    m = re.search(minta, ki)
    return m.group(1) if m else (ki.splitlines()[0][:60] if ki else "megvan")


def eszkozok() -> dict:
    return {
        "python": platform.python_version(),
        "node": _verzio(["node", "--version"]),
        "npx": bool(shutil.which("npx")),
        "ffmpeg": _verzio(["ffmpeg", "-version"], r"ffmpeg version (\S+)"),
        "ffprobe": bool(shutil.which("ffprobe")),
        "git": _verzio(["git", "--version"]),
        "nvidia_smi": bool(shutil.which("nvidia-smi")),
    }


def ajanlas(g: dict) -> dict:
    """Egyszerű első tipp a felméréshez; a skill táblázata és a motor saját leírása dönt."""
    kartyak = [k for k in g["videokartyak"] if k["gyarto"] in ("nvidia", "amd", "intel", "apple")]
    rendszer = g["rendszer"]["nev"]
    sorrend = {"nvidia": 0, "apple": 1, "amd": 2, "intel": 3}
    kartyak.sort(key=lambda k: (sorrend[k["gyarto"]], -(k["vram_gb"] or 0)))
    if not kartyak:
        return {"gpu_ut": "cpu", "megjegyzes": "nincs ismert videókártya: processzoros vagy felhős hangmotor"}
    k = kartyak[0]
    ut = {"nvidia": "cuda", "apple": "mps", "intel": "xpu",
          "amd": "rocm" if rendszer == "Linux" else "vulkan/directml (korlátozott)"}[k["gyarto"]]
    megj = f"{k['nev']}"
    if k["vram_gb"]:
        megj += f", {k['vram_gb']} GB"
        if k["gyarto"] != "apple" and k["vram_gb"] < 6:
            megj += " (kevés lehet nagyobb hangmodellhez)"
    elif k["gyarto"] == "intel" and "arc" not in k["nev"].lower():
        megj += " (beépített grafika: valószínűleg processzoros vagy felhős hang a jobb)"
    return {"gpu_ut": ut, "kartya": k["nev"], "megjegyzes": megj}


def felmer(mappa: str) -> dict:
    hely = shutil.disk_usage(os.path.abspath(mappa))
    g = {
        "rendszer": {"nev": platform.system(), "verzio": platform.release(), "reszletes": platform.platform()},
        "processzor": processzor(),
        "memoria_gb": memoria_gb(),
        "videokartyak": videokartyak(),
        "szabad_hely_gb": round(hely.free / 2**30, 1),
        "munkamappa": os.path.abspath(mappa),
        "eszkozok": eszkozok(),
    }
    g["ajanlas"] = ajanlas(g)
    return g


def osszefoglalo(g: dict) -> str:
    p, e = g["processzor"], g["eszkozok"]
    sorok = [
        f"Rendszer:     {g['rendszer']['nev']} {g['rendszer']['verzio']}",
        f"Processzor:   {p['nev']} ({p['magok'] or '?'} mag, {p['szalak']} szál)",
        f"Memória:      {g['memoria_gb'] or 'ismeretlen'} GB",
    ]
    if g["videokartyak"]:
        for k in g["videokartyak"]:
            sorok.append(f"Videókártya:  {k['nev']} [{k['gyarto']}], "
                         f"{str(k['vram_gb']) + ' GB' if k['vram_gb'] else 'memória ismeretlen'}")
    else:
        sorok.append("Videókártya:  nem találtam (vagy csak virtuális)")
    sorok += [
        f"Szabad hely:  {g['szabad_hely_gb']} GB ({g['munkamappa']})",
        f"Python {e['python']} · Node {e['node'] or 'NINCS'} · FFmpeg {e['ffmpeg'] or 'NINCS'} · "
        f"git {e['git'] or 'nincs'}",
        f"Első tipp:    {g['ajanlas']['gpu_ut']} – {g['ajanlas']['megjegyzes']}",
    ]
    if not e["node"] or not e["ffmpeg"]:
        sorok.append("Hiányzik:     " + ", ".join(n for n in ("node", "ffmpeg") if not e[n]) +
                     " (a telepítés állomás pótolja)")
    return "\n".join(sorok)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gépfelmérés a videógyárhoz")
    ap.add_argument("--ki", default="gep.json", help="kimeneti JSON (alapból gep.json)")
    ap.add_argument("--mappa", default=".", help="a munkamappa (a szabad helyhez)")
    a = ap.parse_args(argv)
    g = felmer(a.mappa)
    with open(a.ki, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=1)
    print(osszefoglalo(g))
    print(f"\nkiírva: {os.path.abspath(a.ki)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
