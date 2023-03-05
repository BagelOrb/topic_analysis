import os.path
import pickle
from sanitization import sanitize_tokenize
import csv
import nltk
import gensim.models
from nltk.corpus import brown
from functools import reduce


class Specificity:
    '''
    Get specificity scores for a word based on their frequency in normal language.
    '''

    def __init__(self, tokens):
        # Initialize global_tokens
        if os.path.exists('ciphix NLP/global_tokens.pickle'):
            print("loading specificity info")
            with open('ciphix NLP/global_tokens.pickle', 'rb') as file:
                self.global_tokens = pickle.load(file)
        else:
            print("gathering global specificity data")
            try:
                nltk.data.find('brown')
            except LookupError:
                nltk.download('brown')

            self.global_tokens = sanitize_tokenize(brown.words())  # Use brown corpus as single tweet

            # Add random twitter data to the curpus
            lines = []
            #  Downloaded from https://www.kaggle.com/datasets/kazanova/sentiment140/discussion/60512
            with open('ciphix NLP/training.1600000.processed.noemoticon.csv', 'r', encoding='ISO-8859-1') as file:
                reader = csv.reader(file)
                for line in reader:
                    lines.append(line[5])  # Column 5 is the actual tweet

            rnd_twitter_tokens = sanitize_tokenize(lines)
            self.global_tokens.extend(rnd_twitter_tokens)

            # Add our tokens to the set so we don't get problems with unknown tokens
            self.global_tokens.extend(tokens)

            with open('ciphix NLP/global_tokens.pickle', 'wb') as file:
                pickle.dump(self.global_tokens, file)

        # Initialize self.global_freq_dist
        if os.path.exists('ciphix NLP/freqs.csv'):
            print("loading frequency data")
            # Create mapping from words to their frequency in 'normal language'
            self.global_fdist = {}

            with open('ciphix NLP/freqs.csv') as csvfile:
                reader = csv.reader(csvfile)
                for [word, freq] in reader:
                    self.global_fdist[word] = float(freq)

            assert (len(self.global_fdist))  # We should have loaded actual data
        else:
            print("creating frequency data")
            from nltk.probability import FreqDist

            # Create a frequency distribution of all words from a different context then our current dataset
            self.global_fdist = FreqDist()
            for line in self.global_tokens:
                for word in line:
                    self.global_fdist[word] += 1

            # Save it to file
            with open('ciphix NLP/freqs.csv', 'w') as file:
                writer = csv.writer(file)
                for word in self.global_fdist:
                    writer.writerow([word, self.global_fdist.freq(word)])

        self.global_size = reduce(lambda count, l: count + len(l), self.global_tokens, 0)

        # local_size = reduce(lambda count, l: count + len(l), tokens, 0)

    def word2freq(self, word):
        """Get the frequency of a word"""
        try:
            return self.global_fdist[word]
            # return local_fdist[word]
        except KeyError:  # word didn't occur in our dataset
            return 1. / self.global_size
