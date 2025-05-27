from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ReportListView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/report_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'reports'
        # Aqui você pode adicionar lógica para buscar relatórios do banco de dados
        context['reports'] = [
            {
                'title': 'Relatório de Contratos Ativos',
                'description': 'Lista de todos os contratos ativos no sistema',
                'url': '#',
                'icon': 'file-earmark-text',
            },
            {
                'title': 'Relatório de Vencimentos',
                'description': 'Contratos próximos ao vencimento',
                'url': '#',
                'icon': 'calendar-check',
            },
            {
                'title': 'Relatório Financeiro',
                'description': 'Análise financeira dos contratos',
                'url': '#',
                'icon': 'graph-up',
            },
        ]
        return context
