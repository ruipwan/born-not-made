# Print plan for the Bambu Lab H2S: simplified Born, Not Made, round 11

Three prints, each in one piece: the head, the front of the tail and the rear of the tail. The two tail prints are joined for good (bonded and sealed) behind the arm. All files are in millimeters, watertight, already oriented as they lie on the plate (centered, lowest point at z = 0).

## Files

| Part | File | Watertight (trimesh) | Bodies | Plastic, cm3 | Mass, kg | Time, h | Box on the plate, mm | Margin to 340 x 320 x 340, mm |
|---|---|---|---|---|---|---|---|---|
| Head | `bnm_simple_head.stl` | yes | 1 | 733 | 0.93 | 21 | 336 x 314 x 335 | 4, 6, 5 |
| Tail, front | `bnm_simple_tail_front.stl` | yes | 1 | 803 | 1.02 | 23 | 336 x 314 x 251 | 4, 6, 89 |
| Tail, rear | `bnm_simple_tail_rear.stl` | yes | 1 | 375 | 0.48 | 11 | 318 x 222 x 226 | 22, 98, 114 |

Files: `/home/claude/bnm_design/simple/print/` and, published, `simulator/simple/print/`. The script is `print_pkg.py` (run as `BNM_DBG0=print_pkg.py python3 design.py`); the numbers above are in `print/print_report.json`. The single tail file of rounds 8 to 10 (`bnm_simple_tail.stl`) is replaced by the two tail files.

How the solids are made: the simulated inner surface is kept exactly. The 3 mm wall is grown outward from it, section by section, so the space the arm works in is the simulated one. The ridge of the tail shell that ends the gel is a solid rib (the outside floor runs flat under it). Checked with trimesh after writing and reading the STL again: watertight, consistent winding, one body, volume, bounding box.

Mass is mesh volume times 1.27 g per cm3 (PETG). Time is mesh volume divided by a flow of 12 mm3 per second, times 1.25 for travel and slow outer walls. The slicer gives the real numbers; supports are not in these figures (allow about 10 to 15 percent more plastic for the front of the tail).

Round 11: the tail is longer (462 mm from the docking plane to the tip, round 10: 302 mm) and runs out in a slender taper to a small point, so it no longer fits one plate. It is cut once, at x = -215 mm, 247 mm behind the docking plane and 22 mm behind the rearmost point the arm reaches. The head is unchanged.

## What is in each print

Head: the shell from the docking plane to the mouth, with the lower shell that holds the gel and the long lower lip; three seat bumps; three bosses with pockets for steel discs; two pin sockets; the seam flange with the cord groove.

Tail, front: the shell from the joint to the docking plane; the ridge in front of the arm base; the two saddles (ledges, stops, one plate under the ledges, one bracket to the wall each); the kit magazine (two rails on six posts, four end stops; three kits sit on it); three magnet bosses with pockets; two alignment pins; the seam flange round the gel and the floor sill; four bosses for the arm base. At the joint the front print ends in a plain open edge (the socket for the sleeve).

Tail, rear: the slender taper from the joint to the tip, closed at the tip, open at the joint, with the sleeve of the joint: 12 mm long, 2.5 mm thick, standing out of the joint face, its outside 0.2 mm inside the inner surface of the front print. The store (two silicone cartridges, the stepper, nine cells, the gel reservoir and pump, the Raspberry Pi 5, the inflator) is seated in the rear print after printing; its mounts are not in the file.

Nothing else is printed. No baffle, no ballast block, no separate mouth piece.

## The joint of the two tail prints

- Where: x = -215 mm in the frame of the simulation, behind the arm (the arm reaches -193 mm at most), where the section is 214 mm wide and 310 mm tall inside. The inside is dry; outside, the water stands 91.5 mm high on the lower part of the joint ring, so the joint must be sealed.
- How it is aligned: the sleeve on the rear print slides 12 mm into the front print. The section is not round (flat floor, arched roof), so the sleeve fixes position and rotation by itself; no pins are needed.
- How it is made: dry fit first. Then a PETG compatible structural adhesive (a two part methacrylate or epoxy) on the outside of the sleeve and on the end face, the rear print pushed home, wiped, clamped with tape for the cure. Then a bead of clear silicone sealant round the outside of the seam, at least up to 30 mm above the waterline. Leak test before any gel: tail standing in water to 95 mm for one hour, inside on paper.
- The store goes in through the open joint before bonding: seat the cartridges, cells, reservoir, pump, board and inflator in the rear print, run the lines and wires forward through the joint, then bond.

## Orientation: four compared for each part

