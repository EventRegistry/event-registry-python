"""
Using the bottom classes you can obtain information about articles and events that
were shared the most on social media (Twitter and Facebook) on a particular day.
Given a date, articles published on that date are checked and top shared ones are returned. For an event,
events on that day are checked and top shared ones are returned.
Social score for an article is computed as the sum of shares on facebook and twitter.
Social score for an event is computed by checking 30 top shared articles in the event and averaging their social scores.
"""
from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class DailySharesBase(QueryParamsBase):
    def _getPath(self):
        return "/json/topDailyShares"

# get top shared articles for today or any other day
class GetTopSharedArticles(DailySharesBase):
    def __init__(self,
                 date = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count = 20,      # number of top shared articles to return
                 returnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getArticles")
        self._setVal("count", count)
        self._update(returnInfo.getParams())

        if date == None:
            date = datetime.date.today()
        self._setDateVal("date", date)


# get top shared events for today or any other day
class GetTopSharedEvents(DailySharesBase):
    def __init__(self,
                 date = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count = 20,      # number of top shared articles to return
                 returnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getEvents")
        self._setVal("count", count)
        self._update(returnInfo.getParams())

        if date == None:
            date = datetime.date.today()
        self._setDateVal("date", date)
