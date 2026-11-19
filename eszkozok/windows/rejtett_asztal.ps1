# Egy parancsfájl futtatása KÜLÖN, LÁTHATATLAN Windows-asztalon, hogy semmi ne ugorjon fel a képernyőn.
#
# Miért: a HyperFrames egy fej nélküli Chrome-ot indít, aminek a gyerekfolyamatai Windowson saját
# konzolablakot kaphatnak. Ha a Windows Terminal az alapértelmezett terminál (Windows 11-en ez az alap),
# ezek felugró ablakként jelennek meg, és elveszik a fókuszt. Ami megbízhatóan működik: a folyamat egy
# másik asztalon fut (CreateDesktop), így minden ablaka oda kerül. A futás idejére a konzolok gazdája a
# klasszikus konzol (conhost), mert a Windows Terminal a saját asztalán nyitná meg őket; utána visszaáll.
#
# Használat:
#   rejtett_asztal.ps1 -Fajl C:\...\render_s0.cmd [-Mappa C:\...]
#   rejtett_asztal.ps1 -Vissza          # ha egy futás félbeszakadt, és a terminálbeállítás nem állt vissza
#
# A kilépési kód a futtatott parancsfájlé. A kimenetet a parancsfájl maga irányítsa naplóba (a rejtett
# asztal konzolja nem látszik).
param(
  [string]$Fajl = "",
  [string]$Mappa = (Get-Location).Path,
  [string]$Asztal = "videogyar_render",
  [switch]$Vissza
)

$KS = "HKCU:\Console\%%Startup"
$CONHOST = "{B23D10C0-E52E-411E-9D5B-C09FDF709C7D}"
$NEVEK = "DelegationConsole", "DelegationTerminal"
# Közös állapotfájl SZÁMLÁLÓVAL: több egyidejű futás is lehet; az első menti az eredetit, az utolsó állítja vissza.
$ALLAPOT = Join-Path $env:LOCALAPPDATA "videogyar_konzol.json"

function Olvas { if (Test-Path $ALLAPOT) { Get-Content $ALLAPOT -Raw | ConvertFrom-Json } else { $null } }
function Ir($a) { $a | ConvertTo-Json | Out-File $ALLAPOT -Encoding utf8 }

function Konzol-Rejtett {
  if (-not (Test-Path -LiteralPath $KS)) { New-Item -Path $KS -Force | Out-Null }
  $a = Olvas
  if ($null -eq $a) {
    $a = @{ db = 1 }
    foreach ($n in $NEVEK) { $a[$n] = (Get-ItemProperty -LiteralPath $KS -Name $n -ErrorAction SilentlyContinue).$n }
  } else {
    $a = @{ DelegationConsole = $a.DelegationConsole; DelegationTerminal = $a.DelegationTerminal; db = [int]$a.db + 1 }
  }
  Ir $a
  foreach ($n in $NEVEK) { Set-ItemProperty -LiteralPath $KS -Name $n -Value $CONHOST }
}

function Konzol-Vissza([switch]$Mind) {
  $a = Olvas
  if ($null -eq $a) { return }
  $db = [int]$a.db - 1
  if ($db -gt 0 -and -not $Mind) {
    Ir @{ DelegationConsole = $a.DelegationConsole; DelegationTerminal = $a.DelegationTerminal; db = $db }
    return
  }
  foreach ($n in $NEVEK) {
    $v = $a.$n
    if ($null -eq $v -or $v -eq "") { Remove-ItemProperty -LiteralPath $KS -Name $n -ErrorAction SilentlyContinue }
    else { Set-ItemProperty -LiteralPath $KS -Name $n -Value $v }
  }
  Remove-Item $ALLAPOT -Force
}

if ($Vissza) { Konzol-Vissza -Mind; "visszaállítva"; exit 0 }
if ($Fajl -eq "" -or -not (Test-Path -LiteralPath $Fajl)) { Write-Error "Nincs ilyen parancsfájl: $Fajl"; exit 2 }

if (-not ("VideogyarAsztal" -as [type])) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class VideogyarAsztal {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct STARTUPINFO {
    public int cb; public string lpReserved; public string lpDesktop; public string lpTitle;
    public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
    public short wShowWindow, cbReserved2;
    public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
  }
  [StructLayout(LayoutKind.Sequential)]
  public struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }

  [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  static extern IntPtr CreateDesktop(string name, IntPtr dev, IntPtr mode, int flags, uint access, IntPtr sa);
  [DllImport("user32.dll", SetLastError = true)] static extern bool CloseDesktop(IntPtr h);
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  static extern bool CreateProcess(string app, StringBuilder cmd, IntPtr pa, IntPtr ta, bool inherit,
    uint flags, IntPtr env, string dir, ref STARTUPINFO si, out PROCESS_INFORMATION pi);
  [DllImport("kernel32.dll")] static extern uint WaitForSingleObject(IntPtr h, uint ms);
  [DllImport("kernel32.dll")] static extern bool GetExitCodeProcess(IntPtr h, out uint code);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);

  public static int Futtat(string asztal, string parancs, string mappa) {
    IntPtr d = CreateDesktop(asztal, IntPtr.Zero, IntPtr.Zero, 0, 0x10000000, IntPtr.Zero);  // GENERIC_ALL
    if (d == IntPtr.Zero) throw new Exception("CreateDesktop hiba: " + Marshal.GetLastWin32Error());
    try {
      STARTUPINFO si = new STARTUPINFO();
      si.cb = Marshal.SizeOf(typeof(STARTUPINFO));
      si.lpDesktop = "WinSta0\\" + asztal;
      PROCESS_INFORMATION pi;
      // CREATE_NEW_CONSOLE: a konzol a rejtett asztalon jön létre, a gyerekfolyamatok ezt öröklik
      if (!CreateProcess(null, new StringBuilder(parancs), IntPtr.Zero, IntPtr.Zero, false,
                         0x00000010, IntPtr.Zero, mappa, ref si, out pi))
        throw new Exception("CreateProcess hiba: " + Marshal.GetLastWin32Error());
      WaitForSingleObject(pi.hProcess, 0xFFFFFFFF);
      uint kod; GetExitCodeProcess(pi.hProcess, out kod);
      CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
      return (int)kod;
    } finally { CloseDesktop(d); }
  }
}
"@
}

$teljes = (Resolve-Path -LiteralPath $Fajl).Path
Konzol-Rejtett
try {
  $kod = [VideogyarAsztal]::Futtat($Asztal, "cmd.exe /c `"$teljes`"", $Mappa)
} finally {
  Konzol-Vissza
}
exit $kod
