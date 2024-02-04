# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable
# pylint: disable=too-many-arguments

from typing import Set
from image_syncer import organize_images
from pathlib import Path
from datetime import datetime

import pytest


@pytest.fixture
def media_filenames() -> Set[str]:
    return set(("2018-05-20 20.05.24.jpg","2015-03-26 12.46.36.mp4",))



@pytest.fixture
def source_filenames(media_filenames: Set[str]) -> Set[str]:
    return set([
     ".ignore",
     "picasa.ini"
    ]).union(media_filenames)


@pytest.fixture
def source_folder(tmp_path: Path, source_filenames: Set[str]):
    folder = tmp_path / "Camera Uploads"
    folder.mkdir(parents=True, exist_ok=True)
    for name in source_filenames:
        (folder / name).touch(exist_ok=True)
    return folder


def test_organize_images(tmp_path: Path, source_folder: Path, media_filenames: Set[str] ):

    destination_folder = tmp_path / "pictures"

    organize_images(source_folder, destination_folder, dry_run=False)

    assert destination_folder.exists()

    for filename in media_filenames:
        new_path = destination_folder.rglob(f"{filename}")
        assert new_path
        assert datetime.strptime(new_path.parent.name, "%Y-%m-%d")