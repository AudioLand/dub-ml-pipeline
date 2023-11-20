from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from config.logger import catch_error
from config.tts_config import tts_config
from elevenlabs_provider import generate_audio_with_elevenlabs_provider
from microsoft_provider import generate_audio_with_microsoft_provider

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

incorrect_language_exception = Exception('Incorrect language')

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

AUDIO_SEGMENT_PAUSE = 3000  # 3 sec


def add_audio_timestamps_to_segments(
    audio_file_path: str,
    text_segments: list[dict],
    min_silence_len=2000,
    silence_thresh=-30,
    padding=500
):
    """
    Detects pauses in an audio file and adds audio_timestamps to segments.

    :param audio_file_path: Path to the audio file.
    :param text_segments: A list of text segments with 'timestamp' and 'text' keys.
    :param min_silence_len: Minimum length of silence to consider as a pause in milliseconds.
    :param silence_thresh: Silence threshold in dB.
    :param padding: Additional time in milliseconds to add to the end of each segment.
    :return: A list of tuples where each tuple is (start, end) time of pauses.
    """
    audio = AudioSegment.from_file(audio_file_path)
    speak_times = detect_nonsilent(
        audio_segment=audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    adjusted_speak_times = [(max(start - padding, 0), min(end + padding, len(audio))) for start, end in speak_times]
    for segment, (start, end) in zip(text_segments, adjusted_speak_times):
        segment['audio_timestamp'] = [start, end]

    # Check the time difference between the end of one segment and the start of the next
    # for i in range(len(adjusted_speak_times) - 1):
    #     end_of_current = adjusted_speak_times[i][1]
    #     start_of_next = adjusted_speak_times[i + 1][0]
    #     time_diff = start_of_next - end_of_current
    #     if abs(time_diff - 3000) > 100:  # Allowing a 100ms deviation
    #         print(f'Time gap discrepancy between segments {i} and {i + 1}: {time_diff}ms')


def get_voice_by_id(voice_id: int):
    """
    Return voice from tts-config by specified voice_id

    :param voice_id: Target voice id

    :returns: Voice object from tts-config
    """
    for voice_from_config in tts_config:
        if voice_from_config['voice_id'] == voice_id:
            return voice_from_config


def text_to_speech(
    text_segments: list[dict],
    voice_id: int,
    project_id: str,
):
    translated_audio_file_path = f"{project_id}-translated.mp3"
    try:
        voice_from_config = get_voice_by_id(voice_id)
        original_voice_id = voice_from_config['original_id']
        voice_language = voice_from_config['languages'][0]

        if voice_from_config['provider'] == "eleven_labs":
            generate_audio_with_elevenlabs_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                original_voice_id=original_voice_id,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE
            )
        elif voice_from_config['provider'] == "azure":
            generate_audio_with_microsoft_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                original_voice_id=original_voice_id,
                language=voice_language,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE
            )
        else:
            # TODO: raise Exception вызывает бесконечный цикл
            catch_error(
                tag="text_to_speech",
                error=incorrect_language_exception,
                project_id=project_id
            )
            raise incorrect_language_exception

        add_audio_timestamps_to_segments(
            audio_file_path=translated_audio_file_path,
            text_segments=text_segments
        )
        return translated_audio_file_path

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception


# For local test
if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28],
         'text': 'Языковые модели сегодня все еще ограничены.'},
        {'timestamp': [3.28, 5.04],
         'text': 'Эта информация может быть устаревшей.'},
        {'timestamp': [5.5, 5.9],
         'text': 'Ура!'},
        {'timestamp': [6.0, 15.0],
         'text': 'Этот текст может содержать полезные инструкции, но чтобы действительно ...'}
    ]
    voice_id = 559
    project_id = "07fsfECkwma6fVTDyqQf"
    text_to_speech(
        text_segments=sample_text_segments,
        voice_id=voice_id,
        project_id=project_id
    )
    print(sample_text_segments)
