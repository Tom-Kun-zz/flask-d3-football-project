import pandas as pd
import numpy as np
import json

import sys
sys.path.append('lib/statsmodels')
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson

# importing the tools required for the Poisson regression model
#import statsmodels.api as sm
#import statsmodels.formula.api as smf

def get_data():
	# import data from the football-data.co.uk website which are in a CSV format (picking the result of the current Premier League 16-17)
	data = pd.read_csv('http://www.football-data.co.uk/mmz4281/1617/E0.csv')	
	return data

def display_data():
	data_load = get_data()
	data = data_load[['HomeTeam','AwayTeam','FTHG','FTAG', 'HTHG', 'HTAG']]
	data = data.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals', 'HTHG' : 'HomeHalfGoals', 'HTAG' : 'AwayHalfGoals'})
	data = data.head(20)
	json = data.to_json(orient='records')
	return json

def get_goals():
	# import data from the football-data.co.uk website which are in a CSV format (picking the result of the current Premier League 16-17)
	data_1617 = get_data()

	# delimit informations that i'll need into my pandas frame
	data_1617 = data_1617[['FTHG','FTAG']]

	# rename non-explicits columns
	data_1617 = data_1617.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

	# create a new dataframe which contain the required columns
	data = pd.DataFrame(columns=['Goals', 'HomeGoals', 'AwayGoals'])


	# get all the away goals by goals (goals is the index in this case)
	data = data_1617['AwayGoals'].value_counts().to_frame()

	# add the HomeGoals with the same method
	data['HomeGoals'] = data_1617['HomeGoals'].value_counts()

	# replace the NaN by 0
	data.fillna(0, inplace=True)

	# sort the data by goals in ascending
	data = data.sort_index()

	# give the value of the index to the Goals column
	data['Goals'] = data.index

	# create the json by orient the json on the records (possible to do it on index or columns)
	json = data.to_json(orient='records')

	return json

def get_prediction(homeTeam, awayTeam, max_goals=10):
	data = get_data()
	data = data[['HomeTeam','AwayTeam','FTHG','FTAG']]
	data = data.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})
	goal_model_data = pd.concat([data[['HomeTeam','AwayTeam','HomeGoals']].assign(home=1).rename(columns={'HomeTeam':'team', 'AwayTeam':'opponent','HomeGoals':'goals'}),
    data[['AwayTeam','HomeTeam','AwayGoals']].assign(home=0).rename(columns={'AwayTeam':'team', 'HomeTeam':'opponent','AwayGoals':'goals'})])
	poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data, family=sm.families.Poisson())
	poisson_results = poisson_model.fit()

	home_goals_avg = poisson_results.predict(pd.DataFrame(data={'team': homeTeam, 
                                                            'opponent': awayTeam,'home':1},
                                                      index=[1])).iloc[0]
	away_goals_avg = poisson_results.predict(pd.DataFrame(data={'team': awayTeam, 
                                                            'opponent': homeTeam,'home':0},
                                                      index=[1])).iloc[0]
	team_prediction = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
	result = np.outer(np.array(team_prediction[0]), np.array(team_prediction[1]))
	home_team_win = np.sum(np.tril(result, -1))
	away_team_win = np.sum(np.triu(result, 1))
	draw = np.sum(np.diag(result))
	df = pd.DataFrame({'HomeTeamWin': home_team_win, 'AwayTeamWin': away_team_win, 'Draw': draw}, index=[1])
	prediction = df.to_json(orient='records')
	return prediction