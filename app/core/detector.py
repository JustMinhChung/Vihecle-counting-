import cv2
import numpy as np
from collections import deque
from app import config

class VehicleDetector:
    """
    Lightweight Motion Detector and Centroid Tracker using 0.1s frame differencing.
    Replaces deep learning (YOLO) with highly optimized pixel-level change analysis
    to run in real-time on any hardware without internet or GPU requirements.
    """
    def __init__(self):
        # UI Compatibility Attributes
        self.confidence = config.CONFIDENCE_THRESHOLD
        
        # Motion History Buffer
        self.frame_queue = deque()
        self.fps = 30.0
        
        # Centroid Tracker variables
        self.next_object_id = 1
        # active_trackers: track_id -> {'centroid': (x,y), 'bbox': [x1,y1,x2,y2], 'lost_frames': int}
        self.active_trackers = {}
        
        # Configuration Tunables
        self.min_contour_area = 500   # Minimum area in pixels to filter noise
        self.max_distance = 90        # Max distance (pixels) between frames to associate tracks
        self.max_lost_frames = 6      # Grace period to keep tracking a temporarily lost object

    def set_fps(self, fps):
        """
        Updates the FPS value to ensure the frame delay matches exactly 0.1 seconds.
        """
        self.fps = fps or 30.0

    def detect_and_track(self, frame):
        """
        Computes the frame difference over 0.1 seconds, isolates moving contours,
        associates centroids across frames, and returns tracking results.
        """
        # Calculate frame buffer size for exactly 0.1 seconds delay
        delay_frames = max(1, int(0.1 * self.fps))
        self.frame_queue.append(frame.copy())
        
        if len(self.frame_queue) <= delay_frames:
            return []
            
        # Get historical frame from 0.1s ago
        ref_frame = self.frame_queue.popleft()
        
        # 1. Absolute frame subtraction (intensity change in 0.1s)
        diff = cv2.absdiff(frame, ref_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Gaussian Blur to smooth noise
        blurred = cv2.GaussianBlur(gray_diff, (9, 9), 0)
        
        # Threshold: map self.confidence (0.1 to 0.9) to a threshold limit of (10 to 60) gray levels
        thresh_limit = int(10 + (self.confidence * 60))
        _, thresh = cv2.threshold(blurred, thresh_limit, 255, cv2.THRESH_BINARY)
        
        # Morphological dilation to group close-by motion blobs into single objects
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # 2. Extract contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        current_detections = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < self.min_contour_area:
                continue
                
            x, y, w_box, h_box = cv2.boundingRect(c)
            cx = int(x + w_box / 2)
            cy = int(y + h_box / 2)
            
            current_detections.append({
                'bbox': [x, y, x + w_box, y + h_box],
                'centroid': (cx, cy)
            })
            
        # 3. Associate tracks using closest Euclidean distance (Centroid Tracker)
        updated_trackers = {}
        used_detection_indices = set()
        
        # Match existing trackers
        for track_id, tracker in list(self.active_trackers.items()):
            prev_centroid = tracker['centroid']
            best_dist = float('inf')
            best_idx = -1
            
            for idx, det in enumerate(current_detections):
                if idx in used_detection_indices:
                    continue
                
                det_centroid = det['centroid']
                dist = np.sqrt((prev_centroid[0] - det_centroid[0])**2 + (prev_centroid[1] - det_centroid[1])**2)
                
                if dist < best_dist and dist < self.max_distance:
                    best_dist = dist
                    best_idx = idx
            
            if best_idx != -1:
                # Associated!
                used_detection_indices.add(best_idx)
                updated_trackers[track_id] = {
                    'centroid': current_detections[best_idx]['centroid'],
                    'bbox': current_detections[best_idx]['bbox'],
                    'lost_frames': 0
                }
            else:
                # Object lost in this frame, increment counter
                lost_count = tracker['lost_frames'] + 1
                if lost_count <= self.max_lost_frames:
                    updated_trackers[track_id] = {
                        'centroid': prev_centroid,
                        'bbox': tracker['bbox'],
                        'lost_frames': lost_count
                    }
                    
        # Spawn new tracks for unassociated detections
        for idx, det in enumerate(current_detections):
            if idx not in used_detection_indices:
                track_id = self.next_object_id
                self.next_object_id += 1
                
                updated_trackers[track_id] = {
                    'centroid': det['centroid'],
                    'bbox': det['bbox'],
                    'lost_frames': 0
                }
                
        self.active_trackers = updated_trackers
        
        # 4. Format outputs (simulating detector outputs for UI compatibility)
        detections = []
        for track_id, tracker in self.active_trackers.items():
            if tracker['lost_frames'] == 0:
                detections.append({
                    'id': track_id,
                    'class_id': 0,
                    'class_name': "Object",  # Object-agnostic class
                    'bbox': tracker['bbox'],
                    'centroid': tracker['centroid'],
                    'confidence': 1.0
                })
                
        return detections
