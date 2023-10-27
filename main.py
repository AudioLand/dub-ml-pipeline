# Local imports
# from integrations.youtube_utils import youtube_download
import os
from datetime import datetime

from fastapi import FastAPI

from config.logger import catch_error
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id
from integrations.firebase.google_cloud_storage import download_blob, upload_blob_and_delete_local_file
from integrations.stripe.send_usage_record import send_usage_record
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
    original_file_location: str,
    subscription_item_id: str
):
    try:
        # original_file_location for example = XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4
        source_blob_name = original_file_location

        # pipeline execution
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        # 1. Download video from cloud storage to local storage
        print('Downloading video from cloud storage...')
        destination_local_file_name = project_id + ".mp4"
        download_blob(
            source_blob_name=source_blob_name,
            destination_file_name=destination_local_file_name,
            project_id=project_id
        )
        print('Download completed.')

        local_video_path = destination_local_file_name

        # 1.1. Change project status to "translating"
        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status="translating",
            translated_file_link=""
        )

        # 2. Convert video to text
        print('start speech to text, video_path - ', local_video_path)
        text, used_minutes_count = speech_to_text(
            local_video_path,
            project_id
        )
        print("original text - ", text)

        # 3. Translate text
        print('Translating text ...')
        translated_text = translate_text(
            language=target_language,
            text=text,
            project_id=project_id
        )
        print("translated_text - ", translated_text)

        # 4. Detect gender of the voice
        # gender = voice_gender_detection(video_path)

        # 5. Generate audio from translated text
        print('Text to speech started ...')
        translated_audio_local_path = text_to_speech(
            text=translated_text,
            project_id=project_id,
            detected_gender='male',
        )
        print('Audio generation done')

        # 6. Upload audio to cloud storage
        source_file_name = translated_audio_local_path  # имя файла на локальной машине после обработки сеткой
        destination_blob_name = source_blob_name[:-4] + '-translated.mp3'  # выгружаем обратно с заменённым окончанием

        print('Uploading video from cloud storage...')
        file_public_link = upload_blob_and_delete_local_file(
            source_file_name=source_file_name,
            destination_blob_name=destination_blob_name,
            project_id=project_id
        )
        print('Upload completed, destination_blob_name - ', destination_blob_name)

        os.remove(destination_local_file_name)

        # 7. Change project status to "translated"
        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status="translated",
            translated_file_link=file_public_link
        )

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Job Done! Current Time =", current_time)

        # 8. Send usage record to Stripe
        send_usage_record(
            subscription_item_id=subscription_item_id,
            used_minutes_count=used_minutes_count,
            project_id=project_id
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
    # user_id = "UZD72svk8tVRXE5PlqxmpA36VIt1"
    # project_id = "8yFG22MbYelc0SwxELxf"
    # target_language = "Russian"
    # original_file_location = f"{user_id}/{project_id}/test-video-1min.mp4"
    # generate(project_id, target_language, original_file_location)
