from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from restaurent import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login, logout
from .token import generatorToken

# Create your views here.
def home(request):
    return render(request, 'app1/index.html')

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
        user.is_active  =True
        user.save()
        messages.success(request, "Votre compte a bien été activer Felicitation !!! connectez vous maintenant")
        return redirect('login')
    else:
        messages.error(request, 'activation échoué !!!')
        return redirect('home')