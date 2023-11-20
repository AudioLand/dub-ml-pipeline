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
    Transforms the given dictionary of timestamps and texts to the string, where segments are divided by ] symbol.

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
    original_text_segments: list,
    project_id: str,
    show_logs: bool = False
) -> list[dict]:
    """
    Translates a given text segment into the specified language.

    Parameters:
    - language (str): The target language for translation.
    - original_dictionary (list): The list of dictionaries with original text segments and timestamps.
    - project_id (str): The ID of the project.

    Returns:
    - list: The list of dictionaries with translated text segments and timestamps.
    """

    formatted_segments_str = format_original_segments_to_special_str(original_text_segments)
    try:
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
            print(f"(translate_text) Translating completed, translated_text_chunks - {translated_text_chunks}")

        if show_logs:
            print(f"(translate_text) Splitting translated chunks to segments by ] symbol...")

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

            for i in range(min(original_segments_count, translated_segments_count)):
                print(f"\nOriginal segment: {original_text_segments[i]}")
                print(f"Translated segment: {translated_text_segments[i]}\n")

            raise Exception(f"Segments count not match")

        for segment_index in range(len(translated_text_segments)):
            translated_segment = translated_text_segments[segment_index]
            # original_text_segments[segment_index]['text'] = translated_segment[1: len(translated_segment)]
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
    # original_text_segments = [
    #     {'timestamp': [0.0, 4.5], 'text': ' The next generation of Rayban meta smart glasses.'},
    #     {'timestamp': [4.5, 14.52],
    #      'text': ' These are the first smart glasses that are built in shipping with meta AI in them.'},
    #     {'timestamp': [14.52, 23.5],
    #      'text': " Starting in the US, you're going to get this state of the art AI that you can interact with, hands free, wherever you go."},
    #     {'timestamp': [23.5, 26.0], 'text': " We're going to be issuing a free software update"},
    #     {'timestamp': [26.0, 27.8], 'text': ' to the glasses that makes them multimodal.'}
    # ]
    original_text_segments = [
        {'timestamp': [0.0, 4.52],
         'text': ' I wake up in the morning and I want to reach for my phone, but I know that even if I were'},
        {'timestamp': [4.52, 9.8],
         'text': " to crank up the brightness on that phone screen, it's not bright enough to trigger that cortisol"},
        {'timestamp': [9.8, 15.42],
         'text': ' spike and for me to be at my most alert and focus throughout the day and to optimize my'},
        {'timestamp': [15.42, 16.42], 'text': ' sleep at night.'},
        {'timestamp': [16.42, 23.76],
         'text': " So what I do is I get out of bed and I go outside and if it's a bright clear day and the"},
        {'timestamp': [23.76, 26.08], 'text': ' sun is low in the sky, or the sun is,'},
        {'timestamp': [26.08, 27.2], 'text': ' you know, starting to get overhead,'},
        {'timestamp': [27.2, 28.72], 'text': ' what we call low solar angle,'},
        {'timestamp': [28.72, 31.76], 'text': " and I know I'm getting outside at the right time."},
        {'timestamp': [31.76, 34.8], 'text': " If there's cloud cover, and I can't see the sun,"},
        {'timestamp': [34.8, 36.4], 'text': " I also know I'm doing a good thing"},
        {'timestamp': [36.4, 38.56], 'text': ' because it turns out, especially on cloudy days,'},
        {'timestamp': [38.56, 40.64], 'text': ' you want to get outside and get as much light energy'},
        {'timestamp': [40.64, 42.4], 'text': ' or photons in your eyes.'},
        {'timestamp': [42.4, 44.32], 'text': " But let's say it's a very clear day,"},
        {'timestamp': [44.32, 45.36], 'text': ' and I can see where the'},
        {'timestamp': [45.36, 52.08],
         'text': " sun is. I do not need to stare directly into the sun. If it's very low in the sky, I might do that"},
        {'timestamp': [52.08, 56.48],
         'text': " because it's not going to be very painful to my eyes. However, if the sun is a little bit brighter,"}
    ]
    target_language = "Russian"
    project_id = "07fsfECkwma6fVTDyqQf"
    print(f"\nOriginal text segments - {original_text_segments}")
    translated_text = translate_text(
        language=target_language,
        original_text_segments=original_text_segments,
        project_id=project_id
    )
