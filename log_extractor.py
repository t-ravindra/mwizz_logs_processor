# """
# Zip file extractor
# """
from zipfile import ZipFile, is_zipfile
import logging
import os
import traceback
import sys
import argparse

logging.basicConfig(filename="logextractor.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
log = logging.getLogger()
log.setLevel(logging.DEBUG)




class Zip:
     def __init__(self, zip_file):
         self.zip_file = zip_file

     def recurse_zip(self, zip_file):
         """
         TODO: a zip file can have zips inside hece we should recurse and extract all files before
         processing them.
         """
         log.info("Processing zip file: %s" %(zip_file) )
         extracted_in_dir = None
         if zip_file and is_zipfile(zip_file):
             extracted_in_dir = self.extract_zip(self.zip_file)
             self.recurse_zip(extracted_in_dir)
             return extracted_in_dir
         elif zip_file and os.path.isdir(zip_file):
             log.info("Found dir, recursing to extract any zip files inside.")
             for f in os.listdir(zip_file):
                 self.recurse_zip(f)
         else:
             log.info("Not a zip file ignoring.")

     def extract_zip(self, file):
        log.info("Extracting zip file %s started." %(file))
        extract_in = os.path.join(os.path.dirname(file), os.path.splitext(file)[0])
        log.info("Extracting in: %s" %(extract_in))
        self.extracted_in = extract_in
        try:
            with ZipFile(file, 'r') as zObject:
                if extract_in and not os.path.exists(extract_in):
                    os.makedirs(extract_in)
                zObject.extractall(extract_in)
            return extract_in
        except Exception as e:
            log.error("Failed to extract the zip file.", e)
            traceback.print_exc()
        log.info("Extracting zip file: Completed")
        return None

def main():
    parser = argparse.ArgumentParser(description="Log process cli.")
    parser.add_argument("-l", "--log-path", type=str, help="path to debuglogs zip file.")
    args = parser.parse_args()
    zip = Zip(args.log_path)
    zip.recurse_zip(args.log_path)

if __name__ == "__main__":
    main()
