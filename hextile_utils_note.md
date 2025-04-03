hextile_utils.py module

Main Classes and Functions:

    HexTile Class - Represents a single hexagonal tile

        Initialization: HexTile(cx=0, cy=0, side_length=36, path_width=3)

            cx, cy: Center coordinates of the hexagon

            side_length: Length of hexagon sides (default 36)

            path_width: Width of paths (default 3)

        Key Methods:

            creategeometry(): Generates the hexagon's vertices and paths

            svgexport(): Returns SVG string representation of the tile

        Attributes:

            occupancy: List of 13 values (0/1) controlling path generation

            mainverts: List of main hexagon vertices

            pathverts: List of path vertices

    Helper Functions:

        shift(key, array): Rotates array elements

            Returns: Shifted array

        create_svg_polyline(array): Creates SVG polyline from points

            Returns: SVG polyline string

        create_svg_line_path(array): Creates SVG path from points

            Returns: SVG path string

        shift_and_find_zero_groups(occupancy): Finds continuous 0 groups

            Returns: List of zero groups

        drawline(x, y, x2, y2, ...): Creates SVG line

            Returns: SVG line element

        makelabel(label, x, y): Creates SVG text label

            Returns: SVG text element


hextile example
```
# Create a grid of random hex tiles
final_svg = '<svg width="3000" height="3000" xmlns="http://www.w3.org/2000/svg" style="background-color: black;">'

for r in range(16):
    for c in range(16):
        tile = HexTile(cx=r*100+50, cy=c*100+50)
        tile.occupancy = [random.randint(0,1) for _ in range(13)]
        tile.creategeometry()
        final_svg += tile.svgexport()

final_svg += '</svg>'

# Save to file
with open('output.svg', 'w') as f:
    f.write(final_svg)
```