# coding=utf-8
import os
from Queue import Queue
import sys
import spade
from sentimenter import SentimentCounterAgent
from supervisor import SupervisorAgent
from utils import config
from utils.tweet import TwitterStreamListener
from tweepy import OAuthHandler
from tweepy.streaming import Stream

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class TwitterCrawlerAgent(spade.Agent.Agent):
    def init_stream(self):
        self.q = Queue()
        self.keywords = []
        self.listener = TwitterStreamListener(self.keywords, self.q)
        auth = OAuthHandler(config.con_secret, config.con_secret_key)
        auth.set_access_token(config.token, config.token_key)
        self.stream = Stream(auth, self.listener)

    def restart_stream(self):
        print "Restarting stream"
        self.stream.disconnect()
        self.stream.filter(track=self.keywords, async=True, languages=["en"])

    def update_stream(self, keywords):
        print "Updating stream with keywords: "
        print keywords
        if len(keywords) != 0:
            self.keywords = keywords
            self.listener.set_keywords(self.keywords)
            self.restart_stream()
        else:
            print "Empty keyword list!"

    def prepare_and_send_message(self):
        print "Preparing message"
        receiver = spade.AID.aid(name=config.sentimenter,
                                 addresses=["xmpp://" + config.sentimenter])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.raw_tweet)
        self.msg.addReceiver(receiver)
        content = self.get_tweets_from_queue()
        str_content = ""
        for tweet in content:
            str_content += tweet.serialize() + "|"
        str_content = str_content[:-1]
        self.msg.setContent(str_content)
        self.send(self.msg)

    def get_tweets_from_queue(self):
        print "Preparing tweet package content"
        tweets_list = []
        while len(tweets_list) < config.batch_size and not self.q.empty():
            item = self.q.get()
            if item is None:
                break
            tweets_list.append(item)
        return tweets_list

    def _setup(self):
        print "Tweeter crawler is starting"
        self.setDebugToScreen()
        self.init_stream()
        self.addBehaviour(ListenForTweetsBehav(10), None)

        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.keyword_msg)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(UpdateKeywordsBehav(), t)


class ListenForTweetsBehav(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        pass

    def _onTick(self):
        print "crawler tick"
        if not self.myAgent.stream.running and len(self.myAgent.keywords) != 0:
            print "Stream dead, restarting"
            self.myAgent.restart_stream()
        if not self.myAgent.q.empty():
            self.myAgent.prepare_and_send_message()
        else:
            print "Empty tweet queue"


class UpdateKeywordsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Received keyword message!"
        self.msg = self._receive(False)
        if self.msg:
            keyword_list = self.msg.getContent().split(',')
            if len(keyword_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.update_stream(keyword_list)
            else:
                print "invalid message"


if __name__ == "__main__":
    a = TwitterCrawlerAgent(config.crawler, "secret")
    b = SupervisorAgent(config.master, "secret")
    c = SentimentCounterAgent(config.sentimenter, "secret")
    a.start()
    b.start()
    c.start()
