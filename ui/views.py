from django.db.models import Avg, Count
from django.shortcuts import render

from api.models import Keyword, KeywordSentiment, KeywordTweet


def keyword_list(request):
    keywords = Keyword.objects.all()
    return render(request, 'keyword_list.html', {
        'keywords': keywords,
        'breadcrumb': [
            {
                'url': '/ui/keywords',
                'title': 'Lista',
                'active': True
            }
        ]
    })


def keyword_detail(request, key):
    keyword = Keyword.objects.get(key=key)
    keywords = Keyword.objects.all()
    return render(request, 'keyword_detail.html', {
        'keyword': keyword,
        'keywords': keywords,
        'sentiments': KeywordSentiment.objects.filter(keyword=keyword)
                  .aggregate(avg=Avg('value'), count=Count('value')),
        'last_tweet': KeywordTweet.objects.filter(keywordsentiment__keyword=keyword)
                  .order_by('keywordsentiment__created_date').last(),
        'breadcrumb': [
            {
                'url': '/ui/keywords',
                'title': 'Lista',
                'active': False
            },
            {
                'url': '/ui/keywords/{0}'.format(key),
                'title': key,
                'active': True
            }
        ]
    })
