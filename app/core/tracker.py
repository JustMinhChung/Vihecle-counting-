from collections import deque
import numpy as np

def ccw(A, B, C):
    """
    Checks if points A, B, C are in counter-clockwise order.
    """
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def intersect(A, B, C, D):
    """
    Returns True if line segment AB intersects with CD.
    """
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

class GateTracker:
    """
    Tracks vehicle trajectories and handles gate crossing logic.
    """
    def __init__(self, history_len=20):
        self.history_len = history_len
        # track_id -> deque of centroids (x, y)
        self.trajectories = {}
        # Track IDs that already crossed the line to avoid duplicate counting
        self.counted_ids = set()
        
        # Counters
        self.in_count = 0
        self.out_count = 0
        
    def reset(self):
        self.trajectories.clear()
        self.counted_ids.clear()
        self.in_count = 0
        self.out_count = 0
        
    def update(self, detections, line_pt1, line_pt2):
        """
        Updates trajectories and checks for crossings against the gate line.
        detections: list of dictionaries from detector
        line_pt1, line_pt2: tuples of (x, y) absolute coordinates of the gate line
        
        Returns:
            list of crossing events: [{'id': id, 'class_name': name, 'direction': 'In'/'Out'}]
        """
        events = []
        active_ids = set()
        
        if not detections:
            print("[Tracker Debug] No vehicles detected in this frame.")
        else:
            print(f"[Tracker Debug] Vehicles detected: {len(detections)}")
            
        for det in detections:
            track_id = det['id']
            centroid = det['centroid']
            class_name = det['class_name']
            active_ids.add(track_id)
            
            # Update trajectory
            if track_id not in self.trajectories:
                self.trajectories[track_id] = deque(maxlen=self.history_len)
            self.trajectories[track_id].append(centroid)
            
            print(f"  - ID: {track_id} ({class_name}) at {centroid}, Traj points: {len(self.trajectories[track_id])}")
            
            # Check crossing if we have at least 2 points in trajectory and haven't counted yet
            if track_id not in self.counted_ids and len(self.trajectories[track_id]) >= 2:
                # We check the crossing of the segment from the previous centroid to the current one
                c_prev = self.trajectories[track_id][-2]
                c_curr = self.trajectories[track_id][-1]
                
                # Check intersection between line (line_pt1, line_pt2) and trajectory segment (c_prev, c_curr)
                intersected = intersect(line_pt1, line_pt2, c_prev, c_curr)
                print(f"    Check Crossing: ID {track_id} Prev {c_prev} -> Curr {c_curr} | Gate Line: {line_pt1} -> {line_pt2} | Intersect: {intersected}")
                
                if intersected:
                    self.counted_ids.add(track_id)
                    
                    # Calculate direction using 2D cross product of gate vector and travel vector
                    # Gate vector: line_pt2 - line_pt1
                    # Travel vector: c_curr - c_prev
                    gate_dx = line_pt2[0] - line_pt1[0]
                    gate_dy = line_pt2[1] - line_pt1[1]
                    
                    travel_dx = c_curr[0] - c_prev[0]
                    travel_dy = c_curr[1] - c_prev[1]
                    
                    cross_product = (gate_dx * travel_dy) - (gate_dy * travel_dx)
                    
                    # Decide IN vs OUT based on cross product sign
                    # If we draw a line left-to-right, crossing downwards yields cross_product > 0 (In)
                    # crossing upwards yields cross_product < 0 (Out)
                    if cross_product > 0:
                        direction = "In"
                        self.in_count += 1
                    else:
                        direction = "Out"
                        self.out_count += 1
                    
                    print(f"    *** ID {track_id} ({class_name}) CROSSED GATE ({direction})! IN: {self.in_count}, OUT: {self.out_count} ***")
                        
                    events.append({
                        'id': track_id,
                        'class_name': class_name,
                        'direction': direction,
                        'centroid': c_curr
                    })
                    
        # Clean up old trajectories for IDs that are no longer active (to free memory)
        # We keep trajectories for a bit, but if they disappear for too long, delete them.
        inactive_ids = set(self.trajectories.keys()) - active_ids
        for inactive_id in inactive_ids:
            # Optionally remove, or keep a small buffer. Let's remove them if they are gone.
            del self.trajectories[inactive_id]
            
        return events
