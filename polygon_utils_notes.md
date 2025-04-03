module: polygon_utils.py
## polygon_utils Classes

### `Point`
- **Attributes**:
  - `x`, `y`, `z`: Coordinates
  - `status`: Boolean (active/inactive)
  - `edges`: List of connected edges
- **Methods**:
  - `update_position(x, y, z)`: Updates coordinates
  - Equality comparison based on coordinates

### `Edge`
- **Attributes**:
  - `point1`, `point2`: Connected points
  - `status`: Boolean (active/inactive)
  - `faces`: List of connected faces
  - `midpoint`: Reference to midpoint (optional)
- **Methods**:
  - `other_point(point)`: Returns the opposite point
  - Equality comparison based on connected points

### `Face`
- **Attributes**:
  - `edges`: List of boundary edges
  - `status`: Boolean (active/inactive)
- **Methods**:
  - Equality comparison based on edge set

### `PolygonFramework`
- **Attributes**:
  - `points`, `edges`, `faces`: Sets of all elements

## Core Functions

### Point Operations
| Function | Arguments | Returns | Description |
|----------|-----------|---------|-------------|
| `add_point` | `point: Point` | `Point` | Adds point or returns existing |
| `remove_point` | `point: Point` | `bool` | Removes point and connected elements |
| `update_point` | `point: Point`, `x,y,z: float` | `bool` | Updates point coordinates |

### Edge Operations
| Function | Arguments | Returns | Description |
|----------|-----------|---------|-------------|
| `add_edge` | `point1, point2: Point` | `Edge` | Creates edge between points |
| `remove_edge` | `edge: Edge` | `bool` | Removes edge and connected faces |
| `update_edge` | `edge: Edge`, `new_point1, new_point2: Point` | `bool` | Updates edge endpoints |

### Face Operations
| Function | Arguments | Returns | Description |
|----------|-----------|---------|-------------|
| `add_face` | `edges: List[Edge]` | `Face` | Creates face from edges |
| `remove_face` | `face: Face` | `bool` | Removes face |
| `update_face` | `face: Face`, `new_edges: List[Edge]` | `bool` | Updates face edges |

### Utility Functions
| Function | Arguments | Returns | Description |
|----------|-----------|---------|-------------|
| `find_edges_with_shared_point` | `point: Point` | `List[Edge]` | Finds all edges connected to point |
| `find_faces_with_shared_point` | `point: Point` | `List[Face]` | Finds all faces connected to point |
| `find_faces_with_shared_edge` | `edge: Edge` | `List[Face]` | Finds all faces using edge |
| `add_polygon` | `points: List[Point]` | `Face` | Creates polygon from points |
