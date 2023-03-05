from specificity import Specificity
import sanitization
import pickle
import os.path
from lda import LDA


# Read the CSV file and extract the text data
print("Loading data...")
with open('ciphix NLP/untranslated_data.csv', 'r') as file:
    lines = file.readlines()

lines = lines[0:len(lines) // 10]

if os.path.exists('ciphix NLP/tokens.pickle'):
    print("loading tokens")
    with open('ciphix NLP/tokens.pickle', 'rb') as file:
        tokens = pickle.load(file)
else:
    print("tokenizing")
    tokens = sanitization.sanitize_tokenize(lines)
    with open('ciphix NLP/tokens.pickle', 'wb') as file:
        pickle.dump(tokens, file)

print("Creating LDA...")
lda = LDA(tokens)

print("Getting top topics")
lda.print_top_topics(lines, tokens)

lda.visualize_topics()