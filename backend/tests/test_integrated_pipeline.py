from pathlib import Path
import cv2
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms
from ultralytics import YOLO

from backend.ml.severity import (
    get_defect_type_score,
    calculate_severity,
    assess_quality,
)


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

YOLO_MODEL_PATH = PROJECT_ROOT / "models" / "yolo_model.pt"
RESNET_MODEL_PATH = (
    PROJECT_ROOT / "models" / "defect_classifier_resnet18_final.pth"
)

DATASET_PATH = PROJECT_ROOT / "dataset1"


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device:", DEVICE)



CLASS_NAMES = [
    "bent",
    "bent_lead",
    "bent_wire",
    "broken",
    "broken_large",
    "broken_small",
    "broken_teeth",
    "cable_swap",
    "color",
    "combined",
    "contamination",
    "crack",
    "cut",
    "cut_inner_insulation",
    "cut_lead",
    "cut_outer_insulation",
    "damaged_case",
    "defective",
    "fabric_border",
    "fabric_interior",
    "faulty_imprint",
    "flip",
    "fold",
    "glue",
    "glue_strip",
    "gray_stroke",
    "hole",
    "liquid",
    "manipulated_front",
    "metal_contamination",
    "misplaced",
    "missing_cable",
    "missing_wire",
    "oil",
    "pill_type",
    "poke",
    "poke_insulation",
    "print",
    "rough",
    "scratch",
    "scratch_head",
    "scratch_neck",
    "split_teeth",
    "squeeze",
    "squeezed_teeth",
    "thread",
    "thread_side",
    "thread_top",
]



print("\nLoading YOLO model...")
print("Path:", YOLO_MODEL_PATH)

if not YOLO_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"YOLO model not found: {YOLO_MODEL_PATH}"
    )

yolo_model = YOLO(str(YOLO_MODEL_PATH))

print("YOLO model loaded successfully!")




print("\nLoading ResNet18 classifier...")
print("Path:", RESNET_MODEL_PATH)

if not RESNET_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"ResNet model not found: {RESNET_MODEL_PATH}"
    )

resnet_model = models.resnet18(weights=None)

resnet_model.fc = nn.Linear(
    resnet_model.fc.in_features,
    len(CLASS_NAMES)
)

checkpoint = torch.load(
    RESNET_MODEL_PATH,
    map_location=DEVICE
)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    state_dict = checkpoint["model_state_dict"]
else:
    state_dict = checkpoint

resnet_model.load_state_dict(state_dict)

resnet_model = resnet_model.to(DEVICE)
resnet_model.eval()

print("ResNet18 loaded successfully!")




transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])



test_images = list(DATASET_PATH.rglob("*.png"))

if not test_images:
    test_images = list(DATASET_PATH.rglob("*.jpg"))

if not test_images:
    raise FileNotFoundError(
        f"No test images found in {DATASET_PATH}"
    )

print("\nTest images found:", len(test_images))


test_image = None

for image_path in test_images:
    if (
        "bottle" in str(image_path).lower()
        and "broken_large" in str(image_path).lower()
        and image_path.name == "000.png"
    ):
        test_image = image_path
        break

if test_image is None:
    test_image = test_images[0]

print("\nTesting image:")
print(test_image)



image = cv2.imread(str(test_image))

if image is None:
    raise ValueError(f"Could not read image: {test_image}")

image_height, image_width = image.shape[:2]

print("\nImage size:")
print(f"Width : {image_width}")
print(f"Height: {image_height}")




print("\nRunning YOLO detection...")

results = yolo_model.predict(
    source=str(test_image),
    conf=0.25,
    imgsz=640,
    verbose=False
)

result = results[0]

print("\n=======================================================")
print("                 YOLO RESULT")
print("=======================================================")

if result.boxes is None or len(result.boxes) == 0:

    print("No defects detected.")
    print("Quality Status: PASS")

    raise SystemExit


print("Defects detected:", len(result.boxes))




for detection_number, box in enumerate(result.boxes, start=1):

    print("\n-------------------------------------------------------")
    print(f"DETECTION {detection_number}")
    print("-------------------------------------------------------")


    yolo_confidence = float(box.conf[0]) * 100

  
    x1, y1, x2, y2 = box.xyxy[0].tolist()

    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(image_width, int(x2))
    y2 = min(image_height, int(y2))

    print("YOLO confidence:", round(yolo_confidence, 2), "%")
    print("Bounding box:", [x1, y1, x2, y2])


    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        print("Invalid crop. Skipping detection.")
        continue

    print("Crop size:", crop.shape)

    

    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

    pil_image = Image.fromarray(crop_rgb)

    input_tensor = transform(pil_image)

    input_tensor = input_tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = resnet_model(input_tensor)

        probabilities = torch.softmax(outputs, dim=1)

        confidence, predicted_class = torch.max(
            probabilities,
            dim=1
        )

    predicted_index = int(predicted_class.item())

    classification_confidence = (
        float(confidence.item()) * 100
    )

    defect_type = CLASS_NAMES[predicted_index]

    print("\nResNet classification:")
    print("Defect type:", defect_type)
    print(
        "Classification confidence:",
        round(classification_confidence, 2),
        "%"
    )

   

    bbox_width = x2 - x1
    bbox_height = y2 - y1

    bbox_area = bbox_width * bbox_height
    image_area = image_width * image_height

    size_score = min(
        100,
        (bbox_area / image_area) * 100
    )

    defect_center_x = (x1 + x2) / 2
    defect_center_y = (y1 + y2) / 2

    image_center_x = image_width / 2
    image_center_y = image_height / 2

    distance_x = abs(
        defect_center_x - image_center_x
    ) / image_center_x

    distance_y = abs(
        defect_center_y - image_center_y
    ) / image_center_y

    location_score = min(
        100,
        ((distance_x + distance_y) / 2) * 100
    )

    try:

        defect_type_score = get_defect_type_score(
            defect_type
        )

    except ValueError:

        print(
            "Unknown defect type:",
            defect_type
        )

        print("Manual review required.")

        continue

    confidence_score = classification_confidence

  

    severity_result = calculate_severity(
        size_score,
        location_score,
        defect_type_score,
        confidence_score
    )

    severity_score = severity_result["severity_score"]
    severity_level = severity_result["severity_level"]
    recommended_action = severity_result["recommended_action"]

    

    quality_result = assess_quality(
        defect_type=defect_type,
        classification_confidence=classification_confidence,
        severity_score=severity_score,
        severity_level=severity_level,
        recommended_action=recommended_action
    )

    

    print("\nSeverity:")
    print("Size score:", round(size_score, 2))
    print("Location score:", round(location_score, 2))
    print(
        "Defect type score:",
        round(defect_type_score, 2)
    )
    print(
        "Confidence score:",
        round(confidence_score, 2)
    )

    print(
        "Severity score:",
        severity_score
    )

    print(
        "Severity level:",
        severity_level
    )

    print(
        "Recommended action:",
        recommended_action
    )

    print("\nQuality assessment:")
    print(
        "Quality status:",
        quality_result["quality_status"]
    )

    print(
        "Manual review:",
        quality_result["manual_review"]
    )




print("\n=======================================================")
print("           COMPLETE PIPELINE TEST FINISHED")
print("=======================================================")
print("YOLO → Crop → ResNet18 → Severity → Quality")
print("=======================================================")