import time
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from app.core.detector import VehicleDetector
from app.core.tracker import GateTracker
from app import config

class VideoWorker(QThread):
    """
    Worker thread that reads video frames, runs detection and tracking,
    draws overlays, and emits the processed frames and events.
    """
    frame_ready = Signal(QImage, int)
    event_detected = Signal(dict)
    progress_changed = Signal(int, int)  # current_frame, total_frames
    fps_updated = Signal(float)
    playback_finished = Signal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.detector = VehicleDetector()
        self.tracker = GateTracker()
        
        # Thread control flags
        self.running = False
        self.paused = False
        
        # Gate line relative coordinates
        self.rel_line_pt1, self.rel_line_pt2 = config.DEFAULT_LINE
        
        # Seek control
        self.seek_target = -1
        
        # Video properties
        self.total_frames = 0
        self.fps = 30.0
        self.width = 0
        self.height = 0
        
        # Initialize video capture to read metadata
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.detector.set_fps(self.fps)
        cap.release()

    def set_gate_line(self, pt1, pt2):
        """
        Updates the counting line. Points are tuples of floats (0.0 to 1.0)
        representing relative coordinates on the video frame.
        """
        self.rel_line_pt1 = pt1
        self.rel_line_pt2 = pt2

    def set_confidence(self, conf):
        """
        Dynamically updates the detector confidence threshold.
        """
        self.detector.confidence = conf

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.paused = False

    def seek_to_frame(self, frame_num):
        """
        Requests seeking to a specific frame number in the next loop cycle.
        """
        if 0 <= frame_num < self.total_frames:
            self.seek_target = frame_num

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            self.playback_finished.emit()
            return

        self.running = True
        current_frame_idx = 0
        
        # Reset tracker state
        self.tracker.reset()
        
        # FPS calculation variables
        fps_start_time = time.time()
        fps_frame_count = 0
        
        while self.running:
            # Handle seek request
            if self.seek_target >= 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_target)
                current_frame_idx = self.seek_target
                self.seek_target = -1
                
            if self.paused:
                time.sleep(0.05)
                continue
                
            t_start = time.time()
            
            # Read next frame
            ret, frame = cap.read()
            if not ret:
                # Loop video or finish
                break
                
            # Calculate absolute line coordinates
            abs_pt1 = (int(self.rel_line_pt1[0] * self.width), int(self.rel_line_pt1[1] * self.height))
            abs_pt2 = (int(self.rel_line_pt2[0] * self.width), int(self.rel_line_pt2[1] * self.height))
            
            # 1. Detection and Tracking
            detections = self.detector.detect_and_track(frame)
            
            # 2. Update crossing logic
            events = self.tracker.update(detections, abs_pt1, abs_pt2)
            
            # Handle events
            for event in events:
                timestamp = current_frame_idx / self.fps
                # Format timestamp as MM:SS.ms
                mins = int(timestamp // 60)
                secs = int(timestamp % 60)
                ms = int((timestamp - int(timestamp)) * 1000)
                timestamp_str = f"{mins:02d}:{secs:02d}.{ms:03d}"
                
                event_data = {
                    'frame': current_frame_idx,
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'id': event['id'],
                    'class_name': event['class_name'],
                    'direction': event['direction']
                }
                self.event_detected.emit(event_data)
                
            # 3. Draw overlays on the frame
            # Draw Gate Line
            cv2.line(frame, abs_pt1, abs_pt2, (0, 165, 255), 3)  # Orange gate line
            cv2.putText(frame, "GATE", (abs_pt1[0] + 5, abs_pt1[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # Draw Detections
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                track_id = det['id']
                cls_name = det['class_name']
                
                # Draw bounding box
                color = (0, 255, 0) if track_id in self.tracker.counted_ids else (255, 0, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw ID and Label
                label = f"{cls_name} ID:{track_id}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Draw trajectory tails (last 10 points)
                traj = self.tracker.trajectories.get(track_id, [])
                for i in range(1, len(traj)):
                    cv2.line(frame, traj[i-1], traj[i], color, 2)
                    
            # Draw counts on top-left of the screen
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (220, 90), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
            
            cv2.putText(frame, f"IN:  {self.tracker.in_count}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"OUT: {self.tracker.out_count}", (20, 75), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # 4. Prepare frame for UI
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            q_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            
            # Emit frame (creating a copy is safer to avoid garbage collection/segfaults)
            self.frame_ready.emit(q_img.copy(), current_frame_idx)
            self.progress_changed.emit(current_frame_idx, self.total_frames)
            
            current_frame_idx += 1
            fps_frame_count += 1
            
            # Calculate FPS every 1 second
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                fps = fps_frame_count / elapsed
                self.fps_updated.emit(fps)
                fps_frame_count = 0
                fps_start_time = time.time()
                
            # Frame-skipping logic to maintain wall-clock real-time speed
            t_end = time.time()
            process_duration = t_end - t_start
            target_duration = 1.0 / self.fps
            
            if process_duration > target_duration:
                # CPU is too slow, skip decoding of subsequent frames to catch up
                frames_to_skip = int(process_duration / target_duration)
                # Cap maximum skip per loop iteration to avoid excessive stuttering
                frames_to_skip = min(frames_to_skip, 5)
                for _ in range(frames_to_skip):
                    if not cap.grab():
                        break
                    current_frame_idx += 1
            else:
                # CPU is fast, sleep to lock execution rate to matching video FPS
                time.sleep(target_duration - process_duration)
            
        cap.release()
        self.playback_finished.emit()
