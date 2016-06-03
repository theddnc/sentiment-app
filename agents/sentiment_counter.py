import nltk
from googleapiclient.discovery import build
import math

class SentimentCounter(object):
    def __init__(self):
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tokenizer = nltk.tokenize.TweetTokenizer()
        self.service = build("customsearch", "v1",
                        developerKey="AIzaSyC7dxUlRswzAw87teCbOq4TE-UANiSErFE")

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
            if sentence[index][1] == 'JJ':
                if sentence[index+1] and (sentence[index+1][1] == 'NN' or sentence[index+1][1] == 'NNS'):
                    phrases.append([sentence[index], sentence[index+1]])
                elif sentence[index+1] and sentence[index+1][1] == 'JJ':
                    if (sentence[index+2] and (sentence[index+2][1] != 'NN' and sentence[index+2][1] != 'NNS')) or not sentence[index+2]:
                        phrases.append([sentence[index], sentence[index+1]])
            if sentence[index][1] == 'RB' or sentence[index][1] == 'RBR' or sentence[index][1] == 'RBS':
                if sentence[index + 1] and sentence[index + 1][1] == 'JJ':
                    if (sentence[index + 2] and (sentence[index + 2][1] != 'NN' and sentence[index + 2][1] != 'NNS')) or not sentence[index + 2]:
                        phrases.append([sentence[index], sentence[index + 1]])
                elif sentence[index + 1] and (sentence[index + 1][1] == 'VB' or sentence[index + 1][1] == 'VBD' or sentence[index + 1][1] == 'VBN' or sentence[index + 1][1] == 'VBG'):
                    phrases.append([sentence[index], sentence[index + 1]])
            if sentence[index][1] == 'NN' or sentence[index][1] == 'NNS':
                if sentence[index + 1] and sentence[index + 1][1] == 'JJ':
                    if (sentence[index + 2] and (sentence[index + 2][1] != 'NN' and sentence[index + 2][1] != 'NNS')) or not sentence[index + 2]:
                                phrases.append([sentence[index], sentence[index + 1]])
        return phrases

    def count_sentiment_for_phrase(self, phrase):
        phrase_near_poor = self.service.cse().list(
            q='"poor" '+phrase,
            cx='000797812240645302824:8o6spe9gkxa',
        ).execute()['searchInformation']['totalResults']
        phrase_near_poor = float(phrase_near_poor)

        phrase_near_excellent = self.service.cse().list(
            q='"excellent" '+phrase,
            exactTerms=phrase,
            cx='000797812240645302824:8o6spe9gkxa',
        ).execute()['searchInformation']['totalResults']
        phrase_near_excellent = float(phrase_near_excellent)

        excellent = self.service.cse().list(
            q='"excellent"',
            exactTerms=phrase,
            cx='000797812240645302824:8o6spe9gkxa',
        ).execute()['searchInformation']['totalResults']
        excellent = float(excellent)

        poor = self.service.cse().list(
            q='"poor"',
            exactTerms=phrase,
            cx='000797812240645302824:8o6spe9gkxa',
        ).execute()['searchInformation']['totalResults']
        poor = float(poor)
        return math.log((phrase_near_excellent * poor)/(phrase_near_poor * excellent), 2)

    def count_sentiment(self, text):
        tokenized_sentences = self.split_paragraph_into_words(text)
        tagged_sentences = self.pos_tag(tokenized_sentences)
        phrases = [self.split_into_two_words_phrases(sentence) for sentence in tagged_sentences][0]
        sentiment = 0.0
        for phrase in phrases:
            query = phrase[0][0]+' ' + phrase[1][0]
            sentiment += self.count_sentiment_for_phrase(query)
        return sentiment

# text = """The third step is to calculate the average semantic
# orientation of the phrases in the given review
# and classify the review as recommended if the average
# is positive and otherwise not recommended.
# """
# s = SentimentCounter()
# print s.count_sentiment(text)