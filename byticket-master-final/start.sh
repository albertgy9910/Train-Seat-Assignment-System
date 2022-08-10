nohup python manage.py runserver 0.0.0.0:8080 &
sleep 1
tail -1000f nohup.out
