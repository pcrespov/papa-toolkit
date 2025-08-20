#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pillow",
# ]
# ///
"""
This script should help dad moving his pictures from the upload folder in dropbox to
his picture archive that is managed by picasa. Unfortunately picasa is not supported anymore
and somehow the import functionality is not working properly in his computer. This script
should replace that.
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
_logger = logging.getLogger(__name__)


def _get_video_creation_date(video_path: Path) -> datetime:
    """Extract creation date from video metadata using ffprobe."""
    ffprobe_cmd = _get_ffprobe_command()

    result = subprocess.run(
        [
            ffprobe_cmd,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_entries",
            "format_tags=creation_time:stream_tags=creation_time",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        shell=True,
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


def _is_image(path: Path) -> bool:
    """Check if file is an image using PIL."""
    try:
        with Image.open(path) as img:
            img.verify()  # This will raise an exception if it's not a valid image
            return True
    except (IOError, OSError):
        _logger.debug("File %s is not a valid image", path)
        return False


exclude = {
    "desktop.ini",
}


def _get_ffprobe_command() -> str:
    """Get the appropriate ffprobe command for the current platform."""
    try:
        # Try ffprobe.exe first (Windows)
        result = subprocess.run(
            ["where", "ffprobe.exe"], capture_output=True, shell=True, check=True
        )
        if result.returncode == 0:
            return "ffprobe.exe"
    except subprocess.CalledProcessError:
        pass

    try:
        # Try ffprobe (Unix/Linux/Mac)
        result = subprocess.run(
            ["which", "ffprobe"], capture_output=True, shell=True, check=True
        )
        if result.returncode == 0:
            return "ffprobe"
    except subprocess.CalledProcessError:
        pass

    # Fallback to just "ffprobe" and let it fail if not found
    return "ffprobe"


def _check_ffprobe_available() -> bool:
    """Check if ffprobe is available on the system."""
    try:
        ffprobe_cmd = _get_ffprobe_command()
        subprocess.run(
            [ffprobe_cmd, "-version"], capture_output=True, shell=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


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


def _print_progress_bar(iteration, total, prefix="", suffix="", length=50):
    """
    Call in a loop to create terminal progress bar
    """
    fill = "█"
    print_end = "\r"
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    progress_bar = fill * filled_length + "-" * (length - filled_length)
    print(f"\r{prefix} |{progress_bar}| {percent}% {suffix}", end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def _print_banner():
    """Print a nice banner for the application"""
    print("=" * 70)
    print("  📸 ORGANIZADOR DE FOTOS Y VIDEOS - PAPA TOOLKIT 📹")
    print("=" * 70)
    print()


def _print_summary(stats):
    """Print a summary of the operation"""
    print("\n" + "=" * 50)
    print("  📊 RESUMEN DEL PROCESO")
    print("=" * 50)
    print(f"  Archivos procesados: {stats['processed']}")
    print(f"  Imágenes movidas: {stats['images_moved']}")
    print(f"  Videos movidos: {stats['videos_moved']}")
    print(f"  Archivos omitidos: {stats['skipped']}")
    print(f"  Errores: {stats['errors']}")
    if stats["dry_run"]:
        print("  🔍 Modo simulación - No se movieron archivos")
    print("=" * 50)
    print()


def organize_files(
    source_folder: Path,
    destination_folder: Path,
    dry_run: bool,
    file_types: list = None,
) -> None:
    """
    Organize files by creation date into subdirectories.

    Args:
        source_folder: Source directory containing files to organize
        destination_folder: Target directory for organized files
        dry_run: If True, only simulate the operation without moving files
        file_types: List of file types to process ('image', 'video'). If None, process all supported types.
    """
    # Initialize statistics
    stats = {
        "processed": 0,
        "images_moved": 0,
        "videos_moved": 0,
        "skipped": 0,
        "errors": 0,
        "dry_run": dry_run,
    }

    # Get all files first for progress tracking
    all_files = [
        f for f in source_folder.glob("*") if f.is_file() and f.name not in exclude
    ]
    total_files = len(all_files)

    if total_files == 0:
        print("❌ No se encontraron archivos en la carpeta de origen.")
        return

    file_type_str = f" ({file_types[0]}s)" if file_types else ""
    print(f"🔍 Encontrados {total_files} archivos{file_type_str} para procesar...")
    print()

    # Create the destination folder if it doesn't exist
    if not destination_folder.exists() and not dry_run:
        destination_folder.mkdir(parents=True)
        print(f"📁 Creada carpeta de destino: {destination_folder}")

    # Process each file with progress bar
    for i, source_path in enumerate(all_files, 1):
        filename = source_path.name

        # Update progress bar
        _print_progress_bar(
            i,
            total_files,
            prefix="Procesando:",
            suffix=f"({i}/{total_files}) {filename[:30]}..."
            if len(filename) > 30
            else f"({i}/{total_files}) {filename}",
        )

        # Check file type filtering
        is_image = _is_image(source_path)
        is_video = _is_video(source_path.name)

        # Skip files that are not supported
        if not is_image and not is_video:
            stats["skipped"] += 1
            continue

        # Apply file type filter if specified
        if file_types:
            if "image" not in file_types and is_image:
                stats["skipped"] += 1
                continue
            if "video" not in file_types and is_video:
                stats["skipped"] += 1
                continue

        date_taken = None

        # 1st chance: read from metadata
        try:
            date_taken = _get_file_creation_date(source_path)
        except Exception as e:
            _logger.debug("Failed extracting metadata from %s: %s", source_path, e)

        # 2nd chance: read from filename
        if date_taken is None:
            date_taken = _get_date_from_filename(filename)

        if date_taken is None:
            stats["skipped"] += 1
            continue

        # Organize by date
        destination_subfolder = date_taken.strftime("%Y-%m-%d")
        destination_path = destination_folder / destination_subfolder

        try:
            if not destination_path.exists() and not dry_run:
                destination_path.mkdir(parents=True)

            if not dry_run:
                shutil.move(str(source_path), str(destination_path / filename))

            # Update statistics
            stats["processed"] += 1
            if is_image:
                stats["images_moved"] += 1
            else:
                stats["videos_moved"] += 1

        except Exception as e:
            stats["errors"] += 1
            _logger.error("Error procesando %s: %s", filename, e)

    # Print final summary
    _print_summary(stats)

    if stats["processed"] > 0:
        print("✅ ¡Proceso completado exitosamente!")
    else:
        print("⚠️  No se procesaron archivos.")
    print()


def main() -> None:
    # Print banner first
    _print_banner()

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
        "-t",
        "--type",
        choices=["image", "video"],
        help="Tipo de archivo a procesar (image o video). Si no se especifica, procesa ambos.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Modo simulación (sin mover ni crear carpetas)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mostrar información detallada durante el proceso",
    )
    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    source_folder = args.source_folder
    destination_folder = args.destination_folder
    dry_run = args.dry_run
    file_types = [args.type] if args.type else None

    # Check if ffprobe is available when processing videos
    if not file_types or "video" in file_types:
        if not _check_ffprobe_available():
            print("❌ Error: ffprobe no está disponible en el sistema.")
            print("   ffprobe es necesario para procesar videos.")
            print("   Instale ffmpeg para obtener ffprobe.")
            return

    # Validate source folder
    if not source_folder.exists():
        print(f"❌ Error: La carpeta de origen no existe: {source_folder}")
        return

    if not source_folder.is_dir():
        print(f"❌ Error: La ruta de origen no es una carpeta: {source_folder}")
        return

    # Print configuration
    print(f"📂 Carpeta de origen: {source_folder}")
    print(f"📁 Carpeta de destino: {destination_folder}")
    if file_types:
        print(f"🎯 Procesando solo: {file_types[0]}s")
    else:
        print("🎯 Procesando: imágenes y videos")

    if dry_run:
        print("🔍 Modo simulación activado")
    print()

    try:
        organize_files(source_folder, destination_folder, dry_run, file_types)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        if args.verbose:
            _logger.error("Error detallado: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
