import base64
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from restaurent import settings
import qrcode
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout

from .models import Restaurateur, Product, Cart, Order, Restaurant
from .forms import ProduitForm
from .token import generatorToken



# Create your views here.

def home(request):
    user = request.user
    if user.groups.filter(name='Restaurateur').exists():
        restos =  Restaurant.objects.filter(proprietaire__user = user)
        return render(request, 'app1/acceuil.html', context={"restos": restos})
    if user.groups.filter(name='Client').exists():
        products = Product.objects.all()
        return render(request, 'app1/acceuil.html', context={"products": products})
    return render(request, 'app1/acceuil.html' )

def register(request):
    if request.method == "POST" :
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        if User.objects.filter(username=username):
            messages.error(request, "ce nom a été déja pris")
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request, "cette email a déja un compte")
            return redirect('register')
        if not username.isalnum():
            messages.error(request, 'le nom être alphanumérique')
            return redirect('register')
        if password != password1 :
            messages.error(request, 'les deux password ne coincident pas')
            return redirect('register')

        mon_utilisateur = User.objects.create_user(username, email, password)
        mon_utilisateur.first_name = firstname
        mon_utilisateur.last_name  =lastname
        mon_utilisateur.is_active = False
        client_group = Group.objects.get(name='Client')
        client_group.user_set.add(mon_utilisateur)
        mon_utilisateur.save()

        #envoie d'email de bienvenue
        messages.success(request, 'Votre compte a été créer avec success')
        subject ="Bienvenue dans notre app "
        message = "Bienvenue "+ mon_utilisateur.first_name + " " + mon_utilisateur.last_name + " \n nous sommes heureux de vous compter parmis nous \n\n\n Merci \n\n Equipe de app" 
        from_email = settings.EMAIL_HOST_USER
        to_list = [mon_utilisateur.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        #Email de confirmation
        current_site  =get_current_site(request)
        email_subject  ="Confirmation de l'address email sur notre app"
        messageConfirm = render_to_string("emailconfirm.html", {
            'name': mon_utilisateur.first_name,
            'domain': current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(mon_utilisateur.pk)),
            'token': generatorToken.make_token(mon_utilisateur)
        })

        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [mon_utilisateur.email]
        )

        email.fail_silently = False
        email.send()
        return redirect('login')
    
    return render(request, 'app1/register.html')

def registerRestaurateur(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']

        # Vérifier si le nom d'utilisateur ou l'adresse e-mail existe déjà
        if User.objects.filter(username=username):
            messages.error(request, "ce nom a été déja pris")
            return redirect('register_restaurateur')
        if User.objects.filter(email=email):
            messages.error(request, "cette email a déja un compte")
            return redirect('register_restaurateur')

        # Vérifier que le nom d'utilisateur est alphanumérique
        if not username.isalnum():
            messages.error(request, 'le nom doit être alphanumérique')
            return redirect('register_restaurateur')

        # Vérifier que les mots de passe correspondent
        if password != password1 :
            messages.error(request, 'les deux password ne coincident pas')
            return redirect('register_restaurateur')

        # Créer un utilisateur
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = firstname
        new_user.last_name = lastname
        new_user.is_active = False
        client_group = Group.objects.get(name='Restaurateur')
        client_group.user_set.add(new_user)
        new_user.save()

        # Créer un restaurateur associé à l'utilisateur
        

        new_restaurateur = Restaurateur()
        new_restaurateur.user = new_user
        new_restaurateur.save()

        # Envoyer un e-mail de bienvenue
        messages.success(request, 'Votre compte a été créé avec succès')
        subject ="Bienvenue dans notre app"
        message = "Bienvenue "+ new_user.first_name + " " + new_user.last_name + " \n nous sommes heureux de vous compter parmi nous \n\n\n Merci \n\n Equipe de app" 
        from_email = settings.EMAIL_HOST_USER
        to_list = [new_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # Envoyer un e-mail de confirmation
        current_site = get_current_site(request)
        email_subject = "Confirmation de l'adresse email sur notre app"
        messageConfirm = render_to_string("emailconfirm.html", {
            'name': new_user.first_name,
            'domain': current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(new_user.pk)),
            'token': generatorToken.make_token(new_user)
        })

        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [new_user.email]
        )

        email.fail_silently = False
        email.send()
        return redirect('login')

    return render(request, 'app1/register_restaurateur.html')

def logIn(request):
    if request.method == "POST" :
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        my_user = User.objects.get(username=username)
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'app1/index.html', {"firstname":firstname})
        elif my_user.is_active == False:
            messages.error(request, "Confirmez votre address mail avant de vous connecter")
        else :
            messages.error(request, 'Mauvaise authentification')
            return redirect('login')
    return render(request, 'app1/login.html')


