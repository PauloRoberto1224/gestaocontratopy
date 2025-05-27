from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'contracts'

urlpatterns = [
    # Lista de contratos
    path('', views.ContractListView.as_view(), name='contract_list'),
    # Detalhes do contrato
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    # Criar novo contrato
    path('novo/', views.ContractCreateView.as_view(), name='contract_create'),
    # Editar contrato
    path('<int:pk>/editar/', views.ContractUpdateView.as_view(), name='contract_update'),
    # Excluir contrato
    path('<int:pk>/excluir/', views.ContractDeleteView.as_view(), name='contract_delete'),
    # Tipos de contrato
    path('tipos/', views.ContractTypeListView.as_view(), name='contract_type_list'),
    path('tipos/novo/', views.ContractTypeCreateView.as_view(), name='contract_type_create'),
    path('tipos/<int:pk>/editar/', views.ContractTypeUpdateView.as_view(), name='contract_type_update'),
    path('tipos/<int:pk>/excluir/', views.ContractTypeDeleteView.as_view(), name='contract_type_delete'),
    # Status de contrato
    path('status/', views.ContractStatusListView.as_view(), name='contract_status_list'),
    path('status/novo/', views.ContractStatusCreateView.as_view(), name='contract_status_create'),
    path('status/<int:pk>/editar/', views.ContractStatusUpdateView.as_view(), name='contract_status_update'),
    path('status/<int:pk>/excluir/', views.ContractStatusDeleteView.as_view(), name='contract_status_delete'),
    # Partes do contrato
    path('<int:contract_pk>/partes/', views.ContractPartyListView.as_view(), name='contract_party_list'),
    path('<int:contract_pk>/partes/novo/', views.ContractPartyCreateView.as_view(), name='contract_party_create'),
    path('<int:contract_pk>/partes/<int:pk>/editar/', views.ContractPartyUpdateView.as_view(), name='contract_party_update'),
    path('<int:contract_pk>/partes/<int:pk>/excluir/', views.ContractPartyDeleteView.as_view(), name='contract_party_delete'),
    # Lembretes
    path('<int:contract_pk>/lembretes/', views.ContractReminderListView.as_view(), name='contract_reminder_list'),
    path('<int:contract_pk>/lembretes/novo/', views.ContractReminderCreateView.as_view(), name='contract_reminder_create'),
    path('<int:contract_pk>/lembretes/<int:pk>/editar/', views.ContractReminderUpdateView.as_view(), name='contract_reminder_update'),
    path('<int:contract_pk>/lembretes/<int:pk>/excluir/', views.ContractReminderDeleteView.as_view(), name='contract_reminder_delete'),
    path('<int:contract_pk>/lembretes/<int:pk>/concluir/', views.ContractReminderCompleteView.as_view(), name='contract_reminder_complete'),
    # Histórico
    path('<int:pk>/historico/', views.ContractHistoryView.as_view(), name='contract_history'),
    # Relatórios
    path('relatorios/', views.ContractReportView.as_view(), name='contract_reports'),
    # Exportação
    path('exportar/', views.ContractExportView.as_view(), name='contract_export'),
    # Verificação de número de contrato
    path('verificar-numero/', views.check_contract_number, name='check_contract_number'),
]
