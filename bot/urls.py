'''
Created on 10 apr 2017

@author: Geko
'''

from django.conf.urls import url
from . import views

urlpatterns = [
    # /bot/
    url(r'^(?P<chat_id>[0-9]+)/$', views.index, name='index'),
    
    #/bot/194214391
    #url(r'^(?P<chat_id>[0-9]+)/$', views.detail, name='detail'),
    
    #/bot/userLogin
    url(r'^$', views.userLogin, name='userLogin')
    #url(r'^(?P<chatId>\w{0,50})/$', views.userLogin, name='userLogin'),
]