# auth-service

Migraciones propias de este servicio (independientes de los otros 4):
```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:3001
```
