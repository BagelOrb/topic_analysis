from os import environ
import random
from google.cloud import translate
import html  # for parsing response

project_id = 'topic-analysis-379505'

parent = f"projects/{project_id}"
client = translate.TranslationServiceClient()


with open('ciphix NLP/data.csv', 'r') as file:
    text = file.readlines()

random_subset = random.sample(text, len(text) // 10)  # TODO: Try to convert more into English!


print(len(text))

translated = []
for i, line in enumerate(random_subset):
    response = client.translate_text(
        contents=[line],
        target_language_code='en',
        parent=parent,
    )
    translated_line = ''
    for translation in response.translations:
        translated_line += html.unescape(translation.translated_text)
    translated.append(translated_line)

    # Print progress
    if i % max(1, len(text) // 1000) == 0:
        print(f"{i / (len(text) // 100):.1f}%")

with open('ciphix NLP/translated_data.csv', 'w') as f:
    f.write(''.join(translated))

print("Done!")
