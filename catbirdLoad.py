import webapp2
import logging
import jinja2
import os

from models import *
import rosters
import playersRaw

class rosters(webapp2.RequestHandler):
    def get(self):
		teams = []
		for team in rosters.rosters:
			thisTeam = Team(id=team["teamName"], teamName=team["teamName"], remainingDollars=team["remainingDollars"],remainingSpots=team["remainingSpots"])
			teams.append(thisTeam)
		ndb.put_multi(teams)
		self.response.write("Rosters were re-loaded from static")

class players(webapp2.RequestHandler):
    def get(self):
		players = []
	
		for player in playerRaw.players:
			thisPlayer = Player(id=playerName["name"], name=player["name"], value=player["value"], draftedBy=player["draftedBy"], preRanking=player["preRanking"])
			players.append(thisPlayer)
		ndb.put_multi(players)
		self.response.write("%d players were imported") % len(players)

app = webapp2.WSGIApplication([
    ('/rosters', rosters),
    ('/players', players)
], debug=True)		