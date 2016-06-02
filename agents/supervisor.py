import sqlite3 as lite

import spade
from agents.utils import config


class SupervisorAgent(spade.Agent.Agent):
    def _setup(self):
        self.setDebugToScreen()
        self.keywords = []
        print "SUPERWIZOR OPERATING"
        self.addBehaviour(WakeUp(10), None)

    def init_database(self):
        self.connection = lite.connect('../sentiment_app/db.sqlite3')

    def disconnect_database(self):
        self.connection.close()

    def get_cursor(self):
        return self.connection.cursor()

    def are_keywords_updated(self):
        self.init_database()
        print "getting keywords"
        cur = self.get_cursor()
        cur.execute('SELECT * FROM api_keyword')
        new_keywords = []
        for record in cur.fetchall():
            new_keywords.append(str(record[1]))
        self.disconnect_database()
        print new_keywords
        if set(new_keywords) != set(self.keywords):
            self.keywords = new_keywords
            return True
        return False

    def send_keywords(self):
        print "sending keywords"
        receiver = spade.AID.aid(name="agent@0.0.0.0",
                                 addresses=["xmpp://agent@0.0.0.0"])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.tweet_ontology)
        self.msg.addReceiver(receiver)
        content = ''
        for word in self.keywords:
            content += word + ','
        content = content[:-1]
        self.msg.setContent(content)
        self.send(self.msg)


class WakeUp(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        print "starting behav"

    def _onTick(self):
        print "TICK"
        if self.myAgent.are_keywords_updated():
            self.myAgent.send_keywords()

