import time

from elevenlabs import generate, set_api_key
from elevenlabs import APIError, generate, set_api_key
from moviepy.audio.io.AudioFileClip import AudioFileClip

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


def text_to_speech(text_segments: list, project_id: str, detected_gender: str = None):
    try:
        voice = VOICE_MAPPING.get(detected_gender, "Josh")  # Default to "Josh" if gender is not recognized
        translated_audio_file_name = f"translated-{project_id}.mp3"

        open(translated_audio_file_name, mode='w').close()
        prev_moment = 0.0

        for segment in text_segments:
            # Recording start moment in the audio for the segment.
            segment['audio_timestamp'] = [prev_moment]
            text = segment['text']

            if len(text) > MAX_SYMBOLS_NUMBER:
                chunks = split_text(text)
                for chunk in chunks:
                    create_sound(chunk, voice, translated_audio_file_name)
            else:
                create_sound(text, voice, translated_audio_file_name)

            # Recording end moment in the audio for the segment.
            prev_moment = AudioFileClip(str(translated_audio_file_name)).duration
            segment['audio_timestamp'].append(prev_moment)

        return translated_audio_file_name

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception


def create_sound(text: str, voice: str, translated_audio_file_name: str):
    try:
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        with open(translated_audio_file_name, 'ab+') as f:
            f.write(audio)

    except APIError as error:
        print("[text_to_speech] API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if error.status == "too_many_concurrent_requests":
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            create_sound(text, voice, translated_audio_file_name)
        raise text_to_speech_exception

if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28], 'text': 'Language models today, while useful for a variety of tasks, are still limited. The only information they can learn from is their training data.'},
        {'timestamp': [3.28, 5.04], 'text': 'This information can be out-of-date and is one-size fits all across applications. Furthermore, the only thing language models can do out-of-the-box is emit text.'},
        {'timestamp': [6.0, 15.0], 'text': 'This text can contain useful instructions, but to actually follow these instructions you need another process.'}
    ]

    project_id_sample = "sample_project_id"
    detected_gender_sample = "male"

    path = text_to_speech(sample_text_segments, project_id_sample, detected_gender_sample)
    print(f'path: {path}\n Modified_text_segments: {sample_text_segments}')

    assert isinstance(sample_text_segments, list), "Output should be a list."

    for segment in sample_text_segments:
        assert 'audio_timestamp' in segment, "Each segment should have an 'audio_timestamp' key."
        assert isinstance(segment['audio_timestamp'], list), "'audio_timestamp' should be a list."
        assert len(segment['audio_timestamp']) == 2, "'audio_timestamp' should have two values: start and end times."
        assert segment['audio_timestamp'][0] < segment['audio_timestamp'][1], "Start time should be less than end time."

    print("All tests passed!")