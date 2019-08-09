from flask import Flask, request, jsonify
app = Flask(__name__, static_url_path='/static')
from MusicalAnalysis import musical_analysis

@app.route("/")
def flaskWrapper():
    return jsonify(musical_analysis(request.args.get('artist_name')))
