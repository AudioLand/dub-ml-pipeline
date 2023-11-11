import os
import azure.cognitiveservices.speech as speechsdk
import json


VOICE_MAPPING = {
    "female": 'female',
    "male": 'male'
}

with open('languages_gender_microsoft_tts_dict.txt', 'r') as f:
    language_gender_dict = json.load(f)

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
# speech_config = speechsdk.SpeechConfig(subscription='1fe5549cbd074a67881077a17ba9d1bd', region='eastus')
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)


def microsoft_provider(text: str, language: str, detected_gender: str = None):
    detected_gender = VOICE_MAPPING.get(detected_gender, 'male')
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = language_gender_dict[language][detected_gender]
    # Could we gt it from the function?
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


    return speech_synthesis_result


# For local test
# if __name__ == "__main__":
#     microsoft_provider('한국어', 'Korean (Korea)', 'female')
