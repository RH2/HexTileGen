#hexgrid_utils.py 
#to use: import hexgrid_utils.py

# What is included in hexgrid_utils.py:
# 1. Coordinate Conversions
# Function	Arguments	Returns	Description
# axial_to_cube	(q, r)	(q, r, s)	Axial → Cube
# cube_to_axial	(q, r, s)	(q, r)	Cube → Axial
# cube_to_oddr	(q, r, s)	(col, row)	Cube → Odd-R Offset
# oddr_to_cube	(col, row)	(q, r, s)	Odd-R → Cube
# cube_to_evenr	(q, r, s)	(col, row)	Cube → Even-R Offset
# evenr_to_cube	(col, row)	(q, r, s)	Even-R → Cube
# (Similar for oddq/evenq variants)			
# 2. Hex Arithmetic
# Function	Arguments	Returns	Description
# cube_add	a: CubeHex, b: CubeHex	(q, r, s)	Hex addition
# cube_subtract	a: CubeHex, b: CubeHex	(q, r, s)	Hex subtraction
# cube_scale	hex: CubeHex, k: int	(q, r, s)	Scale hex by k
# cube_rotate_left	hex: CubeHex	(q, r, s)	60° counter-clockwise
# cube_rotate_right	hex: CubeHex	(q, r, s)	60° clockwise
# 3. Distance Calculations
# Function	Arguments	Returns	Description
# cube_distance	a: CubeHex, b: CubeHex	int	Distance between hexes
# axial_distance	a: AxialHex, b: AxialHex	int	Axial distance
# offset_distance	a: OffsetHex, b: OffsetHex, offset_type: str	int	Offset distance
# 4. Neighbor Operations
# Function	Arguments	Returns	Description
# cube_neighbor	hex: CubeHex, direction: int (0-5)	CubeHex	Neighbor in direction
# cube_neighbors	hex: CubeHex	List[CubeHex]	All 6 neighbors
# (Axial/offset variants available)			
# 5. Range Finding
# Function	Arguments	Returns	Description
# cube_ring	center: CubeHex, radius: int	List[CubeHex]	Hexes in ring
# cube_spiral	center: CubeHex, radius: int	List[CubeHex]	Hexes in filled radius
# (Axial/offset variants available)			
# 6. Line Drawing
# Function	Arguments	Returns	Description
# cube_line	a: CubeHex, b: CubeHex	List[CubeHex]	Straight line between hexes
# axial_line	a: AxialHex, b: AxialHex	List[AxialHex]	Axial line
# offset_line	a: OffsetHex, b: OffsetHex, offset_type: str	List[OffsetHex]	Offset line
# 7. Pathfinding
# Function	Arguments	Returns	Description
# cube_path	start: CubeHex, goal: CubeHex, obstacles: Set[CubeHex]	List[CubeHex]	Shortest path (A*)
# cube_bfs	start: CubeHex, goals: Set[CubeHex], obstacles: Set[CubeHex]	Dict[CubeHex, int]	BFS distances
# (Axial/offset variants available)			
# 8. Field of View
# Function	Arguments	Returns	Description
# cube_visible	center: CubeHex, radius: int, obstacles: Set[CubeHex]	Set[CubeHex]	Visible hexes
# (Axial/offset variants available)			
# 9. Visualization
# Function	Arguments	Returns	Description
# hex_to_pixel	hex: CubeHex, size: float, layout: str	(x, y)	Hex → Pixel coords
# pixel_to_hex	point: (x, y), size: float, layout: str	CubeHex	Pixel → Hex
# polygon_corners	hex: CubeHex, size: float, layout: str	List[(x, y)]	Hex corner points
# Key Types

#     CubeHex: (q, r, s) where q + r + s = 0
#     AxialHex: (q, r) (omits s)
#     OffsetHex: (col, row) (odd/even-r/q variants)
#     layout: 'pointy' or 'flat' for visualization