from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Lista de relatórios
    path('', views.ReportListView.as_view(), name='report_list'),
    
    # Aqui você pode adicionar outras URLs para geração de relatórios específicos
    # Exemplo:
    # path('contratos-ativos/', views.contratos_ativos, name='contratos_ativos'),
]
