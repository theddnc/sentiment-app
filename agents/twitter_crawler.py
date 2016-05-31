# coding=utf-8
from Queue import Queue

import spade
from agents.utils import config
from agents.utils.tweet import TwitterStreamListener
from tweepy import OAuthHandler
from tweepy.streaming import Stream


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
        self.stream.filter(self.keywords, async=True)

    def update_stream(self, keywords):
        print "Stream update: " + keywords
        if len(keywords) != 0:
            for word in keywords:
                if word not in self.keywords:
                    self.keywords.append(word)
            self.listener.set_keywords(self.keywords)
            self.restart_stream()
        else:
            print "Empty keyword list!"

    def prepare_and_send_message(self):
        print "Preparing message"
        receiver = spade.AID.aid(name="agent@0.0.0.0",
                                 addresses=["xmpp://agent@0.0.0.0"])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.tweet_ontology)
        self.msg.addReceiver(receiver)
        self.msg.setContent(self.get_tweets_from_queue())
        # self.send(self.msg)

    def get_tweets_from_queue(self):
        print "Preparing message content"
        tweets_list = []
        while len(tweets_list) < config.batch_size and not self.q.empty():
            item = self.q.get()
            if item is None:
                break
            tweets_list.append(item)
            print item
        return tweets_list

    def _setup(self):
        print "Agent is starting"
        self.init_stream()
        b = ListenForTweetsBehav(10)
        self.addBehaviour(b, None)

        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.tweet_ontology)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(UpdateKeywordsBehav(), t)


class ListenForTweetsBehav(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        print "Initialized periodic behaviour"

    def _onTick(self):
        print "tick"
        if not self.myAgent.stream.running and not self.myAgent.keywords.empty:
            print "Stream dead, restarting"
            self.myAgent.restart_stream()
        if not self.myAgent.q.empty():
            self.myAgent.prep_and_send_message()
        else:
            print "Empty tweet queue"


class UpdateKeywordsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Updating keywords!"
        self.msg = self._receive(False)
        if self.msg:
            keyword_list = self.msg.getContent().split(',')
            if len(keyword_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.update_stream(keyword_list)
            else:
                print "invalid message"


class SupervisorAgent(spade.Agent.Agent):
    def _setup(self):
        print "SUPERWIZOR OPERATING"
        b = WakeUp(10)
        self.addBehaviour(b, None)


class WakeUp(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        self.counter = 0

    def _onTick(self):
        print "super tick"
        keywords = ''
        if self.counter == 1:
            keywords = "dupa"
        if self.counter >= 2:
            keywords = "sex"
        print "Preparing message"
        print keywords
        receiver = spade.AID.aid(name="agent@0.0.0.0",
                                 addresses=["xmpp://agent@0.0.0.0"])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.tweet_ontology)
        self.msg.addReceiver(receiver)
        self.msg.setContent(keywords)
        self.myAgent.send(self.msg)
        self.counter += 1


if __name__ == "__main__":
    a = TwitterCrawlerAgent("agent@0.0.0.0", "secret")
    b = SupervisorAgent("agent1@0.0.0.0", "secret")
    a.start()
    b.start()
