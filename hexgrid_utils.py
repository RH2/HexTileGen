"""
Hex Grid Utilities

Includes:
- Hex coordinate systems (axial, cube, offset)
- Conversions between coordinate systems
- Hex arithmetic
- Distance calculations
- Neighbor finding
- Range finding
- Line drawing
- Field of view
- Pathfinding
- Map generation
"""

import math
from collections import deque
from typing import List, Tuple, Dict, Set

# Define hex coordinate types
AxialHex = Tuple[int, int]
CubeHex = Tuple[int, int, int]
OffsetHex = Tuple[int, int]
Orientation = Dict[str, float]

# Hex orientation constants
LAYOUT_POINTY = {
    'f0': math.sqrt(3.0),
    'f1': math.sqrt(3.0) / 2.0,
    'f2': 0.0,
    'f3': 3.0 / 2.0,
    'b0': math.sqrt(3.0) / 3.0,
    'b1': -1.0 / 3.0,
    'b2': 0.0,
    'b3': 2.0 / 3.0,
    'start_angle': 0.5
}

LAYOUT_FLAT = {
    'f0': 3.0 / 2.0,
    'f1': 0.0,
    'f2': math.sqrt(3.0) / 2.0,
    'f3': math.sqrt(3.0),
    'b0': 2.0 / 3.0,
    'b1': 0.0,
    'b2': -1.0 / 3.0,
    'b3': math.sqrt(3.0) / 3.0,
    'start_angle': 0.0
}

# Hex direction vectors (cube coordinates)
CUBE_DIRECTIONS = [
    (1, 0, -1), (1, -1, 0), (0, -1, 1),
    (-1, 0, 1), (-1, 1, 0), (0, 1, -1)
]

# ======================
# Coordinate Conversions
# ======================

def axial_to_cube(hex: AxialHex) -> CubeHex:
    """Convert axial coordinates to cube coordinates."""
    q, r = hex
    s = -q - r
    return (q, r, s)

def cube_to_axial(hex: CubeHex) -> AxialHex:
    """Convert cube coordinates to axial coordinates."""
    q, r, s = hex
    return (q, r)

def cube_to_oddr(hex: CubeHex) -> OffsetHex:
    """Convert cube coordinates to odd-r offset coordinates."""
    q, r, s = hex
    col = q + (r - (r & 1)) // 2
    row = r
    return (col, row)

def oddr_to_cube(hex: OffsetHex) -> CubeHex:
    """Convert odd-r offset coordinates to cube coordinates."""
    col, row = hex
    q = col - (row - (row & 1)) // 2
    r = row
    s = -q - r
    return (q, r, s)

def cube_to_evenr(hex: CubeHex) -> OffsetHex:
    """Convert cube coordinates to even-r offset coordinates."""
    q, r, s = hex
    col = q + (r + (r & 1)) // 2
    row = r
    return (col, row)

def evenr_to_cube(hex: OffsetHex) -> CubeHex:
    """Convert even-r offset coordinates to cube coordinates."""
    col, row = hex
    q = col - (row + (row & 1)) // 2
    r = row
    s = -q - r
    return (q, r, s)

def cube_to_oddq(hex: CubeHex) -> OffsetHex:
    """Convert cube coordinates to odd-q offset coordinates."""
    q, r, s = hex
    col = q
    row = r + (q - (q & 1)) // 2
    return (col, row)

def oddq_to_cube(hex: OffsetHex) -> CubeHex:
    """Convert odd-q offset coordinates to cube coordinates."""
    col, row = hex
    q = col
    r = row - (col - (col & 1)) // 2
    s = -q - r
    return (q, r, s)

def cube_to_evenq(hex: CubeHex) -> OffsetHex:
    """Convert cube coordinates to even-q offset coordinates."""
    q, r, s = hex
    col = q
    row = r + (q + (q & 1)) // 2
    return (col, row)

def evenq_to_cube(hex: OffsetHex) -> CubeHex:
    """Convert even-q offset coordinates to cube coordinates."""
    col, row = hex
    q = col
    r = row - (col + (col & 1)) // 2
    s = -q - r
    return (q, r, s)

# ==============
# Hex Arithmetic
# ==============

def cube_add(a: CubeHex, b: CubeHex) -> CubeHex:
    """Add two cube hex coordinates."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def cube_subtract(a: CubeHex, b: CubeHex) -> CubeHex:
    """Subtract two cube hex coordinates."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def cube_scale(hex: CubeHex, k: int) -> CubeHex:
    """Scale a cube hex coordinate by a factor."""
    return (hex[0] * k, hex[1] * k, hex[2] * k)

