import nltk
from googleapiclient.discovery import build
import math
import urllib2
import json
import pprint

class SentimentCounter(object):
    def __init__(self):
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tokenizer = nltk.tokenize.TweetTokenizer()

    # function which tokenize text (ex. tweet) into list of lists of words
    def split_paragraph_into_words(self, text):
        sentences = self.sent_detector.tokenize(text)
        tokenized_sentences = [self.tokenizer.tokenize(sentence) for sentence in sentences]
        return tokenized_sentences

    def pos_tag(self, sentences):
        tags = [nltk.pos_tag(sentence) for sentence in sentences]
        return tags

    def split_into_two_words_phrases(self, sentence):
        phrases = []
        for index in range(len(sentence)):
            if sentence[index][1] == 'JJ' or sentence[index][1] == 'JJR' or sentence[index][1] == 'JJS' or sentence[index][1] == 'RB' or sentence[index][1] == 'RBR' or sentence[index][1] == 'RBS':
                if index+1 < len(sentence) and (sentence[index+1][1] == 'NN' or sentence[index+1][1] == 'NNS' or sentence[index+1][1] == 'NNP' or sentence[index+1][1] == 'NNPS'):
                    phrases.append([sentence[index], sentence[index+1]])
        return phrases

    def count_sentiment_for_phrase(self, phrase):
        keyBing = 'AXxEt0tlz+z8DRMf8PIW7vH5llUGdSHqv20KF5YwplA'  # get Bing key from: https://datamarket.azure.com/account/keys
        credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1]  # the "-1" is to remove the trailing "\n" which encode adds
        query = '%22'+phrase+'%22%22poor%22'
        url = 'https://api.datamarket.azure.com/Bing/Search/Composite?Sources=%27web%27&Query=%27' + query + '%27&$top=1&$format=JSON'
        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)
        results = json.load(response)
        phrase_near_poor =  float(results['d']['results'][0]['WebTotal'])

        query = '%22' + phrase + '%22%22excellent%22'
        url = 'https://api.datamarket.azure.com/Bing/Search/Composite?Sources=%27web%27&Query=%27' + query + '%27&$top=1&$format=JSON'
        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)
        results = json.load(response)
        phrase_near_excellent = float(results['d']['results'][0]['WebTotal'])

        query = '%22excellent%22'
        url = 'https://api.datamarket.azure.com/Bing/Search/Composite?Sources=%27web%27&Query=%27' + query + '%27&$top=1&$format=JSON'
        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)
        results = json.load(response)
        excellent = float(results['d']['results'][0]['WebTotal'])

        query = '%22poor%22'
        url = 'https://api.datamarket.azure.com/Bing/Search/Composite?Sources=%27web%27&Query=%27' + query + '%27&$top=1&$format=JSON'
        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)
        results = json.load(response)
        poor = float(results['d']['results'][0]['WebTotal'])

        return math.log((phrase_near_excellent * poor)/(phrase_near_poor * excellent), 2)

    def count_sentiment(self, text):
        tokenized_sentences = self.split_paragraph_into_words(text)
        tagged_sentences = self.pos_tag(tokenized_sentences)
        phrases = [self.split_into_two_words_phrases(sentence) for sentence in tagged_sentences][0]
        sentiment = 0.0
        print phrases
        for phrase in phrases:
            query = phrase[0][0]+'+' + phrase[1][0]
            print query
            sentiment += self.count_sentiment_for_phrase(query)
        return sentiment

# text = """good job
# # """
# s = SentimentCounter()
# print s.count_sentiment(text)
