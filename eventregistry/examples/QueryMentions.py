"""
examples that illustrate how to query for mentions using different search options
"""
from eventregistry import *

er = EventRegistry(allowUseOfArchive=False)

# get 10.000 uris of mentions that are related to mergers and acquisitions
q = QueryMentions(eventTypeUri="et/business/acquisitions-mergers")
q.setRequestedResult(RequestMentionsUriWgtList())
res = er.execQuery(q)
uriList = er.getUriFromUriWgt(res.get("uriWgtList", {}).get("results", []))


# get mentions related to labor issues and print first 100 of them
q = QueryMentions(eventTypeUri="et/business/labor-issues")
res = er.execQuery(q)
for m in res.get("mentions", {}).get("results", []):
    print(m)
