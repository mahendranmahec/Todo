from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from telusko import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token


# Create your views here.


def login(request):
    if request.method== 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Logged In Sucessfully!!")
            return redirect("/")
        else:
            messages.info(request,'invalid credentials')
            return redirect('login')

    else:
        return render(request,'login.html')    

def register(request):

    if request.method == 'POST': 
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('register')
            # elif User.objects.filter(email=email).exists():
            #     messages.info(request,'Email Taken')
            #     return redirect('register')
            elif len(username)>20:
                messages.error(request, "Username must be under 20 charcters!!")
                return redirect('register')
            elif not username.isalnum():
                messages.error(request, "Username must be Alpha-Numeric!!")
                return redirect('register')
            else:   
                user = User.objects.create_user(username=username, password=password1, email=email,first_name=first_name,last_name=last_name)
                user.is_active = False
                user.save();
                messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
                
                # Welcome Email
                subject = "Welcome to Django Login!!"
                message = "Hello " + user.first_name + "!! \n" + "Welcome !! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You.. :)"        
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject, message, from_email, to_list, fail_silently=True)

                
                # Email Address Confirmation Email
                current_site = get_current_site(request)
                email_subject = "Confirm your Email  - Django Login!!"
                message2 = render_to_string('email_confirmation.html',{
                    'name': user.first_name,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                })
                email = EmailMessage(email_subject,message2,settings.EMAIL_HOST_USER,[user.email])
                email.fail_silently = True
                email.send()
        


                return redirect('login')

        else:
            messages.info(request,'password not matching..')    
            return redirect('register')
        return redirect('/')
        
    else:
        return render(request,'register.html')


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        # user.profile.signup_confirmation = True
        user.save()
        auth.login(request,user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'activation_failed.html')


def logout(request):
    auth.logout(request)
    messages.success(request,"Logged Out Successfully!")
    return redirect('/')
