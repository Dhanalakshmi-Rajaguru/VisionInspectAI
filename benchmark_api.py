import os
import time
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

EMAIL = os.getenv("VISIONINSPECT_EMAIL")
PASSWORD = os.getenv("VISIONINSPECT_PASSWORD")

DATASET_ROOT = Path(
    r"C:\Users\User\Desktop\VisionInspectAI\dataset1"
)

# Categories to benchmark
CATEGORIES = [
    "cable",
    "bottle",
    "transistor",
    "metal_nut",
    "capsule",
]

# Number of images from each category
IMAGES_PER_CATEGORY = 10

# Supported image formats
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


# ============================================================
# LOGIN
# ============================================================

def login():

    if not EMAIL:
        raise RuntimeError(
            "VISIONINSPECT_EMAIL is not set."
        )

    if not PASSWORD:
        raise RuntimeError(
            "VISIONINSPECT_PASSWORD is not set."
        )

    print("\nLogging in...")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=30,
    )

    if response.status_code != 200:

        print("\nLOGIN FAILED")
        print("-" * 60)
        print("Status code :", response.status_code)
        print("Response    :", response.text)
        print("-" * 60)

        response.raise_for_status()

    data = response.json()

    if "access_token" not in data:
        raise RuntimeError(
            "access_token was not found in login response."
        )

    print("Login successful.")

    return data["access_token"]



# ============================================================
# FIND TEST IMAGES
# ============================================================

def get_test_images(category):

    test_directory = (
        DATASET_ROOT
        / category
        / "test"
    )

    if not test_directory.exists():

        print(
            f"\n[{category}] Test directory not found:"
        )

        print(test_directory)

        return []

    images = sorted(
        [
            path
            for path in test_directory.rglob("*")
            if path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ]
    )

    return images[:IMAGES_PER_CATEGORY]


# ============================================================
# BENCHMARK ONE CATEGORY
# ============================================================

def benchmark_category(category, token):

    image_files = get_test_images(category)

    if not image_files:

        print(
            f"\n[{category}] No images found."
        )

        return None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    times = []

    successful = 0
    failed = 0

    print("\n")
    print("=" * 80)
    print(f"TESTING CATEGORY: {category.upper()}")
    print(f"Images selected : {len(image_files)}")
    print("=" * 80)

    for index, image_path in enumerate(
        image_files,
        start=1
    ):

        start_time = time.perf_counter()

        try:

            with open(
                image_path,
                "rb"
            ) as image_file:

                response = requests.post(
                    f"{BASE_URL}/inspection/predict",

                    headers=headers,

                    files={
                        "file": (
                            image_path.name,
                            image_file,
                            "application/octet-stream",
                        )
                    },

                    data={
                        "product_category": category
                    },

                    timeout=120,
                )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                successful += 1

                times.append(elapsed)

                # Read response information
                try:

                    result = response.json()

                    prediction = result.get(
                        "prediction",
                        "N/A"
                    )

                    defect_count = result.get(
                        "defect_count",
                        "N/A"
                    )

                except ValueError:

                    prediction = "N/A"
                    defect_count = "N/A"

                print(
                    f"{index:02d}. "
                    f"{image_path.name:<25} "
                    f"200  "
                    f"{elapsed:.3f} sec  "
                    f"prediction={prediction:<12} "
                    f"defects={defect_count}"
                )

            # ------------------------------------------------
            # FAILED REQUEST
            # ------------------------------------------------

            else:

                failed += 1

                print(
                    f"{index:02d}. "
                    f"{image_path.name:<25} "
                    f"{response.status_code}  "
                    f"{elapsed:.3f} sec"
                )

                print(
                    "    Response:",
                    response.text[:500]
                )

        except requests.RequestException as error:

            failed += 1

            elapsed = (
                time.perf_counter()
                - start_time
            )

            print(
                f"{index:02d}. "
                f"{image_path.name:<25} "
                f"REQUEST ERROR  "
                f"{elapsed:.3f} sec"
            )

            print(
                "    Error:",
                error
            )

        except Exception as error:

            failed += 1

            elapsed = (
                time.perf_counter()
                - start_time
            )

            print(
                f"{index:02d}. "
                f"{image_path.name:<25} "
                f"ERROR  "
                f"{elapsed:.3f} sec"
            )

            print(
                "    Error:",
                error
            )

    # ========================================================
    # CATEGORY SUMMARY
    # ========================================================

    print("\n")
    print(
        f"--- {category.upper()} SUMMARY ---"
    )

    print(
        f"Successful images : {successful}"
    )

    print(
        f"Failed images     : {failed}"
    )

    if not times:

        print(
            "No successful requests."
        )

        return {
            "category": category,
            "successful": successful,
            "failed": failed,
            "average": None,
            "minimum": None,
            "maximum": None,
            "throughput": None,
            "times": [],
        }

    average = sum(times) / len(times)

    minimum = min(times)

    maximum = max(times)

    total_time = sum(times)

    throughput = (
        len(times) / total_time
    )

    print(
        f"Average time      : {average:.3f} sec"
    )

    print(
        f"Minimum time      : {minimum:.3f} sec"
    )

    print(
        f"Maximum time      : {maximum:.3f} sec"
    )

    print(
        f"Images/sec        : {throughput:.2f}"
    )

    return {
        "category": category,
        "successful": successful,
        "failed": failed,
        "average": average,
        "minimum": minimum,
        "maximum": maximum,
        "throughput": throughput,
        "times": times,
    }


