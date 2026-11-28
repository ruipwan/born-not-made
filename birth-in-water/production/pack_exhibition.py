"""Build the portable gallery copy and mock-up materials from tested site files."""
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

root=Path(__file__).resolve().parents[1]
media,study=root/'media',root/'studies'
with tempfile.TemporaryDirectory(dir=media) as tmp:
    work=Path(tmp)
    planner=(study/'live-window.html').read_text()
    # Inline the small module for file:// origins with network access disabled.
    module=(study/'live-window.mjs').read_text().replace('export const ','const ').replace('export function ','function ')
    planner=planner.replace("import {windowLength,visits,rehearse,encounter} from './live-window.mjs';",module)
    planner=planner.replace('<script type="module">','<script>').replace('href="room.html#reset-status"','href="index.html"')
    portable=work/'arrivals.html'
    portable.write_text(planner)
    # Take the centre pass losslessly from the derived 48 kHz mono WAV.
    sound=work/'mono-placement.flac'
    subprocess.run(['ffmpeg','-v','error','-i',str(media/'bay-soundcheck.wav'),'-ss','13.25','-t','12.5',
                    '-c:a','flac','-compression_level','8',str(sound)],check=True)
    files={
        'index.html':root/'production/gallery_kit.html',
        'gallery-projection-1080.mp4':media/'gallery-projection-1080.mp4',
        'arrivals.html':portable,
        'gallery-rehearsal.pdf':study/'gallery-rehearsal.pdf',
        'caption-distance.pdf':study/'caption-distance.pdf',
        'film-wall-label.pdf':study/'film-wall-label.pdf',
        'beam-section.svg':study/'beam-section.svg',
        'tank-status.pdf':study/'tank-status.pdf',
        'film-wall.jpg':study/'room-views/film-wall.jpg',
        'film-poster.jpg':media/'film-poster.jpg',
        'mono-placement.flac':sound,
        'source-register.csv':study/'source-register.csv'
    }
    manifest=work/'SHA256SUMS.txt'
    entries=[]
    for name,source in files.items():
        with source.open('rb') as handle:
            entries.append(f"{hashlib.file_digest(handle,'sha256').hexdigest()}  {name}\n")
    manifest.write_text(''.join(entries))
    files[manifest.name]=manifest
    for page in (files['index.html'],portable):
        for link in re.findall(r'(?:src|href|poster)="([^"#]+)"',page.read_text()):
            if link not in files:
                raise ValueError(f'Missing offline asset {link}')
    bundle=work/'birth-in-water-gallery.zip'
    with ZipFile(bundle,'w') as archive:
        for name,source in files.items():
            method=ZIP_STORED if source.suffix in ('.mp4','.flac','.jpg') else ZIP_DEFLATED
            archive.write(source,name,compress_type=method)
    with ZipFile(bundle) as check:
        assert check.testzip() is None
    bundle.replace(media/bundle.name)
