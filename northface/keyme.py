from rake_nltk import Rake


def get_keywords(text, topn=10):
    """
    Use Rake to get keywords from some text!

    :param str text: Text to get keywords from
    :param int topn: How many keywords to extract

    :return list: List of keywords
    """
    rake = Rake()
    rake.extract_keywords_from_text(text)
    kwds = rake.get_ranked_phrases_with_scores()[: int(topn)]
    return kwds
