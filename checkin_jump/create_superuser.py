import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'checkin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=None, password=password)
    print(f"Superusuário '{username}' criado com sucesso!")
else:
    print(f"Superusuário '{username}' já existe.")
