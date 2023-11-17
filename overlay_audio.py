from pathlib import Path

from moviepy.editor import *
from pydub import AudioSegment

from config.logger import catch_error

overlay_audio_exception = Exception(
    "Error while processing overlay audio"
)

SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi']
SUPPORTED_AUDIO_EXTENSIONS = ['.mp3']


def overlay_audio(
    video_path: str,
    audio_path: str,
    text_segments: list[dict],
    project_id: str,
    show_segment_logs=False
):
    try:
        video_path = Path(video_path)
        audio_path = Path(audio_path)

        # Check if paths exist
        if not video_path.exists() or not audio_path.exists():
            raise ValueError("Either video or audio path does not exist")

        # Check for supported file extensions
        if video_path.suffix not in SUPPORTED_VIDEO_EXTENSIONS:
            raise ValueError(
                f"Video format {video_path.suffix} not supported. Only {SUPPORTED_VIDEO_EXTENSIONS} are supported."
            )
        if audio_path.suffix not in SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"Audio format {audio_path.suffix} not supported. Only {SUPPORTED_AUDIO_EXTENSIONS} are supported."
            )

        translated_video_path = f"{video_path.parent}/{video_path.stem}-translated{video_path.suffix}"

        video = VideoFileClip(str(video_path))
        audio = AudioFileClip(str(audio_path))

        print(f"(overlay_audio) Input audio duration: {audio.duration}s")
        print(f"(overlay_audio) Input video duration: {video.duration}s")

        final_audio = AudioSegment.from_file(str(video_path), format=video_path.suffix[1:])

        # Remove original video sound
        final_audio = final_audio.silent(duration=video.duration * 1000)

        for segment in text_segments:
            if show_segment_logs:
                print(f"(overlay_audio) Processing segment {segment}")

            # If translation is missing for audio segment
            if 'audio_timestamp' not in segment:
                print(f"(overlay_audio) Missing translation sound for {segment}")
                continue

            audio_start_time, audio_end_time = segment['audio_timestamp']
            audio_segment = AudioSegment.from_file(audio_path)[audio_start_time:audio_end_time]

            video_start_time, video_end_time = segment['timestamp']
            video_duration = (video_end_time - video_start_time) * 1000
            audio_duration = audio_end_time - audio_start_time
            if show_segment_logs:
                print(f"(overlay_audio) Video segment duration: {video_duration:.2f}ms | {video_duration / 1000:.2f}s")
                print(f"(overlay_audio) Audio segment duration: {audio_duration:.2f}ms | {audio_duration / 1000:.2f}s")

                # Speed up audio if it's need
                # if audio_duration - video_duration > 0.5:
                #     ratio = audio_duration / video_duration
                #     audio_segment = audio_segment.speedup(playback_speed=ratio)
                #     if show_segment_logs:
                #         print(f"(overlay_audio) Speeding up audio by a factor of: {ratio:.2f}")

            final_audio = final_audio.overlay(audio_segment, position=video_start_time * 1000)
            if show_segment_logs:
                print(f"(overlay_audio) Overlaying audio at {video_start_time:.2f}s in video.")

        print("(overlay_audio) Processing all segments completed.")
        overlay_audio_name = f"overlay-audio-{project_id}.mp3"
        final_audio.export(overlay_audio_name, format="mp3")
        final_audio_clip = AudioFileClip(overlay_audio_name)

        # Set the audio of the video to the new audio clip
        video = video.set_audio(final_audio_clip)

        print(f"(overlay_audio) Output audio duration: {final_audio_clip.duration}")
        print(f"(overlay_audio) Output video duration: {video.duration}")

        # video.write_videofile(str(translated_video_path), audio=str(audio_path), fps=30, logger=None)
        video.write_videofile(str(translated_video_path), fps=30, logger=None)

        # TODO use clean FFmpeg
        # input_video = ffmpeg.input(video_path)
        # input_audio = ffmpeg.input(audio_path)
        # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(str(translated_video_path)).run()  # Error here

        # Close the clips to free up memory
        video.close()
        audio.close()
        os.remove(overlay_audio_name)

        print(f"(overlay_audio) Translated video saved, path: {translated_video_path}")

        return translated_video_path
    except Exception as e:
        catch_error(
            tag="overlay_audio",
            error=e,
            project_id=project_id
        )
        raise overlay_audio_exception


# For local test
if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28],
         'text': 'Language models today, while useful for a variety of tasks, are still limited. The only information they can learn from is their training data.',
         'audio_timestamp': [0.0, 2.28]},
        {'timestamp': [3.28, 5.04],
         'text': 'This information can be out-of-date and is one-size fits all across applications. Furthermore, the only thing language models can do out-of-the-box is emit text.',
         'audio_timestamp': [3.0, 5.0]},
        {'timestamp': [6.0, 15.0],
         'text': 'This text can contain useful instructions, but to actually follow these instructions you need another process.',
         'audio_timestamp': [7.0, 15.0]}
    ]
    overlay_audio('test-video.mp4', 'final_audio.mp3', sample_text_segments)
    # overlay_audio('0qQ7IMhjgf40Bb6pKftb.mp4', 'long.mp3')
