from django.shortcuts import render

def home(request):
    context = {
        'request': request,
    }
    return render(request, 'webPage/home.html', context)