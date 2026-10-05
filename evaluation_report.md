# VisionInspect AI

## Testing, Evaluation & Optimization Report

---

## 1. Overview

VisionInspect AI is an AI-powered manufacturing quality inspection system designed to detect product defects from images and automatically support quality decisions.

The current inspection pipeline combines:

```text
Input Product Image
        ↓
YOLO26n Defect Detection
        ↓
Defect Bounding Box + Confidence
        ↓
Defect Crop
        ↓
ResNet18 Defect Classification
        ↓
Severity Calculation
        ↓
Quality Decision
        ↓
FastAPI Backend
        ↓
PostgreSQL Database
        ↓
React Dashboard
```

It is focused on testing and optimization of the machine-learning pipeline and the integrated application.

The main activities completed were:

* Frozen test-set evaluation
* YOLO detection evaluation
* Confidence-threshold tuning
* Targeted augmentation
* Visual failure analysis
* Error analysis
* ResNet18 classification evaluation
* End-to-end API performance testing
* Unit testing of severity/manual-review logic

---

# 2. Evaluation Methodology

## 2.1 Frozen Test Set

A fixed held-out test set was used for the final YOLO evaluation.

The frozen test set contains:

| Metric            |     Value |
| ----------------- | --------: |
| Test images       |       817 |
| Defect instances  |       290 |
| Background images |       616 |
| YOLO image size   | 640 × 640 |
| IoU threshold     |      0.50 |

The test set was verified before evaluation.

The verification confirmed:

* 817 test images
* 290 ground-truth defect boxes
* 616 background images

The test images and labels were not modified during threshold evaluation.

This ensured that the final threshold comparison was performed on the same fixed evaluation data.

---

# 3. YOLO Defect Detection Evaluation

The project uses YOLO26n as the defect detection model.

The model predicts:

* Whether a defect is present
* Defect bounding-box location
* Detection confidence

The YOLO detector uses a single detection class:

```text
defect
```

Detailed MVTec defect types are handled later by the classification stage.

---

## 3.1 Baseline YOLO Performance

The original YOLO model was evaluated on the frozen test set.

Baseline results:

| Metric         |          Baseline |
| -------------- | ----------------: |
| Precision      |             71.5% |
| Recall         |             65.5% |
| mAP@50         |             72.3% |
| mAP@50–95      |             40.2% |
| Inference time | ~4.6–4.9 ms/image |

These results provided the baseline for subsequent optimization.

---

# 4. Targeted Augmentation

Error analysis identified several weak defect categories, particularly:

* `cable_swap`
* `bent_lead`
* `cut_lead`

The original training data contained very few examples for these defects.

Original training counts included:

| Defect     | Original samples |
| ---------- | ---------------: |
| cable_swap |                8 |
| bent_lead  |                7 |
| cut_lead   |                4 |

Targeted augmentation was therefore applied to increase representation of these weak defect patterns.

The augmented target was 20 samples per weak category.

The augmentation operations included:

* Horizontal flipping
* Mild affine transformation
* Rotation
* Scaling
* Translation
* Brightness/contrast adjustment
* Small Gaussian blur

Validation and test data were not augmented.

---

# 5. Optimized YOLO Performance

After targeted augmentation, the YOLO26n model was retrained.

The optimized model was evaluated on the same frozen test set.

Results:

| Metric    |    Baseline | Targeted Augmentation |
| --------- | ----------: | --------------------: |
| Precision |       71.5% |             **79.3%** |
| Recall    |       65.5% |             **67.6%** |
| mAP@50    |       72.3% |             **77.2%** |
| mAP@50–95 |       40.2% |             **43.9%** |
| Inference | ~4.6–4.9 ms |               ~4.9 ms |

Improvement:

| Metric    |            Improvement |
| --------- | ---------------------: |
| Precision | +7.8 percentage points |
| Recall    | +2.1 percentage points |
| mAP@50    | +4.9 percentage points |
| mAP@50–95 | +3.7 percentage points |

The targeted augmentation therefore improved the overall detection metrics.

However, the test support for the weak categories was very small. Therefore, the category-specific improvement should not be treated as statistically conclusive.

For example:

* `cable_swap`: 1/3 detected after optimization vs 0/3 before
* `cut_lead`: 2/3 detected after optimization vs 1/3 before
* `bent_lead`: 0/1 detected in both cases

