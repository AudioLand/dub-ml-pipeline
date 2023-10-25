import openai

from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

translate_text_exception = Exception(
    "Error while translating text"
)


def translate_text(language: str, text: str, project_id: str):
    """
      Translates a given text into the specified language using OpenAI's model.

      Parameters:
      - language (str): The target language for translation.
      - text (str): The text to be translated.

      Returns:
      - str: Translated text or original text if translation is not possible.
      """

    prompt = (f"Translate the below text in {language}. Text: {text} "
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
        print(f"Error during translation: {e}")
        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status="translationError",
            translated_file_link=""
        )
        raise translate_text_exception
