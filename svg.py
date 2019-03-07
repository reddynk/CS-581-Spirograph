import svgwrite

def create(name, shape):
    dwg = svgwrite.Drawing(name+'.svg', profile='full')

    for line_string in shape.boundary:
        x,y = line_string.coords.xy
        for i in range(len(x[:-1])):
            dwg.add(dwg.line((x[i], y[i]), (x[i+1], y[i+1]), stroke=svgwrite.rgb(0, 0, 0, '%')))

        dwg.add(dwg.line((x[-1], y[-1]), (x[0], y[0]), stroke=svgwrite.rgb(0, 0, 0, '%')))

    dwg.save()
