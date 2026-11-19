# Born, Not Made

A mother robot prints a baby robot inside its body, in gel, and gives birth in water.
MAS thesis, Ruipeng Wang, MIT Media Lab, 2026.

Live site: https://ruipwan.github.io/born-not-made/

| Tab | Path | What it is |
|---|---|---|
| Trunk | `index.html#trunk` | Why: soft robotics meets artificial life, under the umbrella of reproduction |
| Branches | `index.html#branches` | Side readings: matrix, cyberfeminism, artificial womb, labour |
| Build | `build/` | Parametric teardown: every part, spec, tolerance and source |
| Simulator | `simulator/` | Blender style console: signal, G-code, print, inflate, birth |
| Society | `society/` | Population model: relation, inheritance with drift, capacity |

Everything is static HTML and JavaScript (three.js r147 from jsDelivr). No build step.
Run locally with any static server, for example `python3 -m http.server` in this folder.

`simulator/scene_glb.txt` is the Blender scene (DexArm version, printing pose) exported as glTF and base64 encoded.
`build/data/*.json` holds the part list, physics numbers and sources used by the Build page.