def cube_rotate_left(hex: CubeHex) -> CubeHex:
    """Rotate a cube hex coordinate 60 degrees left (counter-clockwise)."""
    q, r, s = hex
    return (-s, -q, -r)

def cube_rotate_right(hex: CubeHex) -> CubeHex:
    """Rotate a cube hex coordinate 60 degrees right (clockwise)."""
    q, r, s = hex
    return (-r, -s, -q)

# =================
# Distance Functions
# =================

def cube_distance(a: CubeHex, b: CubeHex) -> int:
    """Calculate the distance between two cube hex coordinates."""
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) // 2

def axial_distance(a: AxialHex, b: AxialHex) -> int:
    """Calculate the distance between two axial hex coordinates."""
    ac = axial_to_cube(a)
    bc = axial_to_cube(b)
    return cube_distance(ac, bc)

def offset_distance(a: OffsetHex, b: OffsetHex, offset_type: str = 'odd-r') -> int:
    """Calculate the distance between two offset hex coordinates."""
    if offset_type == 'odd-r':
        ac = oddr_to_cube(a)
        bc = oddr_to_cube(b)
    elif offset_type == 'even-r':
        ac = evenr_to_cube(a)
        bc = evenr_to_cube(b)
    elif offset_type == 'odd-q':
        ac = oddq_to_cube(a)
        bc = oddq_to_cube(b)
    elif offset_type == 'even-q':
        ac = evenq_to_cube(a)
        bc = evenq_to_cube(b)
    else:
        raise ValueError("Invalid offset type")
    return cube_distance(ac, bc)

# ================
# Neighbor Finding
# ================

def cube_neighbor(hex: CubeHex, direction: int) -> CubeHex:
    """Get the neighbor of a cube hex in the specified direction (0-5)."""
    return cube_add(hex, CUBE_DIRECTIONS[direction % 6])

def axial_neighbor(hex: AxialHex, direction: int) -> AxialHex:
    """Get the neighbor of an axial hex in the specified direction (0-5)."""
    cube = axial_to_cube(hex)
    neighbor = cube_neighbor(cube, direction)
    return cube_to_axial(neighbor)

def offset_neighbor(hex: OffsetHex, direction: int, offset_type: str = 'odd-r') -> OffsetHex:
    """Get the neighbor of an offset hex in the specified direction (0-5)."""
    if offset_type == 'odd-r':
        cube = oddr_to_cube(hex)
    elif offset_type == 'even-r':
        cube = evenr_to_cube(hex)
    elif offset_type == 'odd-q':
        cube = oddq_to_cube(hex)
    elif offset_type == 'even-q':
        cube = evenq_to_cube(hex)
    else:
        raise ValueError("Invalid offset type")
    
    neighbor = cube_neighbor(cube, direction)
    
    if offset_type == 'odd-r':
        return cube_to_oddr(neighbor)
    elif offset_type == 'even-r':
        return cube_to_evenr(neighbor)
    elif offset_type == 'odd-q':
        return cube_to_oddq(neighbor)
    elif offset_type == 'even-q':
        return cube_to_evenq(neighbor)

def cube_neighbors(hex: CubeHex) -> List[CubeHex]:
    """Get all six neighbors of a cube hex."""
    return [cube_neighbor(hex, dir) for dir in range(6)]

def axial_neighbors(hex: AxialHex) -> List[AxialHex]:
    """Get all six neighbors of an axial hex."""
    return [axial_neighbor(hex, dir) for dir in range(6)]

def offset_neighbors(hex: OffsetHex, offset_type: str = 'odd-r') -> List[OffsetHex]:
    """Get all six neighbors of an offset hex."""
    return [offset_neighbor(hex, dir, offset_type) for dir in range(6)]

# =============
# Range Finding
# =============

def cube_ring(center: CubeHex, radius: int) -> List[CubeHex]:
    """Get all hexes in a ring around the center at the given radius."""
    if radius == 0:
        return [center]
    
    results = []
    # Start at the top and rotate right
    hex = cube_add(center, cube_scale(CUBE_DIRECTIONS[4], radius))
    
    for i in range(6):
        for j in range(radius):
            results.append(hex)
            hex = cube_neighbor(hex, i)
    
    return results

def cube_spiral(center: CubeHex, radius: int) -> List[CubeHex]:
    """Get all hexes in a spiral around the center up to the given radius."""
    results = [center]
    for k in range(1, radius + 1):
        results.extend(cube_ring(center, k))
    return results

