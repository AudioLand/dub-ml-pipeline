import os.path
from moviepy.editor import *


def overlay_audio(is_video, video_path, audio_path):
    # Only video formats are supported: mp4 and avi, audio: mp3
    if is_video:
        suffix = f'.{os.path.split(video_path)[-1].split(".")[-1]}'

        translated_video_path = f'{os.path.split(video_path)[-1].removesuffix(suffix)}_translated{suffix}'

        if os.path.isfile(video_path):
            if os.path.split(video_path)[-1].endswith(".mp4") or os.path.split(video_path)[-1].endswith(".avi"):
                video = VideoFileClip(video_path)

                video = video.without_audio()

                audio = AudioFileClip(audio_path)
                if audio_path.endswith(".mp3"):
                    video.audio = audio
                    video.write_videofile(translated_video_path)
                    print(f'Translated video saved, path: "{translated_video_path}"')

                return video, translated_video_path
