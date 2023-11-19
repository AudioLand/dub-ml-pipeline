from pathlib import Path

# from ffmpeg.video import playback_speed
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
        {
            'timestamp': [0.0, 4.52],
            'text': 'Я просыпаюсь утром и хочу дотянуться до своего телефона, но я знаю, что даже если я',
            'audio_timestamp': [2985, 8959]
        },
        {
            'timestamp': [4.52, 9.8],
            'text': 'увеличу яркость экрана, это все равно не будет достаточно ярко, чтобы вызвать скачок кортизола',
            'audio_timestamp': [11582, 17909]
        },
        {
            'timestamp': [9.8, 15.42],
            'text': 'и для того, чтобы я был максимально бодрым и сосредоточенным в течение дня и оптимизировал свой',
            'audio_timestamp': [20576, 26696]
        },
        {
            'timestamp': [15.42, 16.42],
            'text': 'сон ночью.',
            'audio_timestamp': [29366, 30503]
        },
        {
            'timestamp': [16.42, 23.76],
            'text': 'Поэтому я встаю из кровати и выхожу на улицу, и если день светлый и ясный, а',
            'audio_timestamp': [34132, 39918]
        },
        {
            'timestamp': [23.76, 26.08],
            'text': 'солнце низко в небе, или солнце,',
            'audio_timestamp': [42570, 45069]
        },
        {
            'timestamp': [26.08, 27.2],
            'text': ' знаете, начинает подниматься над головой,',
            'audio_timestamp': [47868, 50767]
        },
        {
            'timestamp': [27.2, 28.72],
            'text': ' то, что мы называем низким солнечным углом,',
            'audio_timestamp': [53412, 56276]
        },
        {
            'timestamp': [28.72, 31.76],
            'text': ' и я знаю, что выхожу на улицу в нужное время.',
            'audio_timestamp': [58982, 62149]
        },
        {
            'timestamp': [31.76, 34.8],
            'text': 'Если облачно, и я не вижу солнца,',
            'audio_timestamp': [65830, 68568]
        },
        {
            'timestamp': [34.8, 36.4],
            'text': 'я также знаю, что делаю правильное дело',
            'audio_timestamp': [71331, 74083]
        },
        {
            'timestamp': [36.4, 38.56],
            'text': ' потому что оказывается, особенно в облачные дни,',
            'audio_timestamp': [76748, 80054]
        },
        {
            'timestamp': [38.56, 40.64],
            'text': ' вы хотите выйти на улицу и получить как можно больше световой энергии',
            'audio_timestamp': [82773, 87412]
        },
        {
            'timestamp': [40.64, 42.4],
            'text': ' или фотонов в ваши глаза.',
            'audio_timestamp': [90171, 92258]
        },
        {
            'timestamp': [42.4, 44.32],
            'text': 'Но допустим, день очень ясный,',
            'audio_timestamp': [95874, 98348]
        },
        {
            'timestamp': [44.32, 45.36],
            'text': ' и я вижу, где находится',
            'audio_timestamp': [101133, 103199]
        },
        {
            'timestamp': [45.36, 52.08],
            'text': ' солнце. Мне не нужно смотреть прямо на солнце. Если оно очень низко в небе, я могу сделать это',
            'audio_timestamp': [105861, 106748]
        },
        {
            'timestamp': [52.08, 56.48],
            'text': ' потому что это не будет очень больно для моих глаз. Однако, если солнце немного ярче,',
            'audio_timestamp': [107394, 110020]
        }
    ]
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
