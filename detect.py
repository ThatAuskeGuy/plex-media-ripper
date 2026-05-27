import os
import subprocess
from config import CD_DEVICE


def get_drive(device=None):
    """ Return the CD/DVD device path, checking it actually exists """
    path = device or CD_DEVICE
    if not os.path.exists(path):
        raise FileNotFoundError(f"No disc drive found at {path}. "
                                f"Check your CD_DEVICE value in .env"
                                )
    return path

def _run_cd_info(device):
    """
    Run cd-info and return its output as a string.
    Raises RuntimeError if the command fails.
    """
    result = subprocess.run(
        ["cd-info", "--no-headed". device],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cd-info failed: {result.stderr.strip()}"
        )
    return result.stdout

def detect_disc_type(device=None):
    """ 
    Inspect the disc and return one of:
    'audio_cd', 'data_cd', 'vcd', 'dvd', 'empty'
    """
    device = get_drive(device)

    try:
        info = _run_cd_info(device)
    except RuntimeError:
        return "empty"

    if "CD-DA" in info:
        return "audio_cd"
    elif "DVD" in info:
        return "dvd"
    elif "VCD" in info or "VIDEO_CD" in info:
        return "vcd"
    else:
        return "data_cd"

def get_disc_label(device=None):
    """Return the disc's volume label (e.g. 'MY_MOVIE_2004')."""
    device = get_drive(device)
    result = subprocess.run(
        ["blkid", "-s", "LABEL", "-o", "value", device],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "UNKNOWN_DISC"
    

if __name__ == "__main__":
    # EXAMPLE USAGE
    device = get_drive()
    print(f"Drive: {device}")
    print(f"Disc type: {detect_disc_type()}")
    print(f"Disc label: {get_disc_label()}")