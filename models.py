from google.appengine.ext import ndb

class Team(ndb.Model):
	teamName = ndb.StringProperty()
	remainingDollars = ndb.IntegerProperty(indexed=False,default=300)
	remainingSpots = ndb.IntegerProperty(indexed=False,default=25)
	# maxBid = ndb.ComputedProperty(remainingDollars - remainingSpots + 1)


class Player(ndb.Model):
	playerName = ndb.StringProperty()
	lastName = ndb.StringProperty()
	value = ndb.IntegerProperty(default=0)
	draftedBy = ndb.StringProperty(default="FA")
	preRanking = ndb.IntegerProperty(default=9999)




	

