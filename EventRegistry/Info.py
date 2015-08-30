from Base import *
from ReturnInfo import *

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
        self.queryParams.update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search sources by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search sources by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/source"


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
        self.queryParams.update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search concepts by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search concepts by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/concept"


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
        self.queryParams.update(returnInfo.getParams())

    def queryById(self, idOrIdList):
        """search categories by their id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search categories by their uri(s)"""
        self._setVal("uri", uriOrUriList)

    def _getPath(self):
        return "/json/category"
