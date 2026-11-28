"""Print a close-reading wall label from three uncaptioned frames of the actual edit."""
from io import BytesIO
from pathlib import Path
import subprocess

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).resolve().parents[1]
film = root/'media/gallery-cut.mp4'
page = Canvas(str(root/'studies/film-wall-label.pdf'), pagesize=A3, invariant=1, pageCompression=1)
page.setTitle('Birth in Water | The two tanks in the film')
ink = HexColor('#1a312e')
muted = HexColor('#455e55')
page.setFillColor(ink)
def text(x, y, value, font, size, color=ink):
    page.setFont(font, size)
    page.setFillColor(color)
    page.drawString(x*mm, y*mm, value)

def paragraph(x, y, value, width, size, leading):
    for line in simpleSplit(value, 'Helvetica', size, width*mm):
        text(x, y, line, 'Helvetica', size)
        y -= leading
    return y

text(15, 396, 'BIRTH IN WATER', 'Helvetica-Bold', 14, muted)
text(15, 371, 'The two tanks in the film', 'Times-Roman', 41)
paragraph(15, 353, 'Ruipeng Wang. Recorded workshop tests and a seven-generation digital ecology. The film repeats every 79 seconds.', 258, 18, 8.7)

rows = [
    (318, '3.0', 'Water Beings', 'Opening and closing images',
     'In this digital population, contact can produce another generation. The dead remain where they fall and change where later bodies can grow.'),
    (222, '49.7', 'First tank', '24 to 60 seconds',
     'A smaller white body leaves a larger one. Watch the carrier turn. The artist made the child separately and loaded it into this prototype.'),
    (126, '62.20', 'Second tank', '60 to 65 seconds',
     'Two copper-coloured interiors appear in a blue-lit tank. This is a later prototype with a different hull.')
]
for y, time, heading, interval, body in rows:
    page.setStrokeColor(HexColor('#a8b6ac'))
    page.line(15*mm, y*mm, 282*mm, y*mm)
    encoded = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', time, '-i', str(film),
        '-vf', 'scale=592:-2:flags=lanczos', '-frames:v', '1', '-c:v', 'mjpeg', '-q:v', '3',
        '-threads', '1', '-f', 'image2pipe', '-'])
    page.drawImage(ImageReader(BytesIO(encoded)), 15*mm, (y-72)*mm, width=112*mm, height=63*mm)
    text(136, y-16, heading, 'Times-Roman', 29)
    text(136, y-27, interval, 'Helvetica', 13, muted)
    last = paragraph(136, y-42, body, 142, 16.5, 8.5)
    if last < y-88:
        raise ValueError(f'Text crosses into the next label: {heading}')

page.setStrokeColor(HexColor('#a8b6ac'))
page.line(15*mm, 35*mm, 282*mm, 35*mm)
text(15, 22, 'All three images come from the recorded film. The live tank has its own status card.', 'Helvetica', 13, muted)
page.save()
