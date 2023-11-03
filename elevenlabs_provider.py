import time

from elevenlabs import APIError, generate, set_api_key, voices
from config.config import LABS11_API_KEY

set_api_key(LABS11_API_KEY)

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

VOICE_MAPPING = {
    "female": '21m00Tcm4TlvDq8ikWAM',
    "male": 'TxGEqnHWrfWFTfGW9XjX'
}

ELEVENLABS_VOICES_ID = list(map(lambda voice: voice.voice_id, voices()))


def elevenlabs_provider(text: str, voice_id: str = None, detected_gender: str = None):
    try:
        if voice_id is None or voice_id not in ELEVENLABS_VOICES_ID:
            voice_id = VOICE_MAPPING.get(detected_gender,
                                         'TxGEqnHWrfWFTfGW9XjX')  # Default to Josh_id if gender is not recognized

        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
    except APIError as error:
        print("[text_to_speech] API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if error.status == "too_many_concurrent_requests":
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return elevenlabs_provider(text, voice_id, detected_gender)
        raise text_to_speech_exception

    return audio
