# The same film at three ears

The closer speaker gives a visitor a quieter entrance in both of the room models. Its effect on the two voices is unequal. At film 52–58 s the carrier’s lower tone can become more prominent at the door with the film-wall speaker. A visitor could hear the work quite differently before reaching the seat. A quieter doorway cannot be guaranteed by the distance rule alone.

The [36-second listening study](../media/room-listening.mp4) repeats one six-second gallery passage at three positions, first with the source at the film wall, then beside the seated bay. All six chapters use the actual movie soundtrack summed to mono, passed through a modelled room. The listener stays at one mark for each pass. The small plan identifies speaker and ear. The picture stays identical; its sound changes. The chapter times are 0, 6, 12, 18, 24 and 30 s.

| Source | Ear | Direct sound only | With reflections, amplitude 0.55 | With reflections, amplitude 0.80 |
|---|---|---:|---:|---:|
| Film wall | Seat | 0.0 dB | 0.0 dB | 0.0 dB |
| Film wall | Entrance | −3.4 | +5.8 | +2.1 |
| Film wall | Staff bench | +2.2 | +9.1 | +4.7 |
| Beside bay | Seat | 0.0 | 0.0 | 0.0 |
| Beside bay | Entrance | −9.9 | −7.2 | −5.0 |
| Beside bay | Staff bench | −5.7 | −3.2 | −2.5 |

Each speaker is matched to the same six-second programme RMS at the central seat. Values in the table are dB relative to that seat in the same condition. Moving the speaker is followed by a single gain change. There is no subsequent level matching at the entrance or bench. In the more reflective case, moving the listening point 15 cm in four directions around the entrance gave +0.4 to +4.5 dB with the film-wall source, and −6.0 to −3.4 dB with the bay source. A small movement can change what the listener hears. [Station and band results](room-audio-levels.csv) · [Ear-position trials](room-ear-offsets.csv)

The model is a closed 8 × 6 × 3 m rectangular room with an omnidirectional point source. Image sources give reflected path lengths. Each path contributes an amplitude proportional to reflection amplitude to the power of its bounce count, divided by distance. Delayed copies add with their phase intact. The audible trial uses a frequency-independent pressure reflection amplitude of 0.80 on every face and paths up to 36 bounces. Increasing the limit from 24 to 36 changed the reported full-band relative levels by less than 0.02 dB. The 0.55 and 0.80 settings are hypothetical. The real door, other rooms, tank, audience, speaker response and absorption spectra are absent. No pump recording has been added. A mono ear signal cannot recreate binaural localisation. [Allen and Berkley, 1979](https://doi.org/10.1121/1.382599) · [Rebuild the signals](../production/room_acoustics.py)

At installation, put a single speaker at the marked wall position and match its film level at the seated ear. Measure or record the same six seconds at the door and bench with the room empty, then occupied. Move the speaker to the separate bay stand and repeat, keeping programme and seated level fixed. Repeat with the actual door open and the pump running. Ask the operator whether the film masks the sound they use to recognise a faulty cycle. Choose placement from those observations.
