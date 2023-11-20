# Local imports
# from integrations.youtube_utils import youtube_download
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI

from config.logger import catch_error
from get_file_type_by_suffix import get_file_type_by_suffix
from nonsilent_audio_timestamps import get_nonsilent_audio_timestamps
from overlay_audio import overlay_audio_to_video
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
    voice_id: int,
    original_file_location: str,
    organization_id: str,
):
    try:
        # original_file_location for example = XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4
        source_blob_name = original_file_location

        start_time = datetime.now()
        print(f"[START] Job Started! Current Time: {start_time}")

        """Download video from cloud storage to local storage"""

        print("[START] Downloading video from cloud storage...")
        # Extract extension from the original file location
        original_file_extension = Path(original_file_location).suffix
        # Combine project_id with the extracted extension
        original_file_local_path = f"{project_id}{original_file_extension}"
        # FIXME: uncomment
        # download_blob(
        #     source_blob_name=source_blob_name,
        #     destination_file_name=original_file_local_path,
        #     project_id=project_id
        # )
        print("[DONE] Download completed.")

        """Change project status to "translating"""

        print("[START] Updating project status to 'translating'...")
        # FIXME: uncomment
        # update_project_status_and_translated_link_by_id(
        #     project_id=project_id,
        #     status="translating",
        #     translated_file_link=""
        # )
        print("[DONE] Project status updated.")

        """Detect original video pauses and get nonsilent timestamps"""

        print(f"[START] Detecting nonsilent audio timestamps from {original_file_local_path}")
        original_audio_nonsilent_timestamps = get_nonsilent_audio_timestamps(
            audio_file_path=original_file_local_path,
            min_silence_len_ms=1000
        )
        print(f"[DONE] Detecting nonsilent audio timestamps completed.")

        """Convert original video speech to text"""

        print(f"[START] Speech to text by timestamps for video - {original_file_local_path}")
        original_text_segments_with_timestamps, used_seconds_count = speech_to_text(
            original_file_path=original_file_local_path,
            nonsilent_timestamps=original_audio_nonsilent_timestamps,
            project_id=project_id,
            show_logs=True
        )
        print(f"[DONE] Speech to text completed.")

        """Translate text"""

        print("[START] Translating text ...")
        translated_text_segments = translate_text(
            language=target_language,
            original_text_segments=original_text_segments_with_timestamps,
            project_id=project_id,
            show_logs=True
        )
        print(f"[DONE] Translation completed.")

        """Detect gender of the voice"""

        # gender = voice_gender_detection(video_path)

        """Generate audio from translated text"""

        print("[START] Text to speech ...")
        translated_audio_local_path = text_to_speech(
            text_segments=translated_text_segments,
            voice_id=voice_id,
            project_id=project_id,
            show_logs=True
        )
        print(f"[DONE] Text to speech completed.")

        # From translated video
        print(f"[START] Detecting nonsilent audio timestamps from {translated_audio_local_path}")
        translated_audio_nonsilent_timestamps = get_nonsilent_audio_timestamps(
            audio_file_path=translated_audio_local_path,
            min_silence_len_ms=2000
        )
        print(f"[DONE] Detecting nonsilent audio timestamps completed.")

        processed_project_is_video = get_file_type_by_suffix(original_file_local_path) == "video"
        if processed_project_is_video:
            print("[START] Overlay audio to video ...")
            # Overlay audio on video
            final_file_path = overlay_audio_to_video(
                original_video_path=original_file_local_path,
                translated_audio_path=translated_audio_local_path,
                original_text_segments_with_timestamps=original_text_segments_with_timestamps,
                translated_nonsilent_timestamps=translated_audio_nonsilent_timestamps,
                project_id=project_id,
                silent_original_audio=False,
                show_logs=True
            )
            print(f"[DONE] Overlay audio completed.")
        else:
            # TODO: create overlay for audio too.
            final_file_path = translated_audio_local_path

        """Upload audio to cloud storage"""

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
        destination_blob_name = f"{original_path}/{original_filename_without_extension}-translated{original_file_extension}"

        print("[START] Uploading translated file to cloud storage ...")
        # FIXME: uncomment
        # file_public_link = upload_blob(
        #     source_file_name=source_file_name,
        #     destination_blob_name=destination_blob_name,
        #     project_id=project_id
        # )
        print(f"[DONE] File uploaded to cloud storage, destination_blob_name - {destination_blob_name}")

        """Remove all processed files"""

        # Remove original file
        # FIXME: uncomment
        # os.remove(local_file_path)
        # Remove translated file
        # os.remove(final_file_path)
        # Remove
        # if processed_project_is_video:
        #     os.remove(translated_audio_local_path)

        """Change project status to "translated"""

        print("[START] Updating project status to 'translated'...")
        # FIXME: uncomment
        # update_project_status_and_translated_link_by_id(
        #     project_id=project_id,
        #     status="translated",
        #     translated_file_link=file_public_link
        # )
        print("[DONE] Project status updated.")

        """Update user tokens"""

        print("[START] Updating user used tokens...")
        # FIXME: uncomment
        # update_user_tokens(
        #     organization_id=organization_id,
        #     tokens_in_seconds=used_seconds_count,
        #     project_id=project_id,
        # )
        print("[START] User used tokens updated.")

        end_time = datetime.now()
        print(f"[DONE] Job Done! Current Time: {end_time}")
        time_difference = end_time - start_time
        print(f"[DONE] Projects translation time {time_difference}")

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
    user_id = "z8Z5j71WbmhaioUHDHh5KrBqEO13"
    project_id = "07fsfECkwma6fVTDyqQf"
    target_language = "English"
    voice_id = 147
    original_file_location = f"{user_id}/{project_id}/test-video-1min.mp4"
    organization_id = "ZXIFYVhPAMql66Vg5f5Q"
    generate(
        project_id=project_id,
        target_language=target_language,
        voice_id=voice_id,
        original_file_location=original_file_location,
        organization_id=organization_id
    )
