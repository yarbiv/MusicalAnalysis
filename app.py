from flask import Flask, request, jsonify
from flask_cors import CORS
from MusicalAnalysis import musical_analysis, setup_dirs
import json
import threading
import uuid
import os

app = Flask(__name__, static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

@app.route("/analyze")
def flaskWrapper():
    if not os.path.exists('static'):
        os.mkdir('static')
    job_id = str(uuid.uuid4())[:8]
    os.mkdir(f'static/{job_id}')
    artist_name = request.args.get('artist_name')
    thread = threading.Thread(target=musical_analysis, kwargs={'artist_name': artist_name, 'job_id': job_id})
    thread.start()
    with open(f'static/{job_id}/results.json', 'w+') as file:
        json.dump({'status': 'processing'}, file)
    return jsonify({'job_id': job_id})