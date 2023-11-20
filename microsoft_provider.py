import os

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, ResultReason, CancellationReason
from azure.cognitiveservices.speech.audio import AudioOutputConfig

from config.config import SPEECH_REGION, SPEECH_KEY

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = SpeechConfig(
    subscription=SPEECH_KEY,
    region=SPEECH_REGION
)


# languages can be found at https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
def create_ssml_with_pauses(
    text_segments: list[dict],
    original_voice_id: str,
    language: str,
    pause_duration_ms: int
):
    """
    Create an SSML string with pauses and voice specification for Azure's Speech Service.

    :param text_segments: A list of dictionaries with 'text' keys.
    :param original_voice_id: The name of the voice to be used for speech synthesis.
    :param language: Language value in format expected from Microsoft.
    :param pause_duration_ms: The duration of pauses in milliseconds (default is 1.5 seconds).
    :return: A string formatted in SSML with pauses, voice tag, and necessary namespaces.
    """
    ssml_parts = [
        f"<speak version=\"1.0\"",
        "xmlns=\"http://www.w3.org/2001/10/synthesis\"",
        "xmlns:mstts=\"https://www.w3.org/2001/mstts\"",
        f" xml:lang=\"{language}\">",
        f"<voice name=\"{original_voice_id}\">",
        f"<break time=\"{pause_duration_ms}ms\"/>"
    ]

    for segment in text_segments:
        ssml_parts.append(segment['text'])
        ssml_parts.append(f'<break time="{pause_duration_ms}ms"/>')
    ssml_parts.append('</voice></speak>')

    return " ".join(ssml_parts)


def generate_audio_with_microsoft_provider(
    output_audio_file_path: str,
    text_segments: list[dict],
    original_voice_id: str,
    language: str,
    pause_duration_ms: int = 1000,
    show_logs: bool = False
):
    audio_config = AudioOutputConfig(filename=output_audio_file_path)

    speech_synthesizer = SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    if show_logs:
        print(f"(elevenlabs_provider) Creating SSML with break tags for {pause_duration_ms / 1000}s...")

    # Joins segments into text with pause marks.
    text_for_synthesizing = create_ssml_with_pauses(
        text_segments=text_segments,
        original_voice_id=original_voice_id,
        language=language,
        pause_duration_ms=pause_duration_ms
    )

    if show_logs:
        print(f"(elevenlabs_provider) Synthesizing audio with SSML - {text_for_synthesizing}")

    speech_synthesis_result = speech_synthesizer.speak_ssml(text_for_synthesizing)

    # If synthesizing completed
    if speech_synthesis_result.reason == ResultReason.SynthesizingAudioCompleted:
        if show_logs:
            print(f"(elevenlabs_provider) Audio synthesize completed and saved to - {output_audio_file_path}")

    # If synthesizing canceled
    elif speech_synthesis_result.reason == ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"(microsoft_provider) Speech synthesis canceled: {cancellation_details.reason}")

        if cancellation_details.reason == CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"(microsoft_provider) Error details: {cancellation_details.error_details}")


# For local test
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
    output_audio_file_path = "07fsfECkwma6fVTDyqQf-translated.mp3"
    open(output_audio_file_path, 'wb').close()
    text_segments = sample_text_segments
    original_voice_id = "ru-RU-DariyaNeural"
    language = "russian"
    os.remove(output_audio_file_path)
    generate_audio_with_microsoft_provider(
        output_audio_file_path=output_audio_file_path,
        text_segments=text_segments,
        original_voice_id=original_voice_id,
        language=language,
        pause_duration_ms=3000,
        show_logs=True
    )
