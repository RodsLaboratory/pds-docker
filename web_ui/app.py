from flask import Flask, render_template, jsonify, request, send_from_directory, abort
import os
import shutil
from pathlib import Path
import threading

app = Flask(__name__, template_folder='templates')

# Resolve mailbox directories relative to repository root
BASE_DIR = Path(__file__).resolve().parent.parent
MAILBOXES = BASE_DIR / 'mailboxes'
LOG_PATH = MAILBOXES / 'log' / 'filewatcher.log'
METAMAP_ARCHIVE = MAILBOXES / 'metamap_archive'
METAMAP_INBOX = MAILBOXES / 'metamap_inbox'
PDS_OUTPUT = MAILBOXES / 'pds_output'
# fallback name seen in repo listing
PDS_OUTPUT_FALLBACK = MAILBOXES / 'pds_outbox'

# Simple lock to avoid concurrent copy operations
_copy_lock = threading.Lock()

print(f"Using MAILBOXES directory: {MAILBOXES}")

def tail_lines(path: Path, n=200):
    """Return last n lines from file as a single string."""
    if not path.exists():
        return f"Log file not found: {path}\n"
    # Read efficiently from end
    try:
        with path.open('rb') as f:
            avg_line_length = 100
            to_read = n * avg_line_length
            try:
                f.seek(-to_read, os.SEEK_END)
            except OSError:
                f.seek(0)
            data = f.read().decode(errors='replace')
    except Exception as e:
        return f"Error reading log: {e}\n"
    lines = data.splitlines()
    return '\n'.join(lines[-n:]) + '\n'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logs')
def logs():
    # allow client to request how many lines
    n = request.args.get('n', default=200, type=int)
    text = tail_lines(LOG_PATH, n=n)
    return jsonify({'log': text})


@app.route('/images')
def images():
    dir_path = PDS_OUTPUT if PDS_OUTPUT.exists() else PDS_OUTPUT_FALLBACK
    if not dir_path.exists():
        return jsonify({'images': [], 'path': str(dir_path)})
    files = [f for f in os.listdir(dir_path) if f.lower().endswith('.png')]
    files.sort()
    return jsonify({'images': files})


@app.route('/image/<path:filename>')
def image(filename):
    dir_path = PDS_OUTPUT if PDS_OUTPUT.exists() else PDS_OUTPUT_FALLBACK
    if not dir_path.exists():
        abort(404)
    # send_from_directory handles path traversal safety
    return send_from_directory(str(dir_path), filename)


# Added: return number of files in mailboxes/metamap_inbox (recursive)
@app.route('/metamap_inbox_count')
def metamap_inbox_count():
    dir_path = METAMAP_INBOX
    if not dir_path.exists():
        return jsonify({'count': 0, 'exists': False})
    # count files recursively
    try:
        count = sum(1 for _ in dir_path.rglob('*') if _.is_file())
    except Exception:
        count = 0
    return jsonify({'count': count, 'exists': True})


@app.route('/copy_metamap', methods=['POST'])
def copy_metamap():
    src = METAMAP_ARCHIVE
    dst = METAMAP_INBOX
    if not src.exists():
        return jsonify({'ok': False, 'error': f'source not found: {src}'}), 400
    dst.mkdir(parents=True, exist_ok=True)

    copied = 0
    errors = []
    with _copy_lock:
        for root, dirs, files in os.walk(src):
            rel_root = os.path.relpath(root, str(src))
            target_root = dst if rel_root == '.' else dst / rel_root
            os.makedirs(target_root, exist_ok=True)
            for fname in files:
                s = Path(root) / fname
                t = Path(target_root) / fname
                try:
                    shutil.copy2(s, t)
                    copied += 1
                except Exception as e:
                    errors.append(str(e))
    return jsonify({'ok': True, 'copied': copied, 'errors': errors})

@app.route('/reset_ili', methods=['POST'])
def reset_ili():
    """Delete files from pds_output/pds_outbox and cumulative.csv from pds_working
       Also delete any files inside metamap_inbox (recursive)."""
    pds_working = MAILBOXES / 'pds_working'
    cumulative_csv = pds_working / 'cumulative.csv'

    # Determine which output directory exists
    output_dir = PDS_OUTPUT if PDS_OUTPUT.exists() else PDS_OUTPUT_FALLBACK

    deleted_count = 0
    errors = []

    with _copy_lock:
        # Delete PNG files from output directory
        if output_dir.exists():
            try:
                for f in output_dir.iterdir():
                    if f.is_file() and f.suffix.lower() == '.png':
                        try:
                            f.unlink()
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"Failed to delete {f.name}: {e}")
            except Exception as e:
                errors.append(f"Error reading output directory: {e}")

        # Delete cumulative.csv
        if cumulative_csv.exists():
            try:
                cumulative_csv.unlink()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete cumulative.csv: {e}")

        # Delete any files inside metamap_inbox (recursive)
        try:
            if METAMAP_INBOX.exists():
                # Iterate recursively and delete files only (leave directories)
                for p in METAMAP_INBOX.rglob('*'):
                    if p.is_file():
                        try:
                            p.unlink()
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"Failed to delete metamap_inbox file {p}: {e}")
        except Exception as e:
            errors.append(f"Error processing metamap_inbox: {e}")

    return jsonify({'ok': True, 'deleted': deleted_count, 'errors': errors})

if __name__ == '__main__':
    # Default run for development
    app.run(host='0.0.0.0', port=5001, debug=True)
