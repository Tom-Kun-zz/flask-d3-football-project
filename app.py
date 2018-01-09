from flask import Flask, render_template, jsonify, request
from football_analysis import get_goals, display_data, simulate_match
import json

def get_prediction():
	data = get_data()
	goal_model_data = pd.concat([data[['HomeTeam','AwayTeam','HomeGoals']].assign(home=1).rename(columns={'HomeTeam':'team', 'AwayTeam':'opponent','HomeGoals':'goals'}),
    data[['AwayTeam','HomeTeam','AwayGoals']].assign(home=0).rename(columns={'AwayTeam':'team', 'HomeTeam':'opponent','AwayGoals':'goals'})])
	poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data, family=sm.families.Poisson())
	poisson_results = poisson_model.fit()
	return poisson_results

app = Flask(__name__)

@app.route("/data")
def data():
    return display_data()

@app.route("/goals")
def goals():
    return get_goals()

@app.route('/send_teams', methods=['POST'])
def send_teams():
    home =  request.form['home_team'];
    away = request.form['away_team'];
    teams = json.dumps({'status':'OK','home_team':home,'away_team':away});
    return teams

@app.route("/prediction")
def prediction():
	model = get_prediction()
	home = send_teams()[0]
	away = send_teams()[1]
	goals = 10
	return simulate_match(model, home, away, goals)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)