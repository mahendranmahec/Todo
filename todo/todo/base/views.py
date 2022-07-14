from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm

from django.contrib import messages
from django.contrib.auth.models import User, auth
from todo_list import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token





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
                message2 = render_to_string('base/email_confirmation.html',{
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
        return redirect('/login')
        
    else:
        return render(request,'base/register.html')


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
        return render(request,'base/activation_failed.html')


def logout(request):
    auth.logout(request)
    messages.success(request,"Logged Out Successfully!")
    return redirect('/')


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')



class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(status="completed").count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description','status']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description','status']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

def deleteCompleted(request):
    Task.objects.filter(status="completed").delete()

    return redirect('/')

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))








# background: linear-gradient(90deg, #EEA390 0%, #EB796F 43%, #EB796F 100%);