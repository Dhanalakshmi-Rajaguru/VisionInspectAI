from pathlib import Path
import csv
import cv2
from ultralytics import YOLO


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    r"C:\Users\User\Desktop\VisionInspectAI"
)


# ============================================================
# 2. MODEL AND DATASET PATHS
# ============================================================

MODEL_PATH = PROJECT_ROOT / "models" / "yolo_model.pt"

DATASET_ROOT = PROJECT_ROOT / "yolo_dataset_final"

TEST_IMAGES = DATASET_ROOT / "images" / "test"
TEST_LABELS = DATASET_ROOT / "labels" / "test"


# ============================================================
# 3. FROZEN TEST SET EXPECTATIONS
# ============================================================

EXPECTED_IMAGES = 817
EXPECTED_GT_BOXES = 290
EXPECTED_BACKGROUND_IMAGES = 616


# ============================================================
# 4. THRESHOLD SETTINGS
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

IMAGE_SIZE = 640


# ============================================================
# 5. SUPPORTED IMAGE EXTENSIONS
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


# ============================================================
# 6. CHECK PATHS
# ============================================================

print("=" * 75)
print("FROZEN TEST SET THRESHOLD EVALUATION")
print("=" * 75)

print()
print("Project root:")
print(PROJECT_ROOT)

print()
print("Model:")
print(MODEL_PATH)

print()
print("Test images:")
print(TEST_IMAGES)

print()
print("Test labels:")
print(TEST_LABELS)

print()


if not PROJECT_ROOT.exists():
    raise FileNotFoundError(
        f"Project root does not exist:\n{PROJECT_ROOT}"
    )


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"YOLO model not found:\n{MODEL_PATH}"
    )


if not TEST_IMAGES.exists():
    raise FileNotFoundError(
        f"Test images folder not found:\n{TEST_IMAGES}"
    )


if not TEST_LABELS.exists():
    raise FileNotFoundError(
        f"Test labels folder not found:\n{TEST_LABELS}"
    )


# ============================================================
# 7. FIND TEST IMAGES
# ============================================================