| Part | Orientation | Box, mm | Fits | Margin, mm | Overhang beyond 45 degrees, cm2 |
|---|---|---|---|---|---|
| Head | on the docking face | 336 x 314 x 335 | yes | 4, 6, 5 | 226 |
| Head | on the floor | 335 x 314 x 336 | yes | 5, 6, 4 | 1096 |
| Head | on the side | 335 x 336 x 314 | no | 4, -16, 26 | 1520 |
| Head | on the mouth | 336 x 314 x 335 | yes | 4, 6, 5 | 266 |
| Tail, front | on the docking face | 336 x 314 x 251 | yes | 4, 6, 89 | 661 |
| Tail, front | on the floor | 251 x 314 x 336 | yes | 89, 6, 4 | 753 |
| Tail, front | on the side | 251 x 336 x 314 | yes | 4, 69, 26 | 1434 |
| Tail, front | on the joint face | 336 x 314 x 251 | yes | 4, 6, 89 | 632 |
| Tail, rear | on the joint face (sleeve down) | 318 x 222 x 226 | yes | 22, 98, 114 | 66 |
| Tail, rear | on the floor | 226 x 222 x 318 | yes | 114, 98, 22 | 253 |
| Tail, rear | on the side | 226 x 318 x 222 | yes | 114, 2, 118 | 988 |
| Tail, rear | on the tip | 318 x 222 x 226 | yes | 22, 98, 114 | 73 |

Choice: the head and the front of the tail on the docking face, the rear of the tail on its joint face.

Reasons, head. Unchanged from round 9: on the docking face the head is a bell that closes upward toward the mouth with walls steeper than 45 degrees nearly everywhere; the overhang is the smallest, mainly the shoulder where the lower shell meets the wide upper shell and the underside of the lower lip. The mouth rim is printed last, as a clean open edge. On the side the head does not fit.

Reasons, tail front. On the docking face and on the joint face the overhang is about the same (661 and 632 cm2). The docking face wins: the face that must seal against the head, with the magnet pockets, the pins and the flange, is printed on the plate as the flattest surface of the part, and the layers are rings round the body axis, so the water and the pull of the magnets load each layer in its own plane. The joint edge then prints last as a plain ring, which is all it needs to be. On the floor the whole inside of the roof needs support; on the side one flank carries supports.

Reasons, tail rear. On the joint face the taper closes upward to the tip with walls steeper than 45 degrees everywhere but the last few centimeters at the tip: 66 cm2 of overhang, the least of the four. The sleeve is the first layers on the plate, so its fit is the most accurate part of the print; above it the shell steps 3.2 mm outward (a small ledge, part of the 66 cm2). On the tip the overhang is about the same but the part would stand on a point. On the floor the inside of the roof needs supports; on the side the margin is 2 mm and the overhang is the largest.

Layer seam: set the seam to "aligned" and to the rear, so it runs along the keel line under the floor (all three parts), away from the gel walls at the sides and away from the roof.

Margins are small for the head and the front of the tail: 4 mm in one plate direction and 6 mm in the other, 5 mm in height for the head. There is no room for a brim or a skirt on the 336 mm side: switch both off, and switch off the purge line and the prime tower (one material). The rear of the tail has room for a brim, which helps the rear print stand on the narrow sleeve.

## Material and settings

- Material: clear PETG, dried (65 degrees C for 6 hours), from one batch for all three parts (about 2.7 kg with supports).
- Nozzle 0.6 mm hardened or stainless; layer height 0.24 mm for the shell. A 0.4 mm nozzle works with 0.2 mm layers and more loops, at about twice the time.
- Wall: the 3 mm wall as five loops of 0.6 mm, no infill inside the wall (set wall loops to 5 or more, so the slicer fills the wall with loops only). Loops in one direction read clearer than loops plus infill.
- For clarity: print slow and hot. Outer and inner walls 30 to 40 mm per second, 250 to 255 degrees C, part cooling fan 0 to 20 percent, flow raised 2 to 3 percent so the loops fuse without air lines. Volumetric flow kept under 12 mm3 per second.
- What to expect: a 3 mm PETG wall printed this way is translucent, like ribbed or frosted glass, not optically clear. Shapes and movement inside are visible, the arm and the newborn read well against a lit background, fine detail does not. The layer lines run as rings round the body. A thin coat of clear epoxy or clear polyurethane outside and inside fills the lines and brings the wall much closer to glass clear; sanding to 2000 grit and polishing is the alternative for the outside.
- Supports: tree supports, on build plate and on model, threshold 45 degrees, top interface 2 layers with 0.2 mm gap. Expected places are listed above. The saddles, the kit rails and the bosses are small and break clean.
- Bed: textured PEI at 80 degrees C with glue stick as a release (PETG bonds hard to smooth PEI). Chamber closed, not heated above 45 degrees C.
- First layer: the docking face (head, front of the tail) or the sleeve (rear of the tail). Elephant foot compensation 0.15 mm, so the pockets, the groove and the sleeve stay to size.

