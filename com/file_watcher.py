#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

def unsafe_move(src_path, dest_path):
    """Move a file, overwriting if it exists and showing a warning."""
    if os.path.exists(dest_path):
        print(f"WARNING: File already exists at destination, deleting: {src_path}")
        # Remove the existing file to avoid permission issues on some systems
        os.remove(src_path)
    else:
        shutil.move(src_path, dest_path)


class MetamapEventHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def on_created(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            self.process_file(event.src_path)
    
    def on_moved(self, event):
        """Handle file moved events."""
        # print("Move event")
        if not event.is_directory:
            self.process_file(event.dest_path)
    
    def process_file(self, file_path):
        """Process a new file (equivalent to process_new_file in file_actions.sh)."""
        # output date and time for debugging
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - METAMAP\nFile detected: {file_path} (created or moved into directory)")

        # move .ann files to brat2csv_inbox
        # if file_path.endswith('.ann'):
        #     print(f"Moving .ann file to {BRAT2CSV_INBOX}")
        #     unsafe_move(file_path, os.path.join(BRAT2CSV_INBOX, os.path.basename(file_path)))
        #     return

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.txt', '.text']:
            print(f"Skipping file with unsupported extension: {file_path}")
            return
        
        # Execute MetaMap processing
        # try:
        #     subprocess.run(["cat", file_path, "|", METAMAP_CMD, "--brat", "--usecontext", "--", ">", file_path],
        #                   check=True, cwd=METAMAP_WORKING_DIR)
        #     print(f"MetaMap processing completed for {file_path}")
        #
        #     # Move processed file to archive
        #     basename = os.path.basename(file_path)
        #     archive_path = os.path.join(METAMAP_ARCHIVE, basename)
        #     unsafe_move(file_path, archive_path)
        #     print(f"Moved processed file: {basename} to {METAMAP_ARCHIVE}")
        #
        # except subprocess.CalledProcessError as e:
        #     print(f"Error processing file with MetaMap: {e}")


        # Define the input and output file paths
        input_file_path = file_path
        output_file_path = BRAT2CSV_INBOX + "/" + file_path.split('/')[-1].replace('.txt', '.ann').replace('.text', '.ann')



        # Define the command to execute (e.g., 'cat' to demonstrate)
        # Replace 'cat' with your actual command and its arguments
        command = [METAMAP_CMD, "--brat", "--usecontext", "--"]

        try:
            with open(input_file_path, 'r') as infile, \
                    open(output_file_path, 'w') as outfile:

                # Execute the command with STDIN from infile and STDOUT to outfile
                result = subprocess.run(
                    command,
                    stdin=infile,
                    stdout=outfile,
                    cwd=METAMAP_WORKING_DIR,
                    check=True,  # Raise an exception for non-zero exit codes
                    text=True    # Treat stdin/stdout as text (universal newlines)
                )
            print(f"Command '{' '.join(command)}' executed successfully.")
            print(f"Input read from '{input_file_path}'.")
            print(f"Output written to '{output_file_path}'.")

        except FileNotFoundError:
            print(f"Error: One of the files ('{input_file_path}' or '{output_file_path}') not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")



class Brat2CsvEventHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def on_closed(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            self.process_file(event.src_path)

    # def on_moved(self, event):
    #     """Handle file moved events."""
    #     # print("Move event")
    #     if not event.is_directory:
    #         self.process_file(event.dest_path)

    def process_file(self, file_path):
        """Process a new file (equivalent to process_new_file in file_actions.sh)."""
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - BRAT2CSV\nFile detected: {file_path} (created or moved into directory)")

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.ann']:
            print(f"Skipping file with unsupported extension: {file_path}")
            return


        # Execute MetaMap processing
        try:
            subprocess.run(["python3", BRAT2CSV_CMD, "-i", file_path, "-o", f"{CDS_INBOX}/output.arff"],
                           check=True)
            print(f".ann file processing completed for {file_path}")

            # Move processed file to archive
            basename = os.path.basename(file_path)
            archive_path = os.path.join(BRAT2CSV_ARCHIVE, basename)
            unsafe_move(file_path, archive_path)
            print(f"Moved processed file: {basename} to {BRAT2CSV_ARCHIVE}")

        except subprocess.CalledProcessError as e:
            print(f"Error processing file with MetaMap: {e}")


class CdsEventHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def on_created(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        """Handle file moved events."""
        # print("Move event")
        if not event.is_directory:
            self.process_file(event.dest_path)
            
    def on_modified(self, event):
        """Handle file modified events."""
        # print("Modified event")
        if not event.is_directory:
            self.process_file(event.src_path)
        

    def process_file(self, file_path):
        """Process a new file (equivalent to process_new_file in file_actions.sh)."""
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - CDS\nFile detected: {file_path} (created moved or modified in directory)")

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.arff']:
            print(f"Skipping file with unsupported extension: {file_path}")
            return

        
        
        # output filename uses the current date as the base filename
        cds_output = os.path.join(PDS_INBOX, f"cds_output_{time.strftime('%Y%m%d')}.csv")
        

        try:
            subprocess.run(["java", "-cp", f"{CDS_JAR}:{WEKA_JAR}", CDS_CMD, MODEL_DIR, MODEL_YEAR, file_path, cds_output],
                           check=True)
            print(f"CDS .arff file processing completed for {file_path}")
            print(f"Output saved to {cds_output}")

            # Move processed file to archive
            # basename = os.path.basename(file_path)
            # archive_path = os.path.join(CDS_ARCHIVE, basename)
            # safe_move(file_path, archive_path)
            # print(f"Moved processed file: {basename} to {CDS_ARCHIVE}")

        except subprocess.CalledProcessError as e:
            print(f"Error processing file with MetaMap: {e}")
            
            
class PdsEventHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def on_created(self, event):
        """Handle file creation events."""
        # print("Create event")
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        """Handle file moved events."""
        # print("Move event")
        if not event.is_directory:
            self.process_file(event.dest_path)

    def process_file(self, file_path):
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - PDS\nFile detected: {file_path}")
    
        # Wait for file to stabilize (no size changes)
        prev_size = -1
        current_size = os.path.getsize(file_path)
    
        while prev_size != current_size:
            time.sleep(2)  # Wait 1 second
            prev_size = current_size
            try:
                current_size = os.path.getsize(file_path)
            except FileNotFoundError:
                print(f"File disappeared during size check: {file_path}")
                return
    
        print(f"File {file_path} appears to be complete, processing...")

        # move png files to pds_outbox
        if file_path.endswith('.png'):
            print(f"Moving .png file to {PDS_OUTBOX}")
            unsafe_move(file_path, os.path.join(PDS_OUTBOX, os.path.basename(file_path)))
            return

        # Only process files with extensions we care about
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.csv']:
            print(f"Skipping file with unsupported extension: {file_path}")
            return


        
        # Execute PDS processing
        try:
            subprocess.run(["python3", PDS_CMD, "--data_directory", PDS_INBOX, "--data_file", os.path.basename(file_path)],
                           check=True)
            print(f"PDS .csv file processing completed for {file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing file with PDS: {e}")
            return
        
        # Move processed file to archive
        basename = os.path.basename(file_path)
        archive_path = os.path.join(PDS_ARCHIVE, basename)
        unsafe_move(file_path, archive_path)
        print(f"Moved processed file: {basename} to {PDS_ARCHIVE}")
        


def start_monitoring():

    # Create an observer and event handler
    event_handler = MetamapEventHandler()
    observer = Observer()
    observer.schedule(event_handler, METAMAP_INBOX, recursive=False)
    observer.start()
    print(f"Monitoring started on {METAMAP_INBOX} for new files.")

    # Create observer and handler for brat2csv_inbox
    brat2csv_handler = Brat2CsvEventHandler()
    brat2csv_observer = Observer()
    brat2csv_observer.schedule(brat2csv_handler, BRAT2CSV_INBOX, recursive=False)
    brat2csv_observer.start()
    print(f"Monitoring started on {BRAT2CSV_INBOX} for .ann files.")

    # Create observer and handler for cds_inbox
    cds_handler = CdsEventHandler()
    cds_observer = Observer()
    cds_observer.schedule(cds_handler, CDS_INBOX, recursive=False)
    cds_observer.start()
    print(f"Monitoring started on {CDS_INBOX} for new files.")
    
    # Create observer and handler for pds_inbox
    pds_handler = PdsEventHandler()
    pds_observer = Observer()
    pds_observer.schedule(pds_handler, PDS_INBOX, recursive=False)
    pds_observer.start()
    print(f"Monitoring started on {PDS_INBOX} for new files.")
    
    


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
        print(f"Error: Directory not found: {METAMAP_INBOX}")
        sys.exit(1)
    
    # Check if METAMAP_CMD exists and is executable
    if not os.path.isfile(METAMAP_CMD) or not os.access(METAMAP_CMD, os.X_OK):
        print(f"Error: MetaMap command not found or not executable: {METAMAP_CMD}")
        sys.exit(1)
    
    start_monitoring()
