from flask import Flask, request, jsonify
from flask_cors import CORS
from MusicalAnalysis import musical_analysis

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route("/analyze")
def flaskWrapper():
    return jsonify(musical_analysis(request.args.get('artist_name')))
