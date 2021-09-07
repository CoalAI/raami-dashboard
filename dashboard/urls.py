from django.urls import path

from dashboard.views import (UserLoginView, calculate_score, file_available,
                             index, logoutUser)

urlpatterns = [
    path('', index, name='index'),
    path('files/', file_available, name='file-available'),
    path('calculate-score/', calculate_score, name='calculate-score'),

    path('login/', UserLoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', logoutUser, name='logout'),
]
