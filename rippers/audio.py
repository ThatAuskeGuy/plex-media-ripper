import subprocess
from pathlib import Path
from config import CD_DEVICE, TEMP_RIP_DIR


def rip_to_wav(device=None, output_dir=None):
    """
    Use cdparanoia to rip all tracks from an audio CD to WAV files.
    Returns the output directory path.
    """
    device = device or CD_DEVICE
    output_dir = Path(output_dir or TEMP_RIP_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Ripping audio tracks from {device}...")
    print(f"Output directory: {output_dir}")

    result = subprocess.run(
        [
            "cdparanoia",
            "--batch", # rip all tracks
            "--output-wav", # output as WAV files
            "-d", device, # specify the CD device
        ],
        cwd=output_dir, # run from the output directory so files land there
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"cdparanoia failed:\n{result.stderr}"
        )
    
    wav_files = sorted(output_dir.glob("*.wav"))

    if not wav_files:
        raise FileNotFoundError(
            "cdparanoia ran successfully but produced no WAV files. "
            "Check that the disc is an audio CD and that the drive is working."
        )
    
    print(f"Ripped {len(wav_files)} tracks.")
    return output_dir

def convert_to_flac(wav_dir):
    """
    Convert all WAV files in the given directory to FLAC format.
    Deletes the original WAV files after successful conversion.
    Returns a list of the created FLAC file paths.
    """
    wav_file = Path(wav_dir)
    wav_files = sorted(wav_dir.glob("*wav"))
    flac_files = []

    if not wav_files:
        raise FileNotFoundError(f"No WAV files found in {wav_dir}")
    
    print(f"\nConverting {len(wav_files)} WAV files to FLAC...")

    for wav in wav_files:
        flac = wav.with_suffix(".flac")

        print(f" Converting: {wav.name} -> {flac.name}")
              
        result = subprocess.run(
            [
            "ffmpeg",
            "-i", str(wav), # input file
            "-compression_level", "8", # highest FLAC compression
            str(flac), # output file
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed on {wav.name}:\n{result.stderr}"
            )
        
        wav.unlink() # delete the WAV file after successful conversion
        flac_files.append(flac)
        print(f" Done: {flac.name}")

    print(f"\nConverted {len(flac_files)} tracks to FLAC.")
    return flac_files

def rip_audio_cd(device=None, output_dir=None):
    """
    Full pipline: rip an audio CD to Flac files.
    Returns a list of FLAC file paths.
    """
    wav_dir = rip_to_wav(device, output_dir)
    flac_files = convert_to_flac(wav_dir)
    return flac_files


if __name__ == "__main__":
    # Simulate the WAV ripping step using a pre-made WAV file
    # so we can test the conversion pipeline without a disc
    import urllib.request

    test_dir = Path("/tmp/audio_test")
    test_dir.mkdir(exist_ok=True)

    # Download a small public domain WAV file for testing
    test_wav = test_dir / "track01.wav"
    if not test_wav.exists():
        print("Downloading test WAV file...")
        urllib.request.urlretrieve(
            "https://www.kozco.com/tech/piano2.wav",
            test_wav
        )

    print("Testing WAV to FLAC conversion...")
    flac_files = convert_to_flac(test_dir)
    for f in flac_files:
        print(f"Created FLAC file: {f}")