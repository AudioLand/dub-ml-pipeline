from config.logger import catch_error
from elevenlabs_provider import elevenlabs_provider
from microsoft_provider import microsoft_provider
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

AUDIO_SEGMENT_PAUSE = 3000

ELEVENLABS_LANGUAGES = [
    "English", "Japanese", "Chinese", "German", "Hindi",
    "French", "Korean", "Portuguese", "Italian", "Spanish",
    "Indonesian", "Dutch", "Turkish", "Filipino", "Polish",
    "Swedish", "Bulgarian", "Romanian", "Arabic", "Czech",
    "Greek", "Finnish", "Croatian", "Malay", "Slovak",
    "Danish", "Tamil", "Ukrainian", "Russian"
]

with open('languages_microsoft.txt', 'r') as f:
    MICROSOFT_LANGUAGES = f.read().split(',\n')


def add_audio_timestamps_to_segments(audio_file, segments, min_silence_len=500, silence_thresh=-30, padding=300):
    """
    Detects pauses in an audio file and adds audio_timestamps to segments.

    :param audio_file: Path to the audio file.
    :param segments: A list of text segments with 'timestamp' and 'text' keys.
    :param min_silence_len: Minimum length of silence to consider as a pause in milliseconds.
    :param silence_thresh: Silence threshold in dB.
    :param padding: Additional time in milliseconds to add to the end of each segment.
    :return: A list of tuples where each tuple is (start, end) time of pauses.
    """
    audio = AudioSegment.from_file(audio_file)
    speak_times = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    adjusted_speak_times = [(max(start - padding, 0), min(end + padding, len(audio))) for start, end in speak_times]
    for segment, (start, end) in zip(segments, adjusted_speak_times):
        segment['audio_timestamp'] = [start, end]

    # Check the time difference between the end of one segment and the start of the next
    # for i in range(len(adjusted_speak_times) - 1):
    #     end_of_current = adjusted_speak_times[i][1]
    #     start_of_next = adjusted_speak_times[i + 1][0]
    #     time_diff = start_of_next - end_of_current
    #     if abs(time_diff - 3000) > 100:  # Allowing a 100ms deviation
    #         print(f'Time gap discrepancy between segments {i} and {i + 1}: {time_diff}ms')


def text_to_speech(text_segments: list, target_language: str, project_id: str, voice_id: str = None,
                   detected_gender: str = None):
    translated_audio_file_name = f"translated-{project_id}.mp3"
    try:
        if target_language in ELEVENLABS_LANGUAGES:
            elevenlabs_provider(text_segments=text_segments,
                                filename=translated_audio_file_name,
                                voice_id=voice_id,
                                detected_gender=detected_gender
                                )
        elif target_language in MICROSOFT_LANGUAGES:
            microsoft_provider(text_segments=text_segments,
                               filename=translated_audio_file_name,
                               language=target_language,
                               detected_gender=detected_gender,
                               pause_duration_ms=AUDIO_SEGMENT_PAUSE
                               )
        else:
            # TODO: raise Exception вызывает бесконечный цикл
            catch_error(
                tag="text_to_speech",
                error=Exception('Incorrect language'),
                project_id=project_id
            )
            return

        add_audio_timestamps_to_segments(translated_audio_file_name, text_segments)
        return translated_audio_file_name

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
    text_to_speech(sample_text_segments, "English", "test")
    print(sample_text_segments)

    for segment in sample_text_segments:
        assert 'audio_timestamp' in segment, "Each segment should have an 'audio_timestamp' key."
        assert isinstance(segment['audio_timestamp'], list), "'audio_timestamp' should be a list."
        assert len(segment['audio_timestamp']) == 2, "'audio_timestamp' should have two values: start and end times."
        assert segment['audio_timestamp'][0] < segment['audio_timestamp'][1], "Start time should be less than end time."

    print("All tests passed!")