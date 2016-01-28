from django_cron import CronJobBase, Schedule
from client.get_vclients import *

class get_vclients_job(CronJobBase):
	"""
	Cron Job that read apache2 access.log to get recent clients that have downloaded
	videos from the current server
	"""

	# Run every 1 minute
	run_every = 5
	schedule = Schedule(run_every_mins=run_every)
	code = 'client.cron.get_vclients_job'

	# This will be executed every 1 minute
	def do(self):
		get_vclients()
