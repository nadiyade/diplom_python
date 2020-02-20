import time
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.deprecation import MiddlewareMixin

SESSION_TIMEOUT = 5*60


class LogoutAfterSomeTime(MiddlewareMixin):
    def process_request(self, request):
        response = self.get_response(request)
        if not request.user.is_superuser and request.user.is_authenticated:
            last_user_action = request.session.get('last_user_action')
            request.session['last_user_action'] = time.time()
            time_now = time.time()
            time_passed = time_now - last_user_action if last_user_action else 0
            timeout = SESSION_TIMEOUT
            if time_passed > timeout:
                auth.logout(request)
                return redirect('/')
            else:
                #  обнуление времени, если пользователь совершил действие
                request.session['last_user_action'] = time_now
        return self.get_response(request)

