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


# get top shared articles for today or any other day
class GetTopSharedArticles(QueryParamsBase):
    def __init__(self,
                 date: Union[str, datetime.date, datetime.datetime, None] = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count: int = 20,      # number of top shared articles to return
                 returnInfo: ReturnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getArticles")
        self._setVal("resultType", "articles")
        self._setVal("articlesCount", count)
        self._setVal("articlesSortBy", "socialScore")
        self._update(returnInfo.getParams("articles"))

        if date is None:
            date = datetime.date.today()
        self._setDateVal("dateStart", date)
        self._setDateVal("dateEnd", date)


    def _getPath(self):
        return "/api/v1/article"


# get top shared events for today or any other day
class GetTopSharedEvents(QueryParamsBase):
    def __init__(self,
                 date: Union[str, datetime.date, datetime.datetime, None] = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count: int = 20,                                                     # number of top shared articles to return
                 returnInfo: ReturnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getEvents")
        self._setVal("resultType", "events")
        self._setVal("eventsCount", count)
        self._setVal("eventsSortBy", "socialScore")
        self._update(returnInfo.getParams("events"))

        if date is None:
            date = datetime.date.today()
        self._setDateVal("dateStart", date)
        self._setDateVal("dateEnd", date)


    def _getPath(self):
        return "/api/v1/event"
