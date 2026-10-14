from eventregistry.Base import QueryParamsBase
from eventregistry.ReturnInfo import ReturnInfo
from typing import Union, List

# the names exported by "from eventregistry import *"
__all__ = ["GetSourceInfo", "GetConceptInfo", "GetCategoryInfo", "GetSourceStats"]


class GetSourceInfo(QueryParamsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str], None] = None,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        obtain desired information about one or more news sources

        Args:
            uriOrUriList: single source uri or a list of source uris for which to return information
            returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList is not None:
            self.queryByUri(uriOrUriList)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())


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
                 uriOrUriList: Union[str, List[str], None] = None,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        obtain information about concepts

        Args:
            uriOrUriList: single concept uri or a list of concept uris for which to return information
            returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList is not None:
            self._setVal("uri", uriOrUriList)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())


    def _getPath(self):
        return "/api/v1/concept"



class GetCategoryInfo(QueryParamsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str], None] = None,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        obtain information about categories

        Args:
            uriOrUriList: single category uri or a list of category uris for which to return information
            returnInfo: what details about the source should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getInfo")
        if uriOrUriList is not None:
            self.queryByUri(uriOrUriList)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())


    def queryByUri(self, uriOrUriList: Union[str, List[str]]):
        """search categories by their uri(s)"""
        self._setVal("uri", uriOrUriList)


    def _getPath(self):
        return "/api/v1/category"



class GetSourceStats(QueryParamsBase):
    def __init__(self, sourceUri: Union[str, List[str], None] = None):
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
