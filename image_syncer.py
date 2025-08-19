#!/usr/bin/env python3
"""
This script should help dad moving his pictures from the upload folder in dropbox to
his picture archive that is managed by picasa. Unfortunately picasa is not supported anymore
and somehow the import functionality is not working properly in his computer. This script
should replace that.
"""

import argparse
import contextlib
import imghdr
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image
import subprocess
import json

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)



@contextlib.contextmanager
def _suppress_and_log(image_path):
    try:
        yield
    except Exception as e:
        _logger.debug("Error extracting date from %s: %s", image_path, e)
    return None


def _get_video_creation_date(video_path: Path) -> datetime :
    """Extract creation date from video metadata using ffprobe."""
    # Use ffprobe.exe on Windows
    ffprobe_cmd = "ffprobe.exe" if subprocess.run(["where", "ffprobe.exe"], 
                                                    capture_output=True, shell=True, check=True).returncode == 0 else "ffprobe"
    
    result = subprocess.run(
        [
            ffprobe_cmd, "-v", "quiet", "-print_format", "json",
            "-show_entries", "format_tags=creation_time:stream_tags=creation_time",
            str(video_path)
        ],
        capture_output=True, text=True, check=True, shell=True
    )
    metadata = json.loads(result.stdout)
    
    # Try format tags first
    creation_time = metadata.get("format", {}).get("tags", {}).get("creation_time")
    
    # If not found, try stream tags
    if not creation_time and "streams" in metadata:
        for stream in metadata["streams"]:
            creation_time = stream.get("tags", {}).get("creation_time")
            if creation_time:
                break
    
    if creation_time:
        # Handle different datetime formats
        for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(creation_time, fmt)
            except ValueError:
                continue


def _get_image_creation_date(image_path: Path) -> datetime:
    with Image.open(image_path) as img:
        # EXIF (Exchangeable image file format) metadata
        exif_data = img.getexif()
        if exif_data:
            date_taken = exif_data.get(36867)  # Tag for date and time original
            if date_taken:
                date_obj = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                return date_obj



_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _get_date_from_filename(filename: str) -> datetime:
    match = _DATE_RE.search(filename)
    if match:
        date_str = match.group(0)
        return datetime.strptime(date_str, "%Y-%m-%d")
    return None


def _is_video(filename: str) -> bool:
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v")
    return filename.lower().endswith(video_extensions)


def _is_image(path: Path):
    return imghdr.what(path)


exclude = {"desktop.ini",}

def _get_file_creation_date(file_path: Path) -> datetime:
    """Generic function to extract creation date from any supported file type."""
    if _is_image(file_path):
        return _get_image_creation_date(file_path)
    elif _is_video(file_path.name):
        return _get_video_creation_date(file_path)
    raise ValueError(f"Unsupported file type: {file_path.name}")

def _is_supported_file(file_path: Path) -> bool:
    """Check if file is a supported image or video format."""
    return _is_image(file_path) or _is_video(file_path.name)


def organize_files(
    source_folder: Path, destination_folder: Path, dry_run: bool, file_types: list = None
) -> None:
    """
    Organize files by creation date into subdirectories.
    
    Args:
        source_folder: Source directory containing files to organize
        destination_folder: Target directory for organized files  
        dry_run: If True, only simulate the operation without moving files
        file_types: List of file types to process ('image', 'video'). If None, process all supported types.
    """
    # Create the destination folder if it doesn't exist
    if not destination_folder.exists() and not dry_run:
        destination_folder.mkdir(parents=True)

    # Iterate through the files in the source folder
    for source_path in source_folder.glob("*"):
        # Check if it's a file and not a folder
        if source_path.is_file() and source_path.name not in exclude:
            filename = source_path.name
            
            # Check file type filtering
            is_image = _is_image(source_path)
            is_video = _is_video(source_path.name)
            
            # Skip files that are not supported
            if not is_image and not is_video:
                _logger.warning("Archivo no soportado, se omite: %s", filename)
                continue
            
            # Apply file type filter if specified
            if file_types:
                if 'image' not in file_types and is_image:
                    continue
                if 'video' not in file_types and is_video:
                    continue

            date_taken = None

            # 1st chance: read from metadata
            with _suppress_and_log(source_path):
                date_taken = _get_file_creation_date(source_path)

            # 2nd chance: read from filename
            if date_taken is None:
                date_taken = _get_date_from_filename(filename)

            if date_taken is None:
                _logger.warning("No se encontró fecha para el archivo: %s", filename)
                continue

            # Organize by date
            destination_subfolder = date_taken.strftime("%Y-%m-%d")
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

    _logger.info("¡Proceso completado!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organiza archivos multimedia por su fecha de creación."
    )
    parser.add_argument(
        "source_folder",
        type=Path,
        help="Carpeta de origen que contiene los archivos",
    )
    parser.add_argument(
        "destination_folder",
        type=Path,
        help="Carpeta de destino para organizar los archivos",
    )
    parser.add_argument(
        "-t", "--type",
        choices=["image", "video"],
        help="Tipo de archivo a procesar (image o video). Si no se especifica, procesa ambos.",
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
    file_types = [args.type] if args.type else None

    try:
        organize_files(source_folder, destination_folder, dry_run, file_types)
    except Exception as e:
        _logger.error("Ocurrió un error: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
