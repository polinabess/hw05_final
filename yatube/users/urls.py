from django.contrib.auth.views import LoginView as LInV, LogoutView as LOutV
from django.contrib.auth.views import PasswordResetView as PswResV
from django.contrib.auth.views import PasswordResetDoneView as PswResDoneV
from django.contrib.auth.views import PasswordResetConfirmView as PswResConfV
from django.contrib.auth.views import PasswordResetCompleteView as PswResCplV
from django.contrib.auth.views import PasswordChangeView as PswChdV
from django.contrib.auth.views import PasswordChangeDoneView as PswChdDoneV
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LOutV.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LInV.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_reset/',
        PswResV.as_view(template_name='users/password_reset_form.html'),
        name='reset_form'
    ),
    path(
        'password_reset/done/',
        PswResDoneV.as_view(template_name='users/password_reset_done.html'),
        name='reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PswResConfV.as_view(template_name='users/password_reset_confirm.html'),
        name='reset_confirm'
    ),
    path(
        'reset/done/',
        PswResCplV.as_view(template_name='users/password_reset_complete.html'),
        name='reset_complete'
    ),
    path(
        'password_change/',
        PswChdV.as_view(template_name='users/password_change_form.html'),
        name='change_form'
    ),
    path(
        'password_change/done/',
        PswChdDoneV.as_view(template_name='users/password_change_done.html'),
        name='change_done'
    ),
]
