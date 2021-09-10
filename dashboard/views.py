from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from dashboard.score_calc_service.score_calc_utils import (get_counties,
                                                           get_file_list,
                                                           get_states, main)


def index(request):
    return render(request, 'index.html', {'Title': 'Raami Dashboard'})


@login_required
def file_available(request):
    files_list = get_file_list(request.get_port())
    return render(request, 'dashboard/pages/files-available.html', {'Title': 'Raami Dashboard', 'files': files_list})


class CustomResponse(HttpResponse):
    def __init__(self, data, then_callback, callaback_data, **kwargs):
        super().__init__(data, **kwargs)
        self.then_callback = then_callback
        self.callaback_data = callaback_data

    def close(self):
        super().close()
        self.then_callback(self.callaback_data)


@login_required
def calculate_score(request):
    if request.method == 'GET':
        counties = get_counties()
        states = get_states()
        return render(request, 'dashboard/pages/calculate-score.html', {
            'Title': 'Raami Dashboard',
            'counties': counties,
            'states': states
        })
    elif request.method == 'POST':
        county = request.POST.get('county', None)
        state = request.POST.get('state', None)
        state = state if state != "" else None
        message = f'Score Calculation process started for {county} and {state}'

        data = {
            'county_name': county,
            'state': state,
            '_date': None,
            'delta': 720,
            'months': 24
        }

        return CustomResponse(message, main, data)


@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class UserLoginView(LoginView):
    template_name = 'user/login.html'
