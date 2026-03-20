from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def patient_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'patient':
            messages.error(request, 'Access denied. Patient account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def hospital_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'hospital':
            messages.error(request, 'Access denied. Hospital account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Admin account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
