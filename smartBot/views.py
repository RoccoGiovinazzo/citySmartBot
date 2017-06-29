from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User as AuthUser
from bot.models import User
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def home(request):
    template = loader.get_template('login.html')
    chatId = request.GET.get('chatId', '')
    settings.USER = chatId
    request.session['chatId'] = chatId
    print("ID Session: " + str(request.session.session_key))
    print("ID Session: " + str(request.GET))
    context = {
        'request': request,
    }
    return HttpResponse(template.render(context, request))

def accountLogin(request):
    print('sono qui dentro')
    template = loader.get_template('login.html')
    chatId = request.GET.get('chatId', '')
    #settings.USER = chatId
    #request.session['chatId'] = chatId
    #print("ID Session: " + str(request.session.session_key))
    #print("ID Session: " + str(request.GET))  
    context = {
        'request': request,
    }
    response = HttpResponse(template.render(context, request))
    response.set_cookie('chatId', chatId)
    print("Coockies: " + str(request.COOKIES))
    return response

def accountLogout(request):
    print('accountLogout')
    template = loader.get_template('login.html')
    chatId = settings.USER 
    print(chatId)
    print('user authentication')
    context = {
        'request': request,
    }
    return HttpResponse(template.render(context, request))