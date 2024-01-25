ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=123456

echo "from django.contrib.auth import get_user_model; User = get_user_model();
User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell

python manage.py load_data_csv
