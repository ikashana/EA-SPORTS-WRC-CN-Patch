# Translation Guide for EA SPORTS WRC Simplified Chinese Patch

1. Read `glossary.json` in this directory and follow all terminology consistently.
2. Read your assigned `translations/chunks_src/chunk_XX.json` (each item has `id`, `k` key hint, and `en` source text).
3. Translate every `en` string into natural, idiomatic, rally-authentic **Simplified Chinese**.
4. **Formatting & Placeholders (CRITICAL)**:
   - Preserve ALL `<cf>`, `<lf>`, `<img .../>`, `<url>`, `<player nickname>`, `<player name>` tags verbatim. Do NOT convert `<cf>` to `\n`.
   - Preserve ALL `{...}` format arguments (e.g. `{0}`, `{1}`, `{x_value}`, `{champ}`, etc.) verbatim with exact spelling and count.
   - Keep standard acronyms & proper nouns in English/original form where appropriate: `WRC`, `WRC2`, `JWRC`, `FIA`, `EA`, `Racenet`, `DLSS`, `FSR`, `XeSS`, `VR`, `ABS`, `FFB`, `HDR`, `RPM`, `km/h`, `MPH`, `PS4`, `PS5`, `Xbox`, `Steam`, and real driver surnames (in broadcaster/team phrases like `and, Tänak` -> `以及 Tänak`).
5. Write your output to `translations/chunks_zh/chunk_XX.json` as a UTF-8 JSON object mapping `"id"` -> `"translated string"`.
6. Run `python3 scripts/validate_translations.py chunk_XX.json` from the repository root and fix any errors until it prints `[OK]   chunk_XX.json` and exits 0.
