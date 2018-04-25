from unittest.mock import MagicMock, patch
from twitter_mood.mood_gatherer import TwitterMoodGatherer


class TestGetMoodSuite:
    def test_get_mood_empty_tweets(self):
        twitter_mock = MagicMock()
        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')
        mood = mood_gatherer.get_mood()
        assert mood.polarity == 0
        assert mood.subjectivity == 0

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_mood_single_tweet(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetSearch.return_value = [MagicMock(text='bar')]
        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')
        text_mock.return_value = MagicMock(
                sentiment=MagicMock(
                    polarity=-0.1,
                    subjectivity=0.8))

        mood_gatherer.gather_tweets()
        mood = mood_gatherer.get_mood()
        assert mood.polarity == -0.1
        assert mood.subjectivity == 0.8

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_mood_multiple_tweets(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetSearch.return_value = [
                MagicMock(text='bar'),
                MagicMock(text='baz')]
        text_mock.side_effect = [
                MagicMock(
                    sentiment=MagicMock(polarity=-0.3, subjectivity=1)),
                MagicMock(
                    sentiment=MagicMock(polarity=-0.1, subjectivity=0.8))]

        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')

        mood_gatherer.gather_tweets()
        mood = mood_gatherer.get_mood()
        assert mood.polarity == -0.2
        assert mood.subjectivity == 0.9

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_moods(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetSearch.return_value = [
                MagicMock(text='bar', created_at=1,
                          id_str='xxx', user=MagicMock(screen_name='foo')),
                MagicMock(text='baz', created_at=2,
                          id_str='yyy', user=MagicMock(screen_name='bar'))]

        sentiment_a = MagicMock(
                sentiment=MagicMock(polarity=-0.3, subjectivity=1)),
        sentiment_b = MagicMock(
                sentiment=MagicMock(polarity=-0.1, subjectivity=0.8))
        text_mock.side_effect = [
                sentiment_a,
                sentiment_b,
                ]

        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')

        time_tuple = mood_gatherer._TwitterMoodGatherer__time_tuple

        mood_gatherer.gather_tweets()
        moods = mood_gatherer.get_moods()
        assert moods == [time_tuple(sentiment=sentiment_a,
                                    created_at=1,
                                    url='https://twitter.com/foo/status/xxx'),
                         time_tuple(sentiment=sentiment_b,
                                    created_at=2,
                                    url='https://twitter.com/bar/status/yyy')]

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_mood_from_stream(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetStreamFilter.return_value = iter([{'text': 'bar'}, {'text': 'ree'}])
        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')
        text_mock.return_value = MagicMock(
                sentiment=MagicMock(
                    polarity=-0.1,
                    subjectivity=0.8))

        mood_gatherer.gather_tweet_stream()
        stream = mood_gatherer.get_mood_stream()
        mood = next(stream)
        assert mood.sentiment.polarity == -0.1
        assert mood.sentiment.subjectivity == 0.8
        assert mood.created_at == ''
        assert mood.url == 'https://twitter.com//status/'
        mood = next(stream)
        assert mood.sentiment.polarity == -0.1
        assert mood.sentiment.subjectivity == 0.8
        assert mood.created_at == ''
        assert mood.url == 'https://twitter.com//status/'
        mood = next(stream, None)
        assert mood is None
