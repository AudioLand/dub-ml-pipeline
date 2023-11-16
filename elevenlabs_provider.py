import time
from elevenlabs import APIError, generate, set_api_key, voices
from config.config import LABS11_API_KEY

set_api_key(LABS11_API_KEY)

VOICE_MAPPING = {
    "female": '21m00Tcm4TlvDq8ikWAM',
    "male": 'TxGEqnHWrfWFTfGW9XjX'
}

ELEVENLABS_VOICES_ID = list(map(lambda voice: voice.voice_id, voices()))


def elevenlabs_provider(text_segments: list, filename: str, language: str, pause_duration_ms: int,
                        detected_gender: str = None):
    combined_text = ''
    pause_tag = f'<break time="{pause_duration_ms}ms"/>'

    for segment in text_segments:
        combined_text += segment['text'] + pause_tag

    voice_id = VOICE_MAPPING.get(detected_gender, VOICE_MAPPING["male"])

    try:
        audio = generate(
            text=combined_text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        with open(filename, 'wb') as f:
            f.write(audio)

    except APIError as error:
        print("[text_to_speech] API Error:", str(error))
        if error.status == "too_many_concurrent_requests":
            time.sleep(5 * 60)  # 5 minutes delay
            return elevenlabs_provider(text_segments, filename, language, pause_duration_ms, detected_gender)
        raise Exception("Error while processing text to speech")


# Example usage
if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28], 'text': 'Языковые модели сегодня все еще ограничены.'},
        {'timestamp': [3.28, 5.04], 'text': 'Эта информация может быть устаревшей.'},
        {'timestamp': [5.5, 5.9], 'text': 'Ура!'},
        {'timestamp': [6.0, 15.0], 'text': 'Этот текст может содержать полезные инструкции, но чтобы действительно ...'}
    ]
    elevenlabs_provider(sample_text_segments, "translated-test.mp3", 'Russian', 1500, 'male')
