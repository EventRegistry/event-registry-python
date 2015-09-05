from eventregistry import *

er = EventRegistry()

q = GetTopSharedArticles(date = "2015-05-23", count = 30)
ret = er.execQuery(q)
print er.prettyFormatObj(ret)

q = GetTopSharedEvents(date = "2015-05-23", count = 30)
ret = er.execQuery(q)
print er.prettyFormatObj(ret)