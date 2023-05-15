from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from typing import Union, List


class GetSourceInfo(QueryParamsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str]] = None,
                 returnInfo: ReturnInfo = ReturnInfo()):
        """
        obtain desired information about one or more news sources
        @param uriOrUriList: single source uri or a list of source uris for which to return information
        @param returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        self._update(returnInfo.getParams())


    def queryByUri(self, uriOrUriList: Union[str, List[str]]):
        """search sources by uri(s)"""
        self._setVal("uri", uriOrUriList)


    def queryById(self, idOrIdList: Union[str, List[str]]):
        """search concepts by id(s)"""
        self._setVal("id", idOrIdList)


    def _getPath(self):
        return "/api/v1/source"



class GetConceptInfo(QueryParamsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str]] = None,
                 returnInfo: ReturnInfo = ReturnInfo()):
        """
        obtain information about concepts
        @param uriOrUriList: single concept uri or a list of concept uris for which to return information
        @param returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self._setVal("uri", uriOrUriList)
        self._update(returnInfo.getParams())


    def _getPath(self):
        return "/api/v1/concept"



class GetCategoryInfo(QueryParamsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str]] = None,
                 returnInfo: ReturnInfo = ReturnInfo()):
        """
        obtain information about categories
        @param uriOrUriList: single category uri or a list of category uris for which to return information
        @param returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        self._update(returnInfo.getParams())


    def queryByUri(self, uriOrUriList: Union[str, List[str]]):
        """search categories by their uri(s)"""
        self._setVal("uri", uriOrUriList)


    def _getPath(self):
        return "/api/v1/category"



class GetSourceStats(QueryParamsBase):
    def __init__(self, sourceUri: Union[str, List[str]] = None):
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
        return "/api/v1/source"


    def queryByUri(self, uriOrUriList: Union[str, List[str]]):
        """ get stats about one or more sources specified by their uris """
        self.queryParams["uri"] = uriOrUriList
