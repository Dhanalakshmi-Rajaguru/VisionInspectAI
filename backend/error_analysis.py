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

OUTPUT_CSV = PROJECT_ROOT / "error_analysis.csv"


# ============================================================
# 2. SETTINGS
# ============================================================

CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.50


# ============================================================
# 3. LOAD MODEL
# ============================================================

print("=" * 60)
print("YOLO ERROR ANALYSIS")
print("=" * 60)

print(f"\nLoading model:")
print(MODEL_PATH)

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

print(f"\nTest images found: {len(image_paths)}")


# ============================================================
# 5. READ GROUND-TRUTH LABELS
# ============================================================

def read_ground_truth(label_path, image_width, image_height):
    """
    Read YOLO-format labels and convert normalized coordinates
    into pixel coordinates.

    YOLO format:

        class_id x_center y_center width height

    All coordinates are normalized between 0 and 1.

    Example:

        0 0.50 0.40 0.20 0.30
    """

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

            # ------------------------------------------------
            # Convert normalized coordinates -> pixels
            # ------------------------------------------------

            x_center *= image_width
            y_center *= image_height

            width *= image_width
            height *= image_height

            # ------------------------------------------------
            # Convert center format -> xyxy
            # ------------------------------------------------

            x1 = x_center - width / 2
            y1 = y_center - height / 2

            x2 = x_center + width / 2
            y2 = y_center + height / 2

            # ------------------------------------------------
            # Keep coordinates inside image
            # ------------------------------------------------

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
# 6. CALCULATE IoU
# ============================================================

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union.

    box format:

        [x1, y1, x2, y2]
    """

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

    # --------------------------------------------------------
    # Areas
    # --------------------------------------------------------

    box1_width = max(0, box1[2] - box1[0])
    box1_height = max(0, box1[3] - box1[1])

    box2_width = max(0, box2[2] - box2[0])
    box2_height = max(0, box2[3] - box2[1])

    area1 = box1_width * box1_height
    area2 = box2_width * box2_height

    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


# ============================================================
# 7. ANALYZE ONE IMAGE
# ============================================================

def analyze_image(image_path):
    """
    Analyze one test image.

    Returns:

        TP
        FP
        FN
        best IoU
        prediction confidence
    """

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    image_height, image_width = image.shape[:2]

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    label_path = TEST_LABELS / f"{image_path.stem}.txt"

    ground_truth = read_ground_truth(
        label_path,
        image_width,
        image_height,
    )

    # --------------------------------------------------------
    # YOLO prediction
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

            class_id = int(
                box.cls[0].cpu().item()
            )

            predictions.append(
                {
                    "class_id": class_id,
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
    # MATCH PREDICTIONS TO GROUND TRUTH
    # ========================================================

    matched_gt = set()

    true_positives = 0
    false_positives = 0
    false_negatives = 0

    best_iou_overall = 0.0
    best_confidence = 0.0

    # --------------------------------------------------------
    # Match each prediction to the best unused GT box
    # --------------------------------------------------------

    for prediction in predictions:

        best_iou = 0.0
        best_gt_index = None

        for gt_index, gt in enumerate(ground_truth):

            # ------------------------------------------------
            # Already matched GT cannot be reused
            # ------------------------------------------------

            if gt_index in matched_gt:
                continue

            # ------------------------------------------------
            # Since the current YOLO model has ONE class
            # ("defect"), class_id comparison is not useful
            # for subtype analysis.
            #
            # We therefore match based on IoU.
            # ------------------------------------------------

            iou = calculate_iou(
                prediction["box"],
                gt["box"],
            )

            if iou > best_iou:

                best_iou = iou
                best_gt_index = gt_index

        # ----------------------------------------------------
        # Track best IoU seen
        # ----------------------------------------------------

        if best_iou > best_iou_overall:
            best_iou_overall = best_iou

        if prediction["confidence"] > best_confidence:
            best_confidence = prediction["confidence"]

        # ----------------------------------------------------
        # TP
        # ----------------------------------------------------

        if (
            best_gt_index is not None
            and best_iou >= IOU_THRESHOLD
        ):

            true_positives += 1

            matched_gt.add(best_gt_index)

        # ----------------------------------------------------
        # FP
        # ----------------------------------------------------

        else:

            false_positives += 1

    # --------------------------------------------------------
    # FN
    #
    # Any GT that was not matched is a false negative.
    # --------------------------------------------------------

    false_negatives = len(ground_truth) - len(matched_gt)

    # ========================================================
    # IMAGE-LEVEL CLASSIFICATION
    # ========================================================

    if len(ground_truth) == 0:

        if len(predictions) == 0:

            image_result = "CORRECT_BACKGROUND"

        else:

            image_result = "FALSE_POSITIVE"

    else:

        if true_positives > 0:

            image_result = "DETECTED"

        else:

            image_result = "FALSE_NEGATIVE"

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {
        "image": image_path.name,
        "ground_truth_count": len(ground_truth),
        "prediction_count": len(predictions),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "best_iou": round(best_iou_overall, 4),
        "best_confidence": round(best_confidence, 4),
        "result": image_result,
    }


# ============================================================
# 8. MAIN ERROR ANALYSIS
# ============================================================

def main():

    print("\nConfiguration")
    print("-" * 60)

    print(f"Confidence threshold : {CONF_THRESHOLD}")
    print(f"IoU threshold        : {IOU_THRESHOLD}")

    print("\nPaths")
    print("-" * 60)

    print(f"Model       : {MODEL_PATH}")
    print(f"Test images : {TEST_IMAGES}")
    print(f"Test labels : {TEST_LABELS}")

    # --------------------------------------------------------
    # Global counters
    # --------------------------------------------------------

    total_images = 0

    total_ground_truth = 0
    total_predictions = 0

    total_tp = 0
    total_fp = 0
    total_fn = 0

    detected_images = 0
    false_negative_images = 0
    false_positive_images = 0
    correct_background_images = 0

    all_results = []

    # ========================================================
    # PROCESS EACH IMAGE
    # ========================================================

    print("\nStarting error analysis...")
    print("=" * 60)

    for index, image_path in enumerate(image_paths, start=1):

        try:

            result = analyze_image(image_path)

            all_results.append(result)

            # ------------------------------------------------
            # Global counters
            # ------------------------------------------------

            total_images += 1

            total_ground_truth += result[
                "ground_truth_count"
            ]

            total_predictions += result[
                "prediction_count"
            ]

            total_tp += result[
                "true_positives"
            ]

            total_fp += result[
                "false_positives"
            ]

            total_fn += result[
                "false_negatives"
            ]

            # ------------------------------------------------
            # Image-level result counters
            # ------------------------------------------------

            if result["result"] == "DETECTED":

                detected_images += 1

            elif result["result"] == "FALSE_NEGATIVE":

                false_negative_images += 1

            elif result["result"] == "FALSE_POSITIVE":

                false_positive_images += 1

            elif result["result"] == "CORRECT_BACKGROUND":

                correct_background_images += 1

            # ------------------------------------------------
            # Print progress
            # ------------------------------------------------

            print(
                f"[{index}/{len(image_paths)}] "
                f"{image_path.name} | "
                f"GT={result['ground_truth_count']} | "
                f"Pred={result['prediction_count']} | "
                f"TP={result['true_positives']} | "
                f"FP={result['false_positives']} | "
                f"FN={result['false_negatives']} | "
                f"IoU={result['best_iou']:.3f} | "
                f"{result['result']}"
            )

        except Exception as error:

            print(
                f"[ERROR] {image_path.name}: {error}"
            )

    # ========================================================
    # METRICS
    # ========================================================

    if total_tp + total_fp > 0:

        precision = (
            total_tp /
            (total_tp + total_fp)
        )

    else:

        precision = 0.0

    if total_tp + total_fn > 0:

        recall = (
            total_tp /
            (total_tp + total_fn)
        )

    else:

        recall = 0.0

    if precision + recall > 0:

        f1_score = (
            2 * precision * recall /
            (precision + recall)
        )

    else:

        f1_score = 0.0

    # ========================================================
    # SAVE CSV
    # ========================================================

    try:

        import csv

        fieldnames = [
            "image",
            "ground_truth_count",
            "prediction_count",
            "true_positives",
            "false_positives",
            "false_negatives",
            "best_iou",
            "best_confidence",
            "result",
        ]

        with open(
            OUTPUT_CSV,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(all_results)

        print(
            f"\nCSV saved to:\n{OUTPUT_CSV}"
        )

    except Exception as error:

        print(
            f"\nCould not save CSV: {error}"
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 60)
    print("ERROR ANALYSIS SUMMARY")
    print("=" * 60)

    print(
        f"Total images           : {total_images}"
    )

    print(
        f"Total ground-truth     : {total_ground_truth}"
    )

    print(
        f"Total predictions      : {total_predictions}"
    )

    print(
        f"True positives         : {total_tp}"
    )

    print(
        f"False positives        : {total_fp}"
    )

    print(
        f"False negatives        : {total_fn}"
    )

    print("-" * 60)

    print(
        f"Precision              : {precision:.4f}"
    )

    print(
        f"Recall                 : {recall:.4f}"
    )

    print(
        f"F1 Score               : {f1_score:.4f}"
    )

    print("-" * 60)

    print(
        f"Detected images        : {detected_images}"
    )

    print(
        f"False-negative images  : {false_negative_images}"
    )

    print(
        f"False-positive images  : {false_positive_images}"
    )

    print(
        f"Correct backgrounds    : {correct_background_images}"
    )

    print("=" * 60)

    print("\nAnalysis completed.")


# ============================================================
# 9. RUN
# ============================================================

if __name__ == "__main__":
    main()