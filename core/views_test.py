from django.http import HttpResponse
from django.views import View

class TestView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Teste de visualização bem-sucedido!")
