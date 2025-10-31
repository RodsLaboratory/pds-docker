#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

BASE_PATH = "/opt"

METAMAP_CMD = f"{BASE_PATH}/public_mm_lite/metamaplite.sh"
METAMAP_WORKING_DIR = f"{BASE_PATH}/public_mm_lite"
BRAT2CSV_CMD = f"{BASE_PATH}/brat2csv/ann2arff.py"
CDS_JAR = f"{BASE_PATH}/cds/cds-1.0-SNAPSHOT.jar"
WEKA_JAR = f"{BASE_PATH}/cds/weka-stable-3.8.6.jar"
CDS_CMD = "edu.pitt.rods.cds.NaiveBayesEvaluator"
MODEL_DIR = f"{BASE_PATH}/models"
MODEL_YEAR = "2020"
PDS_CMD = f"{BASE_PATH}/PDS/Run_ILI_Tracker.py"

METAMAP_INBOX = f"{BASE_PATH}/mailboxes/metamap_inbox"
METAMAP_ARCHIVE = f"{BASE_PATH}/mailboxes/metamap_archive"
BRAT2CSV_INBOX = f"{BASE_PATH}/mailboxes/brat2csv_inbox"
BRAT2CSV_ARCHIVE = f"{BASE_PATH}/mailboxes/brat2csv_archive"
CDS_INBOX = f"{BASE_PATH}/mailboxes/cds_inbox"
CDS_ARCHIVE = f"{BASE_PATH}/mailboxes/cds_archive"
PDS_INBOX = f"{BASE_PATH}/mailboxes/pds_inbox"
PDS_ARCHIVE = f"{BASE_PATH}/mailboxes/pds_archive"
PDS_OUTBOX = f"{BASE_PATH}/mailboxes/pds_outbox"



def wait_for_file_stabilization(file_path):
    """Wait until the file size stabilizes, indicating that writing is complete."""
    try:
        prev_size = -1
        current_size = os.path.getsize(file_path)

        log_console(f"STABILIZER - Waiting for file to stabilize: {file_path}")

        while prev_size != current_size:
            prev_size = current_size
            time.sleep(1)  # Wait 1 second
            current_size = os.path.getsize(file_path)

    except FileNotFoundError:
        log_console(f"STABILIZER - File disappeared during size check: {file_path}")
        return False

    log_console(f"STABILIZER - File size stabilized: {file_path}")
    return True

def unsafe_move(src_path, dest_path):
    """Move a file, overwriting if it exists and showing a warning."""
    if os.path.exists(dest_path):
        print(f"WARNING: File already exists at destination, deleting: {src_path}")
        # Remove the existing file to avoid permission issues on some systems
        os.remove(src_path)
    else:
        os.rename(src_path, dest_path)

def log_console(message):
    """Log a message to the console with a timestamp."""
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

class MetamapEventHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def on_created(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            self.process_file(event.src_path)


    def process_file(self, file_path):
        # output date and time for debugging
        log_console(f"METAMAP - Processing: {file_path}")


        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.txt', '.text']:
            log_console(f"METAMAP - Skipping file with unsupported extension: {file_path}")
            return

        # Define the input and output file paths
        input_file_path = file_path
        output_file_path = BRAT2CSV_INBOX + "/" + file_path.split('/')[-1].replace('.txt', '.ann').replace('.text', '.ann')

        command = [METAMAP_CMD, "--brat", "--usecontext", "--"]

        try:
            with open(input_file_path, 'r') as infile, \
                    open(output_file_path, 'w') as outfile:

                # Execute the command with STDIN from infile and STDOUT to outfile
                result = subprocess.run(
                    command,
                    stdin=infile,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    cwd=METAMAP_WORKING_DIR,
                    check=True,  # Raise an exception for non-zero exit codes
                    text=True    # Treat stdin/stdout as text (universal newlines)
                )
            log_console(f"METAMAP - Command '{' '.join(command)}' executed successfully.")
            log_console(f"METAMAP - Input read from '{input_file_path}'.")
            log_console(f"METAMAP - Output written to '{output_file_path}'.")
            log_console(f"METAMAP - Stderr: {result.stderr}")

            # delete the original file
            os.remove(input_file_path)
            log_console(f"METAMAP - Deleted original file: {input_file_path}")



        except FileNotFoundError:
            log_console(f"METAMAP - Error: One of the files ('{input_file_path}' or '{output_file_path}') not found.")
        except subprocess.CalledProcessError as e:
            log_console(f"METAMAP - Error executing command: {e}")
        except Exception as e:
            log_console(f"METAMAP - An unexpected error occurred: {e}")



class Brat2CsvEventHandler(FileSystemEventHandler):
    """Handler for file system events."""


    def on_modified(self, event):
        # log_console(f"BRAT2CSV - Modified event: {event}")
        if not event.is_directory:
            self.process_file(event.src_path)


    def process_file(self, file_path):
        log_console(f"BRAT2CSV - Processing: {file_path}")

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.ann']:
            log_console(f"BRAT2CSV - Skipping file with unsupported extension: {file_path}")
            return

        output_file_path = f"{CDS_INBOX}/{os.path.basename(file_path).replace('.ann', '.arff')}"


        # Execute MetaMap processing
        try:
            subprocess.run(["python3", BRAT2CSV_CMD, "-i", file_path, "-o", output_file_path],
                           check=True)
            log_console(f"BRAT2CSV - .ann file processing completed for {file_path}")

            # Move processed file to archive
            basename = os.path.basename(file_path)
            archive_path = os.path.join(BRAT2CSV_ARCHIVE, basename)
            unsafe_move(file_path, archive_path)
            log_console(f"BRAT2CSV - Moved processed file to: {archive_path}")

        except subprocess.CalledProcessError as e:
            log_console(f"BRAT2CSV - Error processing file: {e}")


class CdsEventHandler(FileSystemEventHandler):

    # def on_any_event(self, event):
    #     log_console(f"CDS - Event detected: {event}")

    def on_modified(self, event):
        # log_console(f"CDS - Modified event: {event}")
        if not event.is_directory:
            self.process_file(event.src_path)

    def process_file(self, file_path):
        log_console(f"CDS - Processing: {file_path}")

        wait_for_file_stabilization(file_path)

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.arff']:
            log_console(f"CDS - Skipping file with unsupported extension: {file_path}")
            return

        # output filename uses the current date as the base filename
        cds_output = os.path.join(PDS_INBOX, f"cds_output_{time.strftime('%Y%m%d')}.csv")


        try:
            subprocess.run(["java", "-cp", f"{CDS_JAR}:{WEKA_JAR}", CDS_CMD, MODEL_DIR, MODEL_YEAR, file_path, cds_output],
                           check=True)
            log_console(f"CDS - .arff file processing completed for {file_path}")
            log_console(f"CDS - Output saved to {cds_output}")

            os.remove(file_path)
            log_console(f"CDS - Deleted original file: {file_path}")


        except subprocess.CalledProcessError as e:
            log_console(f"CDS - Error processing file with MetaMap: {e}")


class PdsEventHandler(FileSystemEventHandler):
    # """Handler for file system events."""
    # def on_any_event(self, event):
    #     log_console(f"PDS - Event detected: {event}")

    def on_modified(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            if event.src_path.endswith('.csv'):
                self.process_file(event.src_path)
            if event.src_path.endswith('.png'):
                destPath = os.path.join(PDS_OUTBOX, os.path.basename(event.src_path))
                unsafe_move(event.src_path, destPath)
                log_console(f"PDS - Moved .png file: {destPath}")


    def process_file(self, file_path):
        log_console(f"PDS - Processing: {file_path}")

        wait_for_file_stabilization(file_path)

        # move png files to pds_outbox
        if file_path.endswith('.png'):
            log_console(f"PDS - Moving .png file to {PDS_OUTBOX}")
            unsafe_move(file_path, os.path.join(PDS_OUTBOX, os.path.basename(file_path)))
            return

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.csv']:
            log_console(f"PDS - Skipping file with unsupported extension: {file_path}")
            return



        # Execute PDS processing
        try:
            subprocess.run(["python3", PDS_CMD, "--data_directory", PDS_INBOX, "--data_file", os.path.basename(file_path)],
                           check=True)
            log_console(f"PDS - .csv file processing completed for {file_path}")
        except subprocess.CalledProcessError as e:
            log_console(f"PDS - Error processing file with PDS: {e}")
            return

        # Move processed file to archive
        basename = os.path.basename(file_path)
        archive_path = os.path.join(PDS_ARCHIVE, basename)
        unsafe_move(file_path, archive_path)
        log_console(f"PDS - Moved processed file: {archive_path}")



def start_monitoring():

    # Create an observer and event handler
    event_handler = MetamapEventHandler()
    observer = Observer()
    observer.schedule(event_handler, METAMAP_INBOX, recursive=False)
    observer.start()
    log_console(f"MAIN - Monitoring started on {METAMAP_INBOX} for new files.")

    # Create observer and handler for brat2csv_inbox
    brat2csv_handler = Brat2CsvEventHandler()
    brat2csv_observer = Observer()
    brat2csv_observer.schedule(brat2csv_handler, BRAT2CSV_INBOX, recursive=False)
    brat2csv_observer.start()
    log_console(f"MAIN - Monitoring started on {BRAT2CSV_INBOX} for .ann files.")

    # Create observer and handler for cds_inbox
    cds_handler = CdsEventHandler()
    cds_observer = Observer()
    cds_observer.schedule(cds_handler, CDS_INBOX, recursive=False)
    cds_observer.start()
    log_console(f"MAIN - Monitoring started on {CDS_INBOX} for new files.")

    # Create observer and handler for pds_inbox
    pds_handler = PdsEventHandler()
    pds_observer = Observer()
    pds_observer.schedule(pds_handler, PDS_INBOX, recursive=False)
    pds_observer.start()
    log_console(f"MAIN - Monitoring started on {PDS_INBOX} for new files.")




    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # Check if METAMAP_INBOX exists
    if not os.path.isdir(METAMAP_INBOX):
        log_console(f"MAIN - Error: Directory not found: {METAMAP_INBOX}")
        sys.exit(1)

    # Check if METAMAP_CMD exists and is executable
    if not os.path.isfile(METAMAP_CMD) or not os.access(METAMAP_CMD, os.X_OK):
        log_console(f"MAIN - Error: MetaMap command not found or not executable: {METAMAP_CMD}")
        sys.exit(1)

    start_monitoring()
