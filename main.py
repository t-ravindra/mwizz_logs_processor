import threading
import os
import shutil
from log_extractor import Zip
from log_analyzer import Analyzer
import logging
import traceback
from db_connector import DBConnector

from apscheduler.schedulers.background import BlockingScheduler

logging.basicConfig(filename="main.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
db_obj = DBConnector()


def process_logs():
  for file in os.listdir("/logs_to_be_processed"):
    request_id= file.split(".")[0]
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
    db_obj.db_update_status("bug_info",request_id,"processing")
    analyze = Analyzer(log_path=zip.extracted_in, signature="/issue_signatures/signatures.yml")
    analyze.analyze()
    db_obj.db_update_status("bug_info",request_id,"done")


sched = BlockingScheduler()
sched.add_job(process_logs, 'interval', seconds=30)
sched.start()


