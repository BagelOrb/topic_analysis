import time

import httpcore
from googletrans import Translator
from langdetect import detect, LangDetectException
import random

with open('ciphix NLP/data.csv', 'r') as file:
    text = file.readlines()

random_subset = random.sample(text, len(text) // 10)  # TODO: Try to convert more into English!

print(len(text))
translator = Translator()

translated = []
i = 0
while i < len(text):
    line = text[i]
    lang = 'idk'
    try:
        lang = detect(line)
    except LangDetectException:
        pass  # empty string
    if lang == 'en':
        translated.append(line)
    else:
        try:
            translated.append(translator.translate(line, dest='en').text)
        except httpcore._exceptions.ReadTimeout:
            print("ReadTimeout. Retrying in 5 sec...")
            time.sleep(5)
            continue

    if i % max(1, len(text) // 1000) == 0:
        print(f"{i / (len(text) // 100):.1f}%")

    i += 1

with open('ciphix NLP/translated_data.csv', 'w') as f:
    f.write(''.join(translated))

print("Done!")
