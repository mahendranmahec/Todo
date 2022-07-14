from django.db import models
from django.contrib.auth.models import User
# Create your models here.
import datetime



class Task(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # complete = models.BooleanField(default=False)
    # onprocess = models.BooleanField(default=False)
    # todo = models.BooleanField(default=False)
    state=(('completed',"COMPLETED"),('onprocess',"ONPROCESS"),('todo',"TODO"))
    status = models.CharField(max_length=9,choices=state,default='todo')
    # created = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'user'
