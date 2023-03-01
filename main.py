import csv
import nltk
from collections import Counter

import sanitization

# Read the CSV file and extract the text data
with open('translated_data.csv', 'r') as file:
    lines = file.readlines()

tokens = sanitization.sanitize_tokenize(lines)

# Determine the most prevalent topics in the text data
topic_counts = Counter(tokens)
most_common_topics = topic_counts.most_common(10)

print(most_common_topics)
