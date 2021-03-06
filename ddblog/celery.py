import os

from celery import  Celery
from django.conf import  settings



#添加环境变量 ，告知celery 该追随谁

os.environ.setdefault('DJANGO_SETTINGS_MODULE','ddblog.settings')

app=Celery('ddblog')
app.conf.update(
    BROKER_URL='redis://@127.0.0.1:6379/1'


)


app.autodiscover_tasks(settings.INSTALLED_APPS)