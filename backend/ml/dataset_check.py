from pathlib import Path


DATASET_PATH = Path(r"C:\Users\User\Desktop\VisionInspectAI\dataset1")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


if not DATASET_PATH.exists():
    print("ERROR: Dataset folder not found.")
    exit()


categories = [
    folder for folder in DATASET_PATH.iterdir()
    if folder.is_dir()
]


print("MVTec Dataset Report")
print("=" * 60)


for category in sorted(categories):

    train_count = 0
    test_count = 0

    train_path = category / "train"
    test_path = category / "test"

    if train_path.exists():
        train_count = sum(
            1 for file in train_path.rglob("*")
            if file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        )

    if test_path.exists():
        test_count = sum(
            1 for file in test_path.rglob("*")
            if file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        )

    total = train_count + test_count

    print(f"\nCategory: {category.name}")
    print(f"  Train images : {train_count}")
    print(f"  Test images  : {test_count}")
    print(f"  Total images : {total}")