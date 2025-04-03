import math
import io
import random
file_path = r'C:\Users\Reference\Desktop\svgout_main.svg'


def shift(key, array):
    return array[-key:]+array[:-key]

def create_svg_polyline(array):
    points_str = ' '.join(f"{x},{y}" for x, y in array)
    return f'<polyline points="{points_str}" fill="purple" stroke="white" opacity="0.5" stroke-width="1"/>'

def create_svg_line_path(array):
    outputstring = '<path d="'
    for index,a in enumerate(array):
        if index == 0:
            outputstring+=f'M{a[0]},{a[1]} '
            continue
        else:
            outputstring+=f'L{a[0]},{a[1]} '
    outputstring+=f'L{array[0][0]},{array[0][1]} '
    outputstring+='Z" style="fill:none;stroke:red;stroke-width:1.86px;"/>'
    return outputstring

def create_svg_line_path2(array, centerx, centery,a1,a2):
    distance = 0.0001
    dx = distance*math.cos(a1) 
    dy = distance*math.sin(a1) 
    dx2 = distance*math.cos(a2)
    dy2 = distance*math.sin(a2)

    outputstring = '<path d="'
    for index,a in enumerate(array):
        if index == 0:
            outputstring+=f'M{a[0]},{a[1]} '
        else:
            outputstring+=f'L{a[0]},{a[1]} '
    outputstring+=f'Q{centerx+dx} {centery+dy} {array[0][0]} {array[0][1]} '     
    outputstring+=f'L{array[0][0]},{array[0][1]} '
    outputstring+='Z" style="fill:none;stroke:red;stroke-width:1px;"/>'
    return outputstring

def create_svg_arc_path(center_x, center_y, inner_radius, outer_radius, start_angle, end_angle):
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    large_arc_flag = 1 if end_rad - start_rad > math.pi else 0
    
    x1 = center_x + outer_radius * math.cos(start_rad)
    y1 = center_y + outer_radius * math.sin(start_rad)
    x2 = center_x + outer_radius * math.cos(end_rad)
    y2 = center_y + outer_radius * math.sin(end_rad)
    
    x3 = center_x + inner_radius * math.cos(end_rad)
    y3 = center_y + inner_radius * math.sin(end_rad)
    x4 = center_x + inner_radius * math.cos(start_rad)
    y4 = center_y + inner_radius * math.sin(start_rad)
    
    path = (
        f"M{x1},{y1} " +
        f"A{outer_radius},{outer_radius} 0 {large_arc_flag} 1 {x2},{y2} " +
        f"L{x3},{y3} " +
        f"A{inner_radius},{inner_radius} 0 {large_arc_flag} 0 {x4},{y4} " +
        "Z"
    )
    return path

def shift_and_find_zero_groups(occupancy):
    occupancy.pop(0)
    try:
        first_one_index = occupancy.index(1)
    except:
        return []  # Return empty list when no zeros
    
    shifted_occupancy = occupancy[first_one_index:] + occupancy[:first_one_index]
    zero_groups = []
    current_group = []
    
    for i, val in enumerate(shifted_occupancy):
        if val == 0:
            current_group.append((i+first_one_index)%len(occupancy))
        else:
            if current_group:
                zero_groups.append(current_group)
                current_group = []
    
    if current_group:
        zero_groups.append(current_group)
    
    return zero_groups

def drawline(x, y, x2, y2, stroke_color='red', stroke_width=2):
    return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'

def makelabel(label, x,y):
    return f'<text x="{x}" y="{y}" fill="white" font-weight="light" font-size="4px" font-family="Roboto">{label}</text>'

def makelabel2(label, x,y,color):
    return f'<text x="{x}" y="{y}" fill="{color}" font-weight="light" font-size="4px" font-family="Roboto">{label}</text>'

class Vertex:
    def __init__(self, x=-1, y=-1, z=-1):
        self.x = x
        self.y = y
        self.z = z

class Edge:
    def __init__(self, v1=None, v2=None):
        self.v1 = v1
        self.v2 = v2
    
    def co(self):
        return (self.v1, self.v2)

