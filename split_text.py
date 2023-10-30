import re

MAX_SYMBOLS_NUMBER = 5000


def split_text(text):
    result = []
    text_words = re.split('(?<=[.!?])', text)
    temp = text_words[0]
    for word in text_words[1:]:
        if len(temp + word) > MAX_SYMBOLS_NUMBER:
            result.append(temp)
            temp = word
        else:
            temp += f' {word}'
    result.append(temp)
    return result
