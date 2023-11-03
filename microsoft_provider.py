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


def microsoft_provider(text: str, detected_gender: str = None):
    try:
        audio = generate(
            text=text,
            model="eleven_multilingual_v2"
        )
    except APIError as error:
        print("[text_to_speech] API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if error.status == "too_many_concurrent_requests":
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return microsoft_provider(text, detected_gender)
        raise text_to_speech_exception

    return audio
