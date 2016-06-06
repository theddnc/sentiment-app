from Queue import Queue

import spade
from sentiment_counter import SentimentCounter
from utils import config
from utils.tweet import Tweet


class SentimentCounterAgent(spade.Agent.Agent):
    def log(self, msg):
        print '[SENTIMENT_COUNTER] ' + msg

    def receive_tweets(self, raw_tweet_list):
        for tweet in raw_tweet_list:
            tweet_obj = Tweet.deserialize(tweet)
            self.q.put(tweet_obj)

    def count_sentiment(self):
        self.log("Counting sentiment")
        self.tweet_list = self.get_tweets_from_queue()
        if len(self.tweet_list) == 0:
            return
        for tweet in self.tweet_list:
            try:
                counted_sentiment = self.sentiment_counter.count_sentiment(tweet.text)
            except:
                counted_sentiment = 0
            tweet.sentiment = counted_sentiment

    def get_tweets_from_queue(self):
        self.log("Preparing tweet package content")
        tweets_list = []
        while len(tweets_list) < config.batch_size and not self.q.empty():
            item = self.q.get()
            if item is None:
                break
            tweets_list.append(item)
        return tweets_list

    def send_tweet_with_sentiment(self):
        if len(self.tweet_list) == 0:
            return
        self.log("Preparing message")
        receiver = spade.AID.aid(name=config.master,
                                 addresses=["xmpp://" + config.master])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.tweet_with_sentiment)
        self.msg.addReceiver(receiver)
        content = self.tweet_list
        str_content = ""
        for tweet in content:
            str_content += tweet.serialize() + "|"
        str_content = str_content[:-1]
        self.msg.setContent(str_content)
        self.send(self.msg)
        self.log("Message sent")

    def _setup(self):
        self.sentiment_counter = SentimentCounter()
        self.q = Queue()
        # self.setDebugToScreen()
        self.addBehaviour(ProcessTweets(10), None)
        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.raw_tweet)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(ReceiveTweetsBehav(), t)


class ProcessTweets(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        pass

    def _onTick(self):
        if not self.myAgent.q.empty():
            self.myAgent.log("Processing tweets")
            self.myAgent.count_sentiment()
            self.myAgent.send_tweet_with_sentiment()
        else:
            self.myAgent.log("Empty tweet queue")


class ReceiveTweetsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        self.myAgent.log("Received tweets message!")
        self.msg = self._receive(False)
        if self.msg:
            tweet_list = self.msg.getContent().split('|')
            if len(tweet_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.receive_tweets(tweet_list)
            else:
                self.myAgent.log("invalid message")
