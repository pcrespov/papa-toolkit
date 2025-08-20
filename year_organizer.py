#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
This script organizes date-based folders by year.
Given a target folder, it looks for all folders starting with "YYYY-MM-DD" format
and moves them into year-based folders (YYYY).
"""

import argparse
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
_logger = logging.getLogger(__name__)

# Regex pattern for YYYY-MM-DD format
_DATE_FOLDER_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:.*)?$")


def _validate_date_folder(folder_name: str) -> tuple[bool, str | None, str | None]:
    """
    Validate if folder name starts with valid YYYY-MM-DD format.

    Returns:
        tuple: (is_valid, year, error_message)
    """
    match = _DATE_FOLDER_RE.match(folder_name)
    if not match:
        return False, None, "Does not match YYYY-MM-DD format"

    year, month, day = match.groups()

    try:
        # Validate the date is actually valid
        datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        return True, year, None
    except ValueError as e:
        return False, None, f"Invalid date: {str(e)}"


def _print_progress_bar(iteration, total, prefix="", suffix="", length=50):
    """Create terminal progress bar"""
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
    print("  📅 ORGANIZADOR DE CARPETAS POR AÑO - PAPA TOOLKIT 📁")
    print("=" * 70)
    print()


def _print_summary(stats):
    """Print a summary of the operation"""
    print("\n" + "=" * 50)
    print("  📊 RESUMEN DEL PROCESO")
    print("=" * 50)
    print(f"  Carpetas procesadas: {stats['processed']}")
    print(f"  Carpetas movidas: {stats['moved']}")
    print(f"  Carpetas inválidas: {stats['invalid']}")
    print(f"  Errores: {stats['errors']}")
    if stats["dry_run"]:
        print("  🔍 Modo simulación - No se movieron carpetas")
    print("=" * 50)

    # Print year summary
    if stats["years"]:
        print("\n  📅 CARPETAS POR AÑO:")
        for year in sorted(stats["years"].keys()):
            count = stats["years"][year]
            print(f"    {year}: {count} carpeta(s)")
    print()


def organize_folders_by_year(target_folder: Path, dry_run: bool) -> None:
    """
    Organize date-based folders by year.

    Args:
        target_folder: Directory containing folders to organize
        dry_run: If True, only simulate the operation without moving folders
    """
    # Initialize statistics
    stats = {
        "processed": 0,
        "moved": 0,
        "invalid": 0,
        "errors": 0,
        "dry_run": dry_run,
        "years": {},
    }

    # Get all subdirectories
    all_folders = [f for f in target_folder.iterdir() if f.is_dir()]

    if not all_folders:
        print("❌ No se encontraron carpetas en el directorio de destino.")
        return

    # Filter folders that might be date-based
    date_folders = []
    for folder in all_folders:
        is_valid, year, error = _validate_date_folder(folder.name)
        if is_valid:
            date_folders.append((folder, year))
        elif _DATE_FOLDER_RE.match(folder.name):  # Matches pattern but invalid date
            stats["invalid"] += 1
            _logger.warning("Carpeta inválida '%s': %s", folder.name, error)

    total_folders = len(date_folders)

    if total_folders == 0:
        print("❌ No se encontraron carpetas con formato YYYY-MM-DD válido.")
        if stats["invalid"] > 0:
            print(
                f"⚠️  Se encontraron {stats['invalid']} carpetas con formato incorrecto."
            )
        return

    print(f"🔍 Encontradas {total_folders} carpetas con formato YYYY-MM-DD...")
    if stats["invalid"] > 0:
        print(f"⚠️  Se ignoraron {stats['invalid']} carpetas con fechas inválidas.")
    print()

    # Process each folder with progress bar
    for i, (folder_path, year) in enumerate(date_folders, 1):
        folder_name = folder_path.name

        # Update progress bar
        _print_progress_bar(
            i,
            total_folders,
            prefix="Organizando:",
            suffix=f"({i}/{total_folders}) {folder_name[:30]}..."
            if len(folder_name) > 30
            else f"({i}/{total_folders}) {folder_name}",
        )

        # Create year folder path
        year_folder = target_folder / year
        destination_path = year_folder / folder_name

        try:
            # Create year folder if it doesn't exist
            if not year_folder.exists() and not dry_run:
                year_folder.mkdir(parents=True)
                _logger.debug("Creada carpeta de año: %s", year_folder)

            # Check if destination already exists
            if destination_path.exists():
                _logger.warning("La carpeta de destino ya existe: %s", destination_path)
                if not dry_run:
                    # Try to merge by adding a suffix
                    counter = 1
                    while destination_path.exists():
                        new_name = f"{folder_name}_{counter:02d}"
                        destination_path = year_folder / new_name
                        counter += 1
                    _logger.info("Renombrando a: %s", destination_path.name)

            # Move the folder
            if not dry_run:
                shutil.move(str(folder_path), str(destination_path))

            # Update statistics
            stats["processed"] += 1
            stats["moved"] += 1
            stats["years"][year] = stats["years"].get(year, 0) + 1

            _logger.debug("Movida carpeta %s -> %s", folder_name, destination_path)

        except (OSError, shutil.Error, PermissionError) as e:
            stats["errors"] += 1
            _logger.error("Error moviendo carpeta '%s': %s", folder_name, e)

    # Print final summary
    _print_summary(stats)

    if stats["moved"] > 0:
        print("✅ ¡Proceso completado exitosamente!")
    else:
        print("⚠️  No se movieron carpetas.")
    print()


def main() -> None:
    # Print banner first
    _print_banner()

    parser = argparse.ArgumentParser(
        description="Organiza carpetas con formato YYYY-MM-DD agrupándolas por año."
    )
    parser.add_argument(
        "target_folder",
        type=Path,
        help="Carpeta que contiene las carpetas a organizar",
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

    target_folder = args.target_folder
    dry_run = args.dry_run

    # Validate target folder
    if not target_folder.exists():
        print(f"❌ Error: La carpeta de destino no existe: {target_folder}")
        return

    if not target_folder.is_dir():
        print(f"❌ Error: La ruta no es una carpeta: {target_folder}")
        return

    # Print configuration
    print(f"📂 Carpeta de destino: {target_folder}")
    if dry_run:
        print("🔍 Modo simulación activado")
    print()

    try:
        organize_folders_by_year(target_folder, dry_run)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario.")
    except (OSError, PermissionError) as e:
        print(f"\n❌ Error inesperado: {e}")
        if args.verbose:
            _logger.error("Error detallado: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
