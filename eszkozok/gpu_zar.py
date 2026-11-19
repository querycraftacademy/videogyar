# -*- coding: utf-8 -*-
"""Egyszerre csak egy nagy GPU-s munka: zárfájl a hanggenerálás és a render között.

    from gpu_zar import gpu_zar
    with gpu_zar("render"):
        ...

    python gpu_zar.py allapot                 # ki fogja most a videókártyát
    python gpu_zar.py futtat -- <parancs …>   # egy parancs futtatása a zár alatt

A zárfájl a rendszer ideiglenes mappájában van, így a gép minden videógyár-munkamenete ugyanazt látja.
Ha a zárat tartó folyamat már nem fut (pl. elszállt), a zárat magától felszabadítja.
"""
from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
import time

ZAR = os.path.join(tempfile.gettempdir(), "videogyar_gpu.lock")


def _el(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        kod = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(kod))
        ctypes.windll.kernel32.CloseHandle(h)
        return kod.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def allapot() -> dict | None:
    try:
        with open(ZAR, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    return d if _el(int(d.get("pid", 0))) else None


@contextlib.contextmanager
def gpu_zar(cimke: str, varakozas: float = 5.0, max_var: float | None = None):
    kezdet = time.time()
    szolt = False
    while True:
        try:
            fd = os.open(ZAR, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"pid": os.getpid(), "cimke": cimke, "kezdet": time.strftime("%H:%M:%S")}, f)
            break
        except FileExistsError:
            ki = allapot()
            if ki is None:  # elárvult zár
                with contextlib.suppress(OSError):
                    os.remove(ZAR)
                continue
            if not szolt:
                print(f"várok a videókártyára: most „{ki.get('cimke')}” fut ({ki.get('kezdet')} óta)", flush=True)
                szolt = True
            if max_var is not None and time.time() - kezdet > max_var:
                raise TimeoutError("a videókártya nem szabadult fel időben")
            time.sleep(varakozas)
    try:
        yield
    finally:
        with contextlib.suppress(OSError):
            os.remove(ZAR)


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] == "allapot":
        ki = allapot()
        print("szabad" if ki is None else f"foglalt: {ki.get('cimke')} (pid {ki.get('pid')}, {ki.get('kezdet')} óta)")
        return 0
    if a[0] == "futtat":
        parancs = a[a.index("--") + 1:] if "--" in a else a[1:]
        with gpu_zar(" ".join(parancs)[:60]):
            return subprocess.call(parancs)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
