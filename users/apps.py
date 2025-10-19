def ready(self):
    import os
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError, ProgrammingError

    if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_SETTINGS_MODULE'):
        try:
            User = get_user_model()
            if not User.objects.filter(username='systemadmin').exists():
                system_admin = User.objects.create_user(
                    username='systemadmin',
                    password='SystemAdmin123!',
                    role='admin',
                    email='system@hr-agency.ru',
                    first_name='System',
                    last_name='Administrator'
                )
                system_admin.is_system_user = True
                system_admin.save()
                print("✅ Системный администратор создан: systemadmin / SystemAdmin123!")
        except (OperationalError, ProgrammingError):
            pass