from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from dashboard.score_service.score_calc_utils import get_counties, get_states


def index(request):
    return render(request, 'index.html', {'Title': 'Raami Dashboard'})


@login_required
def file_available(request):
    return render(request, 'dashboard/pages/files-available.html', {'Title': 'Raami Dashboard'})


@login_required
def calculate_score(request):
    counties = []
    states = []
    if request.method == 'GET':
        counties = get_counties()
        states = get_states()
    return render(request, 'dashboard/pages/calculate-score.html', {
        'Title': 'Raami Dashboard',
        'counties': counties,
        'states': states
    })


@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class UserLoginView(LoginView):
    template_name = 'user/login.html'
