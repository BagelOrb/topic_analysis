from googletrans import Translator
from langdetect import detect, LangDetectException
import random

with open('ciphix NLP/data.csv', 'r') as file:
    text = file.readlines()

random_subset = random.sample(text, len(text) // 10)  # TODO: Try to convert more into English!

print(len(text))
translator = Translator()

translated = []
for i, line in enumerate(text):
    lang = 'idk'
    try:
        lang = detect(line)
    except LangDetectException:
        pass  # empty string
    if lang == 'en':
        translated.append(line)
    else:
        translated.append(translator.translate(line, dest='en').text)
    if i % max(1, len(text) // 1000) == 0:
        print(f"{i / (len(text) // 100):.1f}%")

with open('ciphix NLP/translated_data.csv', 'w') as f:
    f.write(''.join(translated))

print("Done!")
