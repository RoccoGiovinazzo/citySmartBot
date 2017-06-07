from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.db.models.fields.reverse_related import ManyToOneRel

# Create your models here.
class User(models.Model):
    
    lat = models.FloatField(max_length=100, blank=True, null=True)
    lon = models.FloatField(max_length=100, blank=True, null=True)
    positionName = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=250)
    surname = models.CharField(max_length=250)
    chat_id = models.CharField(primary_key=True, max_length=250)
    botActived = models.BooleanField(default=True)
    lastCommand = models.CharField(max_length=1000, blank=True)
    auth_user = models.ForeignKey(AuthUser, blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name + " " + self.surname
    
    class Meta:
        app_label = 'bot'
        
class Preference(models.Model):
    lat = models.FloatField(max_length=100, blank=True, null=True)
    lon = models.FloatField(max_length=100, blank=True, null=True)
    label = models.CharField(max_length=250)
    address = models.CharField(max_length=250, null=True)
    bot_user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Cronology(models.Model):
    command = models.CharField(max_length=250)
    date = models.DateTimeField()
    bot_user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'bot'
    