def axial_ring(center: AxialHex, radius: int) -> List[AxialHex]:
    """Get all hexes in a ring around the center at the given radius (axial)."""
    cube_center = axial_to_cube(center)
    return [cube_to_axial(hex) for hex in cube_ring(cube_center, radius)]

def axial_spiral(center: AxialHex, radius: int) -> List[AxialHex]:
    """Get all hexes in a spiral around the center up to the given radius (axial)."""
    cube_center = axial_to_cube(center)
    return [cube_to_axial(hex) for hex in cube_spiral(cube_center, radius)]

def offset_ring(center: OffsetHex, radius: int, offset_type: str = 'odd-r') -> List[OffsetHex]:
    """Get all hexes in a ring around the center at the given radius (offset)."""
    if offset_type == 'odd-r':
        cube_center = oddr_to_cube(center)
        return [cube_to_oddr(hex) for hex in cube_ring(cube_center, radius)]
    elif offset_type == 'even-r':
        cube_center = evenr_to_cube(center)
        return [cube_to_evenr(hex) for hex in cube_ring(cube_center, radius)]
    elif offset_type == 'odd-q':
        cube_center = oddq_to_cube(center)
        return [cube_to_oddq(hex) for hex in cube_ring(cube_center, radius)]
    elif offset_type == 'even-q':
        cube_center = evenq_to_cube(center)
        return [cube_to_evenq(hex) for hex in cube_ring(cube_center, radius)]
    else:
        raise ValueError("Invalid offset type")

def offset_spiral(center: OffsetHex, radius: int, offset_type: str = 'odd-r') -> List[OffsetHex]:
    """Get all hexes in a spiral around the center up to the given radius (offset)."""
    if offset_type == 'odd-r':
        cube_center = oddr_to_cube(center)
        return [cube_to_oddr(hex) for hex in cube_spiral(cube_center, radius)]
    elif offset_type == 'even-r':
        cube_center = evenr_to_cube(center)
        return [cube_to_evenr(hex) for hex in cube_spiral(cube_center, radius)]
    elif offset_type == 'odd-q':
        cube_center = oddq_to_cube(center)
        return [cube_to_oddq(hex) for hex in cube_spiral(cube_center, radius)]
    elif offset_type == 'even-q':
        cube_center = evenq_to_cube(center)
        return [cube_to_evenq(hex) for hex in cube_spiral(cube_center, radius)]
    else:
        raise ValueError("Invalid offset type")

# =============
# Line Drawing
# =============

def cube_lerp(a: CubeHex, b: CubeHex, t: float) -> CubeHex:
    """Linear interpolation between two cube hexes."""
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t)
    )

def cube_line(a: CubeHex, b: CubeHex) -> List[CubeHex]:
    """Draw a line between two cube hexes."""
    N = cube_distance(a, b)
    a_nudge = (a[0] + 1e-6, a[1] + 1e-6, a[2] - 2e-6)
    b_nudge = (b[0] + 1e-6, b[1] + 1e-6, b[2] - 2e-6)
    results = []
    
    for i in range(N + 1):
        t = 1.0 / N * i
        results.append(cube_round(cube_lerp(a_nudge, b_nudge, t)))
    
    return results

def cube_round(frac: CubeHex) -> CubeHex:
    """Round fractional cube coordinates to the nearest whole hex."""
    q = round(frac[0])
    r = round(frac[1])
    s = round(frac[2])
    
    q_diff = abs(q - frac[0])
    r_diff = abs(r - frac[1])
    s_diff = abs(s - frac[2])
    
    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s
    else:
        s = -q - r
    
    return (q, r, s)

def axial_line(a: AxialHex, b: AxialHex) -> List[AxialHex]:
    """Draw a line between two axial hexes."""
    ac = axial_to_cube(a)
    bc = axial_to_cube(b)
    line = cube_line(ac, bc)
    return [cube_to_axial(hex) for hex in line]

def offset_line(a: OffsetHex, b: OffsetHex, offset_type: str = 'odd-r') -> List[OffsetHex]:
    """Draw a line between two offset hexes."""
    if offset_type == 'odd-r':
        ac = oddr_to_cube(a)
        bc = oddr_to_cube(b)
        line = cube_line(ac, bc)
        return [cube_to_oddr(hex) for hex in line]
    elif offset_type == 'even-r':
        ac = evenr_to_cube(a)
        bc = evenr_to_cube(b)
        line = cube_line(ac, bc)
        return [cube_to_evenr(hex) for hex in line]
    elif offset_type == 'odd-q':
        ac = oddq_to_cube(a)
        bc = oddq_to_cube(b)
        line = cube_line(ac, bc)
        return [cube_to_oddq(hex) for hex in line]
    elif offset_type == 'even-q':
        ac = evenq_to_cube(a)
        bc = evenq_to_cube(b)
        line = cube_line(ac, bc)
        return [cube_to_evenq(hex) for hex in line]
    else:
        raise ValueError("Invalid offset type")

