from collections import namedtuple

import re
from tweepy import StreamListener
from tweepy.streaming import json

Tweet = namedtuple('Tweet', ['id', 'tag', 'text', 'create_date'])


class TwitterStreamListener(StreamListener):
    def __init__(self, _keywords, queue, api=None):
        super(TwitterStreamListener, self).__init__(api)
        self.queue = queue
        self.keywords = _keywords

    def on_data(self, data):
        tweet = json.loads(data)
        for key in self.keywords:
            if re.search(key, tweet['text'], re.IGNORECASE):
                twit = Tweet(tweet['id'], key, tweet['text'], tweet['created_at'])
                self.queue.put(twit)
        return True

    def set_keywords(self, keywords):
        self.keywords = keywords

    def on_error(self, status):
        print status
        if status == 420:
            return False
