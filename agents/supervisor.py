import spade
from agents.utils import config
import sqlite3 as lite
import sys


class SupervisorAgent(spade.Agent.Agent):
    def _setup(self):
        print "SUPERWIZOR OPERATING"
        behav = WakeUp(10)
        self.addBehaviour(behav, None)


class WakeUp(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):

        con = None
        try:
            con = lite.connect('../sentiment_app/db.sqlite3')
            cur = con.cursor()
            cur.execute('SELECT * from api_keyword')

            data = cur.fetchone()
            print data
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()

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