# =================
# Field of View
# =================

def cube_visible(center: CubeHex, radius: int, obstacles: Set[CubeHex]) -> Set[CubeHex]:
    """Calculate field of view from center hex within given radius, avoiding obstacles."""
    visible = set()
    visible.add(center)
    
    for ring_radius in range(1, radius + 1):
        ring = cube_ring(center, ring_radius)
        for hex in ring:
            line = cube_line(center, hex)
            blocked = False
            for h in line:
                if h in obstacles:
                    blocked = True
                    break
                if cube_distance(center, h) > radius:
                    blocked = True
                    break
            if not blocked:
                visible.add(hex)
    
    return visible

def axial_visible(center: AxialHex, radius: int, obstacles: Set[AxialHex]) -> Set[AxialHex]:
    """Calculate field of view from center hex within given radius (axial), avoiding obstacles."""
    cube_center = axial_to_cube(center)
    cube_obstacles = {axial_to_cube(hex) for hex in obstacles}
    visible_cubes = cube_visible(cube_center, radius, cube_obstacles)
    return {cube_to_axial(hex) for hex in visible_cubes}

def offset_visible(center: OffsetHex, radius: int, obstacles: Set[OffsetHex], 
                  offset_type: str = 'odd-r') -> Set[OffsetHex]:
    """Calculate field of view from center hex within given radius (offset), avoiding obstacles."""
    if offset_type == 'odd-r':
        cube_center = oddr_to_cube(center)
        cube_obstacles = {oddr_to_cube(hex) for hex in obstacles}
        visible_cubes = cube_visible(cube_center, radius, cube_obstacles)
        return {cube_to_oddr(hex) for hex in visible_cubes}
    elif offset_type == 'even-r':
        cube_center = evenr_to_cube(center)
        cube_obstacles = {evenr_to_cube(hex) for hex in obstacles}
        visible_cubes = cube_visible(cube_center, radius, cube_obstacles)
        return {cube_to_evenr(hex) for hex in visible_cubes}
    elif offset_type == 'odd-q':
        cube_center = oddq_to_cube(center)
        cube_obstacles = {oddq_to_cube(hex) for hex in obstacles}
        visible_cubes = cube_visible(cube_center, radius, cube_obstacles)
        return {cube_to_oddq(hex) for hex in visible_cubes}
    elif offset_type == 'even-q':
        cube_center = evenq_to_cube(center)
        cube_obstacles = {evenq_to_cube(hex) for hex in obstacles}
        visible_cubes = cube_visible(cube_center, radius, cube_obstacles)
        return {cube_to_evenq(hex) for hex in visible_cubes}
    else:
        raise ValueError("Invalid offset type")

# =============
# Pathfinding
# =============

def cube_bfs(start: CubeHex, goals: Set[CubeHex], obstacles: Set[CubeHex], max_distance: int = None) -> Dict[CubeHex, int]:
    """Breadth-first search on a hex grid, returning distances to goal hexes."""
    frontier = deque()
    frontier.append(start)
    came_from = {}
    distance = {}
    came_from[start] = None
    distance[start] = 0
    found_goals = set()
    
    while frontier:
        current = frontier.popleft()
        
        if current in goals:
            found_goals.add(current)
            if len(found_goals) == len(goals):
                break
        
        for neighbor in cube_neighbors(current):
            if neighbor in obstacles:
                continue
            if neighbor not in distance:
                if max_distance is not None and distance[current] >= max_distance:
                    continue
                frontier.append(neighbor)
                came_from[neighbor] = current
                distance[neighbor] = distance[current] + 1
    
    return distance

def cube_path(start: CubeHex, goal: CubeHex, obstacles: Set[CubeHex]) -> List[CubeHex]:
    """Find the shortest path between two hexes, avoiding obstacles."""
    frontier = deque()
    frontier.append(start)
    came_from = {}
    came_from[start] = None
    
    while frontier:
        current = frontier.popleft()
        
        if current == goal:
            break
        
        for neighbor in cube_neighbors(current):
            if neighbor in obstacles:
                continue
            if neighbor not in came_from:
                frontier.append(neighbor)
                came_from[neighbor] = current
    
    if goal not in came_from:
        return None
    
    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def axial_path(start: AxialHex, goal: AxialHex, obstacles: Set[AxialHex]) -> List[AxialHex]:
    """Find the shortest path between two axial hexes, avoiding obstacles."""
    cube_start = axial_to_cube(start)
    cube_goal = axial_to_cube(goal)
    cube_obstacles = {axial_to_cube(hex) for hex in obstacles}
    cube_path_result = cube_path(cube_start, cube_goal, cube_obstacles)
    if cube_path_result is None:
        return None
    return [cube_to_axial(hex) for hex in cube_path_result]

