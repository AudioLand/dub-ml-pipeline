import re

import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.config import OPEN_AI_API_KEY
from config.logger import catch_error

# Set OpenAI API key
openai.api_key = OPEN_AI_API_KEY

translate_text_exception = Exception(
    "Error while translating text"
)

CONTEXT_TOKENS_COUNT = 4000

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CONTEXT_TOKENS_COUNT,
    chunk_overlap=0,
    separators=["."]
)

gpt_model = "gpt-4"
# gpt_model = "gpt-3.5-turbo"

translation_gpt_prompt = """
You are a professional text translator.
You understand the meaning of the text well.
You are able to select the most appropriate formulations so that they fit the context of the text you are translating.
I need you to translate the text below to {language} language.
If the text is already in {language}, you must write this text in the answer without translation.
If you are not able to translate this text, you must write this text in the answer without translation.
You must remain all [] symbols on their places in original text.
Your answer must be only translated text.

The text you need to translate to {language} language:
{text_chunk}
"""


def format_original_segments_to_special_str(original_text_segments: list[dict]) -> str:
    """
    Transforms the given dictionary of timestamps and texts to the string, where segments are divided by [ and ] symbols.

    Parameters:
    - original_text_segments (list[dict]) - the list of dictionaries with text segments and timestamps.

    Returns:
    - str: The string, where all text segments are divided by \n symbol.
    """

    formatted_original_text = ""
    for segment in original_text_segments:
        formatted_original_text += f"[{segment['text']}]"
    return formatted_original_text


def split_text_to_chunks(original_text: str, project_id: str) -> list[str]:
    """
    Splits a given text into chunks.

    Parameters:
    - text (str): The text to split.

    Returns:
    - list[str]: The list of string text chunks.
    """

    try:
        texts = text_splitter.split_text(original_text)
        return texts
    except Exception as e:
        catch_error(
            tag="split_text_to_chunks",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


def translate_text_chunk_with_gpt(language: str, text_chunk: str, project_id: str) -> str:
    """
    Translates a given text into the specified language using OpenAI's model.

    Parameters:
    - language (str): The target language for translation.
    - text (str): The text to be translated.

    Returns:
    - str: Translated text or original text if translation is not possible.
      """

    try:
        query_content = translation_gpt_prompt.format(
            language=language,
            text_chunk=text_chunk
        )
        response = openai.ChatCompletion.create(
            model=gpt_model,
            messages=[{
                "role": "user",
                "content": query_content
            }],
        )

        translated_text = response['choices'][0]['message']['content']
        return translated_text

    except Exception as e:
        catch_error(
            tag="translate_text_chunk_with_gpt",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


def translate_text_chunks(language: str, text_chunks: list[str], project_id: str) -> list[str]:
    """
    Passes the given text chunks to the GPT.

    Parameters:
    - language (str): The target language for translation.
    - text (str): The text to be translated.

    Returns:
    - list[str]: The list of translated text chunks.
    """
    try:
        translated_text_chunks = []

        for chuck in text_chunks:
            translated_chunk = translate_text_chunk_with_gpt(
                language=language,
                text_chunk=chuck,
                project_id=project_id
            )
            translated_text_chunks.append(translated_chunk)

        return translated_text_chunks
    except Exception as e:
        catch_error(
            tag="translate_text_chunks",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


def translate_text(
    language: str,
    original_text_segments: list[dict],
    project_id: str,
    show_logs: bool = False
) -> list[dict]:
    """
    Translates a given text segment into the specified language.

    Parameters:
    - language (str): The target language for translation.
    - original_text_segments (list[dict]): The list of dictionaries with original text segments and timestamps.
    - project_id (str): The ID of the project.

    Returns:
    - list: The list of dictionaries with translated text segments and timestamps.
    """

    try:
        if show_logs:
            print(f"(translate_text) Translating original text segments - {original_text_segments}")

        formatted_segments_str = format_original_segments_to_special_str(original_text_segments)

        if show_logs:
            print(f"(translate_text) Splitting text by {CONTEXT_TOKENS_COUNT} tokens...")

        text_chunks = split_text_to_chunks(
            original_text=formatted_segments_str,
            project_id=project_id
        )

        if show_logs:
            print(f"(translate_text) Splitting completed, text_chunks - {text_chunks}")

        if show_logs:
            print(f"(translate_text) Translating text chunks...")
        translated_text_chunks = translate_text_chunks(
            language=language,
            text_chunks=text_chunks,
            project_id=project_id
        )
        if show_logs:
            print(f"(translate_text) Translation completed, translated_text_chunks - {translated_text_chunks}")

        if show_logs:
            print(f"(translate_text) Splitting translated chunks to segments by [ and ] symbols...")

        # Split translated text to get original segments
        final_translated_text = "".join(translated_text_chunks)
        translated_text_segments = re.findall(r"[^\[\]]+", final_translated_text)

        if show_logs:
            print(f"(translate_text) Splitting completed, translated_text_segments - {translated_text_segments}")

        original_segments_count = len(original_text_segments)
        translated_segments_count = len(translated_text_segments)

        # Check if segments count is different
        if original_segments_count != translated_segments_count:
            print(f"Original count: {original_segments_count}")
            print(f"Translated count: {translated_segments_count}")

            for segment_index in range(min(original_segments_count, translated_segments_count)):
                print(f"\nOriginal segment: {original_text_segments[segment_index]}")
                print(f"Translated segment: {translated_text_segments[segment_index]}\n")

            raise Exception(f"Segments count not match")

        for segment_index in range(len(translated_text_segments)):
            translated_segment = translated_text_segments[segment_index]
            original_text_segments[segment_index]['text'] = translated_segment

        return original_text_segments
    except Exception as e:
        catch_error(
            tag="translate_text",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


if __name__ == "__main__":
    sample_original_text_segments = [
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
    target_language = "Russian"
    project_id = "07fsfECkwma6fVTDyqQf"
    translated_text = translate_text(
        language=target_language,
        original_text_segments=sample_original_text_segments,
        project_id=project_id
    )
    print(translated_text)
