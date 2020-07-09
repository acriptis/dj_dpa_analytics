This is django app which dumps dialogs from DP-Agent API

# Initial Install
1. clone the project

2. Create postgres DB and specify its name, user and password in 
dj_dpa_analytics.settings.py see the block `DATABASES`.
3. Then:
```
pip install requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

# Make first dump:
`python upload_dialogs_to_db.py` - loads all dialogs into database from DP-Agent service

# Migrations
```
python manage.py makemigrations
python manage.py migrate
```

See also:
http://93.175.20.219:8081/index.php/Alexa_Prize_Social_Bot#.D0.9D.D0.B0.D1.81.D1.82.D1.80.D0.BE.D0.B9.D0.BA.D0.B0_postgresql