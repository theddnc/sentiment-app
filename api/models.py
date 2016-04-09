# coding=utf-8
from __future__ import unicode_literals
from django.db import models


class Keyword(models.Model):
    """
    Reprezentuje słowo kluczowe, po którym przeszukiwane jest API Twittera.
    """
    key = models.CharField(max_length=50, blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)


class KeywordTweet(models.Model):
    """
    Treść tweeta, powiązana z sentymentem.
    """
    text = models.CharField(max_length=140, blank=True, null=False, default='')


class KeywordSentiment(models.Model):
    """
    Reprezentuje sentyment powiązany z danym słowem kluczowym oraz Tweetem.
    """
    value = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    keyword = models.ForeignKey(Keyword, null=False, related_name='sentiments')
    tweet = models.ForeignKey(KeywordTweet, null=True)
