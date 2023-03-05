import math

from gensim import corpora
from gensim import models
from gensim.models import LdaModel
from gensim.test.utils import datapath
import os

from matplotlib import pyplot as plt
from wordcloud import WordCloud

from specificity import Specificity
from sanitization import sanitize_tokenize


class LDA:
    """Trains or loads an Latent Dirichlet Allocation on the tokens.
    """

    def __init__(self, tokens, num_topics=50, num_top_topics=10, num_passes=3, ):
        """Performs LDA on the dataset represented by `tokens`

        :param tokens: a list of (list of str) for the tokens in each document in the dataset
        :param num_topics: the total number of topics to create
        :param num_top_topics: the number of top topics to present
        :param num_passes: the number of times the whole dataset is used in training
        """
        self.num_topics = num_topics
        self.num_top_topics = num_top_topics

        self.specificity = Specificity(tokens)

        if os.path.exists('ciphix NLP/lda_model.lda') \
                and os.path.exists('ciphix NLP/dictionary.pickle'):
            print("loading LDA")
            file = datapath(os.getcwd() + "/ciphix NLP/dictionary.pickle")
            self.dictionary = corpora.Dictionary.load(file)
            file = datapath(os.getcwd() + "/ciphix NLP/lda_model.lda")
            self.lda_model = LdaModel.load(file)
        else:
            print("training LDA")
            # Create a dictionary of the tokens
            self.dictionary = corpora.Dictionary(tokens)

            # Create a corpus of the tokens
            corpus = [self.dictionary.doc2bow(line) for line in tokens]

            # Train an LDA model on the corpus
            self.lda_model = models.ldamodel.LdaModel(corpus=corpus,
                                                      id2word=self.dictionary,
                                                      num_topics=num_topics,
                                                      passes=num_passes,
                                                      alpha='auto',
                                                      random_state=42
                                                      )

            # Save model to disk.
            file = datapath(os.getcwd() + "/ciphix NLP/lda_model.lda")
            self.lda_model.save(file)

            file = datapath(os.getcwd() + "/ciphix NLP/dictionary.pickle")
            self.dictionary.save(file)

    def best_topic(self, line_tokens):
        """Find topic best matching a tweet
        :param line_tokens: the tokens of one document
        """
        topic_probs = self.lda_model.get_document_topics(self.dictionary.doc2bow(line_tokens))
        return max(topic_probs, key=lambda pair: pair[1])

    def best_representatives(self, tokens, num_tweets_to_check=100000):
        """Find tweet best matching a topic

        :param tokens: list of (list of str) all documents, tokenized
        :param num_tweets_to_check: Number of documents in the dataset to scour for a good representative
        """
        best_topic_probs = {topic_id: (-1, 0) for topic_id in range(self.num_topics)}
        for i in range(min(len(tokens), num_tweets_to_check)):
            line_tokens = tokens[i]
            bow = self.dictionary.doc2bow(line_tokens)
            topic_probs = self.lda_model.get_document_topics(bow)
            for topic_id, topic_prob in topic_probs:
                if topic_prob > best_topic_probs[topic_id][1]:
                    best_topic_probs[topic_id] = (i, topic_prob)
        return best_topic_probs

    def get_score(self, word, prob):
        """Get the weight of a word, which depends on its specificity score.

        The conditional `prob` P(word|topic) is modulated with the specificity score,
        which is the inverse of word frequency P(word).

        :param word: word for which to ge the score
        :param prob: The conditional probability of the word given a topic
        :return: the weight of the word
        """
        freq = self.specificity.word2freq(word)
        if freq < 1. / self.specificity.global_size * 2:
            return 0
        return prob / (freq + .0001)

    def print_topic(self, topic_index, num_topic_words=10):
        """Print topics most specific keywords (i.e. P(word|model) / P(word_global) or other specificity score)

        :param topic_index: The topic id of the topic to print
        :param num_topic_words: The number of terms to display for the topic
        """
        topic = self.lda_model.get_topics()[topic_index]
        weighted = []
        for i, prob in enumerate(topic):
            word = self.dictionary[i]
            # weighted.append((word, prob / word2freq(word), prob))
            # weighted.append((word, prob / (word2freq(word) - math.log2(word2freq(word))), prob))
            # weighted.append((word, prob**2 / word2freq(word), prob))
            weighted.append((word, self.get_score(word, prob), prob))
        weighted.sort(key=lambda pair: pair[1], reverse=True)
        print(f"Topic {topic_index}:")
        top_keywords = [f"{word} ({prob * 100:.2f}% {weight:.2f})" for word, weight, prob in
                        weighted[0:num_topic_words]]
        print(', '.join(top_keywords))

    def print_top_topics(self, lines, tokens, num_topic_words=10):
        """Print the most important topics, and a representative document for each

        :param lines: The unprocessed input documents of the dataset
        :param tokens: The tokenized input documents of the dataset
        :param num_topic_words: The number of terms to display for the topic
        """
        representative_tweets = self.best_representatives(tokens, num_tweets_to_check=10000)

        # Get topics as list of tuples of word and probability
        topics = self.lda_model.show_topics(self.num_top_topics, num_words=1, formatted=False)

        for topic_index, topic in topics:
            print("")
            self.print_topic(topic_index, num_topic_words)
            print(self.lda_model.print_topic(topic_index))
            best_line_idx, prob = representative_tweets[topic_index]
            if best_line_idx >= 0:
                print(lines[best_line_idx])
                assert (self.best_topic(tokens[best_line_idx])[0] == topic_index)

    def visualize_topics(self, num_topic_words=30):
        """Create and display a figure of the top topics and their words as a word cloud

        :param num_topic_words: The number of terms to display for the topic
        """
        topics = self.lda_model.show_topics(self.num_top_topics, num_words=1, formatted=False)

        grid_size = int(math.ceil(math.sqrt(self.num_top_topics)))
        fig, axs = plt.subplots(grid_size, grid_size)

        for x in range(grid_size):
            for y in range(grid_size):
                axs[x, y].axis("off")

        for topic_index, (topic_id, topic) in enumerate(topics):
            word2size = {}
            # Get the words that we want to include in the word cloud and their corresponding sizes
            topic = self.lda_model.get_topics()[topic_id]
            weighted = []
            for word_index, prob in enumerate(topic):
                word = self.dictionary[word_index]
                word2size[word] = self.get_score(word, prob)

            # Create the WordCloud object with the desired properties
            wc = WordCloud(background_color="white", max_words=num_topic_words)

            # Generate the word cloud from the words and their sizes
            wc.generate_from_frequencies(word2size)

            # Display the word cloud
            axs[topic_index // grid_size, topic_index % grid_size].imshow(wc, interpolation="bilinear")

        plt.show()

    def update(self, tokens, chunksize=None, decay=None, offset=None, passes=None, update_every=None,
               eval_every=None, iterations=None, gamma_threshold=None, chunks_as_numpy=False):
        """Train on new tokens

        :param tokens: list of (list of str) tokens for each document in the new corpus
        """
        # Create a corpus of the tokens
        corpus = [self.dictionary.doc2bow(line) for line in tokens]

        # Update LDA with new documents
        self.lda_model.update(corpus, chunksize=chunksize, decay=decay, offset=offset, passes=passes,
                              update_every=update_every, eval_every=eval_every, iterations=iterations,
                              gamma_threshold=gamma_threshold, chunks_as_numpy=chunks_as_numpy)

    def classify(self, line):
        """Classify new doc

        :param line: The document to classify (untokenized)
        :return: The topic index of the most likely topic
        """
        # Preprocess the new document
        [new_doc] = sanitize_tokenize([line])

        # Get the topic distribution for the new document
        doc_topics = self.lda_model.get_document_topics(self.dictionary.doc2bow(new_doc))

        # Sort the topic distribution in descending order of probability
        doc_topics.sort(key=lambda x: x[1], reverse=True)

        # Get the index of the topic with the highest probability
        most_likely_topic = doc_topics[0][0]  # TODO: is the first of the topics returned always the most likely?

        return most_likely_topic
