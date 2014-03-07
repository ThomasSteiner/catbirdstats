import webapp2
import logging
import jinja2
import os
from operator import attrgetter

from models import *
import rosters
import playersRaw


class welcome(webapp2.RequestHandler):
    def get(self):
	html = standardHeader()
	html +="""
	<head>
		<title>Welcome</title>
	</head>
	<body>
		<a id="linkBox" href="/viewAllTeams">See all team budgets</a><br>
		<a id="linkBox" href="/viewTeam">See a team's roster</a><br>
		<a id="linkBox" href="/viewDraftResults">See draft results</a><br>
		<a id="linkBox" href="/comTools">Commish Tools</a>
	</body>
	</html>"""
	self.response.write(html)


class comTools(webapp2.RequestHandler):
    def get(self):
		password = self.request.get('password')
		html = standardHeader()
		html +="""
		<head>
			<title>Commissioner tools</title>
		</head>"""
		if password == "0":
			html += """
					<body>
						<a id="linkBox" href="/draftPlayer">Add drafted player</a><br>
						<a id="linkBox" href="/changeDrafted">Change drafted player data</a>
						<a id="linkBox" href="/releasePlayer">Release drafted player</a>
						<a id="linkBox" href="/loadRosters">Reset teams</a>
						<a id="linkBox" href="/loadPlayers">Reset players</a>
						<a id="linkBox" href="/welcome">Main menu</a>
					</body></html>"""
		else:
			html += """
					<body>
						<form action="/comTools" method="get">
						<div id="name-select">Password	
						<input type="text" name="password" value=0></div>
						<input type="submit" value="Submit" style="float: left; clear: both;">
					</body></html>"""
		self.response.write(html)

