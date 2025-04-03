import math
import random
from polygon_utils import Point, Edge, Face, PolygonFramework
from hextile_utils import HexTile

def create_hexagon_grid(radius, rows, cols, file_path, 
                       point_status_bias=0.5, edge_status_bias=0.5,
                       debug_mode=False):
    """
    Creates a hexagonal grid with random point/edge statuses and saves as SVG.
    
    Args:
        radius: Radius of each hexagon
        rows: Number of rows
        cols: Number of columns
        file_path: Output SVG path
        point_status_bias: Probability (0-1) for points to be active
        edge_status_bias: Probability (0-1) for edges to be active
        debug_mode: Show status colors if True
    """
    framework = PolygonFramework()
    
    # Hexagon geometry
    hex_width = radius * math.sqrt(3)
    hex_height = radius * 1.5
    
    # Create grid
    for row in range(rows):
        for col in range(cols):
            x_offset = col * hex_width
            if row % 2 == 1:
                x_offset += hex_width / 2
            y_offset = row * hex_height
            
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.pi / 180 * angle_deg
                x = x_offset + radius * math.cos(angle_rad)
                y = y_offset + radius * math.sin(angle_rad)
                points.append(framework.add_point(Point(x, y, 0)))

            edges = []
            for i in range(6):
                edges.append(framework.add_edge(points[i], points[(i+1)%6]))
            
            framework.add_face(edges)
    # Merge points that drifted close during operations
    merged_count = framework.merge_close_points()
    print(f"Merged {merged_count} overlapping points")
    
    # Set random point statuses
    for point in framework.points:
        point.status = random.random() < point_status_bias
    
    # Set random edge statuses
    for edge in framework.edges:
        edge.status = random.random() < edge_status_bias
    
    # Generate SVG with optional debug visualization
    svg_content = generate_svg(framework, radius, debug_mode)
    
    with open(file_path, 'w') as f:
        f.write(svg_content)

def generate_svg(framework, radius, debug_mode):
    """Generates SVG with optional debug visualization and hextile layer."""
    min_x = min(p.x for p in framework.points)
    max_x = max(p.x for p in framework.points)
    min_y = min(p.y for p in framework.points)
    max_y = max(p.y for p in framework.points)
    
    width = max_x - min_x + 20
    height = max_y - min_y + 20
    
    svg_lines = [
        f'<svg width="{width}" height="{height}" viewBox="{min_x-10} {min_y-10} {width} {height}" '
        'xmlns="http://www.w3.org/2000/svg">'
    ]
    
    # Start underpainting group
    svg_lines.append('<g id="underpainting">')
    
    # Draw edges with status colors if debug mode
    for edge in framework.edges:
        if not edge.status and not debug_mode:
            continue
            
        x1, y1 = edge.point1.x, edge.point1.y
        x2, y2 = edge.point2.x, edge.point2.y
        
        if debug_mode:
            color = "green" if edge.status else "red"
            svg_lines.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{color}" stroke-width="2" stroke-opacity="0.7"/>'
            )
        else:
            svg_lines.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                'stroke="black" stroke-width="1"/>'
            )
    
    # Draw points with status colors if debug mode
    if debug_mode:
        for point in framework.points:
            color = "green" if point.status else "red"
            svg_lines.append(
                f'<circle cx="{point.x}" cy="{point.y}" r="{radius/6}" '
                f'fill="{color}" stroke="black" stroke-width="0.5"/>'
            )
    
    # Close underpainting group
    svg_lines.append('</g>')
    
    # Start final group (hextiles)
    svg_lines.append('<g id="final">')
    
    # Create hextiles at each hexagon center
    for face in framework.faces:
        # Calculate hexagon center (average of all vertices)
        x_coords = [edge.point1.x for edge in face.edges] + [edge.point2.x for edge in face.edges]
        y_coords = [edge.point1.y for edge in face.edges] + [edge.point2.y for edge in face.edges]
        cx = sum(x_coords) / len(x_coords)
        cy = sum(y_coords) / len(y_coords)
        
        # Calculate average edge length for sizing
        edge_lengths = [
            math.sqrt((edge.point1.x - edge.point2.x)**2 + (edge.point1.y - edge.point2.y)**2)
            for edge in face.edges
        ]
        edge_length = sum(edge_lengths) / len(edge_lengths)
        
        # Create tile with proper positioning and sizing
        tile = HexTile(cx=cx, cy=cy, side_length=edge_length, path_width=edge_length/10)
        
        # Convert face status to hextile occupancy
        binary_pattern = map_face_to_binary_array(face)
        tile.occupancy = binary_pattern_to_hextile_occupancy(binary_pattern)
        tile.creategeometry()
        
        # Add the tile SVG to our output
        svg_lines.append(tile.svgexport())
    
    # Close final group
    svg_lines.append('</g>')
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

def binary_pattern_to_hextile_occupancy(binary_pattern):
    """
    Converts a 12-element binary pattern (6 points + 6 edges) to a 13-element hextile occupancy.
    
    Args:
        binary_pattern: List of 12 binary values [p1, e1, p2, e2, ..., p6, e6]
        
    Returns:
        List[int]: 13-element hextile occupancy pattern
    """
    # Center path (index 0) - average of point statuses (even indices)
    center = 1 if sum(binary_pattern[::2]) / 6 > 0.5 else 0
    
    # Outer paths (indices 1-12) - interleave point and edge statuses
    # Each point/edge gets two path segments for better visibility
    outer_paths = []
    for i in range(12):
        # Alternate between point and edge statuses
        src_index = (i // 2) % 6 * 2  # Points are at even indices
        if i % 2 == 1:
            src_index += 1  # Edges are at odd indices
        outer_paths.append(binary_pattern[src_index % len(binary_pattern)])
    
    return [center] + outer_paths

def map_face_to_binary_array(face):
    """
    Converts a face's edges and point statuses into a binary array.
    Pattern: [point1_status, edge1_status, point2_status, edge2_status, ...]
    
    Args:
        face: Face object from polygon_utils
        
    Returns:
        List[int]: Binary array of statuses (0=False, 1=True)
    """
    binary_array = []
    
    # Get all edges of the face in order
    edges = face.edges
    
    # For hexagonal faces, we expect 6 edges
    if len(edges) != 6:
        raise ValueError("This function currently only supports hexagonal faces")
    
    # We'll traverse the edges in order and record point/edge statuses
    # Start with the first point of the first edge
    current_point = edges[0].point1
    
    for edge in edges:
        # Verify current_point belongs to this edge
        if current_point not in [edge.point1, edge.point2]:
            # If not, switch to the other point (shouldn't happen with proper face structure)
            current_point = edge.point2 if current_point == edge.point1 else edge.point1
        
        # Add point status (0 or 1)
        binary_array.append(1 if current_point.status else 0)
        
        # Add edge status (0 or 1)
        binary_array.append(1 if edge.status else 0)
        
        # Move to next point (the other point of this edge)
        current_point = edge.point2 if current_point == edge.point1 else edge.point1
    
    return binary_array

# Example usage
if __name__ == "__main__":
    file_path = r'C:\Users\Reference\Desktop\polyhex20250402d.svg'
    
    # Create grid with:
    # - 60% chance points are active
    # - 70% chance edges are active
    # - Debug visualization enabled
    create_hexagon_grid(
        radius=20,
        rows=10,
        cols=10,
        file_path=file_path,
        point_status_bias=0.10,
        edge_status_bias=0.20,
        debug_mode=False
    )
    
    print(f"Hexagon grid with status visualization saved to {file_path}")