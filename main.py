import threading
import os
import shutil
from log_extractor import Zip
from log_analyzer import Analyzer
import logging
import traceback

from apscheduler.schedulers.background import BlockingScheduler

logging.basicConfig(filename="main.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def process_logs():
  for file in os.listdir("/logs_to_be_processed"):
    log.info("found file: %s" % file)
    src_file = os.path.join("/","logs_to_be_processed", file)
    dst_file = os.path.join("/","logs_extracted",os.path.basename(file).split('/')[-1])
    shutil.copyfile(src_file, dst_file)
    if os.path.isfile(src_file):
        try:
            os.remove(src_file)
        except Exception as e:
           traceback.print_exc(e)
    zip = Zip(zip_file=dst_file)
    zip.recurse_zip(dst_file)
    #process logs now
    analyze = Analyzer(log_path=zip.extracted_in, signature="/issue_signatures/signatures.yml")
    analyze.analyze()

sched = BlockingScheduler()
sched.add_job(process_logs, 'interval', seconds=2)
sched.start()
