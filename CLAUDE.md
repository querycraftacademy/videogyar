# Videógyár (Claude Code)

@AGENTS.md

## Claude Code-specifikus megjegyzések

- A skilleket telepítsd a felhasználó munkamappájába: másold a csomag `skills/` mappájának tartalmát a
  `<munkamappa>/.claude/skills/` alá. Így a Claude Code magától betölti őket, amikor az adott feladatra kerül sor.
- A HyperFrames saját skilljei is hasznosak: `npx hyperframes skills` (a telepítés állomáson).
- A felhasználó házirendje a munkamappa gyökerében a `CLAUDE.md` legyen (sablon: `sablonok/HAZIREND.md`).
- Kifelé ható lépés előtt (feltöltés, publikálás) mindig kérdezz, akkor is, ha az engedélyrendszer engedné.
