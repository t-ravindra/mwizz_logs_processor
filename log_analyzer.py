"""
Log Analyzer Module
python.exe .\log_analyzer.py --log-path C:\Users\rtholiya\Desktop\mWizz_Logs_Processor\ -s C:\Users\rtholiya\Desktop\mWizz_Logs_Processor\signatures.yml
"""
import logging
import os
import traceback
import argparse
import glob
import re
import yaml
from datetime import datetime
from uuid import uuid4
import csv
from jinja2 import Environment, FileSystemLoader
from elasticsearch import Elasticsearch, helpers

logging.basicConfig(filename="loganalyzer.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

MWIZZ_RESULTS_CSV_HEADERS = ["Product", "Issue", "Name", "Workaround", "Matched String", "Signature", "Matched Log", "Severity"]


class Analyzer:
     def __init__(self, log_path, signature):
         self.log_path = log_path
         self.signature = signature
         self.results = []

     def analyze(self):
         log.info("loading signature file: %s" % (self.signature))
         with open(self.signature, "r") as stream:
            try:
                results_csv = "mwizz_" + datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4()) + ".csv"
                all_signs = yaml.safe_load(stream)
                log.info("Signatures: %s" % yaml.dump(all_signs, default_flow_style=False))
                for sign in all_signs:
                    log.info("processing sign: %s", sign)
                    self.results.extend(self.recurse_logs(self.log_path, sign))
                self.save_to_csv(results_csv=results_csv)
                self.load_to_elasticsearch(results_csv)
            except Exception as exc:
                traceback.print_exc(exc)

     def save_to_csv(self, results_csv):
         with open(results_csv, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(MWIZZ_RESULTS_CSV_HEADERS)
            csvwriter.writerows(self.results)

     def load_to_elasticsearch(self, csv_path):
        #  environment = Environment(loader=FileSystemLoader("./"))
        #  template = environment.get_template("logstash_template.j2")
        #  content = template.render(csv_path=csv_path, csv_fields=MWIZZ_RESULTS_CSV_HEADERS, table_name="mwizz")
        #  with open("mwizz_logstash"+datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4()) + ".cnf", mode="w", encoding="utf-8") as message:
        #     message.write(content)
        es = Elasticsearch( {'host': 'localhost', 'port': 9200, 'use_ssl': False},)
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            helpers.bulk(es, reader, index='mwizz')

     def recurse_logs(self, log_path, sign):
         log.info("Recursing path: %s" %(log_path))
         if "log_file" in sign and sign["log_file"]:
             log.info("Searching file name: %s", sign["log_file"])
             found_files = glob.glob(os.path.join(self.log_path, "**", sign["log_file"]), recursive=True)
             log.info("Found files %s", found_files)
             if len(found_files) > 0:
                for file in found_files:
                    return self.analyze_log(file, sign)
             else:
                 return []
         elif log_path:
            log.info("No file name provide,")
            if os.path.isfile(log_path):
                log.info("Processing file: %s", log_path)
                return self.analyze_log(log_path, sign)
            elif os.path.isdir(log_path):
                log.info("Found dir, recursing to analyze files inside %s", log_path)
                all_results = []
                for f in os.listdir(log_path):
                    log.info("Recursing through %s", f)
                    all_results.extend(self.recurse_logs(f, sign))
                return all_results
            else:
                log.info("Not a log file ignoring.")
                return []


     def analyze_log(self, file, sign):
        log.info("Analysis of file %s started." %(file))
        rows = []
        try:
            log.info("showing this log for testing purpose ERROR sdflkj sdflkj")
            regex = r"" + re.escape(sign["signature"]) + ""
            pattern = re.compile(regex)
            with open(file, 'r') as f:
                matches = pattern.finditer(f.read())
                i = 0
                for match in matches:
                    row = [sign["product"], sign["name"], sign["workaround"], match.group(), sign["signature"], file, sign["severity"]]
                    rows.append(row)
                    i = i+1
            return rows
        except Exception as e:
            log.error("Failed to analyze the log file.", e)
            traceback.print_exc()
        log.info("Analyzing log file: Completed")

def main():
    parser = argparse.ArgumentParser(description="Log process cli.")
    parser.add_argument("-l", "--log-path", type=str, help="path to extracted debuglogs.")
    parser.add_argument("-s", "--signature", type=str, help="path to yaml containing regex signature to look for.")
    args = parser.parse_args()
    analyzer = Analyzer(args.log_path, args.signature)

    analyzer.analyze()

if __name__ == "__main__":
    main()
