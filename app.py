#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request
from football_analysis import get_goals, display_data, get_prediction
import json

app = Flask(__name__)

@app.route("/data")
def data():
    return display_data()

@app.route("/goals")
def goals():
    return get_goals()

@app.route('/send_teams', methods=['POST'])
def send_teams():
    home =  request.form['home_team']
    away = request.form['away_team']
    return get_prediction(home, away)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
