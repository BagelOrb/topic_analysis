import nltk
import nltk.tokenize
import nltk.corpus
import nltk.stem
import emoji
import re

URL_RE = re.compile(r'^https?://', re.IGNORECASE)


def is_url(word):
    """
    :return: Whether the string is an url
    """
    return URL_RE.search(word) is not None


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
        words = [word for word in words if word not in stop_words]  # remove stopwords before (faulty) lemmatization
        words = [lemmatizer.lemmatize(word) for word in words if word.isalpha()]
        tokens.append(words)

    return tokens
