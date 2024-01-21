#!/usr/bin/env python3
"""
This script should help dad moving his pictures from the upload folder in dropbox to
his picture archive that is managed by picasa. Unfortunately picasa is not supported anymore
and somehow the import functionality is not working properly in his computer. This script
should replace that.
"""

import shutil
import argparse
import logging
import re
import imghdr
from PIL import Image
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def _get_image_creation_date(image_path: Path) -> datetime:
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
        _logger.debug("Error extracting date from %s: %s", image_path, e, exc_info=True)
    return None


date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _get_date_from_filename(filename: str) -> datetime:
    match = date_pattern.search(filename)
    if match:
        date_str = match.group(0)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj
    return None


def _is_video(filename: str) -> bool:
    video_extensions = (".mp4", ".mov", ".avi", ".mkv")  # Add more extensions as needed
    return filename.lower().endswith(video_extensions)


def _is_image(path: Path):
    return imghdr.what(path)


def organize_images(
    source_folder: Path, destination_folder: Path, dry_run: bool
) -> None:
    # Create the destination folder if it doesn't exist
    if not destination_folder.exists() and not dry_run:
        destination_folder.mkdir(parents=True)

    # Iterate through the files in the source folder using source_folder.glob()
    for source_path in source_folder.glob("*"):
        # Check if it's a file and not a folder
        if source_path.is_file():
            filename = source_path.name

            # 1st chance: read from image metadata
            date_taken = _get_image_creation_date(source_path)
            
            if date_taken is None:
                # 2nd chance read from filename
                date_taken = _get_date_from_filename(filename)

            if date_taken is None:
                _logger.warning("No se encontró fecha para el archivo: %s", filename)
            else:
                destination_subfolder = date_taken.strftime("%d-%m-%Y")
                destination_path = destination_folder / destination_subfolder

                if not destination_path.exists() and not dry_run:
                    destination_path.mkdir(parents=True)

                if not dry_run:
                    shutil.move(str(source_path), str(destination_path / filename))
                    _logger.info("Se movió %s a %s", filename, destination_subfolder)
                else:
                    _logger.info(
                        "(Dry run) Se movería %s a %s", filename, destination_subfolder
                    )

    _logger.info("¡Listo!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organiza imágenes y videos por su fecha de creación."
    )
    parser.add_argument(
        "source_folder",
        type=Path,
        help="Carpeta de origen que contiene las imágenes y videos",
    )
    parser.add_argument(
        "destination_folder",
        type=Path,
        help="Carpeta de destino para organizar las imágenes y videos",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Modo simulación (sin mover ni crear carpetas)",
    )
    args = parser.parse_args()

    source_folder = args.source_folder
    destination_folder = args.destination_folder
    dry_run = args.dry_run

    try:
        organize_images(source_folder, destination_folder, dry_run)
    except Exception as e:
        _logger.error("Ocurrió un error: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
