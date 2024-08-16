cd /workspace/backend

echo "Base-port: $BASE_PORT"
python manage.py flush # reset database
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages
python manage.py runserver 0.0.0.0:${BASE_PORT}