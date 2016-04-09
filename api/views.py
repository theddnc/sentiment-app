from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.models import Keyword
from api.serializers import KeywordSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def keyword_list(request):
    if request.method == 'GET':
        keywords = Keyword.objects.all()
        serializer = KeywordSerializer(keywords, many=True)
        return JSONResponse(serializer.data)


@csrf_exempt
def keyword_detail(request, key):
    try:
        keyword = Keyword.objects.get(key=key)
    except Keyword.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = KeywordSerializer(keyword)
        return JSONResponse(serializer.data)
