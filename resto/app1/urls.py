from django.urls import path
from app1 import views
urlpatterns = [
    path('', views.home, name='home'),
    path('<str:slug>/add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('register/client', views.register, name='registerClient'),
    path('register/restaurateur', views.registerRestaurateur, name='register_restaurateur'),
    path('login', views.logIn, name='login'),
    path('logout', views.logOut, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('Ajout_Plat', views.AjoutPlat, name='AjoutPlat'),
    
    ]
