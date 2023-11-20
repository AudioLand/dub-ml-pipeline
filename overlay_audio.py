import os
from pathlib import Path

import moviepy.audio.fx.all as effects
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

from config.logger import catch_error

overlay_audio_exception = Exception(
    "Error while processing overlay audio"
)

SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi']
SUPPORTED_AUDIO_EXTENSIONS = ['.mp3']


def overlay_audio_to_video(
    original_video_path: str,
    translated_audio_path: str,
    original_text_segments_with_timestamps: list[dict],
    translated_nonsilent_timestamps: list[tuple[int, int]],
    project_id: str,
    silent_original_audio: bool = True,
    show_logs: bool = False
):
    try:
        if show_logs:
            print(f"(overlay_audio) Overlaying {translated_audio_path} audio to {original_video_path} video...")

        input_video_path = Path(original_video_path)
        input_audio_path = Path(translated_audio_path)

        # Check if video path exists
        if not input_video_path.exists():
            raise ValueError("Video path does not exist")

        # Check if audio path exists
        if not input_audio_path.exists():
            raise ValueError("Audio path does not exist")

        # Check for supported video extensions
        if input_video_path.suffix not in SUPPORTED_VIDEO_EXTENSIONS:
            raise ValueError(
                f"Video format {input_video_path.suffix} not supported. Only {SUPPORTED_VIDEO_EXTENSIONS} are supported."
            )

        # Check for supported audio extensions
        if input_audio_path.suffix not in SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"Audio format {input_audio_path.suffix} not supported. Only {SUPPORTED_AUDIO_EXTENSIONS} are supported."
            )

        translated_video_path = f"{input_video_path.parent}/{input_video_path.stem}-translated{input_video_path.suffix}"

        original_video_clip = VideoFileClip(str(input_video_path))
        original_audio_clip = AudioFileClip(str(input_video_path))
        translated_audio_clip = AudioFileClip(str(input_audio_path))

        print(f"(overlay_audio) Input video duration: {original_video_clip.duration}s")
        print(f"(overlay_audio) Input audio duration: {translated_audio_clip.duration}s")

        overlay_audio = AudioSegment.from_file(
            file=str(input_video_path),
            format=input_video_path.suffix[1:]
        )

        # Remove original video sound
        if silent_original_audio:
            overlay_audio = overlay_audio.silent(duration=original_video_clip.duration * 1000)

        # Compress original and translated timestamps to one list
        timestamps_list = list(zip(
            original_text_segments_with_timestamps,
            translated_nonsilent_timestamps
        ))
        # Beautify final compressed list
        text_segments_with_timestamps = []
        for segment, translated_timestamps in timestamps_list:
            segment['translated_timestamps'] = translated_timestamps
            text_segments_with_timestamps.append(segment)

        if show_logs:
            print(f"(overlay_audio) Text segments with timestamps - {text_segments_with_timestamps}")

        # TODO: надо подкрутить считывание пауз у переведённого аудио

        # Overlay translated audio segments to video by original timestamps
        for index, segment in enumerate(text_segments_with_timestamps):
            video_timestamps = segment['original_timestamps']
            audio_timestamps = segment['translated_timestamps']
            segment_text = segment['text']

            # Video timestamps
            video_start_time, video_end_time = video_timestamps
            video_duration = video_end_time - video_start_time

            # Audio timestamps
            audio_start_time, audio_end_time = audio_timestamps
            audio_duration = audio_end_time - audio_start_time

            if show_logs:
                print(f"\n(overlay_audio) Processing audio segment - '{segment_text}'")

                original_timestamps_s = f"{video_start_time / 1000}s, {video_end_time / 1000}s"
                original_timestamps_ms = f"{video_start_time}ms, {video_end_time}ms"
                print(f"(overlay_audio) Original timestamps - {original_timestamps_ms} | {original_timestamps_s}")

                translated_timestamps_s = f"{audio_start_time / 1000}s, {audio_end_time / 1000}s"
                translated_timestamps_ms = f"{audio_start_time}ms, {audio_end_time}ms"
                print(f"(overlay_audio) Translated timestamps - {translated_timestamps_ms} | {translated_timestamps_s}")

            # # If translation is missing for audio segment
            # if 'audio_timestamp' not in segment:
            #     print(f"(overlay_audio) Missing translation sound for {segment}")
            #     continue

            # Get segment from translated audio file
            audio_segment = AudioSegment.from_file(input_audio_path)[audio_start_time:audio_end_time]
            # audio_segment_clip: AudioFileClip = translated_audio_clip.subclip(
            #     t_start=audio_start_time / 1000,
            #     t_end=audio_end_time / 1000
            # )

            if show_logs:
                print(f"(overlay_audio) Video segment duration: {video_duration:.2f}ms | {video_duration / 1000:.2f}s")
                print(f"(overlay_audio) Audio segment duration: {audio_duration:.2f}ms | {audio_duration / 1000:.2f}s")

            # durations_ratio = video_duration / audio_duration
            # print(f"(overlay_audio) Video to audio duration ration - {durations_ratio}")
            #
            # # Change audio segment speed if audio shorter or longer than video
            # if durations_ratio != 1.0:
            #     audio_segment_clip = audio_segment_clip.fx(vfx.speedx, durations_ratio)
            #     if show_logs:
            #         # Speed up
            #         if durations_ratio < 1.0:
            #             print(f"(overlay_audio) Speeding up audio by a factor of {durations_ratio:.2f}")
            #         # Slow down
            #         elif durations_ratio > 1.0:
            #             print(f"(overlay_audio) Slowing down audio by a factor of {durations_ratio:.2f}")

            # audio_segment_clip_path = f"audio-segment-{index}.mp3"
            # audio_segment_clip.write_audiofile(
            #     filename=audio_segment_clip_path,
            #     fps=audio_segment_clip.fps,
            #     logger=None
            # )
            # audio_segment = AudioSegment.from_file(input_audio_path)
            # os.remove(audio_segment_clip_path)
            overlay_audio = overlay_audio.overlay(
                seg=audio_segment,
                position=video_start_time
            )
            if show_logs:
                print(f"(overlay_audio) Overlaying audio at {video_start_time / 1000:.2f}s in video.\n")

        print("(overlay_audio) Processing all segments completed.")
        overlay_audio_path = f"overlay-audio-{project_id}.mp3"
        overlay_audio.export(overlay_audio_path, format="mp3")
        overlay_audio_clip = AudioFileClip(overlay_audio_path)

        original_audio_clip = original_audio_clip.fx(effects.volumex, 0.15)
        final_audio = CompositeAudioClip([original_audio_clip, overlay_audio_clip])

        # Set overlay audio to video
        translated_video: VideoFileClip = original_video_clip.set_audio(final_audio)
        translated_video.write_videofile(
            filename=translated_video_path,
            fps=translated_video.fps,
            logger=None
        )

        print(f"(overlay_audio) Output video duration: {translated_video.duration}")
        print(f"(overlay_audio) Output audio duration: {overlay_audio_clip.duration}")

        # TODO use clean FFmpeg
        # input_video = ffmpeg.input(video_path)
        # input_audio = ffmpeg.input(audio_path)
        # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(str(translated_video_path)).run()  # Error here

        # Close processed clips
        translated_video.close()
        translated_audio_clip.close()
        # Remove overlay audio file
        os.remove(overlay_audio_path)

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
    sample_original_text_segments = [
        {'original_timestamps': (0, 959), 'text': 'Я просыпаюсь утром'},
        {'original_timestamps': (1156, 2656), 'text': 'и хочу достать свой телефон.'},
        {'original_timestamps': (3379, 4686), 'text': 'Но я знаю, что даже если бы я'},
        {'original_timestamps': (4868, 6667), 'text': 'увеличил яркость на экране телефона.'},
        {'original_timestamps': (7137, 8161), 'text': 'Этого не будет достаточно.'},
        {'original_timestamps': (8526, 10176), 'text': 'чтобы вызвать резкий подъем кортизола.'},
        {'original_timestamps': (10314, 10844), 'text': 'и для меня.'},
        {'original_timestamps': (11329, 11605), 'text': 'чтобы'},
        {'original_timestamps': (11753, 12289), 'text': 'может быть.'},
        {'original_timestamps': (12516, 18409),
         'text': 'быть наиболее бодрым и сосредоточенным в течение дня и оптимизировать свой сон ночью. Так что я делаю так: я встаю с кровати.'},
        {'original_timestamps': (18707, 19862), 'text': 'и выхожу на улицу.'},
        {'original_timestamps': (20219, 20852), 'text': 'А если это.'},
        {'original_timestamps': (21400, 21800), 'text': 'правильно?'},
        {'original_timestamps': (21952, 22685), 'text': 'ясный день.'},
        {'original_timestamps': (23332, 25872), 'text': 'и солнце низко в небе или солнце уже.'},
        {'original_timestamps': (26078, 28440),
         'text': 'начинает подниматься над горизонтом, то, как мы говорим, угол падения солнечного света мал.'},
        {'original_timestamps': (28722, 29663), 'text': 'И я знаю, что я'},
        {'original_timestamps': (30183, 31453), 'text': 'вышел на улицу в правильное время.'},
        {'original_timestamps': (31741, 32804), 'text': 'Если небо в облаках.'},
        {'original_timestamps': (32920, 34074), 'text': 'и я не вижу солнца.'}, {'original_timestamps': (34787, 41637),
                                                                                 'text': 'Я также понимаю, что делаю правильное дело, потому что, оказывается, особенно в облачные дни, нужно выходить на улицу и получать как можно больше световой энергии или фотонов в глаза.'},
        {'original_timestamps': (42425, 44105), 'text': 'Но предположим, что день очень ясный.'},
        {'original_timestamps': (44315, 46013), 'text': 'и я вижу, где находится солнце.'},
        {'original_timestamps': (46437, 48854), 'text': 'Мне не нужно смотреть прямо на солнце.'},
        {'original_timestamps': (49252, 49530), 'text': 'Если оно'},
        {'original_timestamps': (49911, 51078), 'text': 'Очень низко на горизонте.'},
        {'original_timestamps': (51428, 55109),
         'text': 'Я могу это сделать, потому что это не будет очень больно для моих глаз.'},
        {'original_timestamps': (55491, 56752), 'text': 'солнце становится немного ярче.'}
    ]
    sample_translated_nonsilent_timestamps = [
        [3043, 4511], [7500, 9426], [13213, 15372], [18204, 20649],
        [24339, 25938], [29985, 32316], [36062, 36990], [40766, 41376],
        [44147, 44922], [48805, 57938], [61754, 63118], [66955, 67933],
        [71681, 72338], [76198, 77228], [80935, 83596], [87567, 92973],
        [96902, 98372], [101201, 103323], [107120, 108536], [112418, 113909],
        [117799, 129597], [133398, 136076], [139959, 142185], [146120, 148461],
        [152369, 153287], [156001, 157753], [161634, 165920], [169736, 171835]
    ]
    project_id = "07fsfECkwma6fVTDyqQf"
    video_path = f"{project_id}.mp4"
    audio_path = f"{project_id}-translated.mp3"
    os.remove(f"{project_id}-translated.mp4")
    overlay_audio_to_video(
        original_video_path=video_path,
        translated_audio_path=audio_path,
        original_text_segments_with_timestamps=sample_original_text_segments,
        translated_nonsilent_timestamps=sample_translated_nonsilent_timestamps,
        project_id=project_id,
        silent_original_audio=True,
        show_logs=True
    )
