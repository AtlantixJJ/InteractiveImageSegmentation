from django.conf.urls import url
 
from . import views
 
urlpatterns = [
    url(r'^homepage$', views.homepage),
    url(r'^consequence$',views.consequence),
]
