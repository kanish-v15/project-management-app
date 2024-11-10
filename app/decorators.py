"""Decorators.py"""

from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    """role required func"""
    def decorator(view_func):
        """decorator func"""
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('login')
        return wrapper
    return decorator
