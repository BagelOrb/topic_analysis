import nltk
import nltk.tokenize
import nltk.corpus
import nltk.stem
import nltk.tag
import emoji
import re

URL_RE = re.compile(r'^https?://', re.IGNORECASE)


def is_url(word):
    """
    :return: Whether the string is an url
    """
    return URL_RE.search(word) is not None


def lemmatize(word, tag, lemmatizer):
    match tag:
        case 'NOUN':
            return lemmatizer.lemmatize(word, 'n')
        case 'VERB':
            return lemmatizer.lemmatize(word, 'v')
        case 'ADV':
            return lemmatizer.lemmatize(word, 'r')
        case 'ADJ':
            return lemmatizer.lemmatize(word, 'a')
        # TODO: what about satellite adjectives? They don't appear in the universal tag set?
        case _:
            return word


def sanitize_tokenize(lines):
    """
    Remove urls, mentions, email addresses, emoji and empty lines.
    Tokenize the input.

    TODO: lemmatizes was into wa! Not the best lemmatization

    :param lines: List of documents / tweets.
    :return: List of tokens for each line.
    """

    lines = [line for line in lines if line]  # Remove all empty lines in input. Keep mapping between input and output.

    # Download the NLTK stopwords and lemmatizer
    try:
        nltk.data.find('stopwords')
    except LookupError:
        nltk.download('stopwords')

    nltk.download('averaged_perceptron_tagger')
    nltk.download('universal_tagset')

    stop_words = set(nltk.corpus.stopwords.words('english'))
    stop_words.update(['u', 'dm'])
    lemmatizer = nltk.stem.WordNetLemmatizer()

    tokens = []
    for line in lines:
        if not line:
            continue  # skip empty lines
        line = re.sub(r'\S+',  # match with any non-white space
                      lambda x: '' if '@' in x.group() or  # Remove @mentions and email@addresses.completely
                                      '&' in x.group() or  # Remove special characters such as &amp
                                      is_url(x.group()) else x.group(), line)  # Remove urls
        emoji.replace_emoji(line)  # Remove all emoji

        words = nltk.tokenize.word_tokenize(line.lower())

        tagged = nltk.tag.pos_tag(words, tagset='universal')

        words = [lemmatize(word, tag, lemmatizer) for word, tag in tagged if word.isalpha()]
        words = [word for word in words if word not in stop_words]
        tokens.append(words)

    return tokens
