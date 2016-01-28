from django_cron import CronJobBase, Schedule
from monitor.cache_monitor import *

class load_job(CronJobBase):
	"""
	Cron Job that checks the server load and add load info to the db
	"""

	# Run every 1 minute
	run_every = 5
	schedule = Schedule(run_every_mins=run_every)
	code = 'monitor.cron.load_job'

	# This will be executed every 1 minute
	def do(self):
		load_monitor()
		bw_monitor()

class sys_stat_job(CronJobBase):
	"""
	Cron Job that checks the server cpu, mem, io, bw and add these info to the db
	"""

	# Run every 1 minute
	run_every = 1
	schedule = Schedule(run_every_mins=run_every)
	code = 'monitor.cron.sys_stat_job'

	# This will be executed every 1 minute
	def do(self):
		sys_monitor()

class monitor_dump_job(CronJobBase):
	# Run every day at mid night
	RUN_AT_TIMES = ['05:00']
	schedule = Schedule(run_at_times=RUN_AT_TIMES)
	code = 'monitor.cron.monitor_dump_job'

	# This will be executed every day at 23:55
	def do(self):
		dump_monitor()
