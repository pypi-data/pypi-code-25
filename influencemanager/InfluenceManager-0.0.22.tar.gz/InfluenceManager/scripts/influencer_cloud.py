import matplotlib.pyplot as plt
import re
import random
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.corpus import stopwords


class InfluencerCloud:
    def __init__(self, topic, twitter, top_results, output_dir):
        self.topic = topic
        self.twitter = twitter
        self.top_results = top_results
        self.output_dir = output_dir
        self.urls = []

    def __str__(self):
        return str(self.top_results)

    def _get_tweets(self, user):
        relevant_tweets = []
        user_timeline = self.twitter.get_user_timeline(screen_name=user[0], count=1500, tweet_mode="extended")
        for tweet in user_timeline:
            tweet_text = tweet["full_text"].lower().replace("\n", "")
            clean_tweet = self._clean_tweet(tweet_text)
            relevant_tweets.append(clean_tweet)

        return relevant_tweets

    @staticmethod
    def _clean_tweet(tweet):
        stop = set(stopwords.words('english'))
        stop.add("amp")
        stop.add("rt")
        tweet = re.sub(r'http(.*)', "", tweet)

        split_tweet = re.split(r'[`\-=~!$%^&*()+\[\]{};\\:"|<,./>? ]', tweet)
        clean_split = list(filter(None, split_tweet))
        cleaned_tweet = " ".join([tkn for tkn in clean_split if tkn not in stop])

        return cleaned_tweet

    def create_cloud(self):
        s_words = set(STOPWORDS)
        name = self.twitter.show_user(screen_name=self.top_results[0][0])["name"]

        tweets = " ".join(self._get_tweets(self.top_results[0]))

        wc = WordCloud(width=800, height=400, background_color="#002b36", max_words=50, stopwords=s_words,
                       random_state=1)
        wc.generate(tweets)
        wc.recolor(color_func=grey_color_func)

        plt.figure(figsize=(9, 5))
        plt.title("{0} Word Cloud".format(name.title()), color="white")
        plt.imshow(wc, interpolation="bilinear")
        plt.tight_layout(pad=0)
        plt.axis("off")
        plt.show()
        plt.savefig("{0}wc.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")

        return self.top_results[0][0]


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
