import os
import tempfile

import openai
from pydub import AudioSegment

from config.config import OPEN_AI_API_KEY
from config.logger import catch_error
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

speech_to_text_exception = Exception(
    "Error while processing speech to text"
)


def speech_to_text(video_path: str, project_id: str):
    """Convert the audio content of a video into text."""
    try:
        # Check if the file exists
        if not os.path.exists(video_path):
            raise ValueError(f"File not found: {video_path}")

        # Get file extension for format
        file_format = os.path.splitext(video_path)[-1].replace(".", "")

        # Extract Audio from Video
        audio_content = AudioSegment.from_file(video_path, format=file_format)
        audio_duration_in_minutes = len(audio_content) // 1000 // 60

        # Determine the 1-minute Mark
        ten_minutes_in_ms = 1 * 60 * 1000

        # Initialize an Empty Transcript
        transcript_parts = []

        # Loop Through 10-minute Segments
        for start_time in range(0, len(audio_content), ten_minutes_in_ms):
            end_time = min(len(audio_content), start_time + ten_minutes_in_ms)
            audio_segment = audio_content[start_time:end_time]

            # Use a temporary file to avoid overwriting conflicts
            with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
                audio_segment.export(temp_file.name, format="wav")

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
