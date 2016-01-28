# Django-AGENS
The AGENS cache agent system implemented in Django 1.9.1
This is the Django version of cache agent in AGENS system described in Globecom 2015!

## Required Libraries
* Python3-pip: '<sudo apt-get install python3-pip>'
* Django 1.9.1: '<sudo pip3 install django>'
* Django\_cron: '<crontab -e>'
  * Add following lines: '<\* \* \* \* \* python3 /home/$(username)/cacheagent/manage.py runcrons > /home/$(username)/cacheagent/cronjob.log>'
* apache-libcloud: '<sudo pip3 install apache-libcloud>'
* PyCrypto: '<sudo pip3 install pycrypto>'
* Screen: '<sudo apt-get install screen>'

## Run the agent
```
screen
cd ~/cacheagent
python3 manage.py makemigrations client home monitor overlay qoe video
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8615
```