These results indicate improvement but also show that additional representative training data would be beneficial.

---

# 6. Error Analysis

Error analysis was performed to understand the types of mistakes made by the detector.

A separate diagnostic test set containing 537 images was used for detailed error investigation.

This dataset is distinct from the final frozen 817-image test set.

Therefore, the 537-image results are treated as diagnostic results rather than final model-performance metrics.

---

## 6.1 Diagnostic Error Analysis Results

At:

```text
Confidence threshold = 0.25
IoU threshold = 0.50
```

the diagnostic evaluation produced:

| Metric             | Result |
| ------------------ | -----: |
| Images             |    537 |
| Ground-truth boxes |    196 |
| Predictions        |    206 |
| True positives     |    160 |
| False positives    |     46 |
| False negatives    |     36 |
| Precision          | 77.67% |
| Recall             | 81.63% |
| F1                 | 79.60% |

The analysis identified:

* 16 false-negative images
* 2 false-positive images
* 400 correctly classified background images

---

# 7. Visual Failure Analysis

Visual inspection was performed on representative failure cases.

Generated failure-case directories:

```text
failure_cases/
├── false_negatives/
├── false_positives/
└── localization_errors/
```

A total of 18 failure-case images were generated.

These consisted of:

* 16 false-negative cases
* 2 false-positive cases
* Selected localization-error cases

---

## 7.1 False-Negative Example

A capsule example contained a small or subtle defect where the ground-truth bounding box was present but the YOLO model did not produce a matching prediction.

This indicates that small, low-contrast defects remain challenging for the detector.

---

## 7.2 False-Positive Examples

A pill example produced a low-confidence prediction on ambiguous surface texture.

A wood example produced a low-confidence prediction on natural wood texture.

These examples indicate that natural or visually ambiguous surface patterns can sometimes resemble defects to the detector.

---

# 8. Weak Defect Analysis

Detailed investigation was also performed for weak defect categories.

## Cable

The cable dataset contained:

* 342 images
* 92 defective images
* 151 defect boxes

At the diagnostic confidence threshold:

| Defect               | Detection |
| -------------------- | --------: |
| bent_wire            |     13/13 |
| cable_swap           |      0/12 |
| combined             |     10/11 |
| cut_inner_insulation |     14/14 |
| cut_outer_insulation |      7/10 |
| missing_cable        |     11/12 |
| missing_wire         |      9/10 |
| poke_insulation      |      7/10 |

`cable_swap` was particularly difficult.

Its maximum prediction confidence was approximately 6.68% during the investigation, indicating that the detector struggled to learn a strong visual representation for this defect.

---

## Transistor

The transistor dataset contained:

* 278 images
* 40 defective images
* 44 defect boxes

Results included:

| Defect       | Detection |
| ------------ | --------: |
| bent_lead    |      0/10 |
| cut_lead     |      1/10 |
| damaged_case |      9/10 |
| misplaced    |      5/10 |

The `bent_lead` defect was especially difficult.

Its maximum observed confidence was approximately 14.2% during the diagnostic investigation.

Increasing inference resolution from 640 to 960 and 1280 did not solve this problem.

A separate 1280 training experiment also performed poorly, with very low validation mAP.

Therefore, the difficulty appears to be related more to:

* Small/subtle visual differences
* Limited training examples
* Weak visual representation

rather than simply image resolution.

---

# 9. Confidence Threshold Evaluation

A confidence-threshold sweep was performed on the exact frozen 817-image test set.

Thresholds evaluated:

```text
0.10
0.15
0.20
0.25
0.30
0.35
0.40
0.45
0.50
```

IoU threshold:

```text
0.50
```

---

## 9.1 Frozen-Test Results

| Threshold |  Precision |     Recall |         F1 |      TP |     FP |     FN |
| --------: | ---------: | ---------: | ---------: | ------: | -----: | -----: |
|      0.10 |     66.97% |     76.90% |     71.59% |     223 |    110 |     67 |
|      0.15 |     72.19% |     75.17% |     73.65% |     218 |     84 |     72 |
|      0.20 |     76.00% |     72.07% |     73.98% |     209 |     66 |     81 |
|  **0.25** | **78.16%** | **70.34%** | **74.05%** | **204** | **57** | **86** |
|      0.30 |     80.08% |     67.93% |     73.51% |     197 |     49 |     93 |
|  **0.35** | **83.55%** | **66.55%** | **74.09%** | **193** | **38** | **97** |
|      0.40 |     85.71% |     64.14% |     73.37% |     186 |     31 |    104 |
|      0.45 |     86.96% |     62.07% |     72.43% |     180 |     27 |    110 |
|      0.50 |     87.94% |     60.34% |     71.57% |     175 |     24 |    115 |

