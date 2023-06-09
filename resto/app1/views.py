import base64
from datetime import date, timedelta, timezone, datetime
import json
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponse, JsonResponse
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

from .models import Reservation, Restaurateur, Product, Cart, Order, Restaurant, Avis, Livraison
from .forms import ProduitForm, AvisForm, ReservationForm, LivraisonForm
from .token import generatorToken
from django.db.models import Count
from django.db.models import Q

# Create your views here.

def home(request):
    user = request.user
    if user.groups.filter(name='Restaurateur').exists():
        restos =  Restaurant.objects.filter(proprietaire__user = user)
        return render(request, 'app1/acceuil.html', context={"restos": restos})
    if user.groups.filter(name='Client').exists():
        commande = Order.objects.filter(user=user).last()
        heurenow = date.today()
        reservation = Reservation.objects.filter(
            Q(date__gte=heurenow) & Q(agreed=True)& Q(user=user)
        )        
        restaurant =  Restaurant.objects.all()

        return render(request, 'app1/acceuil.html', context={"commande": commande, 'reservations': reservation, 'restaurants': restaurant})
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
    message = ""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                if user.is_active:
                    login(request, user)
                    firstname = user.first_name
                    return render(request, 'app1/index.html', {'firstname': firstname})
                else:
                    message = "Confirmez votre adresse mail avant de vous connecter"
            else:
                message = "Username ou password incorrect !"
        except User.DoesNotExist:
            message = "Username ou password incorrect !"

    return render(request, 'app1/login.html', {'message': message})


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
    
    return redirect('menu', product.restaurant.id)

def delete_cart(request, pk):
    cart = Cart.objects.get(id=pk)
    # Supprime toutes les commandes associées au panier
    for order in cart.orders.all():
        order.delete()
    cart.delete()
    return redirect('cart')

def cart(request):
    user = request.user
    try:
        cart = Cart.objects.get(user__id=user.id)
        orders = cart.orders.all()
        return render(request, 'app1/cart.html', {'orders': orders,'cart':cart})
    except Cart.DoesNotExist:
        orders = []
        return render(request, 'app1/cart.html', {'orders': orders})


def commande (request):
    heuretoday = datetime.now(tz=timezone.utc)
    heuretoday = heuretoday - timedelta(hours=12)
    user = request.user
    orders = Order.objects.filter(user = user).order_by('-ordered_date')
    livraisons = Livraison.objects.filter(order__delivery = True)
    return render(request, 'app1/commandes.html', {'user':user, 'orders':orders, 'livraisons':livraisons,'heuremoins12':heuretoday,})


def valider(request):
    user = request.user
    if user.cart: 
        user.cart.orders.update(ordered=True)
        user.cart.delete()
        user.save()
    return redirect('home')

def livraison(request):
    user = request.user
    if request.method == "POST":
        form = LivraisonForm(request.POST)
        if form.is_valid():
            if user.cart: 
                user.cart.orders.update(ordered=True, delivery=True)
                livraison = form.save(commit=False)
                livraison.user = user
                livraison.save()
                # il faut que ce soit des commandes car le cart est supprimer
                livraison.order.set(user.cart.orders.all())
                user.cart.delete()
                user.save()
            return redirect('home')
    else:
        form = LivraisonForm()
    return render(request, 'app1/livraison.html', {"form":form})


''' par mesure de précaution on a garder l'ancienne version
def restaurant_orders(request, pk):
    restaurant = Restaurant.objects.get(id=pk)
    orders = Order.objects.filter(product__restaurant=restaurant, processed=False)
    num_orders = orders.count()  # Nombre de commandes en attente
    return render(request, 'app1/restaurant_orders.html', {'orders': orders, 'num_orders': num_orders})
'''
def restaurant_orders(request, pk):
    restaurant = Restaurant.objects.get(id=pk)

    #les commandes non traités
    orders = Order.objects.filter(product__restaurant=restaurant, processed=False)
    user_orders = orders.values('user__username').annotate(total_orders = Count('id'))
    num_orders = orders.count()  # Nombre de commandes en attente

    #les commandes déjà traité
    orders_done = Order.objects.filter(product__restaurant=restaurant, processed=True)
    user_orders_done = orders_done.values('user__username').annotate(total_orders = Count('id'))


    livraisons = Livraison.objects.filter(order__delivery = True)
    return render(request, 'app1/restaurant_orders.html', {'orders': orders, 'num_orders': num_orders, 'user_orders': user_orders, 'livraisons':livraisons,'resto':restaurant, 'user_orders_done':user_orders_done, 'orders_done':orders_done})


