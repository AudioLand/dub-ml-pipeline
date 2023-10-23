# Local imports
# from integrations.youtube_utils import youtube_download
from speech_to_text import speech_to_text
# from gender_detection import voice_gender_detection
from text_to_speech import text_to_speech
from translation import translate_text
from datetime import datetime

from fastapi import FastAPI

app = FastAPI()

# youtube_link = "https://youtu.be/WDv4AWk0J3U?si=wL3cKW1PCvinxBDy"
video_path = 'test-video-1min.mp4'


@app.get("/")
def generate():
    # pipeline execution
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
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
    translated_audio = text_to_speech(translated_text, 'male')

    print('it is working!!!')
    return {"status": "it is working!!!"}


@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("main started")
