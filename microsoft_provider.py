import os
import azure.cognitiveservices.speech as speechsdk
import json

from pydub import AudioSegment

VOICE_MAPPING = {
    "female": 'female',
    "male": 'male'
}

with open('languages_gender_microsoft_tts_dict.txt', 'r') as f:
    language_gender_dict = json.load(f)

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                       region=os.environ.get('SPEECH_REGION'))


# languages can be found at https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
def create_ssml_with_pauses(text_segments, voice_name, language, pause_duration_ms):
    """
    Create an SSML string with pauses and voice specification for Azure's Speech Service.

    :param text_segments: A list of dictionaries with 'text' keys.
    :param voice_name: The name of the voice to be used for speech synthesis.
    :param language: Language value in format expected from Microsoft.
    :param pause_duration_ms: The duration of pauses in milliseconds (default is 1.5 seconds).
    :return: A string formatted in SSML with pauses, voice tag, and necessary namespaces.
    """
    ssml_parts = [
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts"',
        f' xml:lang="{language}">',
        f'<voice name="{voice_name}">',
        f'<break time="{pause_duration_ms}ms"/>'
    ]
    for segment in text_segments:
        ssml_parts.append(segment['text'])
        ssml_parts.append(f'<break time="{pause_duration_ms}ms"/>')
    ssml_parts.append('</voice></speak>')
    return ''.join(ssml_parts)


def microsoft_provider(text_segments: list, filename: str, language: str, pause_duration_ms: int, detected_gender: str = None):
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    detected_gender = VOICE_MAPPING.get(detected_gender, 'male')
    voice = language_gender_dict[language][detected_gender]
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # Joins segments into text with pause marks.
    text = create_ssml_with_pauses(text_segments, voice, language, pause_duration_ms)
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


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
    microsoft_provider(sample_text_segments, "translated-test.mp3", 'Russian (Russia)', 3000,'male')
    audio = AudioSegment.from_file("translated-test.mp3")
