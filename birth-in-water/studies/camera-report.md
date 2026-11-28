# Birth in Water • first picture assembly

The first continuous take changes the question. The small body takes much longer to cross the rim than to traverse its own length after release. The carrier yaws too. Movement belongs to the pair and to the water in the frame. The shot cannot resolve what produced each increment of motion. Keep the entire wait. In the next edit try cutting to the carrier after the visitor's eye has followed the smaller body away.

| Assembly | Artist source and source time | What the image establishes |
|---|---|---|
| 0–7 s | [Water Beings](https://vimeo.com/1229413082), 7–14 s | Excerpt from the digital ecology. Rui describes seven chromatic generations and contact-triggered succession. This excerpt cannot identify all seven by eye. |
| 7–43 s | [Baby came out and run](https://vimeo.com/1147548218), 1–37 s | Continuous real-time recorded tank view, prototype with rounded rectangular body. The smaller body emerges at the right; the larger body turns. Retain source audio in this shot. |
| 43–48.15 s | [Creative AI 2026 • Born, Not Made](https://vimeo.com/1238506916), 23.85–29 s | Another take, visibly different physical prototype. Specular ripples and a copper-coloured interior. An editorial juxtaposition across versions. Source soundtrack omitted. |
| 48.15–56.15 s | Water Beings, 49–57 s | Return to the digital population as another time scale. Source soundtrack omitted. |

Project media are from Ruipeng Wang's own published project pages: [Water Beings](https://ruipengwang.space/water-beings) and [Born, Not Made](https://ruipengwang.space/born-not-made). No third-party wildlife film or music was added. Reuse in this project study follows the artist's request. No open redistribution licence is asserted.

The overview credits Ruipeng Wang (director, initial prototype, software and hardware), Vera Yu Wu (narrative discussion and visual expression), Jimmy Haochen Xu (video editing and Unreal Engine), Kexin Wang (material) and Leo Liu (music). Contributors listed there are Jacob Li, Yue Yang, Yufan Xie, Richard Haoxi Zhang, Chien Lu, Manini Banerjee, Kenza FeNandez and Sarah Omellas; confirm spellings against the artist's credit sheet before final projection.

## Material distinctions

The optical test uses the repository's two printable STL files in millimetres. Their design belongs to the simplified split-shell proposal. Meshes, simulated milky material, light and displaced water surface are digital. The print plan describes mounting features and estimated fits and weights; the earlier exhibited prototype in the film has a different contour. The footage supports release in water. An actuator diagram in the overview describes a pump. Neither the overhead take nor the render measures force, confirms closed-loop sensing, or documents in-body printing. In the earlier prototype the offspring was made separately and loaded. See the [artist's technical presentation](../../artistic/) and the [design file and print plan](../../simulator/simple/print/PRINT_PLAN.md).

## Shots to carry into the gallery

Kingma asks what would count as being part of a gestating organism. A fabricated chamber makes containment trivial to illustrate. It leaves parthood unresolved. Ask what the carrier loses on release: changes of orientation can be seen, changes of function would need another test. [Kingma, 2019](https://doi.org/10.1093/mind/fzy087)

Ripley's measurements in two pipefish species distinguish pouch fluid from the surrounding sea and track changes in that relationship through gestation. The useful image here is a boundary maintaining a difference over time. The optical render can show a surface; it cannot show osmotic regulation in a robot. [Ripley, 2009](https://pubmed.ncbi.nlm.nih.gov/19447186/)

Feitl and colleagues observed overlapping boundary layers at the lappets of small ephyrae. Their measured swimming regime makes the water between tissue lobes part of an effective paddle. In this film, compare attached water, a rapidly opening gap and the wake against an unmoving tank edge. A larger machine requires separate flow measurements. [Feitl et al., 2009](https://authors.library.caltech.edu/records/mfs4x-vv256)

Painlevé recalls missing a seahorse birth after thirty-six hours at the camera. A hand-operated bellows helped keep his filming subjects alive. The account changes where to put a second camera: the operator, the tubing and the apparatus that maintains the take. Use continuous capture, a fixed wide camera and a second locked seam-height lens for any new shoot. Start both before priming; keep running through reset. Black drape on the camera side and lateral light let the near glass remain legible. [Painlevé, Feet in the Water](https://jeanpainleve.org/writings-feet-water)

Mary Kelly's dated feeding schedule and record of washing a diaper liner locate care in repeated acts with durations. Place the attendant's reset log in the line of travel out of the room. A blank entry during downtime has as much consequence as a successful release. Invite the technician to decide what labour to record and whether their hands can appear. [Getty Research Institute, Mary Kelly Papers](https://www.getty.edu/research/special_collections/notable/kelly.html)

## Production checkpoint • 28 November UTC

Source take and artist page inspected approximately 01:43–01:46. This assembly was encoded and decoded by 01:48. The 1280 × 720 local assembly is H.264 with AAC, approximately 56.19 s. Source motion runs at its recorded speed. Compare [review frames](assembly-review.jpg). Shadow detail lifted slightly in the first tank take. The first Cycles plate took 44.64 s; a 10.46 s waterline proof revealed excessive bright noise and a visible corner of the water plane. The second render extends the surface toward the lens and revises light transport. Render timings are engine output, separate from time spent reviewing.

The sound of the first take is quiet. Do not attribute it to a hydrophone or a particular device. Measure its level at the room playback position and listen against the actual plant before choosing a mix. For a final quiet-room version, keep the film visually intelligible, label abrupt returns to the digital population, and credit each prototype independently. Current assembly is a study cut.

## Looking twice at the last point of contact

A 480 × 270 re-analysis of the first tank recording at 10 samples/s finds a second pale connected region at source 25.9 s, or film 31.9 s. Its nearest edge is already 7 pixels from the carrier's thresholded silhouette. By source 26.2 s the measured gap is 34 pixels. The young body was already visible before this threshold produced two distinct regions. Later, the mask loses it again. Overlap, occlusion, the frame edge and the colour threshold all limit what this measurement can say. Distances are image-plane pixels. [Trace data](tank-trace.csv) · [measurement script](../production/track_release.py).

The second sound pass adds a composed stereo score. One narrow resonance can be heard before the mask divides; a second emerges as the two silhouettes become separable. Its pitch and stereo spread follow the image-space gap. The score makes the observer's criterion audible. It supplies no evidence of a pump, valve or independent propulsion. The original tank track measured −74.0 dB mean and −40.1 dB peak by FFmpeg volumedetect. An initial 960 × 540 audio review measured −28.1 LUFS integrated and −15.1 dB true peak. The separate source and score can be remixed for the venue. Play with captions and muted for the silent visit.

## Contact insert from the 4K camera file

[Contact study · 20 s](../media/contact-study.mp4) compares a fixed 1440 × 810 pixel crop of the artist's 3840 × 2160 record with a full-frame view. Both are from the same camera, in chronological order. Source 15.15–26.40 s holds on the opening. At 26.40 s the cut widens, leaving the previous carrier on screen as the smaller body travels. The film never needs to animate a second release. Along the edge of the smaller body, the change from contact shadow to a visible green channel is legible at this scale. The crop discards the far tank edge, so it cannot replace the wide shot as evidence of relative whole-body movement. [Frame review](contact-review.jpg) · [edit recipe](../production/contact_edit.py)

The artist's page credits Di Wu for 3D printing material and robotic arm work, Kexin Wang for arm control, Vera Yu Wu for narrative and visual expression, Jimmy Haochen Xu for visual development and Unreal Engine, and Leo Liu for background music. Credits on the overview itself describe the contributions for that version somewhat differently. Preserve both sets in context. The artist describes touch as part of the installation design. The two excerpts provide no timing evidence for touch, a heartbeat threshold, hydraulic pressure, or active steering. The existing VISAP installation photograph shows a tank below the luminous population and reflections of the projection on the glass. It supports an optical separation test; visitor occupancy and viewing heights cannot be inferred from it.

### What the workshop record settles

The first tank movie on the artist's portfolio is the same Vimeo source embedded twice in the 2025 HTMAA final project. The artist's final assembly account explicitly says the phone interface commanded the pump and inflated the internal structure. Separate propulsion tests document an off-centre outlet producing rotation and a tube redirecting the jet. The child had its own pump. This supports operator control, a hydraulic release mechanism and prototype propulsion in this version. It does not locate a motor command within a particular frame. The pale hull and little wake can be seen; individual pump contributions cannot be separated from the image alone. [Workshop record, final assembly and propulsion tests](https://fab.cba.mit.edu/classes/863.25/people/RuipengWang/week16.html)

The VISAP catalogue describes touch-assisted participation and the physical/digital pairing. It gives no measured heartbeat threshold or proof of in-body printing. Public labels should specify which apparatus, media and interaction are actually present on exhibition day. The first-generation phone-controlled test and the later public touch design are distinct. [IEEE VIS Arts Program, Born, Not Made](https://visap.net/2026/artwork-4.html)

### The touch mechanism in the later documentation

The 150-second *Born, Not Made* film embedded on the artist's project page is more specific than the exhibition catalogue. At 00:44.1 the artist's annotated frame shows a hand on the mother and describes capacitive touch increasing pump drive to speed release. This is documentation of a particular touch-assisted implementation. It gives a defensible gallery label: “In this version, touch changes the pump drive.” The source supplies no pressure trace, response latency, heartbeat measurement, visitor outcome or evidence that the simple printable shell in the optical test uses the same electronics. The 2025 overhead take is separately documented as phone-initiated. Keep these material histories distinct. [Artist's project page, third embedded film](https://ruipengwang.space/born-not-made) · [VISAP catalogue](https://visap.net/2026/artwork-4.html)
