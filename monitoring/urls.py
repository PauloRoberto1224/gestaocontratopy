from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Página de alertas
    path('alertas/', views.AlertsView.as_view(), name='alerts'),
    # Redireciona a raiz para a página de alertas
    path('', views.AlertsView.as_view(), name='index'),
]
