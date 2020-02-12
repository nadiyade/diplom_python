from django.contrib.auth import models
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, UpdateView, ListView, DetailView, CreateView
from .models import Claim, Comment, MyUser
from .forms import MyForm, UserUpdateViewForm, ClientClaimCreateViewForm


def home(request):
    return render(request, template_name="home.html")


def user_info(request):
    return render(request, template_name="login/user_info.html")


class RegisterFormView(FormView):
    form_class = MyForm
    success_url = "/login/"
    template_name = "login/register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()
        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)


class UserUpdateView(UpdateView):
    model = MyUser
    form_class = UserUpdateViewForm
    success_url = "/"
    template_name = "login/user_update.html"


class LoginFormView(LoginView):
    form_class = AuthenticationForm
    template_name = "login/login.html"


class LogoutFormView(LogoutView):
    next_page = "/"


class UserListView(ListView):
    model = MyUser
    template_name = 'login/user_list.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        return context


class UserDetailView(DetailView):
    model = MyUser
    template_name = 'login/user_detail.html'
    success_url = '/'


class ClientClaimCreateView(CreateView):
    model = Claim
    template_name = 'client/claim_create.html'
    success_url = '/'
    form_class = ClientClaimCreateViewForm

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        else:
            form = self.get_form()
            if form.is_valid():
                instance = form.save(commit="false") # чтобы сохранить данные в БД, commit="true" ?
                # instance.client = MyUser.objects.get(user=request.user) # ошибка, нет аттрибута объекта
                form.client = MyUser.objects.get(user=request.user)
                # form.client = self.request.user
                instance.save()
                return self.form_valid(form)
            else:
                return self.form_invalid(form)


PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )


def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip
