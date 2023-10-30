import time

from elevenlabs import APIError, generate, set_api_key

from config.config import LABS11_API_KEY
from config.logger import catch_error
from split_text import split_text
from split_text import MAX_SYMBOLS_NUMBER

set_api_key(LABS11_API_KEY)

VOICE_MAPPING = {
    "female": "Rachel",
    "male": "Josh"
}

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60


def text_to_speech(text: str, project_id: str, detected_gender: str = None):
    try:
        voice = VOICE_MAPPING.get(detected_gender, "Josh")  # Default to "Josh" if gender is not recognized
        translated_audio_file_name = f"translated-{project_id}.mp3"

        if len(text) > MAX_SYMBOLS_NUMBER:
            chunks = split_text(text)
            file_mode = 'bw'
            for chunk in chunks:
                create_sound(chunk, voice, translated_audio_file_name, file_mode)
                file_mode = 'ab+'
        else:
            create_sound(text, voice, translated_audio_file_name)

        return translated_audio_file_name

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception


def create_sound(text: str, voice: str, translated_audio_file_name: str, file_mode: str = 'bw'):
    try:
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        with open(translated_audio_file_name, mode=file_mode) as f:
            f.write(audio)

    except APIError as error:
        print("[text_to_speech] API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if error.status == "too_many_concurrent_requests":
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            create_sound(text, voice, translated_audio_file_name, file_mode)
        raise text_to_speech_exception