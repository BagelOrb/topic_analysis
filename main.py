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

# ==============

new_lines = ["Good morning, how may we assist you?", "My pants are ripped up and it's all because of company X",
             "I'm trying to roll back the last update, but it keeps crashing when I try to start it back up. Somebody please help!"]

print("Classifying new lines")
for new_line in new_lines:
    topic_id = lda.classify(new_line)
    print('')
    print(new_line)
    lda.print_topic(topic_id)


# ==============

print("Performing update")
new_tokens = sanitization.sanitize_tokenize(new_lines)

lda.update(new_tokens)

print("Getting top topics")
lda.print_top_topics(lines, tokens)
