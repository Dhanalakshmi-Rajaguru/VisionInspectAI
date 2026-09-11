from pathlib import Path

from ultralytics import YOLO


class YOLOService:

    def __init__(self):

        model_path = (
    Path(__file__).resolve().parent.parent.parent
    / "models"
    / "best (2).pt")

        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(str(model_path))

    def predict(self, image_path):

        results = self.model.predict(
            source=str(image_path),
            imgsz=640,
            conf=0.25,
            verbose=False,
        )

        result = results[0]

        detections = []

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            detections.append({
                "class_id": class_id,
                "class_name": "defect",
                "confidence": round(
                    confidence,
                    4
                ),
                "bbox": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2),
                },
            })

        if detections:

            prediction = "defect"

        else:

            prediction = "pass"

        return {
            "prediction": prediction,
            "detections": detections,
            "defect_count": len(detections),
        }