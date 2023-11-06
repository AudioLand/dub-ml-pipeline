import time

from elevenlabs import APIError, generate, set_api_key, voices

from config.config import LABS11_API_KEY
from config.logger import catch_error
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

set_api_key(LABS11_API_KEY)

VOICE_MAPPING = {
    "female": "Rachel",
    "male": "Josh"
}

ELEVENLABS_VOICES_ID = list(map(lambda voice: voice.voice_id, voices()))

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60


def text_to_speech(text: str, project_id: str, voice_id: str = None, detected_gender: str = None):
    try:
        if voice_id is None or voice_id not in ELEVENLABS_VOICES_ID:
            voice_id = VOICE_MAPPING.get(detected_gender, "Josh")  # Default to "Josh" if gender is not recognized
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )

        translated_audio_file_name = f"translated-{project_id}.mp3"
        with open(translated_audio_file_name, mode='bw') as f:
            f.write(audio)

        return translated_audio_file_name

    except APIError as error:
        print("[text_to_speech] API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if error.status == "too_many_concurrent_requests":
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return text_to_speech(text, project_id, detected_gender)
        raise text_to_speech_exception

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception
