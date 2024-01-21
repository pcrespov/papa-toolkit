import os
import shutil
import argparse
import logging
from PIL import Image
from datetime import datetime
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Function to extract the creation date from an image
def _get_image_creation_date(image_path: Path) -> datetime | None:
    try:
        with Image.open(image_path) as img:
            # EXIF (Exchangeable image file format) metadata
            exif_data = img._getexif()
            if exif_data:
                date_taken = exif_data.get(36867)  # Tag for date and time original
                if date_taken:
                    date_obj = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                    return date_obj
    except Exception as e:
        _logger.error(f"Error extracting date from {image_path}: {e}")
    return None

def organize_images(source_folder: Path, destination_folder: Path, dry_run: bool) -> None:
    # Create the destination folder if it doesn't exist
    if not destination_folder.exists():
        destination_folder.mkdir(parents=True)

    # Get today's date for images without date information
    today_date = datetime.now().strftime("%d-%m-%Y")

    # Iterate through the files in the source folder
    for filename in os.listdir(source_folder) and not dry_run:
        source_path = source_folder / filename

        # Check if it's a file and not a folder
        if source_path.is_file():
            # Get the creation date of the image
            date_taken = _get_image_creation_date(source_path)

            if date_taken:
                # Create a subfolder in the destination folder based on the date
                destination_subfolder = date_taken.strftime("%d-%m-%Y")
                destination_path = destination_folder / destination_subfolder

                # Create the subfolder if it doesn't exist
                if not destination_path.exists() and not dry_run:
                    destination_path.mkdir(parents=True)

                # Move the image to the corresponding subfolder (in non-dry-run mode)
                if not dry_run:
                    shutil.move(str(source_path), str(destination_path / filename))
                    _logger.info(f"Se movió {filename} a {destination_subfolder}")
                else:
                    _logger.info(f"(Dry run) Se movería {filename} a {destination_subfolder}")

            else:
                # Move the image to the "Today" folder if no date information is available
                today_path = destination_folder / today_date

                # Create the "Today" folder if it doesn't exist
                if not today_path.exists() and not dry_run:
                    today_path.mkdir(parents=True)

                # Move the image to the "Today" folder (in non-dry-run mode)
                if not dry_run:
                    shutil.move(str(source_path), str(today_path / filename))
                    _logger.info(f"Se movió {filename} a {today_date}")
                else:
                    _logger.info(f"(Dry run) Se movería {filename} a {today_date}")


    _logger.info("¡Listo!")

def main() -> None:
    parser = argparse.ArgumentParser(description="Organiza imágenes por su fecha de creación.")
    parser.add_argument("source_folder", type=Path, help="Carpeta de origen que contiene las imágenes")
    parser.add_argument("destination_folder", type=Path, help="Carpeta de destino para organizar las imágenes")
    parser.add_argument("--dry-run", "n", action="store_true", help="Modo simulación (sin mover ni crear carpetas)")
    args = parser.parse_args()

    try:
        organize_images(
    source_folder = args.source_folder
    destination_folder = args.destination_folder
    dry_run = args.dry_run

        )
    except Exception as e:
        _logger.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()