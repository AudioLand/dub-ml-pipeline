from config.logger import catch_error
from elevenlabs_provider import elevenlabs_provider
from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id
from microsoft_provider import microsoft_provider

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

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


def text_to_speech(text: str, target_language: str, project_id: str, voice_id: str = None, detected_gender: str = None):
    try:
        if target_language in ELEVENLABS_LANGUAGES:
            audio = elevenlabs_provider(text=text,
                                        voice_id=voice_id,
                                        detected_gender=detected_gender
                                        )
        elif target_language in MICROSOFT_LANGUAGES:
            audio = microsoft_provider(text=text,
                                       language=target_language,
                                       detected_gender=detected_gender
                                       )
        else:
            # TODO: raise Exception вызывает бесконечный цикл
            catch_error(
                tag="text_to_speech",
                error=Exception('Incorrect language'),
                project_id=project_id
            )
            return

        translated_audio_file_name = f"translated-{project_id}.mp3"
        with open(translated_audio_file_name, mode='bw') as f:
            f.write(audio)

        return translated_audio_file_name

    except Exception as e:
        catch_error(
            tag="text_to_speech",
            error=e,
            project_id=project_id
        )
        raise text_to_speech_exception
