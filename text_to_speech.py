import os

from elevenlabs import generate, set_api_key

from config.config import LABS11_API_KEY
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

set_api_key(LABS11_API_KEY)

VOICE_MAPPING = {
    "female": "Rachel",
    "male": "Josh"
}

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)


def text_to_speech(text: str, detected_gender: str, project_id: str):
    try:
        voice = VOICE_MAPPING.get(detected_gender, "Josh")  # Default to "Josh" if gender is not recognized
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        with open('new_audio.mp3', mode='bw') as f:
            f.write(audio)

        return 'new_audio.mp3'

    except Exception as e:
        print(f"[text_to_speech] ERROR: {str(e)}")
        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status="translationError",
            translated_file_link=""
        )
        raise text_to_speech_exception
