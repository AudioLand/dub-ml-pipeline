import time

from elevenlabs import APIError, generate as generate_audio, set_api_key, RateLimitError

from config.config import ELEVEN_LABS_API_KEY

set_api_key(ELEVEN_LABS_API_KEY)

text_to_speech_exception = Exception(
    "Error while processing text to speech"
)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60


def generate_audio_with_elevenlabs_provider(
    output_audio_file_path: str,
    text_segments: list[dict],
    original_voice_id: str,
    pause_duration_ms: int = 1000,
    show_logs: bool = False
):
    try:
        pause_tag = f' <break time="{pause_duration_ms / 1000}s"/> '
        combined_text = "" + pause_tag

        if show_logs:
            print(f"(elevenlabs_provider) Combining text with break tags for {pause_duration_ms / 1000}s...")

        for segment in text_segments:
            combined_text += segment['text'] + pause_tag

        if show_logs:
            print(f"(elevenlabs_provider) Generating audio for combined text...")

        audio = generate_audio(
            text=combined_text,
            voice=original_voice_id,
            model="eleven_multilingual_v2"
        )

        with open(output_audio_file_path, 'wb') as f:
            f.write(audio)

        if show_logs:
            print(f"(elevenlabs_provider) Audio generation completed and saved to - {output_audio_file_path}")

    except APIError as error:
        print("(elevenlabs_provider) API Error:", str(error))

        # If too many requests to 11labs, wait and then try again
        if isinstance(error, RateLimitError):
            print(f"(elevenlabs_provider) Wait {DELAY_TO_WAIT_IN_SECONDS} seconds and then repeat request to 11labs...")
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return generate_audio_with_elevenlabs_provider(
                output_audio_file_path,
                text_segments,
                original_voice_id,
                pause_duration_ms,
            )
        raise text_to_speech_exception


# Example usage
if __name__ == "__main__":
    sample_text_segments = [
        {'original_timestamps': (0, 959), 'text': ' I wake up in the morning'},
        {'original_timestamps': (1156, 2656), 'text': ' and I want to reach for my phone.'},
        {'original_timestamps': (3379, 4686), 'text': ' But I know that even if I were to'},
        {'original_timestamps': (4868, 6667), 'text': ' crank up the brightness on that phone screen.'},
        {'original_timestamps': (7137, 8161), 'text': " It's not bright enough."},
        {'original_timestamps': (8526, 10176), 'text': ' to trigger that cortisol spike.'},
        {'original_timestamps': (10314, 10844), 'text': ' and for me.'},
        {'original_timestamps': (11329, 11605), 'text': ' to'},
        {'original_timestamps': (11753, 12289), 'text': ' be it might.'},
        {'original_timestamps': (12516, 18409),
         'text': ' most alert and focused throughout the day and to optimize my sleep at night. So what I do is I get out of bed.'},
        {'original_timestamps': (18707, 19862), 'text': ' and I go outside.'},
        {'original_timestamps': (20219, 20852), 'text': " And if it's a."},
        {'original_timestamps': (21400, 21800), 'text': ' right?'},
        {'original_timestamps': (21952, 22685), 'text': ' clear day.'},
        {'original_timestamps': (23332, 25872), 'text': ' and the sun is low in the sky or the sun is.'},
        {'original_timestamps': (26078, 28440),
         'text': ' you know, starting to get overhead, what we call low solar angle.'},
        {'original_timestamps': (28722, 29663), 'text': " And I know I'm"},
        {'original_timestamps': (30183, 31453), 'text': ' getting outside at the right time.'},
        {'original_timestamps': (31741, 32804), 'text': " If there's cloud cover."},
        {'original_timestamps': (32920, 34074), 'text': " and I can't see the sun."},
        {'original_timestamps': (34787, 41637),
         'text': " I also know I'm doing a good thing because it turns out, especially on cloudy days, you want to get outside and get as much light energy or photons in your eyes."},
        {'original_timestamps': (42425, 44105), 'text': " But let's say it's a very clear day."},
        {'original_timestamps': (44315, 46013), 'text': ' and I can see where the sun is.'},
        {'original_timestamps': (46437, 48854), 'text': ' I do not need to stare directly into the sun.'},
        {'original_timestamps': (49252, 49530), 'text': " If it's"},
        {'original_timestamps': (49911, 51078), 'text': ' Very low in the sky.'},
        {'original_timestamps': (51428, 55109),
         'text': " I might do that because it's not going to be very painful to my eyes."},
        {'original_timestamps': (55491, 56752), 'text': ' sun is a little bit brighter.'}
    ]
    output_audio_file_path = "translated-test.mp3"
    original_voice_id = "N2lVS1w4EtoT3dr4eOWO"
    generate_audio_with_elevenlabs_provider(
        output_audio_file_path=output_audio_file_path,
        text_segments=sample_text_segments,
        original_voice_id=original_voice_id,
        pause_duration_ms=1000,
        show_logs=True
    )
