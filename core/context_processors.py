from django.conf import settings

def site_info(request):
    """
    Adiciona informações do site ao contexto de todos os templates.
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Sistema de Gestão de Contratos'),
        'SITE_DOMAIN': getattr(settings, 'SITE_DOMAIN', 'localhost:8000'),
        'DEBUG': settings.DEBUG,
    }
