import time
from django.contrib import auth
from django.shortcuts import redirect

SESSION_TIMEOUT = 10


class LogoutAfterSomeTime:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        if not request.user.is_superuser:
            request.session['last_user_action'] = time.time()
            last_user_action = request.session.get('last_user_action')
            time_now = time.time()
            time_passed = time_now - last_user_action if last_user_action else 0
            timeout = SESSION_TIMEOUT

            if time_passed > timeout:
                auth.logout(request)
                return redirect('login/login.html')
            else:
                request.session['last_user_action'] = time_now
                time_passed = 0

        response = self.get_response(request)
        # Code to be executed for each request/response after the view is called.

        return response
