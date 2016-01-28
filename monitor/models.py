from django.db import models

# The monitoring variables are defined here
class SYS_STAT(models.Model):
	cpu_util = models.DecimalField(max_digits=10, decimal_places=5)
	mem_util = models.DecimalField(max_digits=10, decimal_places=5)
	io_tps = models.DecimalField(max_digits=10, decimal_places=5)
	io_readblks = models.DecimalField(max_digits=10, decimal_places=5)
	io_writeblks = models.DecimalField(max_digits=10, decimal_places=5)
	inbound_traffic = models.DecimalField(max_digits=10, decimal_places=5)
	outbound_traffic = models.DecimalField(max_digits=10, decimal_places=5)
	total_io_read = models.IntegerField()
	total_io_write = models.IntegerField()
	total_tx_bytes = models.IntegerField()
	total_rx_bytes = models.IntegerField()
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.cpu_util)

class Load(models.Model):
	load = models.IntegerField()
	total = models.IntegerField()
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.load)

class BW(models.Model):
	tx = models.IntegerField()
	bw = models.DecimalField(max_digits=10, decimal_places=5)
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.bw)

class RTTS(models.Model):
	rtts = models.CharField(max_length=9999)
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return rtts
