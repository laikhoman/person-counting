#!/bin/sh
while true; do
 flask deploy
 if [[ "$?" == "0" ]]; then
 break
 fi
 echo Deploy command failed, retrying in 5 secs...
 sleep 5
done
flask run --reload --host 0.0.0.0 --port 5000
#exec gunicorn -b :5000 --access-logfile - --error-logfile - dashboard:app

gunicorn --threads 5 --workers 1 --bind 0.0.0.0:5001 app:restreaming.py
