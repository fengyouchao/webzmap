from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
import json


# Create your views here.

@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')


@require_http_methods(['GET', 'POST'])
def login(request):
    method = request.method
    if method == 'GET':
        next_url = request.GET.get("next", "/")
        return render(request, 'login.html', context={"next": next_url})
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "/")
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            return render(request, 'login.html',
                          context={'error': "Username and password doesn't match", 'next': next_url})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login")