image_paths = sorted(
    [
        path
        for path in TEST_IMAGES.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
)


print("=" * 75)
print("DATASET CHECK")
print("=" * 75)

print()
print(f"Test images found: {len(image_paths)}")
print(f"Expected images  : {EXPECTED_IMAGES}")


if len(image_paths) != EXPECTED_IMAGES:

    raise RuntimeError(
        "\n\nFROZEN TEST SET CHECK FAILED\n"
        f"Expected {EXPECTED_IMAGES} test images, "
        f"but found {len(image_paths)}.\n\n"
        "Do NOT continue until the correct frozen test set "
        "is available locally."
    )


# ============================================================
# 8. IOU FUNCTION
# ============================================================

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union.

    Box format:

        [x1, y1, x2, y2]
    """

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(
        0.0,
        x2 - x1
    )

    intersection_height = max(
        0.0,
        y2 - y1
    )

    intersection_area = (
        intersection_width
        * intersection_height
    )

    area1 = (
        max(0.0, box1[2] - box1[0])
        *
        max(0.0, box1[3] - box1[1])
    )

    area2 = (
        max(0.0, box2[2] - box2[0])
        *
        max(0.0, box2[3] - box2[1])
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
# 9. READ GROUND-TRUTH LABELS
# ============================================================

def read_ground_truth(
    label_path,
    image_width,
    image_height
):
    """
    Read YOLO-format labels.

    YOLO label format:

        class_id x_center y_center width height

    Coordinates are normalized between 0 and 1.

    They are converted to pixel coordinates here.
    """

    boxes = []

    if not label_path.exists():
        return boxes

    with open(
        label_path,
        "r",
        encoding="utf-8"
    ) as file:

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
            # Convert normalized coordinates to pixels
            # ------------------------------------------------

            x_center *= image_width
            y_center *= image_height

            width *= image_width
            height *= image_height

            # ------------------------------------------------
            # Convert center format to xyxy format
            # ------------------------------------------------

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
# 10. COUNT GROUND-TRUTH BOXES
# ============================================================

print()
print("Checking frozen test-set labels...")

total_ground_truth_boxes = 0
total_background_images = 0

for image_path in image_paths:

    label_path = (
        TEST_LABELS
        / f"{image_path.stem}.txt"
    )

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise RuntimeError(
            f"Could not read image:\n{image_path}"
        )

    image_height, image_width = image.shape[:2]

    ground_truth = read_ground_truth(
        label_path,
        image_width,
        image_height
    )

    total_ground_truth_boxes += len(
        ground_truth
    )

    if len(ground_truth) == 0:
        total_background_images += 1


print()
print(
    f"Ground-truth boxes found : "
    f"{total_ground_truth_boxes}"
)

print(
    f"Expected ground-truth   : "
    f"{EXPECTED_GT_BOXES}"
)

print(
    f"Background images found : "
    f"{total_background_images}"
)

print(
    f"Expected backgrounds    : "
    f"{EXPECTED_BACKGROUND_IMAGES}"
)


# ============================================================
# 11. VERIFY FROZEN DATASET
# ============================================================

if (
    total_ground_truth_boxes
    != EXPECTED_GT_BOXES
):

    raise RuntimeError(
        "\n\nFROZEN TEST SET CHECK FAILED\n"
        f"Expected {EXPECTED_GT_BOXES} ground-truth boxes, "
        f"but found {total_ground_truth_boxes}.\n\n"
        "Do NOT continue."
    )


if (
    total_background_images
    != EXPECTED_BACKGROUND_IMAGES
):

    raise RuntimeError(
        "\n\nFROZEN TEST SET CHECK FAILED\n"
        f"Expected {EXPECTED_BACKGROUND_IMAGES} background images, "
        f"but found {total_background_images}.\n\n"
        "Do NOT continue."
    )


print()
print("Frozen test-set verification PASSED.")
print()


# ============================================================
# 12. LOAD YOLO MODEL
# ============================================================

print("=" * 75)
print("LOADING YOLO MODEL")
print("=" * 75)

model = YOLO(
    str(MODEL_PATH)
)

print()
print("Model loaded successfully.")
print(f"Model: {MODEL_PATH}")
print()


# ============================================================
# 13. COLLECT PREDICTIONS ONCE
# ============================================================

print("=" * 75)
print("RUNNING MODEL ON FROZEN TEST SET")
print("=" * 75)

print()
print(
    "YOLO confidence is temporarily set to 0.001 "
    "so that all candidate predictions are collected."
)

print(
    "The actual thresholds will be applied afterward."
)

print()


all_predictions = []


for index, image_path in enumerate(
    image_paths,
    start=1
):

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise RuntimeError(
            f"Could not read:\n{image_path}"
        )

    image_height, image_width = image.shape[:2]

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    label_path = (
        TEST_LABELS
        / f"{image_path.stem}.txt"
    )

    ground_truth = read_ground_truth(
        label_path,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # YOLO prediction
    # --------------------------------------------------------

    results = model.predict(
        source=image,
        imgsz=IMAGE_SIZE,
        conf=0.001,
        iou=0.50,
        verbose=False
    )

    result = results[0]

    predictions = []

    if result.boxes is not None:

        boxes = (
            result.boxes
            .xyxy
            .cpu()
            .numpy()
        )

        confidences = (
            result.boxes
            .conf
            .cpu()
            .numpy()
        )

        class_ids = (
            result.boxes
            .cls
            .cpu()
            .numpy()
        )

        for (
            box,
            confidence,
            class_id
        ) in zip(
            boxes,
            confidences,
            class_ids
        ):

            predictions.append(
                {
                    "box": box.tolist(),
                    "confidence": float(
                        confidence
                    ),
                    "class_id": int(
                        class_id
                    ),
                }
            )

    all_predictions.append(
        {
            "image_name": image_path.name,
            "ground_truth": ground_truth,
            "predictions": predictions,
        }
    )

    if (
        index % 25 == 0
        or index == len(image_paths)
    ):

        print(
            f"Processed "
            f"{index}/{len(image_paths)} images"
        )


print()
print("Prediction collection completed.")
print()


# ============================================================
# 14. EVALUATE ONE THRESHOLD
# ============================================================

def evaluate_threshold(
    dataset,
    confidence_threshold,
    iou_threshold
):
    """
    Calculate TP, FP, FN, precision, recall and F1
    for one confidence threshold.
    """

    TP = 0
    FP = 0
    FN = 0

    for sample in dataset:

        ground_truth = sample[
            "ground_truth"
        ]

        predictions = [
            prediction
            for prediction in sample[
                "predictions"
            ]
            if prediction[
                "confidence"
            ] >= confidence_threshold
        ]

        # ----------------------------------------------------
        # Background image
        # ----------------------------------------------------

        if len(ground_truth) == 0:

            FP += len(predictions)

            continue

        # ----------------------------------------------------
        # Sort predictions by confidence
        # ----------------------------------------------------

        predictions = sorted(
            predictions,
            key=lambda prediction:
                prediction["confidence"],
            reverse=True
        )

        matched_ground_truth = set()

        # ----------------------------------------------------
        # Match predictions to GT
        # ----------------------------------------------------

        for prediction in predictions:

            best_iou = 0.0
            best_gt_index = None

            for (
                gt_index,
                gt
            ) in enumerate(
                ground_truth
            ):

                if (
                    gt_index
                    in matched_ground_truth
                ):
                    continue

                iou = calculate_iou(
                    prediction["box"],
                    gt["box"]
                )

                if iou > best_iou:

                    best_iou = iou
                    best_gt_index = (
                        gt_index
                    )

            # ------------------------------------------------
            # True positive
            # ------------------------------------------------

            if (
                best_gt_index is not None
                and best_iou >= iou_threshold
            ):

                TP += 1

                matched_ground_truth.add(
                    best_gt_index
                )

            # ------------------------------------------------
            # False positive
            # ------------------------------------------------

            else:

                FP += 1

        # ----------------------------------------------------
        # Unmatched GT = false negatives
        # ----------------------------------------------------

        FN += (
            len(ground_truth)
            - len(matched_ground_truth)
        )

    # ========================================================
    # METRICS
    # ========================================================

    if TP + FP > 0:

        precision = (
            TP
            / (TP + FP)
        )

    else:

        precision = 0.0


    if TP + FN > 0:

        recall = (
            TP
            / (TP + FN)
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
        "threshold": confidence_threshold,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ============================================================
# 15. RUN THRESHOLD SWEEP
# ============================================================

print("=" * 75)
print("CONFIDENCE THRESHOLD SWEEP")
print("=" * 75)

print()

results = []


for threshold in CONF_THRESHOLDS:

    result = evaluate_threshold(
        dataset=all_predictions,
        confidence_threshold=threshold,
        iou_threshold=IOU_THRESHOLD
    )

    results.append(result)

    print(
        f"Threshold {threshold:.2f} | "
        f"Precision {result['precision'] * 100:.2f}% | "
        f"Recall {result['recall'] * 100:.2f}% | "
        f"F1 {result['f1'] * 100:.2f}% | "
        f"TP {result['TP']} | "
        f"FP {result['FP']} | "
        f"FN {result['FN']}"
    )


# ============================================================
# 16. FIND BEST F1 THRESHOLD
# ============================================================

best_result = max(
    results,
    key=lambda result: result["f1"]
)


# ============================================================
# 17. FIND CURRENT 0.25 RESULT
# ============================================================

current_result = next(
    result
    for result in results
    if abs(
        result["threshold"] - 0.25
    ) < 1e-9
)


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print()
print("=" * 75)
print("FINAL FROZEN TEST SET RESULTS")
print("=" * 75)

print()

print(
    f"Test images            : "
    f"{len(image_paths)}"
)

print(
    f"Ground-truth boxes     : "
    f"{total_ground_truth_boxes}"
)

print(
    f"Background images      : "
    f"{total_background_images}"
)

print(
    f"IoU threshold          : "
    f"{IOU_THRESHOLD:.2f}"
)

print(
    f"Image size             : "
    f"{IMAGE_SIZE}"
)

print()

print(
    f"Best threshold         : "
    f"{best_result['threshold']:.2f}"
)

print(
    f"Best precision         : "
    f"{best_result['precision'] * 100:.2f}%"
)

print(
    f"Best recall            : "
    f"{best_result['recall'] * 100:.2f}%"
)

print(
    f"Best F1                : "
    f"{best_result['f1'] * 100:.2f}%"
)

print(
    f"Best TP                : "
    f"{best_result['TP']}"
)

print(
    f"Best FP                : "
    f"{best_result['FP']}"
)

print(
    f"Best FN                : "
    f"{best_result['FN']}"
)


# ============================================================
# 19. CURRENT 0.25 VS BEST
# ============================================================

print()
print("=" * 75)
print("CURRENT 0.25 VS BEST THRESHOLD")
print("=" * 75)

print()

print("Current production threshold: 0.25")

print(
    f"Precision : "
    f"{current_result['precision'] * 100:.2f}%"
)

print(
    f"Recall    : "
    f"{current_result['recall'] * 100:.2f}%"
)

print(
    f"F1        : "
    f"{current_result['f1'] * 100:.2f}%"
)

print(
    f"TP        : "
    f"{current_result['TP']}"
)

print(
    f"FP        : "
    f"{current_result['FP']}"
)

print(
    f"FN        : "
    f"{current_result['FN']}"
)

print()

print(
    f"Best threshold: "
    f"{best_result['threshold']:.2f}"
)

print(
    f"Precision : "
    f"{best_result['precision'] * 100:.2f}%"
)

print(
    f"Recall    : "
    f"{best_result['recall'] * 100:.2f}%"
)

print(
    f"F1        : "
    f"{best_result['f1'] * 100:.2f}%"
)

print(
    f"TP        : "
    f"{best_result['TP']}"
)

print(
    f"FP        : "
    f"{best_result['FP']}"
)

print(
    f"FN        : "
    f"{best_result['FN']}"
)


# ============================================================
# 20. SAVE CSV
# ============================================================

OUTPUT_FILE = (
    PROJECT_ROOT
    / "frozen_threshold_results.csv"
)


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "threshold",
            "precision",
            "recall",
            "f1",
            "TP",
            "FP",
            "FN",
        ]
    )

    for result in results:

        writer.writerow(
            [
                result["threshold"],
                result["precision"],
                result["recall"],
                result["f1"],
                result["TP"],
                result["FP"],
                result["FN"],
            ]
        )


# ============================================================
# 21. COMPLETE
# ============================================================

print()
print("=" * 75)
print("THRESHOLD SWEEP COMPLETE")
print("=" * 75)

print()
print(
    f"Results saved to:"
)

print(
    OUTPUT_FILE
)

print()
print(
    "Do NOT change the production threshold yet."
)

print(
    "Use the frozen-test results to decide the final threshold."
)

print()