---

# 10. Final Confidence Threshold Selection

The highest F1 score among the tested thresholds was obtained at:

```text
Threshold = 0.35
F1 = 74.09%
```

However, the current threshold of 0.25 produced:

```text
F1 = 74.05%
```

The difference is only:

```text
0.04 percentage points
```

The threshold of 0.25 provides higher recall:

```text
0.25 → 70.34% recall
0.35 → 66.55% recall
```

At the same time, 0.25 produces more false positives:

```text
0.25 → 57 FP
0.35 → 38 FP
```

The comparison is:

| Metric    | Threshold 0.25 | Threshold 0.35 |
| --------- | -------------: | -------------: |
| Precision |         78.16% |         83.55% |
| Recall    |     **70.34%** |         66.55% |
| F1        |         74.05% |     **74.09%** |
| TP        |        **204** |            193 |
| FP        |             57 |         **38** |
| FN        |         **86** |             97 |

Because this is a manufacturing inspection application, retaining higher defect recall is preferred over a negligible F1 improvement.

Therefore, the selected production confidence threshold is:

```text
FINAL YOLO CONFIDENCE THRESHOLD = 0.25
```

The threshold selection is based on the trade-off between false negatives and false positives rather than selecting the numerically highest F1 value alone.

---

# 11. Final YOLO Detection Metrics

Using the selected confidence threshold of 0.25 on the frozen test set:

| Metric    |     Result |
| --------- | ---------: |
| Precision | **78.16%** |
| Recall    | **70.34%** |
| F1        | **74.05%** |
| TP        |    **204** |
| FP        |     **57** |
| FN        |     **86** |

These custom threshold metrics are different from the standard Ultralytics mAP metrics and should be reported separately.

The optimized model's standard detection metrics were:

| Metric    |     Result |
| --------- | ---------: |
| Precision | **79.29%** |
| Recall    | **67.59%** |
| mAP@50    | **77.17%** |
| mAP@50–95 | **43.86%** |

---

# 12. ResNet18 Defect Classification

After YOLO detects a defect, the detected region is cropped and passed to a ResNet18 classifier.

The classifier predicts the detailed defect type.

The classifier was trained using:

* Input size: 224 × 224
* Pretrained ResNet18
* Horizontal flip
* Rotation
* Color jitter
* ImageNet normalization
* Batch size: 32
* Adam optimizer
* Learning rate: 0.0001
* Class weighting
* Best checkpoint selected using validation macro F1

The classifier contains 48 defect classes.

---

## 12.1 Classification Test Results

The final classifier was evaluated on 290 test images.

| Metric          |     Result |
| --------------- | ---------: |
| Test images     |        290 |
| Classes         |         48 |
| Accuracy        | **78.28%** |
| Macro Precision | **75.14%** |
| Macro Recall    | **82.34%** |
| Macro F1        | **76.60%** |

These results show that the classifier provides useful defect-type classification performance while still having difficulties with certain visually similar or underrepresented classes.

---

## 12.2 Difficult Classes

Some difficult classes included:

* `combined`
* `scratch_neck`
* `bent_lead`
* `bent_wire`

The classifier also had classes with zero test support:

* `pill_type`
* `squeezed_teeth`

Therefore, class-specific conclusions should take test-set support into account.

---

# 13. Severity Evaluation

The system calculates a severity score after defect detection and classification.

The current formula is:

```text
Severity =
    (Size × 0.30)
  + (Location × 0.25)
  + (DefectType × 0.25)
  + (Confidence × 0.20)
```

Severity levels:

|  Score | Severity | Recommended Action |
| -----: | -------- | ------------------ |
| 80–100 | Critical | Reject             |
|  60–79 | High     | Rework             |
|  40–59 | Medium   | Review             |
|   0–39 | Low      | Accept             |

Classification confidence below 70% triggers:

```text
MANUAL_REVIEW
```

