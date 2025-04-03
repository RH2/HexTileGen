class Point:
    def __init__(self, x, y, z, status=True):
        self.x = x
        self.y = y
        self.z = z
        self.status = status  # Active/inactive status
        self.edges = []  # List of edges that reference this point
        
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        tolerance = 0.01
        return (abs(self.x - other.x) <= tolerance and 
                abs(self.y - other.y) <= tolerance and 
                abs(self.z - other.z) <= tolerance)
    
    def __hash__(self):
        return hash((self.x, self.y, self.z))
    
    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z}, status={self.status})"
    
    def update_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Edge:
    def __init__(self, point1, point2, status=True):
        self.point1 = point1
        self.point2 = point2
        self.status = status  # Active/inactive status
        self.faces = []  # List of faces that reference this edge
        self.midpoint = None  # Reference to midpoint (if exists)
        
        # Register this edge with its points
        point1.edges.append(self)
        point2.edges.append(self)
        
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return (self.point1 == other.point1 and self.point2 == other.point2) or \
               (self.point1 == other.point2 and self.point2 == other.point1)
    
    def __hash__(self):
        # Order points consistently for hash
        p1, p2 = sorted([hash(self.point1), hash(self.point2)])
        return hash((p1, p2))
    
    def __repr__(self):
        return f"Edge({self.point1}, {self.point2}, status={self.status})"
    
    def other_point(self, point):
        """Given one point, return the other point of the edge"""
        if point == self.point1:
            return self.point2
        elif point == self.point2:
            return self.point1
        return None


class Face:
    def __init__(self, edges, status=True):
        self.edges = edges  # List of edges that make up this face
        self.status = status  # Active/inactive status
        
        # Register this face with its edges
        for edge in edges:
            edge.faces.append(self)
    
    def __eq__(self, other):
        if not isinstance(other, Face):
            return False
        return set(self.edges) == set(other.edges)
    
    def __hash__(self):
        return hash(frozenset(self.edges))
    
    def __repr__(self):
        return f"Face({self.edges}, status={self.status})"


