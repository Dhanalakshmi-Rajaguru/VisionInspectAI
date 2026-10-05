from pathlib import Path

import cv2
from ultralytics import YOLO


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = PROJECT_ROOT / "models" / "yolo_model.pt"

TEST_IMAGES = PROJECT_ROOT / "yolo_dataset" / "images" / "test"
TEST_LABELS = PROJECT_ROOT / "yolo_dataset" / "labels" / "test"


# ============================================================
# 2. SETTINGS
# ============================================================

CONF_THRESHOLDS = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
]

IOU_THRESHOLD = 0.50


# ============================================================
# 3. LOAD MODEL
# ============================================================

print("=" * 70)
print("YOLO CONFIDENCE THRESHOLD SWEEP")
print("=" * 70)

print(f"\nModel: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

print("Model loaded successfully.")


# ============================================================
# 4. GET TEST IMAGES
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}

image_paths = sorted(
    [
        path
        for path in TEST_IMAGES.iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    ]
)

print(f"Test images: {len(image_paths)}")


# ============================================================
# 5. READ GROUND TRUTH
# ============================================================

def read_ground_truth(
    label_path,
    image_width,
    image_height,
):
    boxes = []

    if not label_path.exists():
        return boxes

    with open(label_path, "r") as file:

        for line in file:

            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            # Convert normalized YOLO coordinates
            # to pixel coordinates.

            x_center *= image_width
            y_center *= image_height

            width *= image_width
            height *= image_height

            x1 = x_center - width / 2
            y1 = y_center - height / 2

            x2 = x_center + width / 2
            y2 = y_center + height / 2

            boxes.append(
                {
                    "class_id": class_id,
                    "box": [
                        x1,
                        y1,
                        x2,
                        y2,
                    ],
                }
            )

    return boxes


# ============================================================
# 6. IoU
# ============================================================

def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(
        0,
        x2 - x1,
    )

    intersection_height = max(
        0,
        y2 - y1,
    )

    intersection_area = (
        intersection_width
        * intersection_height
    )

    if intersection_area <= 0:
        return 0.0

    area1 = (
        max(0, box1[2] - box1[0])
        * max(0, box1[3] - box1[1])
    )

    area2 = (
        max(0, box2[2] - box2[0])
        * max(0, box2[3] - box2[1])
    )

    union_area = (
        area1
        + area2
        - intersection_area
    )

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


# ============================================================
# 7. RUN ONE THRESHOLD
# ============================================================

def evaluate_threshold(conf_threshold):

    total_tp = 0
    total_fp = 0
    total_fn = 0

    total_ground_truth = 0
    total_predictions = 0

    for image_path in image_paths:

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        image = cv2.imread(str(image_path))

        if image is None:
            continue

        image_height, image_width = image.shape[:2]

        # ----------------------------------------------------
        # Ground truth
        # ----------------------------------------------------

        label_path = (
            TEST_LABELS
            / f"{image_path.stem}.txt"
        )

        ground_truth = read_ground_truth(
            label_path,
            image_width,
            image_height,
        )

        # ----------------------------------------------------
        # Predictions
        # ----------------------------------------------------

        results = model.predict(
            source=str(image_path),
            conf=conf_threshold,
            verbose=False,
        )

        result = results[0]

        predictions = []

        if result.boxes is not None:

            for box in result.boxes:

                xyxy = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                )

                predictions.append(
                    [
                        float(xyxy[0]),
                        float(xyxy[1]),
                        float(xyxy[2]),
                        float(xyxy[3]),
                    ]
                )

        total_ground_truth += len(
            ground_truth
        )

        total_predictions += len(
            predictions
        )

        # ----------------------------------------------------
        # Match predictions to GT
        # ----------------------------------------------------

        matched_gt = set()

        for prediction in predictions:

            best_iou = 0.0
            best_gt_index = None

            for gt_index, gt in enumerate(
                ground_truth
            ):

                if gt_index in matched_gt:
                    continue

                iou = calculate_iou(
                    prediction,
                    gt["box"],
                )

                if iou > best_iou:

                    best_iou = iou
                    best_gt_index = gt_index

            # ------------------------------------------------
            # True positive
            # ------------------------------------------------

            if (
                best_gt_index is not None
                and best_iou >= IOU_THRESHOLD
            ):

                total_tp += 1

                matched_gt.add(
                    best_gt_index
                )

            # ------------------------------------------------
            # False positive
            # ------------------------------------------------

            else:

                total_fp += 1

        # ----------------------------------------------------
        # False negatives
        # ----------------------------------------------------

        total_fn += (
            len(ground_truth)
            - len(matched_gt)
        )

    # ========================================================
    # METRICS
    # ========================================================

    if total_tp + total_fp > 0:

        precision = (
            total_tp
            / (total_tp + total_fp)
        )

    else:

        precision = 0.0

    if total_tp + total_fn > 0:

        recall = (
            total_tp
            / (total_tp + total_fn)
        )

    else:

        recall = 0.0

    if precision + recall > 0:

        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )

    else:

        f1 = 0.0

    return {
        "threshold": conf_threshold,
        "ground_truth": total_ground_truth,
        "predictions": total_predictions,
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ============================================================
# 8. RUN SWEEP
# ============================================================

results = []

print("\n")
print("=" * 70)
print("RUNNING THRESHOLD EXPERIMENTS")
print("=" * 70)

for threshold in CONF_THRESHOLDS:

    print(
        f"\nTesting confidence threshold: "
        f"{threshold:.2f}"
    )

    result = evaluate_threshold(
        threshold
    )

    results.append(result)

    print(
        f"Precision : "
        f"{result['precision'] * 100:.2f}%"
    )

    print(
        f"Recall    : "
        f"{result['recall'] * 100:.2f}%"
    )

    print(
        f"F1        : "
        f"{result['f1'] * 100:.2f}%"
    )

    print(
        f"TP={result['tp']} | "
        f"FP={result['fp']} | "
        f"FN={result['fn']}"
    )


# ============================================================
# 9. PRINT FINAL TABLE
# ============================================================

print("\n")
print("=" * 90)
print("CONFIDENCE THRESHOLD RESULTS")
print("=" * 90)

print(
    f"{'Threshold':<12}"
    f"{'Precision':<14}"
    f"{'Recall':<14}"
    f"{'F1':<14}"
    f"{'TP':<8}"
    f"{'FP':<8}"
    f"{'FN':<8}"
)

print("-" * 90)

for result in results:

    print(
        f"{result['threshold']:<12.2f}"
        f"{result['precision'] * 100:<14.2f}"
        f"{result['recall'] * 100:<14.2f}"
        f"{result['f1'] * 100:<14.2f}"
        f"{result['tp']:<8}"
        f"{result['fp']:<8}"
        f"{result['fn']:<8}"
    )


# ============================================================
# 10. FIND BEST F1
# ============================================================

best_result = max(
    results,
    key=lambda x: x["f1"],
)

print("\n")
print("=" * 70)
print("BEST F1 RESULT")
print("=" * 70)

print(
    f"Confidence threshold : "
    f"{best_result['threshold']:.2f}"
)

print(
    f"Precision             : "
    f"{best_result['precision'] * 100:.2f}%"
)

print(
    f"Recall                : "
    f"{best_result['recall'] * 100:.2f}%"
)

print(
    f"F1                    : "
    f"{best_result['f1'] * 100:.2f}%"
)

print(
    f"TP                    : "
    f"{best_result['tp']}"
)

print(
    f"FP                    : "
    f"{best_result['fp']}"
)

print(
    f"FN                    : "
    f"{best_result['fn']}"
)

print("=" * 70)