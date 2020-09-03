import os
import time

import tweepy
import urllib3
import textblob


TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.environ.get("TWITTER_API_SECRET_KEY")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

MAX_TIME = 10
MAX_TWEETS = 50


def get_sentiment(text):
    """
    Take a piece of text and return the sentiment with a score.

    :param int polarity: Number between -1 and 1.
    :return tuple: Human readable classifier of sentiment, sentiment score.
    """
    blob = textblob.TextBlob(text)
    polarity = blob.sentiment.polarity
    sentiment = ""

    if polarity == 0:
        sentiment = "Neutral"
    elif polarity > 0 and polarity < 0.5:
        sentiment = "Neutral/Positive"
    elif polarity >= 0.5:
        sentiment = "Positive"
    elif polarity <= 0 and polarity > -0.5:
        sentiment = "Neutral/Negative"
    elif polarity <= -0.5:
        sentiment = "Negative"
    else:
        sentiment = f"Unrecognized value: {polarity}"

    return {"sentiment": sentiment, "score": polarity}


class StreamListener(tweepy.StreamListener):
    def __init__(self):
        self.tweets = []
        self.start = time.time()
        super(StreamListener, self).__init__()

    def on_status(self, status):
        tweet_limit = int(os.environ.get("TWEET_LIMIT"))
        time_limit = int(os.environ.get("TIME_LIMIT"))

        if not getattr(status, "retweeted_status", None):
            self.tweets.append(
                {
                    "text": status.text,
                    "sentiment": get_sentiment(status.text)["sentiment"],
                }
            )
            elapsed = time.time() - self.start
            if len(self.tweets) >= tweet_limit or elapsed >= time_limit:
                return False

    def on_error(self, status_code):
        if status_code == 420:
            return False


def get_tweets(topic, time_limit=MAX_TIME, tweet_limit=MAX_TWEETS):
    """
    Get tweets of a certain topic.

    :param str topic: A topic to look for.
    :param int time_limit: How long to look for.
    :param int tweet_limit: How many tweets to fetch.

    :return dict: {Tweet: Sentiment}
    """
    # Handle string inputs from the command line
    time_limit = int(time_limit)
    tweet_limit = int(tweet_limit)

    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    stream_listener = StreamListener()
    stream = tweepy.Stream(
        auth=api.auth, listener=stream_listener, timeout=time_limit
    )

    os.environ["TWEET_LIMIT"] = str(time_limit)
    os.environ["TIME_LIMIT"] = str(tweet_limit)

    try:
        stream.filter(track=[topic])
        print("Finished!")

    except urllib3.exceptions.ReadTimeoutError:
        print("Timeout!")

    finally:
        return stream_listener.tweets
