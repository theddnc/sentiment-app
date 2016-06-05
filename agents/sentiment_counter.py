import nltk
import math
import urllib2
import json
import pprint

BING_SEARCH_URL = 'https://api.datamarket.azure.com/Bing/Search/Composite?Sources=%27web%27&Query=%27{0}%27&$top=1&$format=JSON'

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
        
        value_set = {
            phrase_near_poor: { query: '%22'+phrase+'%22%22poor%22' }, 
            phrase_near_excellent: { query: '%22' + phrase + '%22%22excellent%22' }, 
            excellet: { query: '%22excellent%22' }, 
            poor: { query: '%22poor%22' }, 
        }
        
        value_set = {k: count_results_from_bing(v) for k, v in value_set.items()}

        return math.log((value_set.phrase_near_excellent.value * value_set.poor.value)/(value_set.phrase_near_poor.value * value_set.excellent.value), 2)
        
    def count_results_from_bing(item):
        query = item.query
        request = urllib2.Request(BING_SEARCH_URL.format(query)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)
        results = json.load(response)
        item.value = float(results['d']['results'][0]['WebTotal'])
        return item

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