The size and location scoring rules are currently development/demo rules and are not claimed to be industry-standard severity measurements.

---

# 14. Integrated API Testing

The complete inspection pipeline was tested through the FastAPI endpoint:

```text
POST /inspection/predict
```

The tested pipeline was:

```text
Image Upload
      ↓
YOLO Detection
      ↓
ResNet18 Classification
      ↓
Severity Calculation
      ↓
Quality Decision
      ↓
Database Storage
      ↓
API Response
```

---

## 14.1 Example Inspection Results

### Inspection 130

```text
Prediction: REVIEW
Defect: bent_lead
YOLO confidence: 26.24%
Classification confidence: 99.94%
Severity score: 45.63
Severity level: Medium
Recommended action: Review
Manual review: False
```

### Inspection 131

```text
Prediction: REVIEW
Defect: color
YOLO confidence: 85.14%
Classification confidence: 84.96%
Severity score: 42.63
Severity level: Medium
Recommended action: Review
```

### Inspection 134

A good image produced:

```text
Prediction: PASS
Defect count: 0
```

### Inspection 138

Multiple defects were detected:

```text
Detection 1:
    Defect: missing_wire
    YOLO confidence: 91.72%
    Classification confidence: 98.86%
    Severity: 60.23
    Level: High
    Action: Rework

Detection 2:
    Defect: missing_cable
    YOLO confidence: 46.19%
    Classification confidence: 99.05%
    Severity: 62.88
    Level: High
    Action: Rework
```

This confirms that the integrated system supports multiple detections within a single image.

---

# 15. API Performance Benchmark

The complete API pipeline was benchmarked across five product categories:

* Cable
* Bottle
* Transistor
* Metal nut
* Capsule

A total of:

```text
50 requests
```

were tested.

Results:

| Category   | Requests | Average Time |    Throughput |
| ---------- | -------: | -----------: | ------------: |
| Cable      |    10/10 |      0.287 s | 3.48 images/s |
| Bottle     |    10/10 |      0.299 s | 3.34 images/s |
| Transistor |    10/10 |      0.301 s | 3.32 images/s |
| Metal nut  |    10/10 |      0.330 s | 3.03 images/s |
| Capsule    |    10/10 |      0.323 s | 3.10 images/s |

Overall:

| Metric                |              Result |
| --------------------- | ------------------: |
| Successful requests   |           **50/50** |
| Failed requests       |               **0** |
| Average response time |   **0.308 s/image** |
| Minimum response time |         **0.218 s** |
| Maximum response time |         **0.596 s** |
| Throughput            | **3.25 images/sec** |

The benchmark represents end-to-end API processing rather than isolated model inference.

The higher maximum time observed for some metal-nut images was associated with images containing multiple detections, which naturally increases downstream processing.

---

# 16. Unit Testing

Unit tests were created for severity and manual-review logic.

The tested cases included:

### Test 1 — Low classification confidence

Classification confidence:

```text
65%
```

Expected:

```text
MANUAL_REVIEW
```

Result:

```text
PASSED
```

### Test 2 — Confidence at 70%

Classification confidence:

```text
70%
```

Expected:

```text
Normal quality decision
```

Result:

```text
PASSED
```

Final unit-test result:

```text
2 passed in 0.04 seconds
```

---

# 17. Optimization Attempts

Several optimization approaches were investigated.

## Successful optimization

### Targeted augmentation

Targeted augmentation improved:

* Precision
* Recall
* mAP@50
* mAP@50–95

The optimized model was therefore selected over the original baseline model.

---

## Investigated but unsuccessful approach

A higher-resolution 1280-pixel training experiment was evaluated.

The experiment performed poorly, with extremely low validation performance.

Therefore, increasing training resolution to 1280 was not adopted.

Inference-only testing at 640, 960, and 1280 also did not resolve the `bent_lead` detection problem.

This indicates that simply increasing image resolution was not sufficient for the difficult defect.

---

# 18. Error Analysis Findings

The major findings from Milestone 4 are:

### 1. Small and subtle defects are difficult

Small defects with low contrast can be missed by YOLO.

### 2. Underrepresented defects remain challenging

Defects such as:

```text
cable_swap
bent_lead
cut_lead
```

have very limited training representation.

### 3. Natural surface texture can cause false positives

Examples include:

