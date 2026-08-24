import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")

# Ensure output directories exist
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# YOLO configuration
YOLO_MODEL_NAME = "yolov8n.pt"  # Will automatically download if not present
CONFIDENCE_THRESHOLD = 0.35

# COCO Class IDs for vehicles
# 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]
CLASS_NAMES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Counting Line (Gate) Default Configuration
# Format: ((x1, y1), (x2, y2)) as relative coordinates (0.0 to 1.0)
DEFAULT_LINE = ((0.1, 0.5), (0.9, 0.5))

# Clipper Settings
CLIP_MARGIN_SECONDS = 3.0  # Seconds before and after the crossing event to export
