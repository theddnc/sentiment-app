# coding=utf-8
from rest_framework import serializers
from api.models import Keyword, KeywordSentiment, KeywordTweet


class KeywordTweetSerializer(serializers.ModelSerializer):

    class Meta:
        model = KeywordTweet
        fields = ('text', )


class KeywordSentimentSerializer(serializers.ModelSerializer):
    tweet = KeywordTweetSerializer(many=False)

    class Meta:
        model = KeywordSentiment
        fields = ('value', 'created_date', 'tweet')

    def create(self, validated_data):
        tweet = validated_data.pop('tweet')
        KeywordTweet.objects.create(tweet)
        return KeywordSentiment.objects.create(tweet=tweet, **validated_data)


class KeywordSerializer(serializers.ModelSerializer):
    sentiments = KeywordSentimentSerializer(many=True)

    class Meta:
        model = Keyword
        fields = ('key', 'sentiments')
