from pickle import GET

from django.contrib.auth import models
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, DetailView, CreateView, DeleteView
from .models import Claim, Comment, MyUser, ClientClaimFilter
from .forms import MyForm, UserUpdateViewForm, ClientClaimCreateViewForm, ClientClaimUpdateViewForm, \
    ClaimApproveUpdateViewForm, CommentCreateViewForm


def home(request):
    return render(request, template_name="home.html")


def user_info(request):
    return render(request, template_name="login/user_info.html")


def client_claims(request):
    filter = ClientClaimFilter(request.GET, queryset=Claim.objects.all())
    return render(request, 'admin/claims_all.html', {'filter': filter})


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
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = ClientClaimCreateViewForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.client = self.request.user
        self.object = object
        object.save()
        return HttpResponseRedirect(self.get_success_url())
        # return super().form_valid(form)


class ClientClaimUpdateView(UpdateView):
    model = Claim
    template_name = 'client/claim_update.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = ClientClaimUpdateViewForm


class ClientClaimDeleteView(DeleteView):
    model = Claim
    template_name = 'client/claim_delete.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')


class ClientClaimListView(ListView):
    model = Claim
    template_name = 'client/client_claim_list.html'
    ordering = ['-application_update', 'status']
    paginate_by = 5

    def get_queryset(self):
        queryset = Claim.objects.filter(client=self.request.user)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update(
            {'claim_update_form': ClientClaimUpdateViewForm})
        return context


class ClaimApproveUpdateView(UpdateView):
    model = Claim
    success_url = reverse_lazy('mydiplom:client_claims')
    form_class = ClaimApproveUpdateViewForm
    template_name = 'admin/approve_claim.html'  # форма подтверждения заявки

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.status = str('Принятая')
        self.instance = instance
        instance.save()
        return HttpResponseRedirect(self.get_success_url())


class CommentCreateView(CreateView):
    model = Comment
    template_name = 'client/comment_create.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = CommentCreateViewForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.author = self.request.user
        # object.to_claim = Comment.objects.select_related('to_claim').get(id='claim.pk')
        # object.to_claim = Comment.objects.filter(to_claim=int('claim.pk'))
        object.to_claim = Comment.objects.filter(to_claim=claim.pk)
        self.object = object
        object.save()
        return HttpResponseRedirect(self.get_success_url())


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
