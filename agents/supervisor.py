import sqlite3 as lite
from Queue import Queue
from datetime import datetime
import spade
from utils import config
from utils.tweet import Tweet


class SupervisorAgent(spade.Agent.Agent):
    def log(self, msg):
        print '[SUPERVISOR] '+msg

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
        self.log("sending keywords")
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
        for tweet in raw_tweet_list:
            tweet_obj = Tweet.deserialize(tweet)
            self.q.put(tweet_obj)

    def get_tweets_from_queue(self):
        self.log("Getting tweets from queue")
        tweets_list = []
        while len(tweets_list) < config.batch_size and not self.q.empty():
            item = self.q.get()
            if item is None:
                break
            tweets_list.append(item)
        return tweets_list

    def insert_data(self):
        self.tweet_list = self.get_tweets_from_queue()
        if len(self.tweet_list) == 0:
            self.log("No tweets to insert")
            return
        self.log("inserting tweets")
        self.init_database()
        cur = self.get_cursor()
        for tweet in self.tweet_list:
            if float(tweet.sentiment) == 0:
                continue
            cur.execute("INSERT INTO api_keywordtweet (text) VALUES (?)", (tweet.text,))

            tweet_id = cur.lastrowid
            cur.execute("SELECT id FROM api_keyword WHERE key = ?", (tweet.key,))
            key_id = cur.fetchone()[0]
            cur.execute("INSERT INTO api_keywordsentiment (keyword_id, tweet_id, value, created_date) VALUES (?,?,?,?)",
                        (key_id, tweet_id, tweet.sentiment, datetime.fromtimestamp(int(tweet.created_date) / 1000.0)))
        self.disconnect_database()

    def _setup(self):
        # self.setDebugToScreen()
        self.q = Queue()
        self.keywords = []
        self.addBehaviour(Process(10), None)

        template = spade.Behaviour.ACLTemplate()
        template.setOntology(config.tweet_with_sentiment)
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(ReceiveTweetsBehav(), t)


class Process(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        pass

    def _onTick(self):
        if self.myAgent.are_keywords_updated():
            self.myAgent.send_keywords()
        self.myAgent.insert_data()


class ReceiveTweetsBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        self.myAgent.log("Received tweets with sentiment message!")
        self.msg = self._receive(False)
        if self.msg:
            tweet_list = self.msg.getContent().split('|')
            if len(tweet_list) != 0 and len(self.msg.getContent()) != 0:
                self.myAgent.receive_tweets(tweet_list)
            else:
                self.myAgent.log("invalid message")
