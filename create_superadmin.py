import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trek_annex.settings')
django.setup()

from accounts.models import User

if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser(
        username='superadmin',
        password='Macbook@M1',
        email='superadmin@trekannex.com',
        full_name='Super Admin',
        role='superadmin'
    )
    print('SuperAdmin created successfully!')
else:
    print('SuperAdmin already exists!')
