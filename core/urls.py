from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principais
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('inicio/', RedirectView.as_view(pattern_name='core:dashboard'), name='home'),
    
    # Autenticação
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.UserRegistrationView.as_view(), name='register'),
    
    # Perfil e conta
    path('perfil/', views.UserProfileView.as_view(), name='profile'),
    path('perfil/senha/', views.UserPasswordChangeView.as_view(), name='password_change'),
    
    # Atividades
    path('atividades/', views.ActivityLogView.as_view(), name='activity_log'),
    
    # Redefinição de senha
    path('redefinir-senha/', 
         auth_views.PasswordResetView.as_view(
             template_name='core/password_reset.html',
             email_template_name='core/emails/password_reset_email.html',
             subject_template_name='core/emails/password_reset_subject.txt',
             success_url='email-enviado/'
         ), 
         name='password_reset'),
    path('redefinir-senha/email-enviado/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='core/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('redefinir/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='core/password_reset_confirm.html',
             success_url='/redefinir-concluido/'
         ), 
         name='password_reset_confirm'),
    path('redefinir-concluido/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='core/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Página inicial (redireciona para o dashboard)
    path('', RedirectView.as_view(pattern_name='core:dashboard'), name='index'),
]

# URLs para tratamento de erros
handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
