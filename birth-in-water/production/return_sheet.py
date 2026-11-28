"""Set two A4 sheets for the public return record and the dry-side handover."""
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).resolve().parents[1]
pdf = Canvas(str(root/'studies/tank-return-and-handover.pdf'), pagesize=A4,
             invariant=1, pageCompression=1)
pdf.setTitle('Birth in Water | What returned to the tank?')
ink = HexColor('#1b302b')
soft = HexColor('#40584f')
rule = HexColor('#89998c')

def text(x, y, label, size=11, face='Helvetica', color=ink):
    pdf.setFont(face, size)
    pdf.setFillColor(color)
    pdf.drawString(x*mm, y*mm, label)

def para(x, y, body, width=177, size=11.3, step=5.3):
    for line in simpleSplit(body, 'Helvetica', size, width*mm):
        text(x, y, line, size)
        y -= step
    return y

def line(x, y, end):
    pdf.setStrokeColor(rule)
    pdf.setLineWidth(.55)
    pdf.line(x*mm, y*mm, end*mm, y*mm)

def heading(title, caption):
    text(16, 278, 'BIRTH IN WATER', 10, 'Helvetica-Bold', soft)
    text(16, 259, title, 29, 'Times-Roman')
    return para(16, 245, caption, size=12.3, step=6.0)

heading('What returned to the tank?',
        'The film repeats the same recording. Each entry here describes one observed return in this physical tank. An empty line means no return has been entered.')
text(16, 213, 'Date and room', 11, 'Helvetica-Bold')
line(49, 212, 193)
for top in (199, 142, 85):
    line(16, top, 193)
    text(16, top-8, 'Time', 11, 'Helvetica-Bold')
    line(27, top-9, 62)
    text(69, top-8, 'Body returned / hull mark', 11, 'Helvetica-Bold')
    line(119, top-9, 193)
    text(16, top-18, 'Same body, another body, or unknown?', 10, color=soft)
    line(16, top-26, 193)
    text(16, top-35, 'What did someone change before the next release?', 10, color=soft)
    line(16, top-44, 193)
text(16, 22, 'An operator records only what they observed. A return can be left open.', 10, color=soft)
text(16, 15, 'Place on the dry reading route. Keep the tank-status card visible separately.', 10, color=soft)
pdf.showPage()

heading('Handing the room over',
        'Working proposal for the floor host, wet operator and AV technician. Confirm the actual prototype and room with the artist before opening.')
text(16, 218, 'NORTH   /   Exhibition film', 13, 'Helvetica-Bold')
para(16, 210, 'Extract the north-wall ZIP. Open index.html. The 79.15 s film starts muted with permanent captions. Send optional programme sound to the tested bay speaker. Keep the caption and accessible route lit and clear.')
text(16, 186, 'EAST   /   Recorded population', 13, 'Helvetica-Bold')
para(16, 178, 'On a second player, keep east-display.html and water-beings-east.mp4 together. Start full screen. Check it repeats the 33.033 s passage with no sound. Label this screen as a recording. Its timing is independent of the tank and the north wall.')
text(16, 153, 'WET SIDE   /   Supervised apparatus', 13, 'Helvetica-Bold')
para(16, 145, 'The operator identifies the loaded hull, checks clearance in filled glass and runs a supervised cycle before opening live viewing. Post the actual state. The floor host keeps the side bay open and can explain which images are recorded.')
text(16, 121, 'During a fault, reset or break', 13, 'Helvetica-Bold')
para(16, 113, 'The operator pauses the tank and marks it paused. The host keeps the dry viewing route open. Both recorded walls can continue. Only the assigned operator clears the tank after a successful supervised cycle. If relief is unavailable, change to the agreed film-only presentation.')
text(16, 83, 'Before leaving the next shift', 13, 'Helvetica-Bold')
para(16, 75, 'Write the actual tank state and the last confirmed cycle below. Agree who may authorise a restart. Enter a witnessed return on the public sheet after service, if the team has agreed to display it. A restarted projector is never a tank clearance.')
for y, label in [(47,'Tank state / time'),(35,'Last confirmed cycle / time'),(23,'Incoming operator and floor coverage')]:
    text(16, y, label, 10, 'Helvetica-Bold')
    line(85, y-1, 193)
pdf.showPage()
pdf.save()
