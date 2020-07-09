This is django app which dumps dialogs from DP-Agent API

# Install
pip intsall requirements.txt

python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py runserver

# Make first dump:
python upload_dialogs_to_db.py - loads all dialogs into database from DP-Agent service



See also:
http://93.175.20.219:8081/index.php/Alexa_Prize_Social_Bot#.D0.9D.D0.B0.D1.81.D1.82.D1.80.D0.BE.D0.B9.D0.BA.D0.B0_postgresql