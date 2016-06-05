# coding=utf-8
from collections import namedtuple
from datetime import datetime

import re
from tweepy import StreamListener
from tweepy.streaming import json


class Tweet(namedtuple('Tweet', ['id', 'tag', 'text', 'create_date', 'sentiment'])):
    __slots__ = ()

    def __str__(self):
        return str(str(self.id) + "::" + str(self.tag) + "::" + str(self.text) + "::" + str(
            self.create_date) + "::" + str(self.sentiment))


class TwitterStreamListener(StreamListener):
    def __init__(self, _keywords, queue, api=None):
        super(TwitterStreamListener, self).__init__(api)
        self.queue = queue
        self.keywords = _keywords

    def on_data(self, data):
        tweet = json.loads(data)
        for key in self.keywords:
            if re.search(key, tweet['text'], re.IGNORECASE):
                date = str(datetime.now().strftime("%Y-%m-%d"))
                twit = Tweet(tweet['id'], key, tweet['text'].encode('ascii', 'ignore'), date, 0)
                self.queue.put(twit)
        return True

    def set_keywords(self, keywords):
        self.keywords = keywords

    def on_error(self, status):
        print status
        if status == 420:
            return False