class HexTile:
    def __init__(self, cx=0, cy=0, side_length=36, path_width=3):
        self.cx = cx
        self.cy = cy
        self.center = (cx, cy)
        self.path_width = path_width
        self.radius = side_length
        self.verts = []
        self.mainverts = []
        self.outerverts = []
        self.pathverts = []
        self.angles = []
        self.lines = []
        self.occupancy = [0,1,1,1,1,0,0,1,0,0,0,0,0]
        self.side_length = side_length
        self.labels = []

    def getvert(self, v):
        if v%2 == 1:  # ODD (EDGE)
            v = (v-1)/2
            return (self.pathverts[int(v*2)], self.pathverts[int(v*2+1)])
        else:  # EVEN (CORNER)
            v = v/2
            return (shift(1, self.pathverts)[int(v*2)], shift(1, self.pathverts)[int(v*2+1)])

    def getvpair(self, v):
        vertex = int(v/2)
        if v%2 == 0:
            a = shift(1, self.pathverts)[vertex*2]
            b = shift(1, self.pathverts)[vertex*2+1]
            a1 = shift(1, self.angles)[vertex*2]
            a2 = shift(1, self.angles)[vertex*2+1]
            return ([a,b], [a1,a2])
        else:
            a = self.pathverts[vertex*2]
            b = self.pathverts[vertex*2+1]
            a1 = self.angles[vertex*2]
            a2 = self.angles[vertex*2+1]
            return [[a,b], [a1,a2]]

    def creategeometry(self):
        width = self.side_length * 2
        height = math.sqrt(3) * self.side_length

        # Main vertices
        for i in range(6):
            angle = math.pi / 180 * (60 * i - 30)
            x = self.cx + self.side_length * math.cos(angle)
            y = self.cy + self.side_length * math.sin(angle)
            self.mainverts.append((x, y))

        # Centers of adjacent hexagons
        for i in range(6):
            angle = math.pi / 180 * (60 * i)
            x = self.cx + (self.side_length * 0.8660 * 2) * math.cos(angle) 
            y = self.cy + (self.side_length * 0.8660 * 2) * math.sin(angle) 
            self.outerverts.append((x, y))

        # Path points (subvertices)
        for i in range(6):
            v1 = self.mainverts[i]
            v2 = self.mainverts[(i + 1) % 6]
            mid_x = (v1[0] + v2[0]) / 2
            mid_y = (v1[1] + v2[1]) / 2

            self.angles.append(math.atan2(self.cy-mid_y, self.cx-mid_x))
            self.angles.append(math.atan2(self.cy-mid_y, self.cx-mid_x))

            dx = v2[0] - v1[0]
            dy = v2[1] - v1[1]
            angle = (math.atan2(dy, dx))
            offset = self.path_width / 2
            subx1 = mid_x + (math.cos(angle) * offset)
            subx2 = mid_x - (math.cos(angle) * offset)
            suby1 = mid_y + (math.sin(angle) * offset)
            suby2 = mid_y - (math.sin(angle) * offset)

            self.pathverts.append((subx2, suby2))
            self.pathverts.append((subx1, suby1))

        # Create arcs for gaps
        gap_groups = shift_and_find_zero_groups(self.occupancy)
        if gap_groups:
            for gap in gap_groups:
                if not gap:
                    continue
                    
                construction_points = []
                beginning = gap[0]
                ending = gap[-1]

                coords = self.getvpair(beginning)
                construction_points.append(coords[0][0])
                angle1 = coords[1][0]

                coords = self.getvpair(ending)
                angle = coords[1]
                coords = coords[0]

                for p in gap:
                    if p % 2 == 0:
                        p = int(p/2)
                        middle = self.mainverts[p]
                        construction_points.append(middle)

                construction_points.append((coords[1][0], coords[1][1]))
                self.lines.append(create_svg_line_path2(construction_points, 
                                      self.center[0], self.center[1], 
                                      angle[0], angle[1]))

    def svgexport(self):
        svg_output = ''
        # Only include paths/lines, no debug shapes
        for l in self.lines:
            svg_output += l + "\n"
        return svg_output

# Generate final SVG
finalstring = f'<svg width="{3000}" height="{3000}" xmlns="http://www.w3.org/2000/svg" style="background-color: black;">'

for r in range(0, 16):
    for c in range(0, 16):
        hex_tile = HexTile(cx=r*100+50, cy=c*100+50)
        randombits = []
        for i in range(0, 13):
            randombits.append(1 if random.random() > 0.5 else 0)
        hex_tile.occupancy = randombits
        hex_tile.creategeometry()
        finalstring += hex_tile.svgexport()

finalstring += '</svg>'

with io.open(file_path, 'w') as file:
    file.write(finalstring)