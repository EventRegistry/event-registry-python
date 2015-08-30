from eventregistry import *

er = EventRegistry()

# print recent statistics - number of articles, events, ...
ret = er.getRecentStats()
print er.prettyFormatObj(ret)

# get a list of recently added/updated events
recentEvents = er.getRecentEvents()

# get a list of recently added articles
recentArticles = er.getRecentArticles()
