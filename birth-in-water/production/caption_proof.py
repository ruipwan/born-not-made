"""Print two pieces of the released captioned picture at the proposed wall scale."""
from io import BytesIO
from pathlib import Path
from subprocess import check_output

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).resolve().parents[1]
movie = root / 'media/gallery-cut-open-captions.mp4'
picture = Image.open(BytesIO(check_output([
    'ffmpeg', '-v', 'error', '-ss', '49.5', '-i', str(movie), '-frames:v', '1',
    '-threads', '1', '-f', 'image2pipe', '-c:v', 'png', '-',
])))
assert picture.size == (1280, 720)
paper = Canvas(str(root/'studies/caption-distance.pdf'), pagesize=landscape(A3))
paper.setTitle('Birth in Water | Film wall caption proof')
ink = HexColor('#213b37')
paper.setFillColor(ink)

def line(x, y, size, words, font='Helvetica'):
    paper.setFont(font, size)
    paper.drawString(x*mm, y*mm, words)

line(17, 274, 27, 'Reading the film from the bay', 'Times-Roman')
line(17, 262, 12, 'Two full-size fragments of the permanent-caption exhibition film at 49.5 s.')
line(17, 254, 12, 'Print A3 landscape at 100%. Measure the rule below. Cut out each picture along its edge.')
# Pixel position and size remain tied to the encoded 16:9 picture. The
# full-image width is 1900 mm and its centre is 1485 mm above the floor.
pitch = 1900 / picture.width
screen_top = 1485 + pitch*picture.height/2
def strip(box, bottom, label):
    x, y, right, lower = box
    width, height = (right-x)*pitch, (lower-y)*pitch
    wording = (f'{label}   /   Left edge {x*pitch:.0f} mm from picture left. '
               f'Top edge {screen_top-y*pitch:.0f} mm above floor.')
    line(17, bottom+height+4, 11, wording)
    paper.drawImage(ImageReader(picture.crop(box)), 17*mm, bottom*mm,
                    width*mm, height*mm)

strip((42, 28, 285, 64), 182, 'SOURCE')
strip((391, 624, 600, 661), 110, 'DIALOGUE / SOUND CAPTION POSITION')
line(17, 94, 12, 'Tape the two fragments on the north wall at the indicated positions. Start with eyes at the seated bay mark.')
line(17, 86, 12, 'Try the entrance and standing marks. Log the closest place from which each fragment can be read comfortably.')
line(17, 78, 12, 'Repeat with the actual film, muted, at 1.90 m image width. Switch on the tank and aisle lights.')
line(17, 70, 12, 'The paper reproduces letter size and placement. Projection black level, spill, focus and moving backgrounds need the screen.')
paper.setLineWidth(1)
paper.setStrokeColor(ink)
paper.line(17*mm, 52*mm, 117*mm, 52*mm)
for x in (17,117):
    paper.line(x*mm, 50*mm, x*mm, 54*mm)
line(17, 44, 10, 'Measurement rule: 100 mm')
line(17, 25, 11, 'Observer / eye height __________________     Position __________________     Lights __________________')
line(17, 16, 11, 'Source fragment ______________________     Caption fragment ______________________     Date __________')
paper.save()
