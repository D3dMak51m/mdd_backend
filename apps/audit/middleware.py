# apps/audit/middleware.py

import threading
from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    request = get_current_request()
    if request and getattr(request, 'user', None) and request.user.is_authenticated:
        return request.user
    return None


def get_current_ip():
    request = get_current_request()
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Сохраняем ссылку на request. 
        # Даже если user сейчас Anonymous, позже DRF обновит этот атрибут в этом же объекте request.
        _thread_locals.request = request

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    def process_exception(self, request, exception):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request