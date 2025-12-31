"""
Cross-platform sound player for Windows and Raspberry Pi.
Supports MP3, WAV, OGG, FLAC (requires ffmpeg installed).
"""

##pip install pydub simpleaudio
##
##Also install ffmpeg (needed for MP3, OGG, FLAC):
##
##Windows: Download from https://ffmpeg.org/download.html and add to PATH.
##Raspberry Pi:
##Bash
##
##Copia codice
##sudo apt update
##sudo apt install ffmpeg

import os
import sys
from pydub import AudioSegment
from pydub.playback import play

def play_sound(file_path: str):
    """Play an audio file in a cross-platform way."""
    try:
        # Validate file existence
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect format from extension
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        if ext not in ["mp3", "wav", "ogg", "flac"]:
            raise ValueError(f"Unsupported format: {ext}")

        # Load and play
        audio = AudioSegment.from_file(file_path, format=ext)
        play(audio)

    except FileNotFoundError as fnf:
        print(f"[ERROR] {fnf}")
    except ValueError as ve:
        print(f"[ERROR] {ve}")
    except Exception as e:
        print(f"[ERROR] Could not play sound: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <audio_file>")
        sys.exit(1)

    play_sound(sys.argv[1])
