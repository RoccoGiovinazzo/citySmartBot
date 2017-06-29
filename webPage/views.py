from django.shortcuts import render

def home(request):
    if request.method=='POST':
        name = str(request.POST.get("name",""))
        email = str(request.POST.get("email",""))
        message = str(request.POST.get("message",""))
        print("nome" + name)
        print("email" + email)
        print("message" + message)
    context = {
        'request': request,
    }
    return render(request, 'webPage/home.html', context)