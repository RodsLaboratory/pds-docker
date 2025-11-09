PDS Web UI

This small Flask app provides:

- Live tail of mailboxes/log/filewatcher.log (polled)
- Button to copy files from mailboxes/metamap_archive to mailboxes/metamap_inbox
- Gallery of PNG files from mailboxes/pds_output (falls back to pds_outbox)

To run locally:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

The app listens on port 5000 by default.