def offset_path(start: OffsetHex, goal: OffsetHex, obstacles: Set[OffsetHex], 
               offset_type: str = 'odd-r') -> List[OffsetHex]:
    """Find the shortest path between two offset hexes, avoiding obstacles."""
    if offset_type == 'odd-r':
        cube_start = oddr_to_cube(start)
        cube_goal = oddr_to_cube(goal)
        cube_obstacles = {oddr_to_cube(hex) for hex in obstacles}
    elif offset_type == 'even-r':
        cube_start = evenr_to_cube(start)
        cube_goal = evenr_to_cube(goal)
        cube_obstacles = {evenr_to_cube(hex) for hex in obstacles}
    elif offset_type == 'odd-q':
        cube_start = oddq_to_cube(start)
        cube_goal = oddq_to_cube(goal)
        cube_obstacles = {oddq_to_cube(hex) for hex in obstacles}
    elif offset_type == 'even-q':
        cube_start = evenq_to_cube(start)
        cube_goal = evenq_to_cube(goal)
        cube_obstacles = {evenq_to_cube(hex) for hex in obstacles}
    else:
        raise ValueError("Invalid offset type")
    
    cube_path_result = cube_path(cube_start, cube_goal, cube_obstacles)
    if cube_path_result is None:
        return None
    
    if offset_type == 'odd-r':
        return [cube_to_oddr(hex) for hex in cube_path_result]
    elif offset_type == 'even-r':
        return [cube_to_evenr(hex) for hex in cube_path_result]
    elif offset_type == 'odd-q':
        return [cube_to_oddq(hex) for hex in cube_path_result]
    elif offset_type == 'even-q':
        return [cube_to_evenq(hex) for hex in cube_path_result]

# ================
# Map Generation
# ================

def generate_hex_map(radius: int, center: CubeHex = (0, 0, 0)) -> Set[CubeHex]:
    """Generate a hexagonal map with the given radius around the center."""
    return set(cube_spiral(center, radius))

def generate_rectangular_map(width: int, height: int, offset_type: str = 'odd-r') -> Set[OffsetHex]:
    """Generate a rectangular map with the given width and height."""
    hexes = set()
    for col in range(width):
        for row in range(height):
            hexes.add((col, row))
    return hexes

# =============
# Visualization
# =============

def hex_to_pixel(hex: CubeHex, size: float, layout: str = 'pointy') -> Tuple[float, float]:
    """Convert cube hex coordinates to pixel coordinates."""
    if layout == 'pointy':
        orientation = LAYOUT_POINTY
    else:
        orientation = LAYOUT_FLAT
    
    x = (orientation['f0'] * hex[0] + orientation['f1'] * hex[1]) * size
    y = (orientation['f2'] * hex[0] + orientation['f3'] * hex[1]) * size
    return (x, y)

def pixel_to_hex(point: Tuple[float, float], size: float, layout: str = 'pointy') -> CubeHex:
    """Convert pixel coordinates to cube hex coordinates."""
    if layout == 'pointy':
        orientation = LAYOUT_POINTY
    else:
        orientation = LAYOUT_FLAT
    
    x, y = point
    x /= size
    y /= size
    
    q = orientation['b0'] * x + orientation['b1'] * y
    r = orientation['b2'] * x + orientation['b3'] * y
    return cube_round((q, r, -q - r))

def hex_corner_offset(corner: int, size: float, layout: str = 'pointy') -> Tuple[float, float]:
    """Get the pixel offset for a hex corner (0-5)."""
    angle_deg = 60 * corner + (30 if layout == 'pointy' else 0)
    angle_rad = math.pi / 180 * angle_deg
    return (size * math.cos(angle_rad), size * math.sin(angle_rad))

def polygon_corners(hex: CubeHex, size: float, layout: str = 'pointy') -> List[Tuple[float, float]]:
    """Get all six corner points of a hex in pixel coordinates."""
    corners = []
    center = hex_to_pixel(hex, size, layout)
    for i in range(6):
        offset = hex_corner_offset(i, size, layout)
        corners.append((center[0] + offset[0], center[1] + offset[1]))
    return corners