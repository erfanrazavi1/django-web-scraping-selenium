from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class ErrorRedirectMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if request.path == "/search/":
            request.session["error_message"] = "یا مشکل از سروره یا اطلاعاتی که وارد کردی عزیزوم .دوباره امتخان کن:)"
            return redirect("/")
        return None
