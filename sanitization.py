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


def lemmatize(word, tag, lemmatizer, use_nouns_only=True):
    """
    Lemmatize a word. E.g. "was"->"be" , "mice"->"mouse".

    Converts the universal tagset to the tags expected by the nltk lemmatizer.

    :param word: The word to lemmatize
    :param tag: The universal tag of the syntactical function. E.g. 'NOUN', 'VERB'
    :param lemmatizer: The nltk lemmatizer to use
    :param use_nouns_only: Whether to return an empty string for anything but a noun
    :return: the lemmatized word, or '' if not a noun and `use_nouns_only` is True
    """
    match tag:
        case 'NOUN':
            return lemmatizer.lemmatize(word, 'n')
        case 'VERB':
            return '' if use_nouns_only else lemmatizer.lemmatize(word, 'v')
        case 'ADV':
            return '' if use_nouns_only else lemmatizer.lemmatize(word, 'r')
        case 'ADJ':
            return '' if use_nouns_only else lemmatizer.lemmatize(word, 'a')
        # TODO: what about satellite adjectives? They don't appear in the universal tag set?
        case _:
            return '' if use_nouns_only else word  # Don't lemmatize


def sanitize_tokenize(lines, use_nouns_only=True):
    """
    Remove urls, mentions, email addresses, emoji and empty lines.
    Tokenize the input.

    TODO: lemmatizes was into wa! Not the best lemmatization

    :param lines: List of documents / tweets.
    :param use_nouns_only: Whether to throw away anything but the nouns
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
    stop_words.update(['u', 'ur', 'dm'])
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

        words = [lemmatize(word, tag, lemmatizer, use_nouns_only=use_nouns_only) for word, tag in tagged if word.isalpha()]
        words = [word for word in words if word not in stop_words and word]
        tokens.append(words)

    return tokens
