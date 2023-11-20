import os
from pathlib import Path

from moviepy.editor import VideoFileClip, AudioFileClip
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
    silent_original_audio: bool = True,
    show_logs: bool = False
):
    try:
        if show_logs:
            print(f"(overlay_audio) Overlaying audio, text_segments - {text_segments}")

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
        if silent_original_audio:
            final_audio = final_audio.silent(duration=video.duration * 1000)

        for segment in text_segments:
            if show_logs:
                print(f"\n(overlay_audio) Processing segment {segment}")

            # If translation is missing for audio segment
            if 'audio_timestamp' not in segment:
                print(f"(overlay_audio) Missing translation sound for {segment}")
                continue

            video_start_time, video_end_time = segment['timestamp']
            video_duration = (video_end_time - video_start_time) * 1000

            audio_start_time, audio_end_time = segment['audio_timestamp']
            audio_segment = AudioSegment.from_file(audio_path)[audio_start_time:audio_end_time]
            audio_duration = audio_end_time - audio_start_time

            if show_logs:
                print(f"(overlay_audio) Video segment duration: {video_duration:.2f}ms | {video_duration / 1000:.2f}s")
                print(f"(overlay_audio) Audio segment duration: {audio_duration:.2f}ms | {audio_duration / 1000:.2f}s")

            # Speed up audio if it's need
            # if audio_duration - video_duration > 0.5:
            #     ratio = audio_duration / video_duration
            #     audio_segment = audio_segment.speedup(playback_speed=ratio)
            #     if show_logs:
            #         print(f"(overlay_audio) Speeding up audio by a factor of: {ratio:.2f}")

            final_audio = final_audio.overlay(audio_segment, position=video_start_time * 1000)
            if show_logs:
                print(f"(overlay_audio) Overlaying audio at {video_start_time:.2f}s in video.\n")

        print("(overlay_audio) Processing all segments completed.")
        overlay_audio_name = f"overlay-audio-{project_id}.mp3"
        final_audio.export(overlay_audio_name, format="mp3")
        final_audio_clip = AudioFileClip(overlay_audio_name)

        # Set the audio of the video to the new audio clip
        video = video.set_audio(final_audio_clip)

        print(f"(overlay_audio) Output audio duration: {final_audio_clip.duration}")
        print(f"(overlay_audio) Output video duration: {video.duration}")

        video.write_videofile(str(translated_video_path), fps=30, logger=None)

        # TODO use clean FFmpeg
        # input_video = ffmpeg.input(video_path)
        # input_audio = ffmpeg.input(audio_path)
        # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(str(translated_video_path)).run()  # Error here

        # Close the clips to free up memory
        video.close()
        audio.close()
        # Remove audio overlay file
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
        {'timestamp': [0.0, 3.36], 'text': ' I wake up in the morning and I want to reach for my phone,',
         'audio_timestamp': [2948, 5655]},
        {'timestamp': [3.36, 5.74], 'text': ' but I know that even if I were to crank up the brightness',
         'audio_timestamp': [8473, 11348]},
        {'timestamp': [5.74, 7.0], 'text': ' on that phone screen,', 'audio_timestamp': [13964, 15317]},
        {'timestamp': [7.0, 10.28], 'text': " it's not bright enough to trigger that cortisol spike.",
         'audio_timestamp': [18068, 20836]},
        {'timestamp': [10.28, 14.36], 'text': ' And for me to be at my most alert and focused throughout',
         'audio_timestamp': [24636, 27597]},
        {'timestamp': [14.36, 16.16], 'text': ' the day and to optimize my sleep at night.',
         'audio_timestamp': [30339, 32738]},
        {'timestamp': [16.16, 20.2], 'text': ' So what I do is I get out of bed and I go outside.',
         'audio_timestamp': [36478, 39279]},
        {'timestamp': [20.2, 23.34], 'text': " And if it's a bright, clear day,", 'audio_timestamp': [43058, 44169]},
        {'timestamp': [23.34, 25.18], 'text': ' and the sun is low in the sky,', 'audio_timestamp': [44157, 45038]},
        {'timestamp': [25.18, 27.18], 'text': ' or the sun is starting to get overhead,',
         'audio_timestamp': [47833, 49620]},
        {'timestamp': [27.18, 28.7], 'text': ' what we call low solar angle,', 'audio_timestamp': [52382, 54371]},
        {'timestamp': [28.7, 31.74], 'text': " then I know I'm getting outside at the right time.",
         'audio_timestamp': [57195, 59113]},
        {'timestamp': [31.74, 34.78], 'text': " If there's cloud cover and I can't see the sun,",
         'audio_timestamp': [61920, 64125]},
        {'timestamp': [34.78, 36.38], 'text': " I also know I'm doing a good thing,",
         'audio_timestamp': [67939, 70579]},
        {'timestamp': [36.38, 38.56], 'text': ' because it turns out, especially on cloudy days,',
         'audio_timestamp': [73378, 75020]},
        {'timestamp': [38.56, 40.66], 'text': ' you want to get outside and get as much light energy',
         'audio_timestamp': [77931, 79233]},
        {'timestamp': [40.66, 42.42], 'text': ' or photons in your eyes.', 'audio_timestamp': [79206, 81228]},
        {'timestamp': [42.42, 44.3], 'text': " But let's say it's a very clear day", 'audio_timestamp': [83858, 86576]},
        {'timestamp': [44.3, 46.44], 'text': ' and I can see where the sun is.', 'audio_timestamp': [89346, 91236]},
        {'timestamp': [46.44, 49.24], 'text': ' I do not need to stare directly into the sun.',
         'audio_timestamp': [94728, 96742]},
        {'timestamp': [49.24, 52.2], 'text': " If it's very low in the sky, I might do that",
         'audio_timestamp': [99562, 101342]},
        {'timestamp': [52.2, 54.52], 'text': " because it's not going to be very painful to my eyes.",
         'audio_timestamp': [104873, 107340]},
        {'timestamp': [54.52, 56.84], 'text': ' However, if the sun is a little bit brighter.',
         'audio_timestamp': [110947, 112718]}]
    video_path = "07fsfECkwma6fVTDyqQf.mp4"
    audio_path = "07fsfECkwma6fVTDyqQf-translated.mp3"
    project_id = "07fsfECkwma6fVTDyqQf"
    overlay_audio(
        video_path=video_path,
        audio_path=audio_path,
        text_segments=sample_text_segments,
        project_id=project_id,
        show_logs=True
    )
