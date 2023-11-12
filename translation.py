import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.logger import catch_error

import re

translate_text_exception = Exception(
    "Error while translating text"
)


def convert_original_text_to_special_format(original_dictionary: list):
    """
    Transforms the given dictionary of timestamps and texts to the string, where segments are divided by ] symbol.

    Parameters:
        - original_dictionary (list) - the list of dictionaries with text segments and timestamps.
    Returns:
    - str: .The string, where all text segments are divided by ] symbol.
    """

    original_text_in_format = ""
    for text_and_timestamp in original_dictionary:
        original_text_in_format = "".join([original_text_in_format, f"]{text_and_timestamp['text']}]\n"])
    return original_text_in_format


def split_text_to_chunks(original_text: str, project_id: str):
    """
    Splits a given text into chunks.

    Parameters:
    - text (str): The text to be splited.

    Returns:
    - list[str]: The list of string text chunks.
    """

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=0,
            separators=["\n"]
        )
        texts = text_splitter.split_text(original_text)
        return texts
    except Exception as e:
        catch_error(
            tag="split_text_to_chunks",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


def translate_text_chunk_with_gpt(language: str, text_chunk: str, project_id: str):
    """
    Translates a given text into the specified language using OpenAI's model.

    Parameters:
    - language (str): The target language for translation.
    - text (str): The text to be translated.

    Returns:
    - str: Translated text or original text if translation is not possible.
      """

    prompt = (f"Translate the below text in {language}. Text: {text_chunk} "
              f"If the text is already in {language}, just write this text in the answer without translation. "
              f"If you are not able to translate this text, also write this text in the answer without translation. "
              f"Start your answer with the translated text. Remain all ] and [ symbols from the original text. Your answer:")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
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


def translate_text_chunks(language: str, text_chunks: str, project_id: str):
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

        for text in text_chunks:
            translated_text_chunks.append(
                translate_text_chunk_with_gpt(
                    language=language,
                    text_chunk=text,
                    project_id=project_id
                )
            )

        return translated_text_chunks
    except Exception as e:
        catch_error(
            tag="translate_text_chunks_with_gpt",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


def translate_text(language: str, original_dictionary: list, project_id: str):
    """
    Translates a given text segment into the specified language.

    Parameters:
    - language (str): The target language for translation.
    - original_dictionary (list): The list of dictionaries with original text segments and timestamps.
    - project_id (str): The ID for the project.

    Returns:
    - list: The list of dictionaries with translated text segments and timestamps.
    """
    original_text = convert_original_text_to_special_format(original_dictionary)
    try:
        text_chunks = split_text_to_chunks(
            original_text=original_text,
            project_id=project_id
        )
        translated_text_chunks = translate_text_chunks(
            language=language,
            text_chunks=text_chunks,
            project_id=project_id
        )
        final_translated_text = "".join(translated_text_chunks)
        translated_text_segments = re.split(r"]\n", final_translated_text)

        for segment_number in range(len(translated_text_segments)):
            translated_segment = translated_text_segments[segment_number]
            original_dictionary[segment_number]['text'] = translated_segment[1: len(translated_segment)]

        return original_dictionary
    except Exception as e:
        catch_error(
            tag="translation_pipeline",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


if __name__ == "__main__":
    original_dictionary = [{'timestamp': [0.0, 4.5], 'text': ' The next generation of Rayban meta smart glasses.'},
                           {'timestamp': [4.5, 14.52],
                            'text': ' These are the first smart glasses that are built in shipping with meta AI in them.'},
                           {'timestamp': [14.52, 23.5],
                            'text': " Starting in the US, you're going to get this state of the art AI that you can interact with, hands free, wherever you go."},
                           {'timestamp': [23.5, 26.0], 'text': " We're going to be issuing a free software update"},
                           {'timestamp': [26.0, 27.8], 'text': ' to the glasses that makes them multimodal.'}]
    # sample_text = "] The next generation of Rayban meta smart glasses.]\n\
    #                ] These are the first smart glasses that are built in shipping with meta AI in them.]\n\
    #                ] Starting in the US, you're going to get this state of the art AI that you can interact with, hands free, wherever you go.]\n\
    #                ] We're going to be issuing a free software update]\n\
    #                ] to the glasses that makes them multimodal.]"

    target_language = "Russian"
    project_id = "0G8PmZUbaslMcOaAjPJb"
    print("\nOriginal text segments:\n", original_dictionary)
    translated_text = translate_text(
        language=target_language,
        original_dictionary=original_dictionary,
        project_id=project_id
    )

    print("\nTranslated text segments:\n", translated_text)
