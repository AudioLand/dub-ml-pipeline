import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.logger import catch_error

translate_text_exception = Exception(
    "Error while translating text"
)


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
            separators=[" ", ",", "\n", "."]
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
              f"Start your answer with the translated text. Your answer:")

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


def translation_pipeline(language: str, original_text: str, project_id: str):
    """
    Starts the translation pipeline.

    Parameters:
    - language (str): The target language for translation.
    - text (str): The text to be translated.

    Returns:
    - str: Translated text or original text if translation is not possible.
    """
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
        final_translated_text = " ".join(translated_text_chunks)
        return final_translated_text
    except Exception as e:
        catch_error(
            tag="translation_pipeline",
            error=e,
            project_id=project_id
        )
        raise translate_text_exception


if __name__ == "__main__":
    sample_text = """[Generated with ChatGPT]
    Confidential Document - For Internal Use Only

    Date: July 1, 2023

    Subject: Updates and Discussions on Various Topics

    Dear Team,
    I hope this email finds you well. In this document, I would like to provide you with some important updates and discuss various topics that require our attention. Please treat the information contained herein as highly confidential.
    Security and Privacy Measures
    As part of our ongoing commitment to ensure the security and privacy of our customers' data, we have implemented robust measures across all our systems. We would like to commend John Doe (email: john.doe@example.com) from the IT department for his diligent work in enhancing our network security. Moving forward, we kindly remind everyone to strictly adhere to our data protection policies and guidelines. Additionally, if you come across any potential security risks or incidents, please report them immediately to our dedicated team at security@example.com.
    HR Updates and Employee Benefits
    Recently, we welcomed several new team members who have made significant contributions to their respective departments. I would like to recognize Jane Smith (SSN: 049-45-5928) for her outstanding performance in customer service. Jane has consistently received positive feedback from our clients. Furthermore, please remember that the open enrollment period for our employee benefits program is fast approaching. Should you have any questions or require assistance, please contact our HR representative, Michael Johnson (phone: 418-492-3850, email: michael.johnson@example.com).
    Marketing Initiatives and Campaigns
    Our marketing team has been actively working on developing new strategies to increase brand awareness and drive customer engagement. We would like to thank Sarah Thompson (phone: 415-555-1234) for her exceptional efforts in managing our social media platforms. Sarah has successfully increased our follower base by 20% in the past month alone. Moreover, please mark your calendars for the upcoming product launch event on July 15th. We encourage all team members to attend and support this exciting milestone for our company.
    Research and Development Projects
    In our pursuit of innovation, our research and development department has been working tirelessly on various projects. I would like to acknowledge the exceptional work of David Rodriguez (email: david.rodriguez@example.com) in his role as project lead. David's contributions to the development of our cutting-edge technology have been instrumental. Furthermore, we would like to remind everyone to share their ideas and suggestions for potential new projects during our monthly R&D brainstorming session, scheduled for July 10th.
    Please treat the information in this document with utmost confidentiality and ensure that it is not shared with unauthorized individuals. If you have any questions or concerns regarding the topics discussed, please do not hesitate to reach out to me directly.
    Thank you for your attention, and let's continue to work together to achieve our goals.
    Best regards,

    Jason Fan
    Cofounder & CEO
    Psychic
    jason@psychic.dev
    """
    print(sample_text)
    target_language = "Russian"
    project_id = "0G8PmZUbaslMcOaAjPJb"
    translated_text = translation_pipeline(
        language=target_language,
        original_text=sample_text,
        project_id=project_id
    )
    print(translated_text)