def process_order(request, pk):
    order = Order.objects.get(pk=pk)
    order.processed = True
    if order.delivery == True:
        livraison = Livraison.objects.get(order__id = pk)
        livraison.delivered = True
        livraison.save()
    order.save()
    return redirect('restaurant_orders', order.product.restaurant.pk)

def process_order_user(request, username):
    orders = Order.objects.filter(user__username=username)
    for order in orders:
        order.processed = True
        order.save() 
    return redirect('restaurant_orders', orders[0].product.restaurant.pk)


def search(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        restos = Restaurant.objects.filter(resto_name__icontains=term)[:10]
        results = [{'id': resto.id, 'nom': resto.resto_name} for resto in restos]
        return JsonResponse({'results': results})
    elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'message': 'AJAAAAAXXXXX'})
    return render(request, 'app1/search.html')


def avis_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    avis = Avis.objects.filter(restaurant=restaurant)
    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.restaurant = restaurant
            avis.auteur = request.user
            avis.save()
            messages.success(request, 'Votre avis a été enregistré avec succès.')
            return redirect('avis_restaurant', restaurant_id=restaurant_id)
    else:
        form = AvisForm()
    return render(request, 'app1/avis_restaurant.html', {'resto': restaurant, 'avis': avis, 'avis_form':form})

def supprimer_avis(request, pk):
    avis = Avis.objects.get(id=pk)
    idresto = avis.restaurant.id
    avis_resto = Avis.objects.filter(restaurant__id = idresto)
    div = avis_resto.count()
    print(div)
    moyenne = avis.restaurant.moyenne
    sum = moyenne*div - avis.note
    if div == 1 :
        moyenne = 2.5
    else:
        moyenne = sum / (div-1)
    avis.restaurant.moyenne = moyenne
    print(avis.restaurant.moyenne)

    avis.delete()
        
    return redirect('avis_restaurant', restaurant_id = idresto)


# def ajouter_avis(request, restaurant_id):
#     restaurant = Restaurant.objects.get(id=restaurant_id)
#     if request.method == 'POST':
#         form = AvisForm(request.POST)
#         if form.is_valid():
#             avis = form.save(commit=False)
#             avis.restaurant = restaurant
#             avis.utilisateur = request.user
#             avis.save()
#             messages.success(request, 'Votre avis a été enregistré avec succès.')
#             return redirect('avis_restaurant', restaurant_id=restaurant_id)
#     else:
#         form = AvisForm()
#     return render(request, 'app1/avis_restaurant.html', {'restaurant': restaurant, 'avis_form': form})


######## Restaurant #################################################################################################################################

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
        type = request.POST['type']

        # Créer une nouvelle instance de Restaurant avec les données saisies
        restaurant = Restaurant(proprietaire = restaurateur, resto_name=resto_name, phone_resto = phone_resto, mail_address = mail_address, address = address, map_url=map_url, type=type)
        restaurant.save()

        # Rediriger l'utilisateur vers la page de détails du restaurant
        # Espace restaurant va etre créé prochainement,
        return redirect('home')
    
    return render(request, 'app1/ajout_restaurant.html')

def espace_restaurant(request, pk):
    resto = Restaurant.objects.get(id = pk)
    produits = Product.objects.filter(restaurant_id = resto.id)
    orders = Order.objects.filter(product__restaurant=resto, processed=False)
    num_orders = orders.count()
    reservations = Reservation.objects.filter(restaurant=resto, answered=False)
    num_reservations = reservations.count()

    form = ProduitForm()

    return render(request, 'app1/espace_restaurant.html', context={"form": form, "resto": resto, "produits": produits, "num_orders":num_orders, "num_reservations":num_reservations})

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
        return render(request, "app1/espace_restaurant.html", context = {"form": form,"resto": restaurant})

