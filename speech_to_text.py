import os
import tempfile
import time
from pathlib import Path

import requests
from pydub import AudioSegment
from requests.exceptions import SSLError

from config.config import ENDPOINT_WHISPER_API_URL, WHISPER_BEARER_TOKEN
from config.logger import catch_error

speech_to_text_exception = Exception(
    "Error while processing speech to text"
)

headers = {
    "Authorization": f"Bearer {WHISPER_BEARER_TOKEN}",
    "Content-Type": "audio/m4a"
}

MINIMUM_AUDIO_LENGTH_MS = 100  # 0.1 seconds in milliseconds
DELAY_TO_REPEAT_REQUEST_IN_SECONDS = 3 * 60


def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(ENDPOINT_WHISPER_API_URL, headers=headers, data=data)
    return response.json()


def speech_to_text(file_path: str, project_id: str):
    """Convert the audio content of a video or audio into text."""
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        file = Path(file_path)
        file_format = file.suffix.replace('.', '')  # Strip the dot from the suffix

        # Extract Audio from Video
        audio_segment = AudioSegment.from_file(file_path, format=file_format)
        audio_duration_in_seconds = len(audio_segment) // 1000

        # Determine the 1-minute Mark
        one_minute_in_ms = 1 * 60 * 1000

        # Initialize an Empty Transcript
        transcript_parts = []

        # Loop Through 10-minute Segments
        elapsed_time = 0  # in milliseconds

        for start_time in range(0, len(audio_segment), one_minute_in_ms):
            end_time = min(len(audio_segment), start_time + one_minute_in_ms)
            current_segment = audio_segment[start_time:end_time]

            # Check if segment length is at least 0.1 seconds - Whisper won't accept small files
            if len(current_segment) < MINIMUM_AUDIO_LENGTH_MS:
                continue

            # Use a temporary file to avoid overwriting conflicts
            with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
                current_segment.export(temp_file.name, format="wav")

                # Use OpenAI's Whisper ASR to transcribe
                output = query(temp_file.name)

                # Adjust the timestamps by adding the elapsed_time
                for chunk in output['chunks']:
                    chunk['timestamp'][0] += elapsed_time / 1000  # convert milliseconds to seconds
                    chunk['timestamp'][1] += elapsed_time / 1000  # convert milliseconds to seconds

                transcript_parts += output['chunks']

            # Update the elapsed_time
            elapsed_time += one_minute_in_ms

        # Concatenate and Return the Transcription
        return transcript_parts, audio_duration_in_seconds

    except ValueError as ve:
        catch_error(
            tag="ValueError",
            error=ve,
            project_id=project_id
        )
        raise speech_to_text_exception

    except SSLError as se:
        print("[speech_to_text] Connection Error:", str(se))

        # Wait while endpoint started
        print(f"Wait {DELAY_TO_REPEAT_REQUEST_IN_SECONDS} seconds and then repeat request to whisper endpoint...")
        time.sleep(DELAY_TO_REPEAT_REQUEST_IN_SECONDS)
        return speech_to_text(file_path, project_id)

    except Exception as e:
        # Handle generic exceptions and provide feedback
        catch_error(
            tag="speech_to_text",
            error=e,
            project_id=project_id
        )
        raise speech_to_text_exception
