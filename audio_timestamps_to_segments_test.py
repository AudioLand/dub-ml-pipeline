from pydub import AudioSegment

from text_to_speech import  add_audio_timestamps_to_segments


def extract_and_combine_fragments(audio_path, segments,  output_file='combined_audio.mp3', pause_duration_ms=1000):
    """
    Extracts fragments from an audio file and combines them into a new file with pauses.

    :param audio_path: Path to the original audio file.
    :param segments: A list of tuples with (start, end) times in milliseconds.
    :param pause_duration_ms: The duration of the pause to add between segments in milliseconds.
    :param output_file: The path to save the combined audio file.
    """
    # Load the original audio
    audio = AudioSegment.from_file(audio_path)

    # Create an empty AudioSegment for combining
    combined_audio = AudioSegment.silent(duration=0)

    # Duration of pause
    pause = AudioSegment.silent(duration=pause_duration_ms)

    # Extract and combine segments
    for start, end in segments:
        segment = audio[start:end]
        combined_audio += segment + pause

    # Export the combined audio to a file
    combined_audio.export(output_file, format="mp3")


# For local test
if __name__ == "__main__":
    sample_text_segments = [
        {'timestamp': [0.0, 2.28],
         'text': 'Языковые модели сегодня все еще ограничены.'},
        {'timestamp': [3.28, 5.04],
         'text': 'Эта информация может быть устаревшей.'},
        {'timestamp': [5.5, 5.9],
         'text': 'Ура!'},
        {'timestamp': [6.0, 15.0],
         'text': 'Этот текст может содержать полезные инструкции, но чтобы действительно ...'}
    ]
    add_audio_timestamps_to_segments('translated-test.mp3', sample_text_segments)
    segments_to_extract = [(start, end) for segment in sample_text_segments for start, end in [segment['audio_timestamp']]]
    print(segments_to_extract)
    print(sample_text_segments)
    extract_and_combine_fragments("translated-test.mp3", segments_to_extract)
