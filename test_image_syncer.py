# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
# pylint: disable=unused-variable

import itertools
from datetime import datetime
from pathlib import Path
from typing import Set

import pytest

from image_syncer import organize_images


@pytest.fixture
def media_filenames() -> Set[str]:
    return set(
        (
            "2018-05-20 20.05.24.jpg",
            "2015-03-26 12.46.36.mp4",
        )
    )


@pytest.fixture
def ignore_filenames() -> Set[str]:
    return set([".ignore", "picasa.ini"])


@pytest.fixture
def source_folder(
    tmp_path: Path, media_filenames: Set[str], ignore_filenames: Set[str]
):
    folder = tmp_path / "Camera Uploads"
    folder.mkdir(parents=True, exist_ok=True)

    for name in itertools.chain(media_filenames, ignore_filenames):
        (folder / name).touch(exist_ok=True)
    return folder


def test_organize_images(
    tmp_path: Path,
    source_folder: Path,
    media_filenames: Set[str],
    ignore_filenames: Set[str],
):

    destination_folder = tmp_path / "pictures"

    organize_images(source_folder, destination_folder, dry_run=False)

    assert destination_folder.exists()

    for filename in media_filenames:
        found = list(destination_folder.rglob(f"{filename}"))
        assert len(found) == 1
        new_path = found[0]
        assert new_path
        assert datetime.strptime(new_path.parent.name, "%Y-%m-%d")

    assert set(f.name for f in source_folder.glob("*")) == ignore_filenames
