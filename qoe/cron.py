from django_cron import CronJobBase, Schedule
from qoe.qoe_utils import *

class qoe_dump_job(CronJobBase):
	"""
	Cron Job that dumps QoE job every day
	"""

	# Run every day
	RUN_AT_TIMES = ['05:00']
	schedule = Schedule(run_at_times=RUN_AT_TIMES)
	code = 'qoe.cron.qoe_dump_job'

	# This will be executed every day
	def do(self):
		dumpQoE()
