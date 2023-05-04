from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# AUTHENTICATION
def login(request):
    return render(request, 'atk/login.html')

def resetPassword(request):
    return HttpResponse('reset password')

def home(request):
    return render(request, 'atk/home.html')