from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import User
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.contrib.sessions.models import Session 
import sys 
from django.http.response import HttpResponseRedirect
from django.conf import settings
from .models import Cronology, Preference

# Create your views here.

def index(request, chat_id):
    print('CHAT_ID')
    print(chat_id)
    allUser = User.objects.all()
    template = loader.get_template('bot/index.html')
    User.objects.update(auth_user_id = request.user.id)
    context = {
        'request': request,
    }
    return HttpResponse(template.render(context, request))

def detail(request, chat_id):
    user = User.objects.get(chat_id = chat_id)
    template = loader.get_template('bot/user.html')
    context = {
        'user': user,
        'request' : request,
    }
    return HttpResponse(template.render(context, request))

def userLogin(request):
    user_id = request.user.id
    authUser = AuthUser.objects.get(id = request.user.id)
    print('--------------SIAMO IN USER LOGIN--------')
    print(user_id)
    user = User.objects.filter(chat_id=settings.USER)
    user.update(auth_user_id = authUser.id)
    allCronology = Cronology.objects.filter(bot_user=settings.USER)
    cronology = []
    if len(allCronology) < 20:
        for i in range(0 , len(allCronology)):
            cronology.append(allCronology[i])
    else:     
        for i in range(len(allCronology)-20, len(allCronology)):
            cronology.append(allCronology[i])
    
    preferences = Preference.objects.filter(bot_user=settings.USER)
    template = loader.get_template('bot/userLogin.html')
    context = {
        'botuser': user,
        'user': authUser,
        'request' : request,
        'cronology': cronology,
        'preferences': preferences,
    }
    return HttpResponse(template.render(context, request))
#    return HttpResponseRedirect('/%s/'%chatId) 
