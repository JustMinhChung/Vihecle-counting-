import cv2
from app.core.detector import VehicleDetector
from app import config

def test():
    print("Testing detector and tracking...")
    # Create a dummy frame (black image)
    import numpy as np
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detector = VehicleDetector()
    print("Model loaded successfully.")
    
    # Run tracking on dummy frame
    detections = detector.detect_and_track(dummy_frame)
    print(f"Detections on dummy frame: {detections}")
    
if __name__ == "__main__":
    test()
