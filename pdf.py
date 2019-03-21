import svgwrite
import reportlab as rb
from reportlab.pdfgen import canvas
from shapely.affinity import translate

# How much empty space their will be around the gear in the pdf.
# Don't set this to < 1 or my precious math will breakdown.
BUFFER_FACTOR = 1.25

def create(name, shape, outer_radius, scale_factor):
    # Make sure to translate the gear by its outer radius, as the gears are
    # centered at 0, while in PDFs the entire file must be positive.
    shape = translate(shape,outer_radius, outer_radius)
    # max_x, max_y will be the pdf's page size.
    max_x = 0
    max_y = 0
    for line_string in shape.boundary:
        max_x = max(max_x, max(line_string.coords.xy[0])*scale_factor)
        max_y = max(max_y, max(line_string.coords.xy[1])*scale_factor)
    # We must account for the buffer.
    max_x = max_x * BUFFER_FACTOR
    max_y = max_y * BUFFER_FACTOR

    c = canvas.Canvas(name+".pdf", pagesize=(max_x,max_y))

    # Now translate by the buffer factor to center the gear in our canvas.
    shape = translate(shape, (BUFFER_FACTOR - 1) * outer_radius, (BUFFER_FACTOR - 1) * outer_radius)

    for line_string in shape.boundary:
        # Start a new path at each boundary.
        p = c.beginPath()
        x,y = line_string.coords.xy
        p.moveTo(x[0]*scale_factor,y[0]*scale_factor)
        
        # Move the line along each subsequent point.
        for i in range(len(x[1:])):
            p.lineTo(x[i]*scale_factor,y[i]*scale_factor)
        
        p.close()
        c.drawPath(p)

    c.showPage()
    c.save()