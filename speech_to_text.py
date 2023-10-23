import os
import tempfile
from pydub import AudioSegment
import openai


def speech_to_text(video_path):
    """Convert the audio content of a video into text."""
    # openai.api_key = "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"  # Audioland acc key - not working
    openai.api_key = "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"  # slava's key
    try:
        # Check if the file exists
        if not os.path.exists(video_path):
            raise ValueError(f"File not found: {video_path}")

        # Get file extension for format
        file_format = os.path.splitext(video_path)[-1].replace(".", "")

        # Extract Audio from Video
        audio_content = AudioSegment.from_file(video_path, format=file_format)

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
        return ' '.join(transcript_parts)

    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
        return None
    except Exception as e:
        # Handle generic exceptions and provide feedback
        print(f"An error occurred: {str(e)}")
        return None
