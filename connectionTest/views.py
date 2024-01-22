from django.shortcuts import render

# Create your views here.
def connectionTest(request):
    return render(request, "connectionTest/main.html")
