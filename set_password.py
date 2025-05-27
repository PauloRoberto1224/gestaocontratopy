import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contract_manager.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("Senha do usuário 'admin' foi redefinida com sucesso!")
except User.DoesNotExist:
    print("Usuário 'admin' não encontrado.")
    # Criar o superusuário se não existir
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superusuário 'admin' criado com sucesso!")
