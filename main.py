import threading

from apscheduler.schedulers.background import BlockingScheduler

def process_logs():
  pass

sched = BlockingScheduler()
sched.add_job(process_logs, 'interval', seconds=10)
sched.start()