## Making the gel shell tight

The gel is held by the printed shell itself: the lower shell of the head and of the front of the tail, and the docking seam.

1. Solid wall: five fused loops, no infill, flow slightly raised, as above. A wall printed this way usually holds water; pinholes sit at the layer seam.
2. Seam placement: aligned, on the keel under the floor, as above, where a coat is easy to apply and not seen.
3. A coat: one coat of clear, low viscosity epoxy brushed inside the gel shell of both parts, up to 20 mm above the gel line (the line is 100 mm above the inner floor), and along the seam line outside. This is the measure that makes tightness certain; it also clears the wall there.
4. Test before any gel: fill each part with water to the gel line, standing on paper, for one hour.

The gel stands 10 mm above the water outside, so a leak runs outward, and the gel has a yield stress: it does not pass a gap under about 2 mm at that head. The coat is still worth doing, because water must not creep in when the gel is out.

## Docking face

In the frame of the simulation the docking plane stands at x = 32 mm; on the plate it is z = 0 for both parts.

- Magnets: three K&J DC2 N52 discs, 19.05 mm across, 3.17 mm thick, in the tail. Pockets 19.3 mm across and 3.4 mm deep, open to the face, in bosses 27 mm across inside the ring: two at the sides 215 mm above the floor, one at the top. Positions in the body frame (x, y, z in mm): [[32.0, 142.1, 215.0], [32.0, -142.1, 215.0], [32.0, 0.0, 319.5]]. Glue the magnets in with epoxy, flush or 0.2 mm under the face, all with the same pole out.
- Steel discs in the head, opposite the magnets: pockets 19.3 mm across and 2.2 mm deep for discs 19 mm across and 2 mm thick, glued in.
- Alignment: two pins of 5 mm, 4 mm proud, on the tail face at the sides, 150 mm above the floor; sockets of 5.4 mm in the head. Positions: [[32.0, 148.0, 150.0], [32.0, -148.0, 150.0]].
- Seal, because the gel crosses the seam: round the lower shell, where the gel is, both faces widen to a flange 10 mm wide and 4 mm thick, from the floor up to 102 mm (2.4 mm above the gel). Across the floor the flange is a sill 4 mm high on the inside; the needle tip passes 6 mm above it. The head face carries a groove 3.2 mm wide and 2.2 mm deep for a soft silicone cord of 3 mm, shore 30 to 40 A; the tail face is flat. The cord runs up both sides and across the floor in one piece; its two ends stand above the gel line. The three magnets give about 160 N in all; a 3 mm cord of that hardness over 0.35 m needs roughly 50 to 100 N for 0.5 mm of squeeze (estimate, to test). If the squeeze is too hard, use a softer cord or a hollow one.
- The groove has square corners where the sides meet the floor: file a small radius, or cut the cord and butt the pieces with silicone glue.

## Arm base

Four bosses on the tail floor, 10 mm across and 5 mm tall, with a blind bore of 5.6 mm, 7 mm deep, for M4 heat set inserts. The 5 mm steel plate under the arm has four matching 10.5 mm holes and sits on the floor round the bosses; the arm base is screwed through the plate into the inserts. Positions in the body frame (x, y in mm): [[-65.0, 45.0], [-65.0, -45.0], [-165.0, 45.0], [-165.0, -45.0]]. This pattern is an ESTIMATE: 100 x 90 mm round the arm axis. The hole pattern of the Rotrics DexArm base was not verified from a drawing; measure the arm and move the bosses in `print_pkg.py` (list BASE_H) before printing. The bores are blind, so the floor stays tight.

## Cuts

One, by design: the joint of the two tail prints, described above. Each of the three parts prints in one piece. If a printer with less height is used, the earlier plan applies: split on the horizontal plane at half height, inner lips with M3 bolts on a 50 mm pitch, sealant below the waterline.

## Not checked here

- The files were checked as meshes, not sliced: no slicer was run from here. Slice all three before ordering filament and read the real time, mass and support volume.
- The sleeve fit (0.2 mm gap) and the bond of the joint need a test print of a short ring of each side first.
- Tolerances of the pockets (19.3 mm), the pin sockets and the groove are first guesses for a tuned H2S; print the first 6 mm of each part as a test of the docking face.
- The saddle ledges are thin (3 mm) and carry about 0.1 kg each; they are meant to be printed with the shell. If they sag, raise their thickness in the script.
