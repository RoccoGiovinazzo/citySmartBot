from django.shortcuts import render, render_to_response
import utility

def home(request):
    if request.method=='POST':
        name = str(request.POST.get("name",""))
        email = str(request.POST.get("email",""))
        message = str(request.POST.get("message",""))
        
        utility.sendMail(name , email, message)
    context = {
        'request': request,
    }
    return render_to_response('webPage/home.html', context , message="MESSAGE DELIVERED")