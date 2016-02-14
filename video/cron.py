from django_cron import CronJobBase, Schedule
from video.video_utils import *

class video_update_job(CronJobBase):
	"""
	Cron Job that checks the server load and add load info to the db
	"""

	# Run every 1 hour
	run_every = 60
	schedule = Schedule(run_every_mins=run_every)
	code = 'video.cron.video_update_job'

	# This will be executed every 1 hour
	def do(self):
		periodic_discover()
		
