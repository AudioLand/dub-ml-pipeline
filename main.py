# Local imports
# from integrations.youtube_utils import youtube_download

import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI

from config.logger import catch_error
from get_file_type_by_suffix import get_file_type_by_suffix
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id
from integrations.firebase.firestore_update_user_tokens import update_user_tokens
from integrations.firebase.google_cloud_storage import download_blob, upload_blob_and_delete_local_file
from overlay_audio import overlay_audio
from speech_to_text import speech_to_text
# from gender_detection import voice_gender_detection
from text_to_speech import text_to_speech
from translation import translate_text

app = FastAPI()


# youtube_link = "https://youtu.be/WDv4AWk0J3U?si=wL3cKW1PCvinxBDy"
# video_path = 'test-video-1min.mp4'

# source_blob_name = 'XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4'

# useId, projectId,

# https://audioland.fly.dev/?original_file_location=XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4


@app.get("/")
def generate(
    project_id: str,
    target_language: str,
    voice_id: str,
    original_file_location: str,
    organization_id: str,
):
    try:
        # original_file_location for example = XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4
        source_blob_name = original_file_location

        # pipeline execution
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        """1. Download video from cloud storage to local storage"""

        print('Downloading video from cloud storage...')

        # Extract extension from the original file location
        original_file_extension = Path(original_file_location).suffix
        # Combine project_id with the extracted extension
        destination_local_file_name = f"{project_id}{original_file_extension}"
        # download_blob(
        #     source_blob_name=source_blob_name,
        #     destination_file_name=destination_local_file_name,
        #     project_id=project_id
        # )
        print('Download completed.')

        local_file_path = '/Users/lizashcherbakova/work/notion/files/en_short_2_speakers.mp4'

        """1.1. Change project status to "translating"""
        #
        # update_project_status_and_translated_link_by_id(
        #     project_id=project_id,
        #     status="translating",
        #     translated_file_link=""
        # )

        """2. Convert video to text"""

        print('start speech to text, video_path - ', local_file_path)
        text, used_seconds_count = speech_to_text(
            local_file_path,
            project_id
        )
        print("original text - ", text)

        """3. Translate text"""

        print('Translating text ...')
        translate_text(
            language=target_language,
            text_segments=text,
            project_id=project_id
        )
        print("translated_text - ", text)

        """4. Detect gender of the voice"""

        # gender = voice_gender_detection(video_path)

        """5. Generate audio from translated text"""

        print('Text to speech started ...')

        # translated_audio_local_path {project_id}_audio_translated.mp3 - in mp3
        translated_audio_local_path = text_to_speech(
            text_segments=text,
            project_id=project_id,
            voice_id=voice_id,
            detected_gender='male',
        )
        print('Audio generation done')

        if get_file_type_by_suffix(local_file_path) == 'video':
            # Overlay audio on video
            source_file_name = overlay_audio(local_file_path, translated_audio_local_path, text)
        else:
            # TODO: create overlay for audio too.
            source_file_name = translated_audio_local_path

        return
        """6. Upload audio to cloud storage"""

        """
        Example
        original_file_location = XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4
        original_path = XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/
        original_filename_without_extension = test-video-1min
        original_file_extension = .mp4
        """

        # Extract the path and filename from the original_file_location
        original_path = Path(original_file_location).parent
        original_filename_without_extension = Path(original_file_location).stem
        original_file_extension = Path(original_file_location).suffix

        # Create the destination blob name with "_translated" appended to the filename
        destination_blob_name = f"{original_path}/{original_filename_without_extension}_translated{original_file_extension}"

        print('Uploading video from cloud storage...')
        file_public_link = upload_blob_and_delete_local_file(
            source_file_name=source_file_name,
            destination_blob_name=destination_blob_name,
            project_id=project_id
        )
        print('Upload completed, destination_blob_name - ', destination_blob_name)

        os.remove(destination_local_file_name)

        """7. Change project status to "translated"""

        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status="translated",
            translated_file_link=file_public_link
        )

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Job Done! Current Time =", current_time)

        update_user_tokens(
            organization_id=organization_id,
            tokens_in_seconds=used_seconds_count,
            project_id=project_id,
        )

        return {"status": "it is working!!!"}

    except Exception as e:
        catch_error(
            tag="main",
            error=e,
            project_id=project_id
        )


@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("main started")
    user_id = "UZD72svk8tVRXE5PlqxmpA36VIt1"
    project_id = "8yFG22MbYelc0SwxELxf"
    target_language = "Russian"
    voice_id = "TxGEqnHWrfWFTfGW9XjX" # Josh_id
    original_file_location = f"{user_id}/{project_id}/test-video-1min.mp4"
    generate(project_id, target_language, voice_id, original_file_location, '')
