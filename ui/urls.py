from django.conf.urls import url
from ui import views

urlpatterns = [
    url(r'keywords/$', views.keyword_list),
    url(r'keywords/(?P<key>[a-zA-Z]+)/$', views.keyword_detail),
]
