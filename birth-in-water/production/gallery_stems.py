"""Export unity-sum stereo stems for the picture-locked 79.15 s exhibition edit."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

import numpy as np
from scipy.io.wavfile import write

from gallery_sound import RATE, gallery_signals, pcm16

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('sources', type=Path, help='Directory containing the two original camera audio renditions')
parser.add_argument('output', type=Path)
parser.add_argument('--pcm-reference',type=Path,help='Also write the exact summed PCM for verification')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    tmp=Path(temp)
    score_path=tmp/'image-score.wav'
    subprocess.run([sys.executable, str(root/'production/score.py'),str(root/'studies/tank-trace.csv'),
                    str(score_path),str(root/'studies/carrier-edge.csv')],check=True)
    camera,score=gallery_signals(args.sources,score_path)
    mix=pcm16(camera+score)
    if args.pcm_reference:
        write(args.pcm_reference,RATE,mix)
    location=pcm16(camera)
    # Give the final quantisation remainder to the score so unity reconstructs
    # the edit sample for sample. This correction is at most one 16-bit count.
    composed=mix.astype(np.int32)-location.astype(np.int32)
    assert np.max(np.abs(composed-pcm16(score).astype(np.int32)))<=1
    assert composed.min()>=-32768 and composed.max()<=32767
    assert np.array_equal(location.astype(np.int32)+composed,mix)
    tracks=[]
    for name,data in [('workshop-cameras',location),('image-score',composed.astype(np.int16))]:
        input_wav=tmp/(name+'.wav')
        write(input_wav,RATE,data)
        flac=tmp/(name+'.flac')
        subprocess.run(['ffmpeg','-v','error','-i',str(input_wav),'-compression_level','8',
                        '-metadata','artist=Ruipeng Wang / Born, Not Made','-metadata','title='+name,str(flac)],check=True)
        decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(flac),'-f','s16le','-'])
        if decoded!=data.astype('<i2',copy=False).tobytes():
            raise ValueError(f'Lossless decode failed for {name}')
        tracks.append(flac)
    readme=tmp/'Playout.txt'
    readme.write_text('Birth in Water — two stereo stems\nRuipeng Wang / Born, Not Made\n\n'
        'Both files begin at film time zero and run 79.15 seconds, 48 kHz, 16-bit, stereo. '
        'Put both on the same transport as the projection picture. Use one audio clock. '
        'Mute the film’s embedded audio when playing the stems. Start both at unity gain. '
        'Their digital sum reproduces the PCM mix used for the exhibition AAC.\n\n'
        'Workshop cameras: pink bench test from 8.0–18.4 s and the first overhead recording from 24–60 s. '
        'The overhead audio is very quiet. It is camera sound; the source supplies no hydrophone or isolated pump track.\n'
        'Image score: from 24–60 s. The lower voice responds to the carrier angle; the higher voice follows the image gap. '
        'Both voices were composed for the edit. They do not monitor the live apparatus.\n\n'
        'For commissioning, audition cameras alone, score alone, then both. Test from the seat, doorway and staff bench. '
        'The single-speaker placement cue in the main gallery kit is a separate mono test. '
        'The captioned film runs complete with audio muted.\n')
    manifest=tmp/'SHA256SUMS.txt'
    manifest.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in tracks+[readme]))
    with ZipFile(args.output,'w') as archive:
        for p in tracks+[readme,manifest]:
            archive.write(p,p.name,compress_type=ZIP_STORED if p.suffix=='.flac' else ZIP_DEFLATED)
