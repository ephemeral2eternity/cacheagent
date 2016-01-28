from django.db import models

# Create your models here.
class Video(models.Model):
	name = models.CharField(max_length=200)
	srvs = models.CharField(max_length=1000, default='')
	isLocal = models.BooleanField(default=True)
	def __str__(self):
		return self.name
