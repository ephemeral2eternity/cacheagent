from django.db import models

# Create your models here.
class QoE(models.Model):
	qoe = models.DecimalField(max_digits=6, decimal_places=4)
	srv = models.CharField(max_length=20)
	time = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		str(self.qoe)
