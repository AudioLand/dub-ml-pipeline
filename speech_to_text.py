import os
import tempfile

import openai
from pydub import AudioSegment
from pathlib import Path

from config.config import OPEN_AI_API_KEY
from config.logger import catch_error
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

speech_to_text_exception = Exception(
    "Error while processing speech to text"
)

MINIMUM_AUDIO_LENGTH_MS = 100  # 0.1 seconds in milliseconds

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
        audio_duration_in_minutes = len(audio_segment) // 1000 // 60

        # Determine the 1-minute Mark
        one_minute_in_ms = 1 * 60 * 1000

        # Initialize an Empty Transcript
        transcript_parts = []

        # Loop Through 10-minute Segments
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
                with open(temp_file.name, "rb") as audio_file:
                    transcript_parts.append(openai.Audio.translate("whisper-1", audio_file)['text'])

        # Concatenate and Return the Transcription
        return ' '.join(transcript_parts), audio_duration_in_minutes

    except ValueError as ve:
        catch_error(
            tag="ValueError",
            error=ve,
            project_id=project_id
        )
        raise speech_to_text_exception

    except Exception as e:
        # Handle generic exceptions and provide feedback
        catch_error(
            tag="speech_to_text",
            error=e,
            project_id=project_id
        )
        raise speech_to_text_exception
