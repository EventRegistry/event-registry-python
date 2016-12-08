from eventregistry.Base import *
from eventregistry.ReturnInfo import *

# #################
# GetSourceInfo

class GetSourceInfo(QueryParamsBase):
    """
    obtain desired information about one or more news sources
    """
    def __init__(self,
                 uriOrUriList = None,
                 returnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        self._update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search sources by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search sources by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/source"

# #################
# GetConceptInfo

class GetConceptInfo(QueryParamsBase):
    """
    obtain information about concepts
    """
    def __init__(self,
                 uriOrUriList = None,
                 returnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        self._update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search concepts by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search concepts by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/concept"


# #################
# GetCategoryInfo

class GetCategoryInfo(QueryParamsBase):
    """
    obtain information about categories
    """
    def __init__(self,
                 uriOrUriList = None,
                 returnInfo = ReturnInfo()):
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        self._update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search categories by their id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search categories by their uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/category"


# #################
# GetSourceStats

class GetSourceStats(QueryParamsBase):
    def __init__(self, sourceUri = None):
        """
        get stats about one or more sources - return json object will include:
         "uri"
         "id"
         "totalArticles" - total number of articles from this source
         "withStory" - number of articles assigned to a story (cluster)
         "duplicates" - number of articles that are duplicates of another article
         "duplicatesFromSameSource" - number of articles that are copies from articles
            from the same source (not true duplicates, just updates of own articles)
         "dailyCounts" - json object with date as the key and number of articles for that day as the value
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getStats")
        if sourceUri:
            self._setVal("uri", sourceUri)

    def _getPath(self):
        return "/json/source"

    def queryByUri(self, uriOrUriList):
        """ get stats about one or more sources specified by their uris """
        self.queryParams["uri"] = uriOrUriList;

    def queryById(self, idOrIdList):
        """ get stats about one or more sources specified by their ids """
        self.queryParams["id"] = idOrIdList;