def supprimer_produit(request, pk):
    produit = Product.objects.filter(id=pk)
    
        # On récupère l'id du restaurant auquel appartient le produit
    restoid = produit.first().restaurant.id
        
        # On supprime l'objet Product de la base de données
    produit.delete()
        
        # On redirige l'utilisateur vers la vue espace_restaurant pour le restaurant
    return redirect('espace_restaurant', pk=restoid)

    

def affichage_menu(request, pk):
        resto = Restaurant.objects.get(id = pk)
        menu = Product.objects.filter(restaurant__resto_name  = resto.resto_name)
        return render(request, 'app1/menu.html', context={"menu": menu, "resto" : resto})


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

    return render(request, 'app1/qr_code.html', {'qrcode': qr_image_base64, 'resto' :resto})


####### Reservation ##########

def reserver(request, resto_id):
    restaurant = Restaurant.objects.get(id = resto_id)

    if request.method == 'POST':
        user = request.user
        
        nbr_tables = request.POST['nbr_tables']
        nbr_personnes = request.POST['nbr_personnes']
        date = request.POST['date']
        heure = request.POST['heure']
        commentaire = request.POST['commentaire']

        reservation = Reservation(user = user, restaurant = restaurant, nbr_tables = nbr_tables, nbr_personnes = nbr_personnes, date = date, heure=heure, commentaire = commentaire)
        reservation.save()


        return redirect('menu', pk=resto_id)
    else :
        return render(request, "app1/reserver.html", context = {"resto": restaurant})

def reservations(request):
    user = request.user
    heuretoday = datetime.now(tz=timezone.utc)
    datetoday = date.today()
    reservations = Reservation.objects.filter(user=user).order_by('-id')

    return render(request, 'app1/reservations.html', {'reservations':reservations, 'dateToDay':datetoday, 'heureToDay' : heuretoday})

def reservation_restaurant(request, pk):
    restaurant = Restaurant.objects.get(id=pk)
    reservations = Reservation.objects.filter(restaurant=restaurant, answered=False)
    reservations_answered = Reservation.objects.filter(restaurant=restaurant, answered=True)

    num_reservations = reservations.count()  # Nombre de commandes en attente
    return render(request, 'app1/reservation_restaurant.html', {'resto':restaurant, 'reservations': reservations, 'num_reservations': num_reservations,'reservations_answered':reservations_answered})

def agree_reservation(request, reserv_id):
    reservation = Reservation.objects.get(id=reserv_id)
    reservation.agreed = True
    reservation.answered = True
    reservation.save()
        # Envoyer un mail au client avec la réponse du restaurant
    send_mail(
        'Demande de Reservation au '+ reservation.restaurant.resto_name,
        'Votre demande réservation pour le restaurant est accepté, Nous avons le plaisir d\'approuver votre Demande de reservation pour le ' + reservation.date.strftime('%d/%m/%Y') + ' à ' + reservation.heure.strftime('%H:%M') ,
        settings.EMAIL_HOST_USER,
        [reservation.user.email],
        fail_silently=False,
    )
    return redirect('reservation_restaurant', pk= reservation.restaurant.id)

def disagree_reservation(request, reserv_id):

    reservation = Reservation.objects.get(id=reserv_id)
    reservation.agreed = False
    reservation.answered = True
    reservation.save()

        # Envoyer un mail au client avec la réponse du restaurant
    send_mail(
        'Demande de Reservation au '+ reservation.restaurant.resto_name,
        'Votre demande réservation pour le restaurant est Refusé, Nous avons le regré de refusé votre Demande de reservation pour le ' + reservation.date.strftime('%d/%m/%Y') + ' à ' + reservation.heure.strftime('%H:%M') ,
        settings.EMAIL_HOST_USER,
        [reservation.user.email],
        fail_silently=False,
    )
    return redirect('reservation_restaurant', pk= reservation.restaurant.id)


