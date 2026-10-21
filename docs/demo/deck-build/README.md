# Rebuilding the deck (docs/deck-qa-pipeline.en.pptx)

Built with python-pptx on the user's own Astek template (`~/Downloads/Astek Vietnam_AI powered QA Automation .pptx`).
The cover and agenda slides are reused from the template; every other slide uses layout `3_Page_Standard`.

Palette (user's rule: 4 main colours): dark green 012E2B, light green 02BA71, white, light grey F2F2F2. Body text = template charcoal 332C2C. No red.

1. Icons: `npm i react react-dom react-icons sharp` in a temp folder, then `node mkicons.js` (writes `icons/<Name>_<HEX>.png`).
2. `python3 -m venv venv && venv/bin/pip install python-pptx lxml pillow`
3. Edit the `SRC`, `OUT` and `ICONS` paths at the top of `build_deck.py`, then `venv/bin/python build_deck.py`.
4. Preview: no LibreOffice on this Mac. macOS QuickLook (`qlmanage -t`) renders only the first slide of a file and does NOT draw the
   template's freeform shapes (agenda left panel, text inside the black tag), so open the result in PowerPoint/Keynote to check those.
5. python-pptx gotcha: after deleting slides, rename the kept slide parts (`slide.part.partname = PackURI(...)`) before adding new ones, or the package gets duplicate part names.
Speaker notes of each slide = the English script; keep them in sync with `docs/deck-outline.md`.
