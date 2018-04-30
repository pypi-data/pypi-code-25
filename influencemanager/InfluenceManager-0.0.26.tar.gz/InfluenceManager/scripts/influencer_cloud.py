import matplotlib.pyplot as plt
import re
import random
import string
from wordcloud import WordCloud, STOPWORDS
from nltk.tokenize import TweetTokenizer, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import FreqDist, pos_tag
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from InfluenceManager.definitions import INFDB

tokeniser = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
stopwords = stopwords.words('english')
stm = PorterStemmer()
s_words = set(STOPWORDS)


class InfluencerCloud:
    def __init__(self, topic, twitter, top_results, output_dir):
        self.topic = topic
        self.twitter = twitter
        self.top_results = top_results
        self.output_dir = output_dir
        self.username = ""
        self.words_db = INFDB["pubops"]
        self.sid = SentimentIntensityAnalyzer()
        self.word_dict = {}
        self.cloud_string_list = []

    def __str__(self):
        return str(self.top_results)

    def get_tweets(self, user):
        relevant_tweets = []
        user_timeline = self.twitter.get_user_timeline(screen_name=user[0], count=1500, tweet_mode="extended")
        for tweet in user_timeline:
            tweet_text = tweet["full_text"].lower().replace("\n", "")
            cleaned_tweet = clean_tweet(tweet_text)
            relevant_tweets.append(cleaned_tweet)

        return relevant_tweets

    def create_cloud(self):
        name = self.twitter.show_user(screen_name=self.top_results[0][0])["name"]

        tweets = " ".join(self.get_tweets(self.top_results[0]))

        wc = WordCloud(width=800, height=400, background_color="#002b36", max_words=50, stopwords=s_words,
                       random_state=1)
        wc.generate(tweets)
        wc.recolor(color_func=grey_color_func)

        plt.figure(figsize=(9, 5))
        plt.title("{0} Word Cloud".format(name.title()), color="white")
        plt.imshow(wc, interpolation="bilinear")
        plt.tight_layout(pad=0)
        plt.axis("off")

        plt.savefig("{0}wc.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")

        self.username = self.top_results[0][0]

    def get_mention_tweets(self):
        clean_tweets = []
        for i in range(0, 10):
            next_max_id = None
            if 0 == i:
                results = self.twitter.search(q="'{0} -filter:retweets'".format(self.username), count='100',
                                              tweet_mode="extended")
            else:
                results = self.twitter.search(q="'{0} -filter:retweets'".format(self.username),
                                              include_entities=True, max_id=next_max_id, tweet_mode="extended")

            for result in results["statuses"]:
                clean_tweets.append(clean_tweet(result["full_text"]))

            try:
                next_results_url_params = results["search_metadata"]["next_results"]
                next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
            except KeyError:
                continue

        clean_tweets = list(set(clean_tweets))

        return clean_tweets

    def derive_social_sentiment(self, tweets):
        tkn_tweets = tokeniser.tokenize(tweets)
        freq = FreqDist(tkn_tweets)
        words = {}
        word_summaries = []

        pos_words = 0
        neg_words = 0

        freq_list = [(word, frequency) for word, frequency in freq.most_common(500)]
        for word, frequency in freq_list:
            for w, cat in pos_tag(word_tokenize(word)):
                if cat in ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']:
                    if self.sid.polarity_scores(w)["compound"] > 0.0:
                        word_summaries.append((w, frequency, "pos"))
                        pos_words += 1
                    elif (self.sid.polarity_scores(word)['compound']) < 0.0:
                        word_summaries.append((w, frequency, "neg"))
                        neg_words += 1
                    else:
                        word_summaries.append((w, frequency, "neu"))

        total_words = pos_words + neg_words
        score = (pos_words - neg_words) / total_words
        for word in word_summaries:
            words[word[0]] = (word[1], word[2])

        self.aggregate_words(words, score)

    def aggregate_words(self, words_dict, score):
        word_sents = {
            "_id": self.username,
            "words": words_dict,
            "score": score
        }

        check_query = self.words_db.find_one({"_id": self.username})
        if not check_query:
            self.words_db.insert(word_sents)
        else:
            self.update_words(word_sents)

    def update_words(self, new_words):
        query_result = self.words_db.find({"_id": self.username})
        old_score = query_result[0]["score"]
        new_score = new_words["score"]
        calculated_score = (old_score + new_score) / 2

        db_word_list = []
        new_word_list = []
        updated_freqs = []

        for k, v in query_result[0]["words"].items():
            db_word_list.append({k: v})

        for k, v in new_words["words"].items():
            new_word_list.append({k: v})

        to_remove = []
        for i in new_word_list:
            for j in db_word_list:
                if list(i)[0] == list(j)[0]:
                    sent = i[list(i)[0]][1]
                    new_count = i[list(i)[0]][0] + j[list(j)[0]][0]

                    updated_freqs.append({list(i)[0]: [new_count, sent]})
                    to_remove.append(i)

        for rem in to_remove:
            if rem in new_word_list:
                new_word_list.remove(rem)

        updated_words = updated_freqs + new_word_list

        result = {}
        sorted_words = sorted(updated_words, key=lambda item: item[list(item)[0]][0], reverse=True)[:400]
        for d in sorted_words:
            result.update(d)

        self.words_db.update_one({
            "_id": self.username,
        }, {
            "$set": {
                "words": result,
                "score": calculated_score
            }
        })

        self.word_dict = result
        self.cloud_string_list = self.create_cloud_string()

    def create_cloud_string(self):
        cloud_string_list = []
        for word, attrs in self.word_dict.items():
            cloud_string_list.extend([word for _ in range(attrs[0])])

        return cloud_string_list

    def sent_color_func(self, word):
        hsl = ""
        for k, v in self.word_dict.items():
            if word == k:
                if v[1] == "pos":
                    hsl = "hsl(68, 100%, 30%)"
                elif v[1] == "neg":
                    hsl = "hsl(1, 71%, 52%)"
                elif v[1] == "neu":
                    hsl = "hsl(180, 7%, 60%)"

        return hsl

    def create_mention_cloud(self):
        tweets = " ".join(self.get_mention_tweets())
        self.derive_social_sentiment(tweets)
        cloud_string = " ".join(self.cloud_string_list)

        wc = WordCloud(width=800, height=400, background_color="#002b36", max_words=50, stopwords=s_words,
                       random_state=1, collocations=False)
        wc.generate(cloud_string)
        wc.recolor(color_func=self.sent_color_func)

        plt.figure(figsize=(9, 5))
        plt.title("@{0} Consensus Word Cloud".format(self.username), color="white")
        plt.imshow(wc, interpolation="bilinear")
        plt.tight_layout(pad=0)
        plt.axis("off")

        plt.savefig("{0}swc.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")


def clean_tweet(tweet):
    additional_exc = ["…", "’", "...", "n't"]
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = tweet.encode("ascii", errors="ignore").decode()
    tkns = tokeniser.tokenize(tweet)

    clean = []
    for word in tkns:
        word = word.lower()
        if word not in stopwords and word not in string.punctuation and word not in additional_exc:
            clean.append(word)

    new_tweet = " ".join(clean)
    return new_tweet


def bag_of_words(tweet):
    words = tweet.split()
    word_features = {}

    for word in words:
        word_features[word] = True

    return word_features


def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs
):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
