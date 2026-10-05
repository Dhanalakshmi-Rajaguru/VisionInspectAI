from pathlib import Path

import cv2
import torch
import torch.nn as nn

from PIL import Image
from torchvision import models, transforms
from ultralytics import YOLO

from .severity import (
    get_defect_type_score,
    calculate_severity,
    assess_quality,
)




PROJECT_ROOT = Path(__file__).resolve().parents[2]




YOLO_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "yolo_model.pt"
)

RESNET_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "defect_classifier_resnet18_final.pth"
)


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)




class_names = [
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


print()
print("Loading YOLO26n...")

yolo_model = YOLO(
    str(YOLO_MODEL_PATH)
)

print("YOLO26n loaded successfully!")



print()
print("Loading ResNet18...")

resnet_model = models.resnet18(
    weights=None
)

resnet_model.fc = nn.Linear(
    resnet_model.fc.in_features,
    48
)




checkpoint = torch.load(
    RESNET_MODEL_PATH,
    map_location=device
)

if (
    isinstance(checkpoint, dict)
    and "model_state_dict" in checkpoint
):

    resnet_model.load_state_dict(
        checkpoint["model_state_dict"]
    )

else:

    resnet_model.load_state_dict(
        checkpoint
    )


resnet_model = resnet_model.to(device)

resnet_model.eval()

print("ResNet18 loaded successfully!")



resnet_transform = transforms.Compose([

    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])



def classify_crop(crop):

    
   

    crop_rgb = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2RGB
    )


    image = Image.fromarray(
        crop_rgb
    )

    

    image_tensor = resnet_transform(
        image
    )

    
    image_tensor = image_tensor.unsqueeze(0)

   

    image_tensor = image_tensor.to(device)


    with torch.no_grad():

        output = resnet_model(
            image_tensor
        )

        probabilities = torch.softmax(
            output,
            dim=1
        )

        confidence, predicted = torch.max(
            probabilities,
            dim=1
        )


    predicted_class = class_names[
        predicted.item()
    ]

    
    confidence_percentage = (
        confidence.item() * 100
    )

    return {
        "defect_type": predicted_class,
        "confidence": round(
            confidence_percentage,
            2
        )
    }




def calculate_size_score(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height
):

   

    bbox_width = x2 - x1

    bbox_height = y2 - y1

    bbox_area = (
        bbox_width *
        bbox_height
    )

    image_area = (
        image_width *
        image_height
    )

    if image_area == 0:
        return 0

    area_ratio = (
        bbox_area /
        image_area
    )

    size_score = area_ratio * 100

    size_score = min(
        100,
        max(0, size_score)
    )

    return round(
        size_score,
        2
    )




def calculate_location_score(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height
):

    

    

    defect_center_x = (
        x1 + x2
    ) / 2

    defect_center_y = (
        y1 + y2
    ) / 2

    

    image_center_x = (
        image_width / 2
    )

    image_center_y = (
        image_height / 2
    )

    

    normalized_x = (
        (defect_center_x - image_center_x)
        / (image_width / 2)
    )

    normalized_y = (
        (defect_center_y - image_center_y)
        / (image_height / 2)
    )

    

    distance = (
        normalized_x ** 2 +
        normalized_y ** 2
    ) ** 0.5

    
    max_distance = 2 ** 0.5

    
    location_score = (
        1 -
        (distance / max_distance)
    ) * 100

    location_score = min(
        100,
        max(
            0,
            location_score
        )
    )

    return round(
        location_score,
        2
    )




def inspect_image(
    image_path,
    yolo_confidence=0.25
):

    

    image_path = Path(
        image_path
    )

   

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )

    

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            f"Could not read image:\n{image_path}"
        )

    height, width = image.shape[:2]

    

    results = yolo_model.predict(
        source=str(image_path),
        conf=yolo_confidence,
        verbose=False
    )

    result = results[0]

    

    if (
        result.boxes is None
        or len(result.boxes) == 0
    ):

        return {
            "status": "PASS",
            "defects_detected": 0,
            "detections": []
        }

    
    detections = []

    for index, box in enumerate(
        result.boxes
    ):

       

        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .numpy()
        )

        

        x1 = max(
            0,
            int(x1)
        )

        y1 = max(
            0,
            int(y1)
        )

        x2 = min(
            width,
            int(x2)
        )

        y2 = min(
            height,
            int(y2)
        )

        
        yolo_conf = (
            box.conf[0]
            .cpu()
            .item()
        )

       

        crop = image[
            y1:y2,
            x1:x2
        ]


        if crop.size == 0:
            continue

        

        classification = classify_crop(
            crop
        )

        defect_type = classification[
            "defect_type"
        ]

        classification_confidence = (
            classification["confidence"]
        )

       
        size_score = calculate_size_score(
            x1,
            y1,
            x2,
            y2,
            width,
            height
        )

        
        location_score = calculate_location_score(
            x1,
            y1,
            x2,
            y2,
            width,
            height
        )

        try:

            defect_type_score = (
                get_defect_type_score(
                    defect_type
                )
            )

        except ValueError:

            defect_type_score = None

       

        if defect_type_score is not None:

            severity = calculate_severity(

                size=size_score,

                location=location_score,

                defect_type=defect_type_score,

                confidence=classification_confidence
            )

           

            quality = assess_quality(

                defect_type=defect_type,

                classification_confidence=(
                    classification_confidence
                ),

                severity_score=(
                    severity["severity_score"]
                ),

                severity_level=(
                    severity["severity_level"]
                ),

                recommended_action=(
                    severity["recommended_action"]
                )
            )

        else:

            

            severity = {

                "severity_score": None,

                "severity_level": "UNKNOWN",

                "recommended_action": (
                    "MANUAL_REVIEW"
                )
            }

            quality = {

                "quality_status": (
                    "MANUAL_REVIEW"
                ),

                "manual_review": True
            }

        

        detection = {

            "detection_number": (
                index + 1
            ),

           
            "bounding_box": [
                x1,
                y1,
                x2,
                y2
            ],

            "yolo_confidence": round(
                yolo_conf * 100,
                2
            ),


            "defect_type": (
                defect_type
            ),

            "classification_confidence": (
                classification_confidence
            ),

            

            "size_score": (
                size_score
            ),

            "location_score": (
                location_score
            ),

            "defect_type_score": (
                defect_type_score
            ),

            "confidence_score": (
                classification_confidence
            ),

            

            "severity_score": (
                severity[
                    "severity_score"
                ]
            ),

            "severity_level": (
                severity[
                    "severity_level"
                ]
            ),

            "recommended_action": (
                severity[
                    "recommended_action"
                ]
            ),

        

            "quality_status": (
                quality[
                    "quality_status"
                ]
            ),

            "manual_review": (
                quality[
                    "manual_review"
                ]
            )
        }

      

        detections.append(
            detection
        )

    

    if not detections:

        return {
            "status": "PASS",
            "defects_detected": 0,
            "detections": []
        }


    quality_priority = {
        "PASS": 0,
        "REVIEW": 1,
        "MANUAL_REVIEW": 1,
        "REWORK": 2,
        "FAIL": 3,
    }

    overall_status = "PASS"

    highest_priority = 0

    for detection in detections:

        status = detection.get(
            "quality_status",
            "MANUAL_REVIEW"
        )

        priority = quality_priority.get(
            status,
            1
        )

        if priority > highest_priority:

            highest_priority = priority

           

            if status == "MANUAL_REVIEW":

                overall_status = "REVIEW"

            else:

                overall_status = status

   

    return {

        "status": overall_status,

        "defects_detected": len(
            detections
        ),

        "detections": detections
    }