import time

import httpcore
from googletrans import Translator
from langdetect import detect, LangDetectException
import random
import re

perform_translation = False

with open('ciphix NLP/data.csv', 'r') as file:
    text = file.readlines()

random_subset = random.sample(text, len(text) // 1)  # TODO: work only with subset?

print(len(text))
translator = Translator()

translated = []
i = 0
while i < len(random_subset):
    line = text[i]
    lang = 'idk'
    cleaned_line = re.sub(r'\S+',  # match with any non-white space
                          lambda x: '' if '@' in x.group()
                          or '#' in x.group()
                          or 'http' in x.group()
                          else x.group(), line)  # Don't determine lang based on urls and mentions
    try:
        lang = detect(cleaned_line)
    except LangDetectException:
        pass  # empty string
    if lang == 'en':
        translated.append(line)
    else:
        if perform_translation:
            try:
                translated.append(translator.translate(line, dest='en').text)
            except httpcore._exceptions.ReadTimeout:
                print("ReadTimeout. Retrying in 5 sec...")
                time.sleep(5)
                continue

    if i % max(1, len(text) // 1000) == 0:
        print(f"{i / (len(text) // 100):.1f}%")

    i += 1

filename = 'ciphix NLP/translated_data.csv' if perform_translation else 'ciphix NLP/untranslated_data.csv'

with open(filename, 'w') as f:
    f.write(''.join(translated))

print("Done!")
