# coding=utf-8
import pickle

import re
from tweepy import StreamListener
from tweepy.streaming import json


class Tweet():
    def __init__(self, id, key, text, created_date, sentiment):
        self.id = id
        self.key = key
        self.text = text
        self.created_date = created_date
        self.sentiment = sentiment

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(tweet_str):
        return pickle.loads(tweet_str)


class TwitterStreamListener(StreamListener):
    def __init__(self, _keywords, queue, api=None):
        super(TwitterStreamListener, self).__init__(api)
        self.queue = queue
        self.keywords = _keywords

    def on_data(self, data):
        tweet = json.loads(data)
        for key in self.keywords:
            if re.search(key, tweet['text'], re.IGNORECASE):
                twit = Tweet(tweet['id'], key, tweet['text'].encode('ascii', 'ignore'), tweet['timestamp_ms'], 0)
                self.queue.put(twit)
        return True

    def set_keywords(self, keywords):
        self.keywords = keywords

    def on_error(self, status):
        print status
        if status == 420:
            return False
