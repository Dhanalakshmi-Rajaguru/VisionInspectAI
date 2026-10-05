from pathlib import Path
import csv
import cv2

from ultralytics import YOLO


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = PROJECT_ROOT / "models" / "yolo_model.pt"

TEST_IMAGES = PROJECT_ROOT / "yolo_dataset" / "images" / "test"
TEST_LABELS = PROJECT_ROOT / "yolo_dataset" / "labels" / "test"

ERROR_CSV = PROJECT_ROOT / "error_analysis.csv"

OUTPUT_DIR = PROJECT_ROOT / "failure_cases"


# ============================================================
# 2. SETTINGS
# ============================================================

CONF_THRESHOLD = 0.25


# ============================================================
# 3. CREATE OUTPUT FOLDERS
# ============================================================

FALSE_NEGATIVE_DIR = OUTPUT_DIR / "false_negatives"
FALSE_POSITIVE_DIR = OUTPUT_DIR / "false_positives"
LOCALIZATION_DIR = OUTPUT_DIR / "localization_errors"

FALSE_NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
FALSE_POSITIVE_DIR.mkdir(parents=True, exist_ok=True)
LOCALIZATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 4. LOAD MODEL
# ============================================================

print("=" * 60)
print("VISUAL FAILURE-CASE ANALYSIS")
print("=" * 60)

