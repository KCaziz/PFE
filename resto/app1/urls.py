from django.urls import path
from app1 import views
urlpatterns = [
    path('', views.home, name='home'),
    path('<int:pk>/', views.affichage_menu, name='menu'),
    path('<str:slug>/add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('register/client', views.register, name='registerClient'),
    path('register/restaurateur', views.registerRestaurateur, name='register_restaurateur'),
    path('login', views.logIn, name='login'),
    path('logout', views.logOut, name='logout'),
    path('cart/', views.cart, name="cart"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    #path('ajout_produit', views.ajout_produit, name='ajout_produit'),
    path('restaurateur/espace_restaurant/<int:pk>/ajout_plat', views.ajout_produit, name='ajout_produit'),
    path('cart/commande', views.commande, name='commande'),
    path('register/restaurateur/espace_restaurant/<int:pk>', views.espace_restaurant, name = 'espace_restaurant'),
    path('restaurateur/ajoutRestaurant', views.ajout_restaurant, name = 'ajout_restaurant'),
    path('restaurateur/espace_restaurant/<int:pk>/qr_code', views.qr_code, name='qr_code'),

    ]
 