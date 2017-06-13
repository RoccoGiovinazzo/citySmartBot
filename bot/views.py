import sys 

from django.conf import settings
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.contrib.sessions.models import Session 
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from persistence import preferenceHandler
from .models import Cronology, Preference
from .models import User


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
    user = User.objects.filter(chat_id=request.session['chat_id'])
    user.update(auth_user_id = authUser.id)
    allCronology = Cronology.objects.filter(bot_user=request.session['chat_id'])
    cronology = []
    if len(allCronology) < 20:
        for i in range(0 , len(allCronology)):
            cronology.append(allCronology[i])
    else:     
        for i in range(len(allCronology)-20, len(allCronology)):
            cronology.append(allCronology[i])
    preferences = Preference.objects.filter(bot_user=request.session['chat_id'])
    template = loader.get_template('bot/userLogin.html')
    if request.method == 'POST':
        print('richiesta di post' + str(request.POST.get("label", "")))
        preferenceHandler.deletePreference(request.session['chat_id'], str(request.POST.get("label", "")))
    context = {
        'botuser': user,
        'user': authUser,
        'request' : request,
        'cronology': cronology,
        'preferences': preferences,
    }
    return HttpResponse(template.render(context, request))