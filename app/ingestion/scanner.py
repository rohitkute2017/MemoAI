
from pathlib import Path
from PIL import Image
import hashlib

# Locate the MemoAI project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the folder containing sample photographs
PHOTO_DIR = PROJECT_ROOT / "sample_photos"

# Supported image formats
SUPPORTED_FORMATS = {
    ".jpg", ".jpeg", ".png",
    ".webp", ".bmp", ".tif", ".tiff"
}


def scan_photos(folder):
    photos = []

    for file in folder.rglob("*"):
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            photos.append(file)

    return photos


def extract_metadata(image_path):

    with Image.open(image_path) as img:

        exif = img.getexif()

        metadata = {
            "filename": image_path.name,
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "file_size": image_path.stat().st_size,
            "capture_date": exif.get(36867) or exif.get(306)
        }

    return metadata


def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def find_duplicates(photos):

    hash_map = {}

    for photo in photos:
        file_hash = calculate_sha256(photo)

        if file_hash not in hash_map:
            hash_map[file_hash] = []

        hash_map[file_hash].append(photo)

    duplicates = {
        file_hash: files
        for file_hash, files in hash_map.items()
        if len(files) > 1
    }

    return duplicates



if __name__ == "__main__":

    photos = scan_photos(PHOTO_DIR)

    duplicates = find_duplicates(photos)

    if duplicates:
        for file_hash, files in duplicates.items():
            print("\nDuplicate group:")

            for file in files:
                print(file.name)
    else:
        print("No duplicate photographs found.")
