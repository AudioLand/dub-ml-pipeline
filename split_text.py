import re

MAX_SYMBOLS_NUMBER = 5000

# Divides a long string into chunks of no more than 5000 characters
def split_text(text):
    text = text.strip() # 
    result = []
    text_words = re.split('(?<=[.!?])', text)
    temp = text_words[0]
    for word in text_words[1:]:
        if len(temp + word) > MAX_SYMBOLS_NUMBER:
            result.append(temp.strip())
            temp = word
        else:
            temp += f' {word}'
    result.append(temp.strip())
    return result
