import collections
import re
from textblob import TextBlob


class TwitterMoodGatherer:

    def __init__(self, twitter_api, query):
        self.__twitter_api = twitter_api
        self.__query = query
        self.__sentiment_tool = TextBlob
        self.__tweets = []
        self.__tweet_stream = None
        self.__sentiment_tuple = collections.namedtuple(
                'Sentiment',
                ['polarity', 'subjectivity'])
        self.__time_tuple = collections.namedtuple(
                'TimeSentiment',
                ['sentiment', 'created_at', 'url'])

    def get_mood(self):
        if len(self.__tweets) == 0:
            return self.__sentiment_tool('')
        sentiments = [self.__sentiment_tool(self.__clean_tweet(tweet.text)).sentiment
                      for tweet in self.__tweets]
        polarity_avg = sum(sentiment.polarity
                           for sentiment in sentiments) / len(self.__tweets)
        subjectivity_avg = sum(sentiment.subjectivity
                               for sentiment in sentiments) / len(self.__tweets)
        return self.__sentiment_tuple(polarity_avg, subjectivity_avg)

    def gather_tweets(self):
        self.__tweets = self.__twitter_api.GetSearch(
                term=self.__query,
                count=100)

    def gather_tweet_stream(self):
        self.__tweet_stream = self.__twitter_api.GetStreamFilter(
                track=self.__query)

    def get_moods(self):
        return [self.__time_tuple(self.__sentiment_tool(self.__clean_tweet(tweet.text)),
                                  tweet.created_at,
                                  self.__get_url(tweet.id_str, tweet.user.screen_name))
                for tweet in self.__tweets]

    def get_mood_stream(self):
        for tweet in self.__tweet_stream:
            sentiment = self.__sentiment_tool(self.__clean_tweet(tweet.get('text', ''))).sentiment
            yield self.__time_tuple(
                    sentiment,
                    tweet.get('created_at', ''),
                    self.__get_url(
                        tweet.get('id_str', ''),
                        tweet.get('user', {}).get('screen_name', '')))

    @staticmethod
    def __clean_tweet(tweet):
        """Remove links and special characters."""
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    @staticmethod
    def __get_url(id_str, screen_name):
        return 'https://twitter.com/{}/status/{}'.format(screen_name, id_str)