# ============================================================
# FINAL MULTI-CATEGORY SUMMARY
# ============================================================

def print_final_summary(results):

    print("\n\n")

    print("=" * 105)
    print(
        "FINAL MULTI-CATEGORY PERFORMANCE SUMMARY"
    )
    print("=" * 105)

    print(
        f"{'Category':<15}"
        f"{'Success':<10}"
        f"{'Failed':<10}"
        f"{'Average':<13}"
        f"{'Minimum':<13}"
        f"{'Maximum':<13}"
        f"{'Images/sec':<13}"
    )

    print("-" * 105)

    all_times = []

    total_successful = 0
    total_failed = 0

    for result in results:

        category = result["category"]

        total_successful += (
            result["successful"]
        )

        total_failed += (
            result["failed"]
        )

        all_times.extend(
            result["times"]
        )

        if result["average"] is None:

            print(
                f"{category:<15}"
                f"{result['successful']:<10}"
                f"{result['failed']:<10}"
                f"{'N/A':<13}"
                f"{'N/A':<13}"
                f"{'N/A':<13}"
                f"{'N/A':<13}"
            )

        else:

            print(
                f"{category:<15}"
                f"{result['successful']:<10}"
                f"{result['failed']:<10}"
                f"{result['average']:<13.3f}"
                f"{result['minimum']:<13.3f}"
                f"{result['maximum']:<13.3f}"
                f"{result['throughput']:<13.2f}"
            )

    print("-" * 105)

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    if all_times:

        overall_average = (
            sum(all_times)
            / len(all_times)
        )

        overall_minimum = min(all_times)

        overall_maximum = max(all_times)

        total_time = sum(all_times)

        overall_throughput = (
            len(all_times)
            / total_time
        )

        print(
            f"{'OVERALL':<15}"
            f"{total_successful:<10}"
            f"{total_failed:<10}"
            f"{overall_average:<13.3f}"
            f"{overall_minimum:<13.3f}"
            f"{overall_maximum:<13.3f}"
            f"{overall_throughput:<13.2f}"
        )

    print("=" * 105)

    # --------------------------------------------------------
    # PERFORMANCE INTERPRETATION
    # --------------------------------------------------------

    if all_times:

        print("\nPerformance interpretation")
        print("-" * 50)

        print(
            f"Total successful requests : "
            f"{total_successful}"
        )

        print(
            f"Total failed requests     : "
            f"{total_failed}"
        )

        print(
            f"Overall average latency   : "
            f"{overall_average:.3f} sec/image"
        )

        print(
            f"Overall throughput        : "
            f"{overall_throughput:.2f} images/sec"
        )

        print(
            "\nThis benchmark measures the complete "
            "FastAPI request:"
        )

        print(
            "Image upload -> YOLO -> ResNet18 -> "
            "severity -> database -> response"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "VisionInspectAI - "
        "FULL MULTI-CATEGORY API BENCHMARK"
    )
    print("=" * 80)

    print(
        f"\nAPI URL        : {BASE_URL}"
    )

    print(
        f"Dataset root   : {DATASET_ROOT}"
    )

    print(
        f"Categories     : "
        f"{', '.join(CATEGORIES)}"
    )

    print(
        f"Images/category: "
        f"{IMAGES_PER_CATEGORY}"
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    token = login()

    # --------------------------------------------------------
    # RUN ALL CATEGORIES
    # --------------------------------------------------------

    results = []

    for category in CATEGORIES:

        result = benchmark_category(
            category,
            token
        )

        if result is not None:

            results.append(result)

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    if results:

        print_final_summary(results)

    else:

        print(
            "\nNo benchmark results were generated."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
