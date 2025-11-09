#!/usr/bin/env bash
set -e

# Create log directory if it doesn't exist
LOG_DIR="/opt/mailboxes/log"

# Start file_watcher.py in background and redirect stdout/stderr to a logfile
cd /opt/com
if [ -f "./file_watcher.py" ]; then
  nohup python3 ./file_watcher.py -l "$LOG_DIR/filewatcher.log" > "$LOG_DIR/filewatcher_err.log" 2>&1 &
else
  echo "Warning: file_watcher.py not found in $(pwd)" >> "$LOG_DIR/start_services.log"
fi

# Start app.py in foreground (replace with the correct invocation if your app uses flask run or gunicorn)
cd /opt/web_ui || { echo "Error: /opt/web_ui directory not found" >> "$LOG_DIR/start_services.log"; tail -f /dev/null; }
if [ -f "./app.py" ]; then
  exec python3 ./app.py
else
  echo "Error: app.py not found in $(pwd)" >> "$LOG_DIR/start_services.log"
  # Prevent container from exiting immediately if both scripts are missing
  tail -f /dev/null
fi

