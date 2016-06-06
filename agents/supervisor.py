import sqlite3 as lite

import spade
from utils import config
from utils.tweet import Tweet


class SupervisorAgent(spade.Agent.Agent):
    def init_database(self):
        self.connection = lite.connect('../sentiment_app/db.sqlite3', timeout=10, check_same_thread=False)

    def disconnect_database(self):
        self.connection.commit()
        self.connection.close()

    def get_cursor(self):
        return self.connection.cursor()

    def are_keywords_updated(self):
        self.init_database()
        cur = self.get_cursor()
        cur.execute('SELECT * FROM api_keyword')
        new_keywords = []
        for record in cur.fetchall():
            new_keywords.append(str(record[1]))
        self.disconnect_database()
        if set(new_keywords) != set(self.keywords):
            self.keywords = new_keywords
            return True
        return False

    def send_keywords(self):
        print "sending keywords"
        receiver = spade.AID.aid(name=config.crawler,
                                 addresses=["xmpp://" + config.crawler])
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setOntology(config.keyword_msg)
        self.msg.addReceiver(receiver)
        content = ''
        for word in self.keywords:
            content += word + ','
        content = content[:-1]
        self.msg.setContent(content)
        self.send(self.msg)

    def receive_tweets(self, raw_tweet_list):
        self.tweet_list = []
        for tweet in raw_tweet_list:
            tweet_split = tweet.split('::')
            tweet_tuple = Tweet(tweet_split[0], tweet_split[1], tweet_split[2], tweet_split[3], tweet_split[4])
            self.tweet_list.append(tweet_tuple)

    def insert_data(self):
        print "inserting tweets"
        self.init_database()
        cur = self.get_cursor()
        for tweet in self.tweet_list:
            if float(tweet.sentiment) == 0:
                continue
            cur.execute("INSERT INTO api_keywordtweet (text) VALUES (?)", (tweet.text,))

            tweet_id = cur.lastrowid
            cur.execute("SELECT id FROM api_keyword WHERE key = ?", (tweet.tag,))
            key_id = cur.fetchone()[0]
            cur.execute("INSERT INTO api_keywordsentiment (keyword_id, tweet_id, value, created_date) VALUES (?,?,?,?)",
                        (key_id, tweet_id, tweet.sentiment, tweet.create_date))
        self.disconnect_database()

    def _setup(self):
        self.setDebugToScreen()
        self.keywords = []
        self.addBehaviour(WakeUp(10), None)

        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.tweet_with_sentiment)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(ReceiveTweetsBehav(), t)


class WakeUp(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        pass

    def _onTick(self):
        if self.myAgent.are_keywords_updated():
            self.myAgent.send_keywords()


class ReceiveTweetsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Received tweets with sentiment message!"
        self.msg = self._receive(False)
        if self.msg:
            tweet_list = self.msg.getContent().split('|')
            if len(tweet_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.receive_tweets(tweet_list)
                self.myAgent.insert_data()
            else:
                print "invalid message"
