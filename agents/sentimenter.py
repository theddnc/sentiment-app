import spade
from sentiment_counter import SentimentCounter
from utils import config
from utils.tweet import Tweet


class SentimentCounterAgent(spade.Agent.Agent):
    def receive_tweets(self, raw_tweet_list):
        self.tweet_list = []
        for tweet in raw_tweet_list:
            tweet_obj = Tweet.deserialize(tweet)
            self.tweet_list.append(tweet_obj)

    def count_sentiment(self):
        if len(self.tweet_list) == 0:
            return
        for tweet in self.tweet_list:
            counted_sentiment = self.sentiment_counter.count_sentiment(tweet.text)
            tweet.sentiment = counted_sentiment

    def send_tweet_with_sentiment(self):
        print "Preparing message"
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

    def _setup(self):
        self.sentiment_counter = SentimentCounter()
        self.setDebugToScreen()
        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.raw_tweet)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(ReceiveTweetsBehav(), t)


class ReceiveTweetsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Received tweets message!"
        self.msg = self._receive(False)
        if self.msg:
            tweet_list = self.msg.getContent().split('|')
            if len(tweet_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.receive_tweets(tweet_list)
                self.myAgent.count_sentiment()
                self.myAgent.send_tweet_with_sentiment()
            else:
                print "invalid message"
