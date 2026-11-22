# Print plan for the Bambu Lab H2S: simplified Born, Not Made, round 8

Two printed parts, each in one piece: the tail and the head. Both files are in millimeters, watertight, already oriented as they lie on the plate (docking face down, centered, lowest point at z = 0).

## Files

| Part | File | Watertight (trimesh) | Bodies | Plastic, cm3 | Mass, kg | Time, h | Box on the plate, mm | Margin to 340 x 320 x 340, mm |
|---|---|---|---|---|---|---|---|---|
| Tail | `bnm_simple_tail.stl` | yes | 1 | 808 | 1.03 | 23 | 336 x 314 x 305 | 4, 6, 35 |
| Head | `bnm_simple_head.stl` | yes | 1 | 716 | 0.91 | 21 | 336 x 314 x 335 | 4, 6, 5 |

Files: `/home/claude/bnm_design/simple/print/` and, published, `simulator/simple/print/`. The script is `print_pkg.py` (run as `BNM_DBG0=print_pkg.py python3 design.py`); the numbers above are in `print/print_report.json`.

How the solids are made: the simulated inner surface is kept exactly. The 3 mm wall is grown outward from it, section by section, so the space the arm works in is the simulated one. The ridge of the tail shell that ends the gel is a solid rib (the outside floor runs flat under it). Checked with trimesh after writing and reading the STL again: watertight, consistent winding, one body, volume, bounding box.

Mass is mesh volume times 1.27 g per cm3 (PETG). Time is mesh volume divided by a flow of 12 mm3 per second, times 1.25 for travel and slow outer walls. The slicer gives the real numbers; supports are not in these figures (allow about 10 to 15 percent more plastic for the tail).

## What is in each print

Tail: the shell from the tip to the docking plane; the ridge in front of the arm base; the two saddles (ledges, stops, one plate under the ledges, one bracket to the wall each); the kit store (tray on four posts); three magnet bosses with pockets; two alignment pins; the seam flange round the gel and the floor sill; four bosses for the arm base.

Head: the shell from the docking plane to the mouth, with the lower shell that holds the gel and the long lower lip; three seat bumps; three bosses with pockets for steel discs; two pin sockets; the seam flange with the cord groove.

Nothing else is printed. No baffle, no ballast block, no separate mouth piece.

## Orientation: three compared for each part

| Part | Orientation | Box, mm | Fits | Margin, mm | Overhang beyond 45 degrees, cm2 |
|---|---|---|---|---|---|
| Tail | on the docking face | 336 x 314 x 305 | yes | 4, 6, 35 | 1126 |
| Tail | on the floor | 305 x 314 x 336 | yes | 35, 6, 4 | 561 |
| Tail | on the side | 305 x 336 x 314 | yes | 4, 15, 26 | 1429 |
| Head | on the docking face | 336 x 314 x 335 | yes | 4, 6, 5 | 201 |
| Head | on the floor | 335 x 314 x 336 | yes | 5, 6, 4 | 922 |
| Head | on the side | 335 x 336 x 314 | no | 4, -16, 26 | 1583 |

Choice for both: on the docking face.

Reasons, tail. All three fit. On the docking face the seam face, the magnet pockets, the pins and the flange are printed on the plate, so the face that must seal is the flattest surface of the part. The layers are rings round the body axis: the water pressure on the shell and the pull of the magnets load each layer in its own plane, not across the bond between layers. The overhang is the largest in area of the three, but it lies where it harms least: the inside of the taper near the tip (dry, behind the arm, at the far end of the view), the underside of the saddles and the kit tray, and the ridge. On the floor the overhang is half as large, but it is the whole inside of the roof, the clearest and most visible surface, with supports 300 mm tall standing on the floor between the saddles; and the seam face would be built from layer edges. On the side the overhang is the largest and one whole flank carries supports.

Reasons, head. On the docking face the head is a bell that closes upward toward the mouth with walls steeper than 45 degrees nearly everywhere: the overhang is the smallest by far, mainly the shoulder where the lower shell meets the wide upper shell (a ledge about 50 to 100 mm wide at each side, 105 mm above the floor of the body) and the underside of the lower lip. Supports stand outside the gel volume or on the lip, not inside the bowl walls. The mouth rim is printed last, as a clean open edge. On the floor the inside of the whole roof needs support and the gel floor is printed on the plate (good for tightness, bad for the roof). On the side the head does not fit (336 mm across the 320 mm axis).

Layer seam: set the seam to "aligned" and to the rear, so it runs along the keel line under the floor (tail and head), away from the gel walls at the sides and away from the roof.

Margins are small: 4 mm in one plate direction and 6 mm in the other for both parts, 5 mm in height for the head. There is no room for a brim or a skirt on the 336 mm side: switch both off, and switch off the purge line and the prime tower (one material).

## Material and settings

