from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, DetailView, CreateView, DeleteView
from .models import Claim, Comment, MyUser, ClientClaimFilter
from .forms import MyForm, UserUpdateViewForm, ClientClaimCreateViewForm, ClientClaimUpdateViewForm, \
    ClaimApproveUpdateViewForm, CommentCreateViewForm, ClaimRejectUpdateViewForm, ClaimRestoreUpdateViewForm, \
    ClaimFinalRejectUpdateViewForm


def home(request):
    ip = get_client_ip(request)
    return render(request, "home.html", {"ip": ip})


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
        if self.request.user.is_superuser:
            queryset = Claim.objects.all()
        else:
            queryset = Claim.objects.filter(client=self.request.user)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update(
            {'claim_update_form': ClientClaimUpdateViewForm})
        return context


class ClaimAllRejectedListView(ListView):
    model = Claim
    template_name = 'admin/claims_finally_rejected.html'
    ordering = ['-application_update']
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Claim.objects.filter(finally_rejected=True)
        else:
            queryset = Claim.objects.filter(client=self.request.user)
        return queryset


class ClaimInProgressListView(ListView):
    model = Claim
    template_name = 'admin/claims_in_progress.html'
    ordering = ['-application_update']
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Claim.objects.filter(status="Принятая")
        else:
            queryset = Claim.objects.filter(client=self.request.user)
        return queryset


class ClaimWaitingListView(ListView):
    model = Claim
    template_name = 'admin/claims_waiting.html'
    ordering = ['-application_update']
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Claim.objects.filter(status="В обработке")
        else:
            queryset = Claim.objects.filter(client=self.request.user)
        return queryset


class ClaimApproveUpdateView(UpdateView):
    model = Claim
    success_url = reverse_lazy('mydiplom:client_claim_list')
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
        self.object = object
        object.save()
        return HttpResponseRedirect(self.get_success_url())


class CommentListView(ListView):
    model = Comment
    template_name = 'admin/claims_all.html'
    # template_name = ['client/client_claim_list.html', 'admin/claims_all.html']
    ordering = ['-date_created']
    context_object_name = 'comment_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        return context

    # def get_queryset(self):
    #     queryset = Comment.objects.filter(to_claim='claim.pk')
    #     return queryset

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(object_list=self.model, **kwargs)
    #     # context.update(
    #     #     {'comment_update_form': CommentUpdateViewForm})
    #     return context


class ClaimToRestoreListView(ListView):
    model = Claim
    template_name = 'admin/claims_to_restore.html'
    ordering = ['-application_date']
    context_object_name = 'claim_to_restore_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        return context

    def get_queryset(self):
        queryset = Claim.objects.filter(restore_request=True, finally_rejected=False)
        return queryset


class ClaimRejectUpdateView(UpdateView):
    model = Claim
    template_name = 'admin/reject_claim.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = ClaimRejectUpdateViewForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.status = str('Отклонённая')
        instance.first_rejected = True
        if instance.restore_request:
            instance.status = str('Окончательно отклонённая')
            instance.finally_rejected = True
        self.instance = instance
        instance.save()
        return HttpResponseRedirect(self.get_success_url())


class ClaimFinalRejectUpdateView(UpdateView):
    model = Claim
    template_name = 'admin/final_reject_claim.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = ClaimFinalRejectUpdateViewForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.status = str('Окончательно отклонённая')
        instance.finally_rejected = True
        self.instance = instance
        instance.save()
        return HttpResponseRedirect(self.get_success_url())


class ClaimRestoreUpdateView(UpdateView):
    model = Claim
    template_name = 'client/restore_claim.html'
    success_url = reverse_lazy('mydiplom:client_claim_list')
    form_class = ClaimRestoreUpdateViewForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.restore_request = True
        self.instance = instance
        instance.save()
        return HttpResponseRedirect(self.get_success_url())


PRIVATE_IPS_PREFIX = ('10.', '172.', '192.',)


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
