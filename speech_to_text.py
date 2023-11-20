import os
import time
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from pydub import AudioSegment
from requests.exceptions import SSLError

from config.config import ENDPOINT_WHISPER_API_URL, WHISPER_BEARER_TOKEN
from config.logger import catch_error

speech_to_text_exception = Exception(
    "Error while processing speech to text"
)

whisper_endpoint_exception = Exception(
    "Error while sending request to Whisper endpoint"
)

headers = {
    "Authorization": f"Bearer {WHISPER_BEARER_TOKEN}",
    "Content-Type": "audio/m4a"
}

MINIMUM_AUDIO_LENGTH_MS = 100  # 0.1 seconds in milliseconds
DELAY_TO_REPEAT_REQUEST_IN_SECONDS = 3 * 60


def send_request_to_whisper_endpoint(temp_file_name: str):
    with open(temp_file_name, "rb") as f:
        data = f.read()

    print("(whisper_endpoint_query) Sending request to Whisper endpoint...")
    request_time = datetime.now()
    response = requests.post(ENDPOINT_WHISPER_API_URL, headers=headers, data=data)
    response_time = datetime.now()

    time_difference = response_time - request_time
    print(f"(whisper_endpoint_response) Response time is {time_difference}")

    if not response.ok:
        print(f"(whisper_endpoint_response) Status code: {response.status_code}")
        print(f"(whisper_endpoint_response) Details: {response.json()}")

        if response.status_code == 502:
            # Wait while endpoint started
            print(f"(whisper_endpoint_query) Wait {DELAY_TO_REPEAT_REQUEST_IN_SECONDS} seconds to repeat...")
            time.sleep(DELAY_TO_REPEAT_REQUEST_IN_SECONDS)
            print(f"(whisper_endpoint_query) Trying to send request to Whisper endpoint again...")
            return send_request_to_whisper_endpoint(temp_file_name)
        raise whisper_endpoint_exception

    print(f"(whisper_endpoint_response) Sending request completed.")
    return response.json()


def speech_to_text(
    original_file_path: str,
    nonsilent_timestamps: list[list[int, int]],
    project_id: str,
    show_logs: bool = False
) -> tuple[list[dict], float]:
    """Convert the audio content of a video or audio into text."""
    try:
        # Check if the file exists
        if not os.path.exists(original_file_path):
            raise ValueError(f"File not found: {original_file_path}")

        file = Path(original_file_path)
        file_format = file.suffix.replace('.', '')  # Strip the dot from the suffix

        # Extract Audio from Video
        original_audio = AudioSegment.from_file(original_file_path, format=file_format)
        audio_duration_in_seconds = original_audio.duration_seconds

        if show_logs:
            start, end = nonsilent_timestamps
            print(f"(speech_to_text) Processing audio segments by timestamps - {start}ms, {end}ms")

        # Get nonsilent audio segments by timestamps
        original_audio_transcripts = []
        for video_start_time, video_end_time in nonsilent_timestamps:
            if show_logs:
                print(f"\n(speech_to_text) Processing audio segment - {video_start_time}, {video_end_time}")

            audio_segment = original_audio[video_start_time:video_end_time]

            # Use a temporary file to avoid overwriting conflicts
            with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
                audio_segment.export(temp_file.name, format="wav")

                # Use OpenAI's Whisper ASR to transcribe
                json_response = send_request_to_whisper_endpoint(temp_file.name)

                text = json_response['text']

                if show_logs:
                    print(f"(speech_to_text) Transcribed text - {text}")

                transcribed_part = {
                    "original_timestamps": (video_start_time, video_end_time),
                    "text": text
                }
                original_audio_transcripts.append(transcribed_part)

        return original_audio_transcripts, audio_duration_in_seconds

        # # Determine the 1-minute Mark
        # one_minute_in_ms = 1 * 60 * 1000
        #
        # # Initialize an Empty Transcript
        # transcript_parts = []
        #
        # # Loop Through 10-minute Segments
        # elapsed_time = 0  # in milliseconds
        #
        # for start_time in range(0, len(audio_segment), one_minute_in_ms):
        #     end_time = min(len(audio_segment), start_time + one_minute_in_ms)
        #     current_segment = audio_segment[start_time:end_time]
        #
        #     # Check if segment length is at least 0.1 seconds - Whisper won't accept small files
        #     if len(current_segment) < MINIMUM_AUDIO_LENGTH_MS:
        #         continue
        #
        #     # Use a temporary file to avoid overwriting conflicts
        #     with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
        #         current_segment.export(temp_file.name, format="wav")
        #
        #         # Use OpenAI's Whisper ASR to transcribe
        #         json_response = send_request_to_whisper_endpoint(temp_file.name)
        #
        #         # Adjust the timestamps by adding the elapsed_time
        #         for chunk in json_response['chunks']:
        #             chunk['timestamp'][0] += elapsed_time / 1000  # convert milliseconds to seconds
        #             chunk['timestamp'][1] += elapsed_time / 1000  # convert milliseconds to seconds
        #
        #         transcript_parts += json_response['chunks']
        #
        #     # Update the elapsed_time
        #     elapsed_time += one_minute_in_ms
        #
        # # Concatenate and Return the Transcription
        # return transcript_parts, audio_duration_in_seconds

    except ValueError as ve:
        catch_error(
            tag="ValueError",
            error=ve,
            project_id=project_id
        )
        raise speech_to_text_exception

    except SSLError as se:
        print(f"(speech_to_text) Connection SSLError: {str(se)}")
        # Wait while endpoint started
        print(f"(speech_to_text) Wait {DELAY_TO_REPEAT_REQUEST_IN_SECONDS} seconds to repeat...")
        time.sleep(DELAY_TO_REPEAT_REQUEST_IN_SECONDS)
        print(f"(speech_to_text) Trying to send request to Whisper endpoint again...")
        return speech_to_text(original_file_path, project_id)

    except Exception as e:
        # Handle generic exceptions and provide feedback
        catch_error(
            tag="speech_to_text",
            error=e,
            project_id=project_id
        )
        raise speech_to_text_exception


if __name__ == "__main__":
    original_file_path = "07fsfECkwma6fVTDyqQf.mp4"
    sample_nonsilent_audio_timestamps = [
        [0, 959], [1156, 2656], [3379, 4686], [4868, 6667], [7137, 8161], [8526, 10176], [10314, 10844], [11329, 11605],
        [11753, 12289], [12516, 18409], [18707, 19862], [20219, 20852], [21400, 21800], [21952, 22685], [23332, 25872],
        [26078, 28440], [28722, 29663], [30183, 31453], [31741, 32804], [32920, 34074], [34787, 41637], [42425, 44105],
        [44315, 46013], [46437, 48854], [49252, 49530], [49911, 51078], [51428, 55109], [55491, 56752]
    ]
    project_id = "07fsfECkwma6fVTDyqQf"
    transcript_parts, audio_duration_in_seconds = speech_to_text(
        original_file_path=original_file_path,
        nonsilent_timestamps=sample_nonsilent_audio_timestamps,
        project_id=project_id,
        show_logs=True
    )
    print(transcript_parts)
    print(audio_duration_in_seconds)
