import time

from elevenlabs import APIError, generate as generate_audio, set_api_key, RateLimitError

from config.config import ELEVEN_LABS_API_KEY

set_api_key(ELEVEN_LABS_API_KEY)

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60


def generate_audio_with_elevenlabs_provider(
    output_audio_file_path: str,
    text_segments: list[dict],
    original_voice_id: str,
    pause_duration_ms: int,
):
    pause_tag = f" <break time=\"{pause_duration_ms / 1000}s\"/> "
    combined_text = ""

    for segment in text_segments:
        combined_text += segment['text'] + pause_tag

    try:
        audio = generate_audio(
            text=combined_text,
            voice=original_voice_id,
            model="eleven_multilingual_v2"
        )
        with open(output_audio_file_path, 'wb') as f:
            f.write(audio)

    except APIError as error:
        print("(elevenlabs_provider) API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if isinstance(error, RateLimitError):
            print(f"(elevenlabs_provider) Wait {DELAY_TO_WAIT_IN_SECONDS} seconds and then repeat request to 11labs...")
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return generate_audio_with_elevenlabs_provider(
                output_audio_file_path,
                text_segments,
                original_voice_id,
                pause_duration_ms,
            )
        raise text_to_speech_exception


# Example usage
if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28], 'text': 'Языковые модели сегодня все еще ограничены.'},
        {'timestamp': [3.28, 5.04], 'text': 'Эта информация может быть устаревшей.'},
        {'timestamp': [5.5, 5.9], 'text': 'Ура!'},
        {'timestamp': [6.0, 15.0], 'text': 'Этот текст может содержать полезные инструкции, но чтобы действительно ...'}
    ]
    output_audio_file_path = "translated-test.mp3"
    original_voice_id = "N2lVS1w4EtoT3dr4eOWO"
    generate_audio_with_elevenlabs_provider(
        output_audio_file_path=output_audio_file_path,
        text_segments=sample_text_segments,
        original_voice_id=original_voice_id,
        pause_duration_ms=3000,
    )