- Material: clear PETG, dried (65 degrees C for 6 hours), from one batch for both parts.
- Nozzle 0.6 mm hardened or stainless; layer height 0.24 mm for the shell. A 0.4 mm nozzle works with 0.2 mm layers and more loops, at about twice the time.
- Wall: the 3 mm wall as five loops of 0.6 mm, no infill inside the wall (set wall loops to 5 or more, so the slicer fills the wall with loops only). Loops in one direction read clearer than loops plus infill.
- For clarity: print slow and hot. Outer and inner walls 30 to 40 mm per second, 250 to 255 degrees C, part cooling fan 0 to 20 percent, flow raised 2 to 3 percent so the loops fuse without air lines. Volumetric flow kept under 12 mm3 per second.
- What to expect: a 3 mm PETG wall printed this way is translucent, like ribbed or frosted glass, not optically clear. Shapes and movement inside are visible, the arm and the newborn read well against a lit background, fine detail does not. The layer lines run as rings round the body. A thin coat of clear epoxy or clear polyurethane outside and inside fills the lines and brings the wall much closer to glass clear; sanding to 2000 grit and polishing is the alternative for the outside.
- Supports: tree supports, on build plate and on model, threshold 45 degrees, top interface 2 layers with 0.2 mm gap. Expected places are listed above. The saddles, the kit tray and the bosses are small and break clean.
- Bed: textured PEI at 80 degrees C with glue stick as a release (PETG bonds hard to smooth PEI). Chamber closed, not heated above 45 degrees C.
- First layer: the docking face. Elephant foot compensation 0.15 mm, so the pockets and the groove stay to size.

## Making the gel shell tight

The gel is held by the printed shell itself: the lower shell of the head and of the front of the tail, and the docking seam.

1. Solid wall: five fused loops, no infill, flow slightly raised, as above. A wall printed this way usually holds water; pinholes sit at the layer seam.
2. Seam placement: aligned, on the keel under the floor, as above, where a coat is easy to apply and not seen.
3. A coat: one coat of clear, low viscosity epoxy brushed inside the gel shell of both parts, up to 20 mm above the gel line (the line is 100 mm above the inner floor), and along the seam line outside. This is the measure that makes tightness certain; it also clears the wall there.
4. Test before any gel: fill each part with water to the gel line, standing on paper, for one hour.

The gel stands 10 mm above the water outside, so a leak runs outward, and the gel has a yield stress: it does not pass a gap under about 2 mm at that head. The coat is still worth doing, because water must not creep in when the gel is out.

## Docking face

In the frame of the simulation the docking plane stands at x = 32 mm; on the plate it is z = 0 for both parts.

- Magnets: three K&J DC2 N52 discs, 19.05 mm across, 3.17 mm thick, in the tail. Pockets 19.3 mm across and 3.4 mm deep, open to the face, in bosses 27 mm across inside the ring: two at the sides 215 mm above the floor, one at the top. Positions in the body frame (x, y, z in mm): [[32.0, 140.3, 215.0], [32.0, -140.3, 215.0], [32.0, 0.0, 319.5]]. Glue the magnets in with epoxy, flush or 0.2 mm under the face, all with the same pole out.
- Steel discs in the head, opposite the magnets: pockets 19.3 mm across and 2.2 mm deep for discs 19 mm across and 2 mm thick, glued in.
- Alignment: two pins of 5 mm, 4 mm proud, on the tail face at the sides, 150 mm above the floor; sockets of 5.4 mm in the head. Positions: [[32.0, 146.2, 150.0], [32.0, -146.2, 150.0]].
- Seal, because the gel crosses the seam: round the lower shell, where the gel is, both faces widen to a flange 10 mm wide and 4 mm thick, from the floor up to 102 mm (2.4 mm above the gel). Across the floor the flange is a sill 4 mm high on the inside; the needle tip passes 6 mm above it. The head face carries a groove 3.2 mm wide and 2.2 mm deep for a soft silicone cord of 3 mm, shore 30 to 40 A; the tail face is flat. The cord runs up both sides and across the floor in one piece; its two ends stand above the gel line. The three magnets give about 160 N in all; a 3 mm cord of that hardness over 0.35 m needs roughly 50 to 100 N for 0.5 mm of squeeze (estimate, to test). If the squeeze is too hard, use a softer cord or a hollow one.
- The groove has square corners where the sides meet the floor: file a small radius, or cut the cord and butt the pieces with silicone glue.

## Arm base

Four bosses on the tail floor, 10 mm across and 5 mm tall, with a blind bore of 5.6 mm, 7 mm deep, for M4 heat set inserts. The 5 mm steel plate under the arm has four matching 10.5 mm holes and sits on the floor round the bosses; the arm base is screwed through the plate into the inserts. Positions in the body frame (x, y in mm): [[-65.0, 45.0], [-65.0, -45.0], [-165.0, 45.0], [-165.0, -45.0]]. This pattern is an ESTIMATE: 100 x 90 mm round the arm axis. The hole pattern of the Rotrics DexArm base was not verified from a drawing; measure the arm and move the bosses in `print_pkg.py` (list BASE_H) before printing. The bores are blind, so the floor stays tight.

## Cuts

None. Both parts print in one piece. If a printer with less height is used, the earlier plan applies: split on the horizontal plane at half height, inner lips with M3 bolts on a 50 mm pitch, sealant below the waterline.

## Not checked here

- The files were checked as meshes, not sliced: no slicer was run from here. Slice both before ordering filament and read the real time, mass and support volume.
- Tolerances of the pockets (19.3 mm), the pin sockets and the groove are first guesses for a tuned H2S; print the first 6 mm of each part as a test of the docking face.
- The saddle ledges are thin (3 mm) and carry about 0.1 kg each; they are meant to be printed with the shell. If they sag, raise their thickness in the script.
