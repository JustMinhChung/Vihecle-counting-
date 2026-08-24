import os
import cv2
from PySide6.QtCore import QThread, Signal
from app import config

class ClipperThread(QThread):
    """
    Background thread to extract a segment from a video file and save it locally.
    This prevents UI freezes during disk I/O operations.
    """
    finished_signal = Signal(str)
    failed_signal = Signal(str)

    def __init__(self, src_path, start_time, duration, output_name):
        super().__init__()
        self.src_path = src_path
        self.start_time = max(0.0, start_time)
        self.duration = duration
        self.output_name = output_name

    def run(self):
        try:
            # Ensure output directory exists
            os.makedirs(config.CLIPS_DIR, exist_ok=True)
            out_path = os.path.join(config.CLIPS_DIR, self.output_name)

            cap = cv2.VideoCapture(self.src_path)
            if not cap.isOpened():
                self.failed_signal.emit(f"Could not open source video: {self.src_path}")
                return

            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Using 'mp4v' for MP4 containers, which is widely supported
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
            
            if not writer.isOpened():
                # Fallback to AVI with XVID if MP4 fails
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out_path = out_path.rsplit('.', 1)[0] + '.avi'
                writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
                
                if not writer.isOpened():
                    cap.release()
                    self.failed_signal.emit("Could not create video writer (unsupported codecs)")
                    return

            # Seek to start frame
            start_frame = int(self.start_time * fps)
            total_frames_to_write = int(self.duration * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frames_written = 0
            while frames_written < total_frames_to_write:
                ret, frame = cap.read()
                if not ret:
                    break
                writer.write(frame)
                frames_written += 1

            cap.release()
            writer.release()

            if frames_written > 0:
                self.finished_signal.emit(out_path)
            else:
                self.failed_signal.emit("No frames were extracted. Check video time range.")
        except Exception as e:
            self.failed_signal.emit(str(e))
