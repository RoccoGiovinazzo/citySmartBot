from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User as AuthUser
from bot.models import User
from django.conf import settings

def accountLogin(request):
    print('sono qui dentro')
    template = loader.get_template('login.html')
    chatId = request.GET.get('chatId', '')
    settings.USER = chatId
    print(chatId)
    context = {
        'request': request,
    }
    return HttpResponse(template.render(context, request))

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