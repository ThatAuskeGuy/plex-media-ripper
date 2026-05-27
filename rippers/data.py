import shutil
import os
from pathlib import Path
from config import PLEX_MEDIA_ROOT


def find_mount_point(disc_label):
    """
    Try to locate where Linux mounted the disc.
    Checks common mount locations in order.
    """
    username = os.getenv("USER") or os.getenv("LOGNAME")

    candidates = [
        Path(f"/media/{username}/{disc_label}"),
        Path(f"/media/{disc_label}"),
        Path("/mnt/cdrom"),
        Path("mnt/disc"),
    ]

    for path in candidates:
        if path.exists() and path.is_dir():
            return path
        
    raise FileNotFoundError(
        "Could not find disc mounted at any known location.\n"
        "Try mounting the disc manually with:\n"
        "sudo mount /dev/sr0 /mnt/cdrom"
    )

def copy_data_disc(disc_label, destination=None, source=None):
    """
    Copy all files from a mounted data disc into Plex staging.
    Returns the destination path.
    """
    source = Path(source) if source else find_mount_point(disc_label)

    # Build destination path
    dest = Path(destination) if destination else Path(PLEX_MEDIA_ROOT) / "staging" / disc_label
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Copying from: {source}")
    print(f"Copying to: {dest}")

    copied = 0
    skipped = 0

    for item in source.rglob("*"):
        if item.is_file():
            # Recreate the same folder structure at the destination
            relative = item.relative_to(source)
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                print(f" Skipping (already exists): {relative}")
                skipped += 1
            else:
                shutil.copy2(item, target)
                print(f" Copied: {relative}")
                copied += 1

    print(f"\nDone. {copied} files copied, {skipped} files skipped.")
    return dest


if __name__ == "__main__":
    test_source = Path("/tmp/fake_disc")
    test_source.mkdir(parents=True, exist_ok=True)
    (test_source / "docs").mkdir(exist_ok=True)
    (test_source / "data").mkdir(exist_ok=True)
    (test_source / "docs" / "readme.txt").write_text("hello")
    (test_source / "data" / "file1.txt").write_text("world")

    result = copy_data_disc(
        "MY_TEST_DISC",
        destination="/tmp/plex_test/MY_TEST_DISC",
        source=test_source
    )
    print(f"\nResult path: {result}")