from django.shortcuts import render
from django.contrib import messages
import utility

def home(request):
    if request.method=='POST':
        name = str(request.POST.get("name",""))
        email = str(request.POST.get("email",""))
        message = str(request.POST.get("message",""))
        messages.info(request, "MESSAGE DELIVERED")
        utility.sendMail(name , email, message)
    context = {
        'request': request,
    }
    return render(request, 'webPage/home.html', context)