* Wood texture
* Ambiguous surface patterns
* Low-contrast visual structures

### 4. Higher confidence thresholds reduce false positives

Increasing the threshold from 0.25 to 0.50 reduced:

```text
FP: 57 → 24
```

but also reduced:

```text
Recall: 70.34% → 60.34%
```

Therefore, increasing the threshold too much is not appropriate for the current application.

### 5. Targeted augmentation helped overall detection

The optimized model improved the standard detection metrics compared with the baseline.

---

# 19. Limitations

The current system has several limitations.

## Dataset limitations

Some defect categories have very few examples.

This limits the model's ability to learn subtle visual patterns.

## Detection limitations

The detector still produces:

* False negatives
* False positives
* Localization errors

particularly for small or subtle defects.

## Classification limitations

Some of the 48 defect classes have limited test support.

Therefore, class-specific classification metrics must be interpreted carefully.

## Severity limitations

The current size and location scoring rules are development rules.

They should not be interpreted as validated industrial severity standards.

## Hardware limitations

The API benchmark represents the current development environment and should not be treated as a universal production performance guarantee.

## Generalization

The model has been evaluated on the available MVTec-based dataset and should be further validated using real factory images before deployment in a production manufacturing environment.

---

# 20. Final Results

The major outcomes are summarized below.

| Area                     | Result              |
| ------------------------ | ------------------- |
| Frozen test set          | 817 images          |
| Defect instances         | 290                 |
| Background images        | 616                 |
| Final YOLO threshold     | **0.25**            |
| Frozen-test precision    | **78.16%**          |
| Frozen-test recall       | **70.34%**          |
| Frozen-test F1           | **74.05%**          |
| Optimized YOLO mAP@50    | **77.17%**          |
| Optimized YOLO mAP@50–95 | **43.86%**          |
| ResNet18 accuracy        | **78.28%**          |
| ResNet18 macro precision | **75.14%**          |
| ResNet18 macro recall    | **82.34%**          |
| ResNet18 macro F1        | **76.60%**          |
| API success rate         | **50/50**           |
| API average response     | **0.308 s/image**   |
| API throughput           | **3.25 images/sec** |
| Unit tests               | **2/2 passed**      |
| Visual failure cases     | **18 generated**    |
| Threshold sweep          | **Completed**       |
| Targeted augmentation    | **Completed**       |

---

# 21.Conclusion

The successfully evaluated and optimized the VisionInspect AI inspection pipeline.

The YOLO26n detector was improved through targeted augmentation of weak defect categories. The optimized model achieved:

```text
mAP@50     = 77.17%
mAP@50–95  = 43.86%
```

on the frozen evaluation set.

A dedicated confidence-threshold study was performed on all 817 frozen test images.

Although a threshold of 0.35 produced the highest F1 score of 74.09%, its improvement over the 0.25 threshold was only 0.04 percentage points. The 0.25 threshold provided better recall, detecting 204 of the 290 ground-truth defect instances compared with 193 at 0.35.

Therefore:

```text
Final selected YOLO confidence threshold = 0.25
```

The ResNet18 classification stage achieved:

```text
Accuracy    = 78.28%
Macro F1    = 76.60%
```

The integrated FastAPI system successfully processed:
```text
50/50 API requests
```

with an average end-to-end processing time of:
```text
0.308 seconds/image
```

Unit testing of the severity/manual-review logic also passed successfully.

Overall, the evaluation demonstrates that the current VisionInspect AI pipeline is functional and measurable, while also identifying clear areas for future improvement, particularly for small, subtle, and underrepresented defect types.

---

## 22. Recommended Future Improvements

Future development can focus on:

1. Collecting more examples of rare defect categories.
2. Improving annotation quality for difficult defects.
3. Testing stronger YOLO architectures/backbones.
4. Investigating class-specific training strategies.
5. Improving small-object detection.
6. Expanding real-world manufacturing validation data.
7. Calibrating classification confidence.
8. Validating severity scoring with domain experts.
9. Adding larger-scale API/load testing.
10. Monitoring production false-positive and false-negative rates.

---

## 23. Evaluation Artifacts

The following artifacts were produced during evaluation:


frozen_threshold_results.csv

failure_cases/
├── false_negatives/
├── false_positives/
└── localization_errors/


The evaluation also produced the corresponding model checkpoints and test outputs used during the optimization process.

---

