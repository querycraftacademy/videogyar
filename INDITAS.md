# Indító szöveg

Nyisd meg az AI-eszközödben a munkamappát (benne vagy mellette a letöltött `videogyar` csomaggal), és
másold be ezt:

```
Szia! Ebben a mappában van a „videogyar” csomag. Olvasd el az AGENTS.md-t, és építsük fel
együtt a videógyártó rendszert a gépemen.

Kezdd a gépem felmérésével, és amíg nem tudod, milyen gépen dolgozunk, ne telepíts semmit.
Utána kérdezz ki: milyen videókat szeretnék, milyen hangon, milyen stílusban, és mennyit
fizetnék felhős szolgáltatásért. Minden állomás után próbáld ki, amit építettél, és mondd
el röviden, mit csináltál. Feltölteni, fizetős szolgáltatást használni vagy bármit
nyilvánossá tenni csak az én kifejezett engedélyemmel szabad.
```

## Ha később folytatod

Egy új munkamenetben ennyi is elég:

```
Folytassuk a videógyárat: nézd meg az ALLAPOT.md-t, és mondd meg, hol tartunk és mi a következő lépés.
```

## Új videó, amikor már kész a rendszer

```
Új videót szeretnék erről: <téma>. Kb. <hossz> perc, a megszokott stílusban.
Előbb írd meg a szöveget jelenetenként, és csak az én jóváhagyásom után generálj hangot.
```

## Melyik AI-eszközzel?

| Eszköz | Megjegyzés |
|---|---|
| **Claude Code** (terminál, VS Code, asztali alkalmazás) | a `CLAUDE.md`-t magától olvassa; a skilleket a munkamappa `.claude/skills/` mappájába telepíti |
| **OpenAI Codex** (CLI, IDE) | az `AGENTS.md`-t magától olvassa |
| **Gemini CLI** | a `GEMINI.md`-t olvassa, ami az `AGENTS.md`-re mutat |
| **Cursor**, más szerkesztők ügynökmóddal | kérd meg, hogy olvassa el az `AGENTS.md`-t |
| **Csak csevegőfelület** (ChatGPT, Claude.ai a böngészőben) | működik, de lassabb: a parancsokat neked kell futtatnod, és az eredményt visszamásolnod. Ha teheted, válassz olyan eszközt, amelyik maga futtat parancsot. |
