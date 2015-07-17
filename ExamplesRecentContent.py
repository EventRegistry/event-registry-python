from EventRegistry import *

er = EventRegistry(host = "http://eventregistry.org", logging = True)

# print recent statistics - number of articles, events, ...
print er.getRecentStats()

# get a list of recently added/updated events
recentEvents = er.getRecentEvents()

# get a list of recently added articles
recentArticles = er.getRecentArticles()
