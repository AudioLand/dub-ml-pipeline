from moviepy.editor import *
from pydub import AudioSegment
from pathlib import Path

SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi']
SUPPORTED_AUDIO_EXTENSIONS = ['.mp3']


def overlay_audio(video_path, audio_path):
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    # Check if paths exist
    if not video_path.exists() or not audio_path.exists():
        raise ValueError("Either video or audio path does not exist")

    # Check for supported file extensions
    if video_path.suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise ValueError(
            f"Video format '{video_path.suffix}' not supported. Only {SUPPORTED_VIDEO_EXTENSIONS} are supported.")
    if audio_path.suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"Audio format '{audio_path.suffix}' not supported. Only {SUPPORTED_AUDIO_EXTENSIONS} are supported.")

    translated_video_path = video_path.parent / f"{video_path.stem}_translated{video_path.suffix}"

    video = VideoFileClip(str(video_path))
    audio = AudioFileClip(str(audio_path))

    print('audio.duration', audio.duration)
    print('video.duration', video.duration)

    # Handle duration mismatch: If audio is longer than video, speed up the audio.
    if audio.duration > video.duration:
        audio = AudioSegment.from_file(audio_path, format='mp3')
        speed_ratio = audio.duration_seconds / video.duration
        modified_audio = audio.speedup(playback_speed=speed_ratio)
        modified_audio.export(audio_path, format="mp3")
        audio = AudioFileClip(str(audio_path))

    print('modified_audio.duration', audio.duration)
    # Set the audio of the video to the new audio clip
    final_video = video.set_audio(audio)

    final_video.write_videofile(str(translated_video_path), fps=30, audio=str(audio_path))

    # TODO use clean FFmpeg
    # input_video = ffmpeg.input(video_path)
    # input_audio = ffmpeg.input(audio_path)
    # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(str(translated_video_path)).run() - Error here

    # Close the clips to free up memory
    video.close()
    audio.close()
    final_video.close()

    print(f'Translated video saved, path: "{translated_video_path}"')

    return translated_video_path


# For local test
# overlay_audio('0qQ7IMhjgf40Bb6pKftb.mp4', '0qQ7IMhjgf40Bb6pKftb_audio_translated.mp3')
# overlay_audio('0qQ7IMhjgf40Bb6pKftb.mp4', 'long.mp3')