class PolygonFramework:
    def __init__(self):
        self.points = set()
        self.edges = set()
        self.faces = set()
    
    # Point operations
    def add_point(self, point):
        """Add a point if it doesn't already exist"""
        if point in self.points:
            existing = next(p for p in self.points if p == point)
            return existing
        self.points.add(point)
        return point
    
    def remove_point(self, point):
        """Remove a point and all edges/faces that reference it"""
        if point not in self.points:
            return False
        
        # Find all edges connected to this point
        connected_edges = point.edges.copy()
        
        # Remove all connected edges (which will handle faces)
        for edge in connected_edges:
            self.remove_edge(edge)
        
        self.points.remove(point)
        return True
    
    def update_point(self, point, x, y, z):
        """Update a point's position"""
        if point in self.points:
            point.update_position(x, y, z)
            return True
        return False
    
    # Edge operations
    def add_edge(self, point1, point2):
        """Add an edge between two points if it doesn't exist (checks both point orders)"""
        # First check if both points exist in the framework
        existing_p1 = next((p for p in self.points if p == point1), None)
        existing_p2 = next((p for p in self.points if p == point2), None)
        
        if not existing_p1 or not existing_p2:
            raise ValueError("Both points must exist in the framework before creating an edge")
        
        # Now check if an edge already exists between these points (in either order)
        for edge in self.edges:
            if (edge.point1 == existing_p1 and edge.point2 == existing_p2) or \
            (edge.point1 == existing_p2 and edge.point2 == existing_p1):
                return edge
        
        # If we get here, the edge doesn't exist - create it with the existing points
        edge = Edge(existing_p1, existing_p2)
        self.edges.add(edge)
        return edge
    
    def remove_edge(self, edge):
        """Remove an edge and all faces that reference it"""
        if edge not in self.edges:
            return False
        
        # Find all faces connected to this edge
        connected_faces = edge.faces.copy()
        
        # Remove all connected faces
        for face in connected_faces:
            self.remove_face(face)
        
        # Remove edge from its points' edge lists
        edge.point1.edges.remove(edge)
        edge.point2.edges.remove(edge)
        
        self.edges.remove(edge)
        return True
    
    def update_edge(self, edge, new_point1, new_point2):
        """Update an edge's points"""
        if edge not in self.edges:
            return False
        
        # Remove old references
        edge.point1.edges.remove(edge)
        edge.point2.edges.remove(edge)
        
        # Update points
        edge.point1 = new_point1
        edge.point2 = new_point2
        
        # Add new references
        new_point1.edges.append(edge)
        new_point2.edges.append(edge)
        
        return True
    
    # Face operations
    def add_face(self, edges):
        """Add a face with the given edges"""
        # Check if all edges exist in the framework
        for edge in edges:
            if edge not in self.edges:
                raise ValueError("All edges must exist in the framework before creating a face")
        
        face = Face(edges)
        if face in self.faces:
            existing = next(f for f in self.faces if f == face)
            return existing
        self.faces.add(face)
        return face
    
    def remove_face(self, face):
        """Remove a face"""
        if face not in self.faces:
            return False
        
        # Remove face from its edges' face lists
        for edge in face.edges:
            edge.faces.remove(face)
        
        self.faces.remove(face)
        return True
    
    def update_face(self, face, new_edges):
        """Update a face's edges"""
        if face not in self.faces:
            return False
        
        # Remove old references
        for edge in face.edges:
            edge.faces.remove(face)
        
        # Update edges
        face.edges = new_edges
        
        # Add new references
        for edge in new_edges:
            edge.faces.append(face)
        
        return True
    
    def merge_close_points(self, tolerance=1e-6):
        """
        Merge points that are closer than specified tolerance
        :param tolerance: Maximum distance to consider points the same
        :return: Number of points merged
        """
        original_count = len(self.points)
        points_list = list(self.points)
        
        # Create a spatial index for faster proximity checks
        from scipy.spatial import KDTree
        coords = [(p.x, p.y, p.z) for p in points_list]
        tree = KDTree(coords)
        
        # Find all point pairs within tolerance
        pairs = tree.query_pairs(tolerance)
        
        # Process pairs to find connected components
        merged = set()
        for i, j in pairs:
            if i not in merged and j not in merged:
                # Keep the first point, merge others into it
                keeper = points_list[i]
                to_merge = points_list[j]
                
                # Update all edges referencing to_merge
                for edge in list(to_merge.edges):
                    if edge.point1 == to_merge:
                        edge.point1 = keeper
                    if edge.point2 == to_merge:
                        edge.point2 = keeper
                    keeper.edges.append(edge)
                
                merged.add(j)
                self.points.remove(to_merge)
        
        return original_count - len(self.points)



    # Utility functions
    def find_edges_with_shared_point(self, point):
        """Find all edges that share the given point"""
        return [edge for edge in self.edges if point in (edge.point1, edge.point2)]
    
    def find_faces_with_shared_point(self, point):
        """Find all faces that share the given point"""
        connected_edges = self.find_edges_with_shared_point(point)
        connected_faces = set()
        for edge in connected_edges:
            connected_faces.update(edge.faces)
        return list(connected_faces)
    
    def find_faces_with_shared_edge(self, edge):
        """Find all faces that share the given edge"""
        return edge.faces.copy()
    
    def add_polygon(self, points):
        """Add a polygon by checking for existing points and creating edges/face"""
        # Check if points already exist or add new ones
        existing_points = []
        for point in points:
            existing_point = self.add_point(point)
            existing_points.append(existing_point)
        
        # Create edges between consecutive points
        edges = []
        num_points = len(existing_points)
        for i in range(num_points):
            point1 = existing_points[i]
            point2 = existing_points[(i + 1) % num_points]
            edge = self.add_edge(point1, point2)
            edges.append(edge)
        
        # Create face from the edges
        face = self.add_face(edges)
        return face