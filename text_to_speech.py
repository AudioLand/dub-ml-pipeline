import time

from config.logger import catch_error
from config.tts_config import tts_config
from elevenlabs_provider import generate_audio_with_elevenlabs_provider
from microsoft_provider import generate_audio_with_microsoft_provider

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

incorrect_language_exception = Exception('Incorrect language')

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

AUDIO_SEGMENT_PAUSE_IN_MILLISECONDS = 3000

DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS = 5


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
    show_logs: bool = False
):
    try:
        if show_logs:
            print(f"(speech_to_text) Processing text segments to speech - {text_segments}")

        translated_audio_file_path = f"{project_id}-translated.mp3"
        voice_from_config = get_voice_by_id(voice_id)
        original_voice_id = voice_from_config['original_id']
        voice_provider = voice_from_config['provider']
        voice_language = voice_from_config['languages'][0]

        if show_logs:
            print(f"(text_to_speech) Voice provider for this project - {voice_provider}")

        # Text to speech with 11labs
        if voice_provider == "eleven_labs":
            generate_audio_with_elevenlabs_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                original_voice_id=original_voice_id,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE_IN_MILLISECONDS,
                show_logs=show_logs
            )

        # Text to speech with Microsoft
        elif voice_provider == "azure":
            generate_audio_with_microsoft_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                original_voice_id=original_voice_id,
                language=voice_language,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE_IN_MILLISECONDS,
                show_logs=show_logs,
            )
        else:
            # TODO: raise Exception calls infinite loop
            catch_error(
                tag="text_to_speech",
                error=incorrect_language_exception,
                project_id=project_id
            )
            raise incorrect_language_exception

        return translated_audio_file_path

    except ConnectionResetError as cre:
        print(f"(text_to_speech) ConnectionResetError: {str(cre)}")
        # Try again because something went wrong
        print(f"(text_to_speech) Something went wrong")
        print(f"(text_to_speech) Wait {DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS} seconds to repeat...")
        time.sleep(DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS)
        print(f"(text_to_speech) Repeating...")
        return text_to_speech(
            text_segments=text_segments,
            voice_id=voice_id,
            project_id=project_id,
        )

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception


if __name__ == "__main__":
    sample_text_segments = [
        {'original_timestamps': (0, 959), 'text': 'Я просыпаюсь утром'},
        {'original_timestamps': (1156, 2656), 'text': 'и хочу достать свой телефон.'},
        {'original_timestamps': (3379, 4686), 'text': 'Но я знаю, что даже если бы я'},
        {'original_timestamps': (4868, 6667), 'text': 'увеличил яркость на экране телефона.'},
        {'original_timestamps': (7137, 8161), 'text': 'Этого не будет достаточно.'},
        {'original_timestamps': (8526, 10176), 'text': 'чтобы вызвать резкий подъем кортизола.'},
        {'original_timestamps': (10314, 10844), 'text': 'и для меня.'},
        {'original_timestamps': (11329, 11605), 'text': 'чтобы'},
        {'original_timestamps': (11753, 12289), 'text': 'может быть.'},
        {'original_timestamps': (12516, 18409),
         'text': 'быть наиболее бодрым и сосредоточенным в течение дня и оптимизировать свой сон ночью. Так что я делаю так: я встаю с кровати.'},
        {'original_timestamps': (18707, 19862), 'text': 'и выхожу на улицу.'},
        {'original_timestamps': (20219, 20852), 'text': 'А если это.'},
        {'original_timestamps': (21400, 21800), 'text': 'правильно?'},
        {'original_timestamps': (21952, 22685), 'text': 'ясный день.'},
        {'original_timestamps': (23332, 25872), 'text': 'и солнце низко в небе или солнце уже.'},
        {'original_timestamps': (26078, 28440),
         'text': 'начинает подниматься над горизонтом, то, как мы говорим, угол падения солнечного света мал.'},
        {'original_timestamps': (28722, 29663), 'text': 'И я знаю, что я'},
        {'original_timestamps': (30183, 31453), 'text': 'вышел на улицу в правильное время.'},
        {'original_timestamps': (31741, 32804), 'text': 'Если небо в облаках.'},
        {'original_timestamps': (32920, 34074), 'text': 'и я не вижу солнца.'}, {'original_timestamps': (34787, 41637),
                                                                                 'text': 'Я также понимаю, что делаю правильное дело, потому что, оказывается, особенно в облачные дни, нужно выходить на улицу и получать как можно больше световой энергии или фотонов в глаза.'},
        {'original_timestamps': (42425, 44105), 'text': 'Но предположим, что день очень ясный.'},
        {'original_timestamps': (44315, 46013), 'text': 'и я вижу, где находится солнце.'},
        {'original_timestamps': (46437, 48854), 'text': 'Мне не нужно смотреть прямо на солнце.'},
        {'original_timestamps': (49252, 49530), 'text': 'Если оно'},
        {'original_timestamps': (49911, 51078), 'text': 'Очень низко на горизонте.'},
        {'original_timestamps': (51428, 55109),
         'text': 'Я могу это сделать, потому что это не будет очень больно для моих глаз.'},
        {'original_timestamps': (55491, 56752), 'text': 'солнце становится немного ярче.'}
    ]
    # Voice for english Microsoft TTS tests
    # voice_id = 260
    # Voice for russian Microsoft TTS tests
    voice_id = 165
    # Voice for english 11labs TTS tests
    # voice_id = 1242
    project_id = "07fsfECkwma6fVTDyqQf"
    text_to_speech(
        text_segments=sample_text_segments,
        voice_id=voice_id,
        project_id=project_id,
        show_logs=True
    )