def logOut(request):
    logout(request)
    messages.success(request, 'Vous avez été bien déconnecter')
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a bien été activer Felicitation !!! connectez vous maintenant")
        return redirect('login')
    else:
        messages.error(request, 'activation échoué !!!')
        return redirect('home')

'''
def ajout_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            form = ProduitForm()
            msg = "Type ajouter, vous pouvez ajouter un autre"
        else : 
            msg = "Remplissez tous les champs"
        return render(request, "app1/ajout_produit.html", {"form": form, "message": msg})
    else :
        form = ProduitForm()
        msg = "Remplissez tous les champs"
        return render(request, "app1/ajout_produit.html", {"form":form, "message":msg})
'''
def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    # ici le _ correspond a une 2 eme variable car la func get_or_create retourne 2 chose 1 le cart et 2 l'information si le cart a ete cree ou non
    order, created = Order.objects.get_or_create(user=user,
                                                 ordered = False,
                                                 product=product
                                                 )
    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity +=1
        order.save()
    
    return redirect('home')

def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'app1/cart.html', {'orders': cart.orders.all()})

def delete_cart(request):
    if cart := request.user.cart:
        cart.delete()
    return redirect('home')

def commande(request):
    user = request.user
    if cart : 
        user.cart.delete()
    return redirect('home')

def restaurant_orders(request, pk):
    restaurant = Restaurant.objects.get(pk=pk)
    orders = Order.objects.filter(product__restaurant=restaurant, processed=False)
    return render(request, 'restaurant_orders.html', {'orders': orders})

def process_order(request, pk):
    order = Order.objects.get(pk=pk)
    order.processed = True
    order.save()
    return redirect('restaurant_orders', order.product.restaurant.pk)


######## Restaurant ######

def ajout_restaurant(request):
    if request.method == 'POST':
        # Récupérer les données saisies par l'utilisateur
        user = request.user
        restaurateur = Restaurateur.objects.get(user = user)
        
        resto_name = request.POST['name']
        phone_resto = request.POST['phone_resto']
        mail_address = request.POST['mail_address']
        address = request.POST['address']
        map_url = request.POST['map_url']

        # Créer une nouvelle instance de Restaurant avec les données saisies
        restaurant = Restaurant(proprietaire = restaurateur, resto_name=resto_name, phone_resto = phone_resto, mail_address = mail_address, address = address, map_url=map_url)
        restaurant.save()

        # Rediriger l'utilisateur vers la page de détails du restaurant
        # Espace restaurant va etre créé prochainement,
        return redirect('home')
    
    return render(request, 'app1/ajout_restaurant.html')

def espace_restaurant(request, pk):
    resto = Restaurant.objects.get(id = pk)
    produits = Product.objects.filter(restaurant_id = resto.id)


    form = ProduitForm()

    return render(request, 'app1/espace_restaurant.html', context={"form": form, "resto": resto, "produits": produits})

def ajout_produit(request, restoid):
    restaurant = Restaurant.objects.get(id=restoid)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():            
            produit = form.save(commit=False)
            produit.restaurant = restaurant
            form.save()
            form = ProduitForm()
            
        return redirect('espace_restaurant', pk=restoid)
    else :
        form = ProduitForm()
        return render(request, "espace_restaurant.html", context = {"form": form,"resto": restaurant})

def supprimer_produit(request, pk):
    produit = Product.objects.filter(id=pk)
    if produit.exists():
        # On récupère l'id du restaurant auquel appartient le produit
        restoid = produit.first().restaurant.id
        
        # On supprime l'objet Product de la base de données
        produit.delete()
        
        # On redirige l'utilisateur vers la vue espace_restaurant pour le restaurant
        return redirect('espace_restaurant', pk=restoid)
    else:
        # Si l'objet n'existe pas, on affiche une erreur 404
        raise Http404("Le produit n'existe pas")
    
    return render(request, 'app1/espace_restaurant.html', context={"resto": resto})

def affichage_menu(request, pk):
        resto = Restaurant.objects.get(id = pk)
        menu = Product.objects.filter(restaurant__resto_name  = resto.resto_name)
        return render(request, 'app1/menu.html', context={"menu": menu, "resto_name" : resto.resto_name})


def qr_code(request, pk):
    resto = Restaurant.objects.get(id = pk)
    # slug = slugify(resto.resto_name)  
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    data = f"http://127.0.0.1:8000/{resto.id}" #(remplacer l'id par le slug si besoin)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convertir l'image QR en format PNG pour l'inclure dans l'e-mail
    from io import BytesIO
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image_data = buffer.getvalue()
    qr_image_base64 = base64.b64encode(qr_image_data).decode('utf-8')

    return render(request, 'app1/qr_code.html', {'qrcode': qr_image_base64})
