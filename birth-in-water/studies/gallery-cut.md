# Film trial for the room

The bench film changes the relation between the two tanks. Before anything emerges in water, a pump on a table pushes a ball from a pink test housing. A hand then operates a phone among loose components. The following tank view lasts long enough to wonder where the hand has gone. The operator has moved outside the frame. The question of dependence survives the apparent success of the birth.

| Edit time | Source | Picture and sound |
|---|---|---|
| 00–08 | [Water Beings](https://vimeo.com/1229413082), 7–15 s | Digital population. A silent start allows the next sound to locate the workbench. |
| 08–18.4 | [Hydraulic bench experiment](https://vimeo.com/1147282116), 1–11.4 s | Pink test housing, a hand, a bowl, a ball. Actual camera audio at reduced gain. This was a mechanical trial, before the tank release. |
| 18.4–24 | [Phone control test](https://vimeo.com/1147361501), 14–19.6 s | Separate tabletop recording of human control. Sound drops away. No simultaneous command to the tank is implied. |
| 24–59.967 | [First tank prototype](https://vimeo.com/1147548218), 1–37 s | One recording in chronological order. Wide to fixed detail at edit 38.25 s, wide again at 49.4 s. The measured gap appears at 48.9 s. Original quiet audio and composed optical score. |
| 59.967–65.133 | [Second prototype](https://vimeo.com/1238506916), 23.85–29 s | Different hull and lighting, from the artist's overview. The wet lip appears to follow the departing body. |
| 65.133–70.133 | Project archive: assets/img/society-ref/visap.webp | Held VISAP catalogue preview, tank and digital population sharing a field of view. The catalogue identifies the image as an artwork preview. Capture method and venue are unspecified. |
| 70.133–79.15 | Water Beings, 49–58 s | Return to a changing group. The room can continue into another visitor's arrival. |

The [artist's workshop record](https://fab.cba.mit.edu/classes/863.25/people/RuipengWang/week16.html) identifies the water-inflated bladder and phone-controlled pump. These two bench inserts are from the author's own linked test videos. They depict different experiments. The frame switch at 38.25 s uses extra resolution in the same 4K take. All source motion runs at source speed. The tank soundtrack is editorial; no biological sounds are used.

Do not synchronize this recording with a live motor. If shown alongside the early apparatus, give each a legible label and the attendant a visible way to indicate a pause. In a video-only exhibition the catalogue image shows how the artist presents the tank and population together. Test whether the loaded physical tank adds a genuinely different experience before committing to a wet installation.

In the revised sound mix, the two pitches describe different features. A fitted line on the carrier's upper edge alters the low pitch. The measured gap controls the second voice. The low note holds its changed pitch after the silhouettes overlap again. The clean edit preserves the previously distributed picture stream. To reproduce the mix, generate the stereo score with the optional carrier-edge CSV, then run gallery_cut.py with the existing gallery picture as the third argument. Use gallery_export.py on the master for the captioned distribution copy. The 55-second return edit uses only camera sound during the physical take.

## A copy for the gallery wall

The [1080p MP4 with permanent captions](../media/gallery-projection-1080.mp4) takes its image from the source files for each shot and its AAC track directly from the released web edit. The wide first-tank recording comes from 3840 × 2160. The fixed close view draws on a 1440 × 810 region of that recording. The phone test and second tank have 1920 × 1080 source frames. The digital population and pink test fixture have 1280 × 720 source frames and are enlarged. The catalogue preview is also enlarged. Captions and source labels render at the final projection raster. The resulting file is 1920 × 1080, 30 fps, 2,374 video frames, 79.15 s including the end of the sound.

The film was sampled at 25% and 75% of the duration of each of the nine edit segments. A 1600 × 720 interior crop excludes the two letter areas. At those 18 times, the projection encode preserved more picture detail by luma SSIM and PSNR against the source-derived, lightly compressed 1080p shot intermediates than the 720p exhibition file enlarged with Lanczos. This checks the specific encodes. It cannot measure how the work will look on a particular projector. [Frame sheet](projection-review.jpg) · [Sample results](projection-samples.csv) · [Rebuild from artist sources](../production/projection_master.py)

For frame-accurate playout at 30 fps, the second tank starts at zero-based picture 1,799 (59.9667 s), the catalogue preview at 1,954 (65.1333 s) and the closing population at 2,104 (70.1333 s). The first closer framing starts at frame 1,148 (38.2667 s). Rounded times in the room rehearsal serve as visitor cues. The burnt-in source labels and the English caption track switch with the actual cut pictures.

### Camera sound and score on separate faders

The [two lossless stereo stems](../media/gallery-audio-stems.zip) share the film start and last 3,799,200 samples per channel at 48 kHz. The workshop-camera stem contains the bench test and overhead recording. The image-derived score has its own fader. Keep the MP4 audio muted when using them together on the same transport. At film 46–55 s the stereo camera stem averages −75.44 dBFS RMS and the composed stem −27.17 dBFS RMS. Audition them at their recorded gains before increasing level. The louder sound one hears at release was composed for the image.

The two decoded 16-bit files sum exactly to the pre-AAC master. Encoding that sum with the film's 96 kb/s AAC recipe reproduces every byte of the published ADTS stream. Both source-specific fades are retained. This gives an installer a reversible way to listen to the camera recording and the movement-derived pitches independently. The analogue mix coming from speakers depends on speaker placement, amplifier gain and the room.

## Motion in the delivered cut

A [frame-pair check](gallery-motion.csv) sampled all 2,374 pictures of the clean film. The centre 1152 × 576 pixels were reduced to a 288 × 144 grey image, and neighbouring pictures within each edit segment were compared. The median change in the quiet opening wide of the tank was 0.028 of 255 levels per pixel; the returning wide measured 0.259. The catalogue preview stayed held for five seconds, with a peak change of 0.018 in this calculation. The digital opening and closing each had a median change above two levels. These numbers reflect movement, lighting and compression together. A low whole-field difference can coexist with an operator's hand moving in a small part of a shot.