print("\nLoading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("Model loaded successfully.")


# ============================================================
# 5. READ YOLO GROUND-TRUTH BOXES
# ============================================================

def read_ground_truth(label_path, image_width, image_height):

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

            # Convert normalized coordinates to pixels

            x_center *= image_width
            y_center *= image_height

            width *= image_width
            height *= image_height

            x1 = x_center - width / 2
            y1 = y_center - height / 2

            x2 = x_center + width / 2
            y2 = y_center + height / 2

            x1 = max(0, min(x1, image_width))
            y1 = max(0, min(y1, image_height))

            x2 = max(0, min(x2, image_width))
            y2 = max(0, min(y2, image_height))

            boxes.append(
                {
                    "class_id": class_id,
                    "box": [x1, y1, x2, y2],
                }
            )

    return boxes


# ============================================================
# 6. IoU FUNCTION
# ============================================================

def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(0, x2 - x1)
    intersection_height = max(0, y2 - y1)

    intersection_area = (
        intersection_width * intersection_height
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

    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


# ============================================================
# 7. DRAW GROUND-TRUTH BOX
# ============================================================

def draw_ground_truth(image, box, label="GT"):

    x1, y1, x2, y2 = map(int, box)

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (255, 0, 0),
        2,
    )

    cv2.putText(
        image,
        label,
        (x1, max(20, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2,
    )


# ============================================================
# 8. DRAW PREDICTION BOX
# ============================================================

def draw_prediction(image, box, confidence):

    x1, y1, x2, y2 = map(int, box)

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 0, 255),
        2,
    )

    label = f"YOLO {confidence * 100:.1f}%"

    cv2.putText(
        image,
        label,
        (x1, min(image.shape[0] - 10, y2 + 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
    )


# ============================================================
# 9. LOAD FAILURE CASES FROM CSV
# ============================================================

print("\nReading error_analysis.csv...")

failure_cases = []

with open(
    ERROR_CSV,
    "r",
    encoding="utf-8",
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        result = row["result"]

        best_iou = float(row["best_iou"])

        # ----------------------------------------------------
        # Keep:
        #
        # FALSE_NEGATIVE
        # FALSE_POSITIVE
        # DETECTED with IoU < 0.50
        # ----------------------------------------------------

        if result == "FALSE_NEGATIVE":

            failure_cases.append(row)

        elif result == "FALSE_POSITIVE":

            failure_cases.append(row)

        elif (
            result == "DETECTED"
            and best_iou < 0.50
        ):

            failure_cases.append(row)


print(
    f"Failure cases selected: {len(failure_cases)}"
)


# ============================================================
# 10. PROCESS FAILURE CASES
# ============================================================

processed = 0

for row in failure_cases:

    image_name = row["image"]

    image_path = TEST_IMAGES / image_name

    if not image_path.exists():

        print(
            f"[WARNING] Image not found: {image_name}"
        )

        continue

    image = cv2.imread(str(image_path))

    if image is None:

        print(
            f"[WARNING] Could not read: {image_name}"
        )

        continue

    image_height, image_width = image.shape[:2]

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    label_path = TEST_LABELS / f"{Path(image_name).stem}.txt"

    ground_truth = read_ground_truth(
        label_path,
        image_width,
        image_height,
    )

    # --------------------------------------------------------
    # YOLO predictions
    # --------------------------------------------------------

    results = model.predict(
        source=str(image_path),
        conf=CONF_THRESHOLD,
        verbose=False,
    )

    result = results[0]

    predictions = []

    if result.boxes is not None:

        for box in result.boxes:

            xyxy = box.xyxy[0].cpu().numpy()

            confidence = float(
                box.conf[0].cpu().item()
            )

            predictions.append(
                {
                    "box": [
                        float(xyxy[0]),
                        float(xyxy[1]),
                        float(xyxy[2]),
                        float(xyxy[3]),
                    ],
                    "confidence": confidence,
                }
            )

    # ========================================================
    # DRAW GROUND TRUTH
    # ========================================================

    for gt in ground_truth:

        draw_ground_truth(
            image,
            gt["box"],
            "GROUND TRUTH",
        )

    # ========================================================
    # DRAW PREDICTIONS
    # ========================================================

    for prediction in predictions:

        draw_prediction(
            image,
            prediction["box"],
            prediction["confidence"],
        )

    # ========================================================
    # ADD INFORMATION PANEL
    # ========================================================

    result_type = row["result"]

    best_iou = float(row["best_iou"])

    tp = row["true_positives"]
    fp = row["false_positives"]
    fn = row["false_negatives"]

    info_lines = [
        f"Result: {result_type}",
        f"GT boxes: {len(ground_truth)}",
        f"Predictions: {len(predictions)}",
        f"Best IoU: {best_iou:.3f}",
        f"TP: {tp}  FP: {fp}  FN: {fn}",
    ]

    # Create white information area

    panel_height = 125

    panel = 255 * (
        cv2.UMat(
            panel_height,
            image_width,
            cv2.CV_8UC3
        ).get()
    )

    y = 25

    for text in info_lines:

        cv2.putText(
            panel,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2,
        )

        y += 23

    # Combine panel + image

    final_image = cv2.vconcat(
        [
            panel,
            image,
        ]
    )

    # ========================================================
    # CHOOSE OUTPUT FOLDER
    # ========================================================

    if result_type == "FALSE_NEGATIVE":

        output_path = (
            FALSE_NEGATIVE_DIR / image_name
        )

    elif result_type == "FALSE_POSITIVE":

        output_path = (
            FALSE_POSITIVE_DIR / image_name
        )

    else:

        output_path = (
            LOCALIZATION_DIR / image_name
        )

    # ========================================================
    # SAVE
    # ========================================================

    cv2.imwrite(
        str(output_path),
        final_image,
    )

    processed += 1

    print(
        f"[{processed}/{len(failure_cases)}] "
        f"Saved: {output_path}"
    )


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("VISUAL FAILURE ANALYSIS COMPLETE")
print("=" * 60)

print(
    f"Images generated: {processed}"
)

print(
    f"\nFalse negatives:"
    f"\n{FALSE_NEGATIVE_DIR}"
)

print(
    f"\nFalse positives:"
    f"\n{FALSE_POSITIVE_DIR}"
)

print(
    f"\nLocalization errors:"
    f"\n{LOCALIZATION_DIR}"
)

print("\nDone.")