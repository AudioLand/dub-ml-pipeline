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
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts"',
        f' xml:lang="{language}">',
        f'<voice name="{original_voice_id}">',
        f'<break time="{pause_duration_ms}ms"/>'
    ]
    for segment in text_segments:
        ssml_parts.append(segment['text'])
        ssml_parts.append(f'<break time="{pause_duration_ms}ms"/>')
    ssml_parts.append('</voice></speak>')
    return ''.join(ssml_parts)


def generate_audio_with_microsoft_provider(
    output_audio_file_path: str,
    text_segments: list[dict],
    original_voice_id: str,
    language: str,
    pause_duration_ms: int,
):
    audio_config = AudioOutputConfig(filename=output_audio_file_path)

    speech_synthesizer = SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    # Joins segments into text with pause marks.
    text_for_synthesizing = create_ssml_with_pauses(
        text_segments=text_segments,
        original_voice_id=original_voice_id,
        language=language,
        pause_duration_ms=pause_duration_ms
    )
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(text_for_synthesizing).get()

    # If synthesizing completed
    if speech_synthesis_result.reason == ResultReason.SynthesizingAudioCompleted:
        print(f"(microsoft_provider) Speech synthesized completed")

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
        {'timestamp': [0.0, 2.28],
         'text': 'Языковые модели сегодня все еще ограничены.'},
        {'timestamp': [3.28, 5.04],
         'text': 'Эта информация может быть устаревшей.'},
        {'timestamp': [5.5, 5.9],
         'text': 'Ура!'},
        {'timestamp': [6.0, 15.0],
         'text': 'Этот текст может содержать полезные инструкции, но чтобы действительно ...'}
    ]
    output_audio_file_path = "translated-test.mp3"
    text_segments = sample_text_segments
    original_voice_id = "ru-RU-DmitryNeural"
    language = "russian"
    generate_audio_with_microsoft_provider(
        output_audio_file_path=output_audio_file_path,
        text_segments=text_segments,
        original_voice_id=original_voice_id,
        language=language,
        pause_duration_ms=3000,
    )
