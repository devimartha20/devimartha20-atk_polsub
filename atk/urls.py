from django.urls import path
from . import views
from django.http import HttpResponse


urlpatterns = [
    path('login/', views.login, name='login'),
    path('reset-password/', views.resetPassword, name='reset-password'),
    
    path('', views.home, name='home')
]