import matplotlib.pyplot as plt
import re
import random
import string
import datetime
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


class VisualisationManager:
    def __init__(self, topic, twitter, top_results, output_dir, args):
        self.topic = topic
        self.twitter = twitter
        self.top_results = top_results
        self.output_dir = output_dir
        self.args = args
        self.username = ""
        self.pubops_db = INFDB["pubops"]
        self.newsops_db = INFDB["newsops"]
        self.sid = SentimentIntensityAnalyzer()
        self.word_dict = {}
        self.cloud_string_list = []
        self.sentiment_ratio = []

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

        wc = WordCloud(width=800, height=400, background_color="#002b36",
                       max_words=int(self.args["words"]), stopwords=s_words,
                       random_state=1)
        wc.generate(tweets)
        wc.recolor(color_func=grey_color_func)

        plt.figure(figsize=(9, 5))
        plt.title("{0} Word Cloud".format(name.title()), color="white")
        plt.imshow(wc, interpolation="bilinear")
        plt.tight_layout(pad=0)
        plt.axis("off")

        plt.savefig("{0}wc.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")
        plt.clf()
        plt.cla()
        plt.close()

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

        self.aggregate_words("twitter", words, score)

    def derive_news_sentiment(self, news_words):
        freq = FreqDist(news_words.split())
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
                    elif (self.sid.polarity_scores(word)["compound"]) < 0.0:
                        word_summaries.append((w, frequency, "neg"))
                        neg_words += 1
                    else:
                        word_summaries.append((w, frequency, "neu"))

        total_words = pos_words + neg_words
        score = (pos_words - neg_words) / total_words
        for word in word_summaries:
            words[word[0]] = (word[1], word[2])

        self.aggregate_words("news", words, score)

    def aggregate_words(self, source, words_dict, score):
        db = None
        if source == "twitter":
            db = self.pubops_db
        elif source == "news":
            db = self.newsops_db

        word_sents = {
            "_id": self.username,
            "words": words_dict,
            "score": score
        }

        check_query = db.find_one({"_id": self.username})
        if not check_query:
            db.insert(word_sents)
            self.word_dict = db.find({"_id": self.username})[0]["words"]
            self.cloud_string_list = self.create_cloud_string()
        else:
            self.update_words(source, word_sents)

    def update_words(self, source, new_words):
        db = None
        if source == "twitter":
            db = self.pubops_db
        elif source == "news":
            db = self.newsops_db

        query_result = db.find({"_id": self.username})
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

        db.update_one({
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

    def sent_color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
        hsl = "hsl(180, 7%, 60%)"
        for k, v in self.word_dict.items():
            if word == k:
                if v[1] == "pos":
                    hsl = "hsl(68, 100%, 30%)"
                elif v[1] == "neg":
                    hsl = "hsl(1, 71%, 52%)"
                else:
                    hsl = "hsl(180, 7%, 60%)"

        return hsl

    def get_sent_ratio(self):
        pos_count = 0
        neg_count = 0
        for k, v in self.word_dict.items():
            if v[1] == "pos":
                pos_count += 1
            elif v[1] == "neg":
                neg_count += 1

        return [pos_count, neg_count]

    def create_sentiment_cloud(self, source, word_tokens=None):
        cloud_string = ""
        wc_title = ""
        fig_name = ""

        if source == "twitter":
            tweets = " ".join(self.get_mention_tweets())
            self.derive_social_sentiment(tweets)
            cloud_string = " ".join(self.cloud_string_list)
            wc_title = "@{0} Social Consensus Word Cloud".format(self.username)
            fig_name = "{0}tswc"
        elif source == "news":
            cloud_string = " ".join(word_tokens)
            self.derive_news_sentiment(cloud_string)
            wc_title = "@{0} News Consensus Word Cloud".format(self.username)
            fig_name = "{0}nswc"

        wc = WordCloud(width=800, height=400, background_color="#002b36",
                       max_words=int(self.args["words"]), stopwords=s_words,
                       random_state=1, collocations=False)
        wc.generate(cloud_string)
        wc.recolor(color_func=self.sent_color_func)

        plt.figure(figsize=(9, 5))
        plt.title(wc_title, color="white")
        plt.imshow(wc, interpolation="bilinear")
        plt.tight_layout(pad=0)
        plt.axis("off")

        plt.savefig(fig_name.format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")
        plt.clf()
        plt.cla()
        plt.close()

    def create_pie_chart(self):
        sents = self.get_sent_ratio()
        labels = ["positive - {0}".format(sents[0]), "negative - {0}".format(sents[1])]
        sizes = sents
        colors = ["#859900", "#DC312E"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, textprops={"color": "white"})
        ax.axis("equal")
        plt.title("@{0} Consensus Sentiment Pie Chart".format(self.username), color="white")

        plt.savefig("{0}spi.png".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")
        plt.clf()
        plt.cla()
        plt.close()

    def create_composite_diachronic_sentiment_chart(self, client):
        aggregate_ops = client["influence"]["aggregate_ops"]

        result = aggregate_ops.find_one({"_id": self.username})

        if not result:
            pubops_score = client["influence"]["pubops"].find({"_id": self.username})[0]["score"]
            newsops_score = client["influence"]["newsops"].find({"_id": self.username})[0]["score"]

            entry = {
                "_id": self.username,
                "pubops_score": [{str(datetime.datetime.today().date()): pubops_score}],
                "newsops_score": [{str(datetime.datetime.today().date()): newsops_score}]
            }

            aggregate_ops.insert(entry)

        result = aggregate_ops.find({"_id": self.username})
        pubops_list = result[0]["pubops_score"]
        newsops_list = result[0]["newsops_score"]

        pub_x = []
        pub_y = []
        news_x = []
        news_y = []

        for d in pubops_list:
            entry = list(d)
            date = entry[0]
            score = d[date]
            pub_x.append(date)
            pub_y.append(score)

        for d in newsops_list:
            entry = list(d)
            date = entry[0]
            score = d[date]
            news_x.append(date)
            news_y.append(score)

        fig = plt.figure()
        plt.plot(pub_x, pub_y, "-o", news_x, news_y, "-o")
        plt.margins(x=0)
        plt.axis([pub_x[0], pub_x[-1], -1, 1])
        plt.xticks(pub_x, rotation="vertical")
        plt.tight_layout()
        plt.title("Social & News Media Composite Sentiment Graph")

        plt.savefig("{0}csg".format(self.output_dir), dpi=300, facecolor="#002b36", bbox_inches="tight")
        plt.clf()
        plt.cla()
        plt.close()


def clean_tweet(tweet):
    additional_exc = ["…", "’", "...", "n't", "RT", "rt"]
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


def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
