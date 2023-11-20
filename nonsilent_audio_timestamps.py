import os

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def get_nonsilent_audio_timestamps(
    audio_file_path: str,
    min_silence_len_ms=200,
    silence_thresh=-30,
    padding=50
):
    """
    Detects pauses in an audio file and adds audio_timestamps to segments.

    :param audio_file_path: Path to the audio file.
    :param min_silence_len_ms: Minimum length of silence to consider as a pause in milliseconds.
    :param silence_thresh: Silence threshold in dB.
    :param padding: Additional time in milliseconds to add to the end of each segment.
    :return: A list of tuples where each tuple is (start, end) time of pauses.
    """
    audio = AudioSegment.from_file(audio_file_path)
    nonsilent_timestamps = detect_nonsilent(
        audio_segment=audio,
        min_silence_len=min_silence_len_ms,
        silence_thresh=silence_thresh
    )
    adjusted_speak_times = []
    for start, end in nonsilent_timestamps:
        segment_timestamps = [max(start - padding, 0), min(end + padding, len(audio))]
        adjusted_speak_times.append(segment_timestamps)

    return adjusted_speak_times
    # return nonsilent_timestamps

    # for segment, (start, end) in zip(text_segments, adjusted_speak_times):
    #     segment['audio_timestamp'] = [start, end]

    # Check the time difference between the end of one segment and the start of the next
    # for i in range(len(adjusted_speak_times) - 1):
    #     end_of_current = adjusted_speak_times[i][1]
    #     start_of_next = adjusted_speak_times[i + 1][0]
    #     time_diff = start_of_next - end_of_current
    #     if abs(time_diff - 3000) > 100:  # Allowing a 100ms deviation
    #         print(f'Time gap discrepancy between segments {i} and {i + 1}: {time_diff}ms')


if __name__ == "__main__":
    # sample_original_audio_file_path = "07fsfECkwma6fVTDyqQf.mp4"
    sample_translated_audio_file_path = "07fsfECkwma6fVTDyqQf-translated.mp3"
    nonsilent_timestamps = get_nonsilent_audio_timestamps(
        audio_file_path=sample_translated_audio_file_path,
        min_silence_len_ms=2000,
        padding=300
    )
    print(nonsilent_timestamps)
