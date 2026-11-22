# Born, Not Made

One robot prints another inside the body, in gel, and gives birth in water. Speculative design: a robot giving birth to another.
MAS thesis, Ruipeng Wang, MIT Media Lab, 2026.

Live site: https://ruipwan.github.io/born-not-made/

| Tab | Path | What it is |
|---|---|---|
| Trunk | `index.html#trunk` | Why: soft robotics meets artificial life, under the umbrella of reproduction |
| Branches | `index.html#branches` | Side readings: matrix, cyberfeminism, artificial womb, labour |
| Build | `build/` | Parametric teardown: every part, spec, tolerance and source |
| Simulator | `simulator/` | Stage 3 console: dock under water, place the kit, print from G-code, push and inflate, swim. Data: `stage3.json`, `stage3_print.gcode` (from `bnm_design/stage3/physics.py`). Stage 2 kept in `simulator/old_/stage2/` |
| Society | `society/` | Population in 3D, simplified bodies in one tank close to square under small fixed spot lights: pairs touch at the opening, a body with a tail prints the newborn, tail or no tail is inherited. Earlier 2D model kept in `society/old_/` |
| Academia Research | [`index.html#academia`](https://ruipwan.github.io/born-not-made/#academia) / [`academia/`](https://ruipwan.github.io/born-not-made/academia/) | Image-led reference atlas: universities, labs, artistic works, research keywords, project relevance, and PhD pathways |

Everything is static HTML and JavaScript (three.js r147 from jsDelivr). No build step.
Run locally with any static server, for example `python3 -m http.server` in this folder.

`simulator/scene_glb.txt` is the Blender scene (DexArm version, printing pose) exported as glTF and base64 encoded.
`build/data/*.json` holds the part list, physics numbers and sources used by the Build page.

## Updating Academia Research

Entries live in `academia/data.js` as the `window.ACADEMIA_REFERENCES` array. Each entry includes school, lab, researchers, a specific project, externally hosted and credited artwork image (when a reliable one is available), links to the project, research lab and doctoral programme, relevance to *Born, Not Made* / *Baby Robot*, keywords and a dated admissions note. The page is generated client-side by `academia/render.js` and embedded as the `Academia Research` tab in `index.html`. Entries with a missing/blocked image render a typographic fallback instead of a broken icon. Recheck changing admissions dates before relying on them.
