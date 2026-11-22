# vision/detection.py - YOLO object detection + tracking (Ultralytics)

from ..config import MODEL_PATH, CONFIDENCE

model = None


def load_model():
    """Load the YOLO model only once."""
    global model
    if model is None:
        from ultralytics import YOLO       # imported here so the API starts even without it
        print("Loading YOLO model:", MODEL_PATH)
        model = YOLO(MODEL_PATH)
    return model


def detect_and_track(frame):
    yolo = load_model()
    results = yolo.track(frame, persist=True, tracker="bytetrack.yaml",
                         conf=CONFIDENCE, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        class_number = int(box.cls[0])

        # tracker id can be missing for the first frames
        track_id = int(box.id[0]) if box.id is not None else -1

        detections.append({
            "id": track_id,
            "label": result.names[class_number].lower(),
            "conf": float(box.conf[0]),
            "box": (x1, y1, x2, y2),
        })
    return detections
