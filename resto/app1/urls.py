from django.urls import path
from app1 import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/client', views.register, name='registerClient'),
    path('register/restaurateur', views.registerRestaurateur, name='registerRestaurateur'),
    path('login', views.logIn, name='login'),
    path('logout', views.logOut, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]
