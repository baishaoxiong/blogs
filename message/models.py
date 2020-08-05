from django.db import models
from  topic.models import Topic
from  user.models import UserProfile
# Create your models here.
class Message(models.Model):
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    user_porfile=models.ForeignKey(UserProfile,models.CASCADE)
    content=models.CharField(max_length=50,verbose_name='内容')
    created_time=models.DateTimeField(auto_now_add=True)
    parent_messgae =models.IntegerField(verbose_name='回复的留言id',default=0)