from django.db import models

# Create your models here.
class PClient(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	last_visit = models.DateTimeField(auto_now=True)

class VClient(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	last_visit = models.DateTimeField()
