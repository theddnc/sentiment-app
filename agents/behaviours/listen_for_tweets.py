from Queue import Queue

import re
import spade
from agents.utils import config
from agents.utils.tweet import Tweet
from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import json


class ListenForTweetsBehav(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        self.q = Queue()
        l = TwitterStreamListener(config.keywords, self.q)
        auth = OAuthHandler(config.con_secret, config.con_secret_key)
        auth.set_access_token(config.token, config.token_key)
        stream = Stream(auth, l)
        stream.filter(track=config.keywords, async=True)

    def _onTick(self):
        self.prep_and_send_message()

    def update_keywords(self):
        print "Updating keywords"
        # TODO zdecydowac czy tagi pobieramy z bazy czy na podstawie wiadomosci od szefa

    def prep_and_send_message(self):
        print "Preparing message"
        # TODO Adresowanie wiadomosci z configu/bazy/na podstawie informacji od szefa
        receiver = spade.AID.aid(name="agent@0.0.0.0",
                                 addresses=["xmpp://agent@0.0.0.0"])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.tweet_ontology)
        self.msg.addReceiver(receiver)
        self.msg.setContent(self.get_tweets_from_queue())
        self.myAgent.send(self.msg)

    def get_tweets_from_queue(self):
        print "Preparing message content"
        tweets_list = []
        while len(tweets_list) < config.batch_size:
            item = self.q.get()
            if item is None:
                break
            tweets_list.append(item)
            print item
        return tweets_list


class TwitterStreamListener(StreamListener):
    def __init__(self, _keywords, queue, api=None):
        super(TwitterStreamListener, self).__init__(api)
        self.queue = queue
        self.keywords = _keywords

    def on_data(self, data):
        tweet = json.loads(data)
        print "TWEET RECEIVED"
        print tweet
        for key in self.keywords:
            if re.search(key, tweet['text'], re.IGNORECASE):
                twit = Tweet(tweet['id'], key, tweet['text'], tweet['created_at'])
                self.queue.put(twit)
        return True

    def on_error(self, status):
        print status
        if status == 420:
            return False
