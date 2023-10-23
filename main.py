# Local imports
# from integrations.youtube_utils import youtube_download
from overlay_audio import overlay_audio
from speech_to_text import speech_to_text
# from gender_detection import voice_gender_detection
from text_to_speech import text_to_speech
from translation import translate_text

# youtube_link = "https://youtu.be/WDv4AWk0J3U?si=wL3cKW1PCvinxBDy"
video_path = 'test-video-1min.mp4'

if __name__ == "__main__":
    # pipeline execution

    # 1. Download video from YouTube to local storage
    # video_path = youtube_download(youtube_link)

    # # 2. Convert video to text
    print('start speech to text, video_path - ', video_path)
    text = speech_to_text(video_path)
    print("original text - ", text)

    # 3. Translate text
    translated_text = translate_text('ru', text)
    print("translated_text - ", translated_text)

    # 4. Detect gender of the voice
    # gender = voice_gender_detection(video_path)

    # 5. Generate audio from translated text
    translated_audio, audio_path = text_to_speech(translated_text, 'male')

    # 6. Overlay audio on video
    # first argument is_video: if we translate video - true, else - false
    translated_video = overlay_audio(True, video_path, audio_path)

    print('it is working!!!')
    pass
