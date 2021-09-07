from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {'Title': 'Raami Dashboard'})


@login_required
def file_available(request):
    return render(request, 'dashboard/pages/files-available.html', {'Title': 'Raami Dashboard'})


@login_required
def calculate_score(request):
    return render(request, 'dashboard/pages/calculate-score.html', {'Title': 'Raami Dashboard'})


@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class UserLoginView(LoginView):
    template_name = 'user/login.html'
