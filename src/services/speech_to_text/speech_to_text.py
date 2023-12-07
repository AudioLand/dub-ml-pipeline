import os
from typing import List, Tuple

from pydub import AudioSegment

from constants.files import PROCESSING_FILES_DIR_PATH
from models.text_segment import TextSegment

import whisper

import os

MINIMUM_AUDIO_LENGTH_MS = 100  # 0.1 seconds in milliseconds

file_not_found_exception = Exception("Error file not found while processing audio timestamps")


def speech_to_text(file_path: str, project_id: str, show_logs: bool = False) -> Tuple[List[TextSegment], int]:
    """
        Get timestamps of phrases from audio file.

        Arguments:
          file_path (str): - path to your audio or video file

        Return:
          list: audio segments with text and start and end timestamps
        """

    if not os.path.exists(file_path):
        raise file_not_found_exception

    model = whisper.load_model("base")
    audio = whisper.load_audio(file_path)
    result = model.transcribe(audio)
    segments = result["segments"]
    processed_segments = list(
        map(lambda el: TextSegment(original_timestamp=(el['start'], el['end']), text=el['text']), segments))

    audio_segment = AudioSegment.from_file(file_path)
    audio_len_in_seconds = len(audio_segment) // 1000

    return processed_segments, audio_len_in_seconds


if __name__ == "__main__":
    test_project_id = "07fsfECkwma6fVTDyqQf"
    test_file_path = f"{PROCESSING_FILES_DIR_PATH}/{test_project_id}.mp4"
    test_transcript_parts, test_used_tokens_in_seconds = speech_to_text(
        file_path=test_file_path,
        project_id=test_project_id,
        show_logs=True
    )
    print(test_transcript_parts)
    print(test_used_tokens_in_seconds)
