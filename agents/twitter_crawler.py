# coding=utf-8
import spade
from agents.behaviours.listen_for_tweets import ListenForTweetsBehav
from agents.behaviours.wake_up_on_message import WakeUpOnMessage
from agents.utils import config


class TwitterCrawlerAgent(spade.Agent.Agent):
    def _setup(self):
        print "Agent is starting"
        b = ListenForTweetsBehav(10)
        self.addBehaviour(b, None)

        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.tweet_ontology)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(WakeUpOnMessage(), t)


if __name__ == "__main__":
    a = TwitterCrawlerAgent("agent@0.0.0.0", "secret")
    a.start()
