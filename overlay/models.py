from django.db import models
from decimal import Decimal

# Save all the cache servers in overlay.Server model
class Server(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	rtt = models.DecimalField(max_digits=10, decimal_places=3, default=255.0)
	qoe = models.DecimalField(max_digits=6, decimal_places=4, default=0.00)
	load = models.IntegerField(default=0)
	hop = models.IntegerField(default=60)
	bw = models.DecimalField(max_digits=10, decimal_places=5, default=0.00)
	isLocal = models.BooleanField(default=False)
	def __str__(self):
		self.name

class Peer(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	def __str__(self):
		self.name