class viewDraftResults(webapp2.RequestHandler):
	def get(self):
		players = Player.query(Player.draftedBy !="FA")
		html = standardHeader()
		html += standardNormPage()
		html +="""<table id="tableFmt"><th>Count</><th>Name</th><th>Drafted by</th><th>Drafted for</th><th>Original rank</th>"""
		counter = 0
		spent = 0
		for player in players:			
			counter += 1
			html+="""<tr align="center"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" %(counter,player.playerName,player.draftedBy, player.value,player.preRanking)
		html += "</table></body></html>"
		self.response.write(html)		

class viewTeam(webapp2.RequestHandler):
	def get(self):
		activeTeam = self.request.get('teamName')
		if not activeTeam:
			self.response.write(selectTeam())	
		else:
			players = Player.query(Player.draftedBy == activeTeam)
			html = standardHeader()
			html += standardNormPage()
			html += """<table id="tableFmt"><th>Count</><th>Name</th><th>Original rank</th><th>Drafted for</th>"""
			counter = 0
			spent = 0
			for player in players:			
				counter += 1
				spent += player.value
				html+="""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" %(counter,player.playerName, player.preRanking, player.value)
			html+="""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" %("Total","", "", spent)
			html += "</table></body></html>"
			self.response.write(html)

def selectTeam():
	teams = Team.query().fetch()
	if not teams:
		self.response.write("No teams exists")
	else:
		allTeamNames = map(lambda x: x.teamName, teams)
		html = standardHeader()
		html +="""
				<head>
					<title>Select team</title>
				</head>
				<body>
				<form action="/viewTeam" method="get">
				<div id="dropDownBox">Current team<select name="teamName">"""		
		for teamName in allTeamNames:
			html += """<option value="%s">%s</option>""" % (teamName, teamName)
		html += """
				</select></div>
				<input type="submit" value="Select team" style="float: left; clear: both;">
				</form></body></html>"""
	
	return html

class viewAllTeams(webapp2.RequestHandler):
    def get(self):
		teamKeys = []
		teams = Team.query().fetch()
		html = standardHeader()
		html += standardNormPage()
		html += """<table id="tableFmt"><th>Name</th><th>Remaining roster spots</th><th>Dollars remaining</th><th>Max bid</th>"""
		for team in teams:
			html +="""<tr>
			<td align="center">%s</td>
			<td align="center">%s</td>
			<td align="center">%s</td>
			<td align="center">%s</td>
			</tr>""" %(team.teamName, team.remainingSpots, team.remainingDollars, team.remainingDollars-(team.remainingSpots-1) )
		html += """</table></body></html>"""
		self.response.write(html)

class loadRosters(webapp2.RequestHandler):
    def get(self):
		teams = []
		for team in rosters.rosters:
			thisTeam = Team(id=team["teamName"], teamName=team["teamName"], remainingDollars=team["remainingDollars"],remainingSpots=team["remainingSpots"])
			teams.append(thisTeam)
		ndb.put_multi(teams)
		html = standardHeader()
		html += standardComPage()
		html += """<h1>Teams were reset from static</h1></body></html>"""
		self.response.write(html)

class loadPlayers(webapp2.RequestHandler):
    def get(self):
		players = []
		for player in playersRaw.players:
			thisPlayer = Player(id=player["playerName"], playerName=player["playerName"], lastName=player["lastName"], value=player["value"], preRanking=player["preRanking"],draftedBy="FA")
			players.append(thisPlayer)
		ndb.put_multi(players)
		html = standardHeader()
		html += standardComPage()
		html += """<h1>Players were reset from static</h1></body></html>"""
		self.response.write(html)

class enterPlayer(webapp2.RequestHandler):
    def get(self):	
		draftingTeam = self.request.get('teamName')
		draftedPlayer = self.request.get('playerName')
		draftValue = self.request.get('draftValue')
		inputType = self.request.get('inputType')

		teamToUpdate = ndb.Key('Team', draftingTeam).get()
		playerToUpdate = ndb.Key('Player', draftedPlayer).get()
		if inputType =="manual":
			playerToUpdate = Player(id=draftedPlayer, playerName=draftedPlayer, lastName="Manual Entry", value=int(draftValue), preRanking=int(0),draftedBy=draftingTeam)
		else:
			if playerToUpdate.draftedBy != "FA":
					unEnterPlayer(playerToUpdate)
			teamToUpdate.remainingDollars = teamToUpdate.remainingDollars - int(draftValue)
			teamToUpdate.remainingSpots = teamToUpdate.remainingSpots - int(1)
			playerToUpdate.draftedBy = draftingTeam
			playerToUpdate.value = int(draftValue)
		
		teamToUpdate.put()
		playerToUpdate.put()
		html = standardHeader()
		html += standardComPage()
		html += """
			<h1>%s was drafted by %s for $ %s </body></html>""" % (draftedPlayer, draftingTeam, str(draftValue))
		self.response.write(html)


class draftPlayer(webapp2.RequestHandler):
    def get(self):	
		teams = Team.query().fetch()
		players = Player.query(Player.draftedBy == "FA",Player.preRanking <= 300)
		if not teams or not players:
			self.response.write("Teams and/or players must be loaded")
		else:
			allTeamNames = map(lambda x: x.teamName, teams)
			allPlayerNames = sorted(map(lambda x: x.playerName, players))
			
			html = standardHeader()
			html +="""
		<head>
			<title>Select player details</title>
		</head>"""
			html+= standardComPage()
			html+="""
		<div id="sectionHeading">Search for another player</div>
		<form action="/enterPlayer" method="get">
			<div id="dropDownBox">Select team<select name="teamName">"""		
			for teamName in allTeamNames:
				html += """<option value="%s">%s</option>""" % (teamName, teamName)
			html += """
			</select></div>
			<div id="dropDownBox">Select player<select name="playerName">"""		
			for player in players:
				playerName = player.playerName
				html += """<option value="%s">%s</option>""" % (playerName, playerName)
			html += """
			</select></div>
			<div id="dropDownBox">Enter value	
			<input type="text" name="draftValue" value=0></div>
			<input type="submit" value="Submit" style="float: left; clear: both;">
		</form>"""
			html += searchPlayerForm()
			html += manualEnterForm(allTeamNames)
			html +="""</body></html>"""
		
			self.response.write(html)

class playerSearch(webapp2.RequestHandler):
    def get(self):	
		teams = Team.query().fetch()
		searchedPlayer = self.request.get('searchedPlayer')
		players = Player.query(Player.draftedBy == "FA",Player.lastName == searchedPlayer)
		if not teams or not players:
			self.response.write("Teams and/or players must be loaded")
		else:
			allTeamNames = map(lambda x: x.teamName, teams)
			allPlayerNames = sorted(map(lambda x: x.playerName, players))
			html = standardHeader()
			html += standardComPage()
			html +="""
			
			<form action="/enterPlayer" method="get">
			<div id="sectionHeading">Select player from drop down</div>
			<div id="dropDownBox">Select team<select name="teamName">"""		
			for teamName in allTeamNames:
				html += """<option value="%s">%s</option>""" % (teamName, teamName)
			html += """
			</select></div>
			
			<div id="dropDownBox">Select player<select name="playerName">"""		
			for player in players:
				playerName = player.playerName
				html += """<option value="%s">%s</option>""" % (playerName, playerName)
			html += """
			</select></div>
			
			<div id="dropDownBox">Enter value	
			<input type="text" name="draftValue" value=0></div>
			<input type="submit" value="Submit" style="float: left; clear: both;">
			</form>"""
			html += searchPlayerForm()
			html += manualEnterForm(allTeamNames)
			html += """</body></html>"""
		
		self.response.write(html)

class releasePlayer(webapp2.RequestHandler):
    def get(self):
		changePlayer = self.request.get('playerName')
	    	if len(changePlayer) > 0:
				playerToRelease = ndb.Key('Player', changePlayer).get()
				html = standardHeader()
				html += standardComPage()
				html += "<h1>%s was released freeing up %s for %s<h1>" %(playerToRelease.playerName, playerToRelease.value, playerToRelease.draftedBy)
				if playerToRelease.draftedBy != "FA":
					unEnterPlayer(playerToRelease)
	    	else:
				players = Player.query(Player.draftedBy !="FA")	
				if not players:
					self.response.write("Teams and/or players must be loaded")
				else:
					allPlayerNames = map(lambda x: x.playerName, players)	
					html = standardHeader()
					html +="""
					<head>
						<title>Select player details</title>
					</head>
					<body>
						<form action="/releasePlayer" method="get">			
						<div id="dropDownBox">Select player<select name="playerName">"""		
					for player in players:
						playerName = player.playerName
						html += """<option value="%s">%s</option>""" % (playerName, playerName)
					html += """
					</select></div>
					<input type="submit" value="Submit" style="float: left; clear: both;">
					</form>
				</body>
				</html>"""
			
		self.response.write(html)

class changeDrafted(webapp2.RequestHandler):
    def get(self):
    	changePlayer = self.request.get('playerName')
    	if len(changePlayer) > 0:
			playerChanger = ndb.Key('Player', changePlayer).get()
			html = standardHeader()
			html += standardComPage()
			html +="""
					<h1>%s was drafted by %s for %s</h1><br>
					<h1> Please select new team or value:</h1><br></body>
				<form action="/enterPlayer" method="get">
				<div id="dropDownBox">Select team<select name="teamName">
				"""	 % (playerChanger.playerName, playerChanger.draftedBy, str(playerChanger.value))	
			teams = Team.query().fetch()
			allTeamNames = map(lambda x: x.teamName, teams)
			for teamName in allTeamNames:
				html += """<option value="%s">%s</option>""" % (teamName, teamName)
			
			html += """
				</select></div>
				<div id="dropDownBox">Enter value	
				<input type="text" name="draftValue" value=%s></div>
				</select></div>
				<div id="dropDownBox">Selected player<select name="playerName">
				<option value="%s">%s</option></select></div>
				<input type="submit" value="Submit" style="float: left; clear: both;"></form>
				""" % (str(playerChanger.value),playerChanger.playerName, playerChanger.playerName)

			self.response.write(html)
    	else:
			players = Player.query(Player.draftedBy !="FA")	
			if not players:
				self.response.write("Teams and/or players must be loaded")
			else:
				allPlayerNames = map(lambda x: x.playerName, players)	
				html = standardHeader()
				html +="""
				<head>
					<title>Select player details</title>
				</head>"""
				html += standardComPage()
				html +="""
					<form action="/changeDrafted" method="get">			
					<div id="dropDownBox">Select player<select name="playerName">"""		
				for player in players:
					playerName = player.playerName
					html += """<option value="%s">%s</option>""" % (playerName, playerName)
				html += """
				</select></div>
				<input type="submit" value="Submit" style="float: left; clear: both;">
				</form>
			</body>
			</html>"""
				self.response.write(html)

def unEnterPlayer(player):
		teamToUpdate = ndb.Key('Team', player.draftedBy).get()
		teamToUpdate.remainingDollars = teamToUpdate.remainingDollars + int(player.value)
		teamToUpdate.remainingSpots = teamToUpdate.remainingSpots + int(1)
		player.draftedBy = "FA"
		player.value = int(player.value)
		teamToUpdate.put()
		player.put()

def standardHeader():
	html = """
		<!DOCTYPE html>
		<html>
		<style>
			#linkBox {font-size: 20px; color: rgb(37, 91, 137); padding: 10px; margin: 5px; float: left; clear: both; border: 1px solid rgb(37, 91, 137); background-color: rgb(221, 228, 233)}
			#topHeader ul {background-color: rgb(37, 91, 137); margin: 5; padding: 10px; list-style-type: none; list-style-image: none;}
			#topHeader li {display: inline;}
			#topHeader ul li a {color: rgb(37, 91, 137); padding: 5px; margin: 1px; border: 1px solid rgb(37, 91, 137); background-color: rgb(221, 228, 233)}
			#topHeader ul li a:hover {color: rgb(221, 228, 233) ;background: rgb(37, 91, 137); }
			#dropDownBox {font-size: 20px; color: rgb(37, 91, 137); padding: 10px; margin: 5px 5px; float: left; clear: both; border: 1px solid rgb(37, 91, 137); background-color: rgb(221, 228, 233)}
			#sectionHeading {font-size: 20px; color: rgb(37, 91, 137); padding: 1px; margin: 5px; float: left; clear: both; font-weight:bold}
			#tableFmt {padding: 10px; margin: 0px; text-align:center}
			th {color: white; background-color: rgb(37,91,137);padding: 10px;align="center"}
			td {color: rgb(37, 91, 137);padding: 10px; align="center"}
		</style>"""
	return html

def standardNormPage():
	html = """
				<body>
		<div id="topHeader">
		<ul>
			<li><a href="/welcome">Home</a></li>
			<li><a href="/viewAllTeams">All team budgets</a></li>
			<li><a href="/viewTeam">See a team's roster</a></li>
			<li><a href="/viewDraftResults">Draft results</a></li>
		</div>"""

	return html
def standardComPage():
	html = """
		<body>
		<div id="topHeader">
		<ul>
			<li><a href="/welcome">Home</a></li>
			<li><a href="/viewAllTeams">All team budgets</a></li>
			<li><a href="/viewTeam">See a team's roster</a></li>
			<li><a href="/viewDraftResults">Draft results</a></li>
			<li><a href="/draftPlayer">Draft player</a></li>
			<li><a href="/changeDrafted">Change player</a></li>
			<li><a href="/releasePlayer">Release player</a></li>
		</div>"""
	return html

def manualEnterForm(teamNameMap):
	html = """<div id="sectionHeading">Provide player inputs manually</div>
			<form action="/enterPlayer" method="get">
			<div id="dropDownBox">Select team<select name="teamName">"""		
	for teamName in teamNameMap:
		html += """<option value="%s">%s</option>""" % (teamName, teamName)
	html += """</select></div>
			<div id="dropDownBox">Enter name (this will create a new player)	
				<input type="text" name="playerName" value=0>
			</div>
			<div id="dropDownBox">Enter value	
				<input type="text" name="draftValue" value=0>
			</div>
			<input type="submit" value="Submit" style="float: left; clear: both;">
			<div>
				<input type="hidden" name="inputType" value="manual">	
			</div>
		</form>"""
	return html

def searchPlayerForm():
	html = """<div id="sectionHeading">Search for another player</div>
			<form action="/playerSearch" method="get">
				<div id="dropDownBox">Enter last name
				<input type="text" name="searchedPlayer" value=Enter_name_here></div>
				<input type="submit" value="Submit" style="float: left; clear: both;">
			</form>"""
	return html


app = webapp2.WSGIApplication([
    ('/', welcome),
    ('/welcome', welcome),
    ('/viewTeam', viewTeam),
    ('/selectTeam', selectTeam),
    ('/viewAllTeams', viewAllTeams),
    ('/loadRosters', loadRosters),
    ('/loadPlayers', loadPlayers),
    ('/viewDraftResults', viewDraftResults),
    ('/comTools', comTools),
    ('/draftPlayer', draftPlayer),
    ('/playerSearch', playerSearch),
    ('/releasePlayer', releasePlayer),
    ('/changeDrafted', changeDrafted),
    ('/enterPlayer', enterPlayer)
], debug=True)



# GRAVEYARD

# JINJA_ENVIRONMENT = jinja2.Environment(
#     loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#     extensions=['jinja2.ext.autoescape'])
	# 	template_filename = 'catbirdStats.html'
	# 	template_values = {
	# 	'teams' : teams
	# }
	# 	template = JINJA_ENVIRONMENT.get_template(template_filename)
	# 	html = template.render(template_values)
		# self.response.write(html)
	# 	def getPlayers():
	# players = Players.query().fetch()
	# html ="""<!DOCTYPE html><html><head><title>Roster List</title>
	# 	<style>
	# 	table {align="center"}
	# 	th {border: 1px solid black;padding: 20px}
	# 	td {border: 1px solid black;padding: 20px}
	# 	</style>
	# 	</head><body>"""
	# html += "<table><th>Name</th><th>Drafted by</th><th>Value</th>"
	# for player in players:
	# 		html +="""<tr>
	# 		<td align="center">%s</td>
	# 		<td align="center">%s</td>
	# 		<td align="center">%s</td>
	# 		</tr>""" %(player.name, player.draftedBy, player.value)
	# html += "</table></body></html>"
	
	# self.response.write(html)