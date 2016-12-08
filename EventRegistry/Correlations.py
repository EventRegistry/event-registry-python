"""
provides classes needed to identify concepts or categories that trend the most with a concept, category or a custom time series
"""

import json, six
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.Info import *
from eventregistry.QueryArticles import *
from eventregistry.Counts import *

class GetTopCorrelations(QueryParamsBase):
    def __init__(self,
                 eventRegistry):    # instance of EventRegistry class
        QueryParamsBase.__init__(self)
        self._er = eventRegistry
        self._setVal("action", "findTopCorrelations")


    def _getPath(self):
        return "/json/correlate"

    #
    # input data methods
    #
    def setCustomInputData(self, inputDataArr):
        """
        specify the user defined array of input data

        @param inputDataArr: array of tuples (date, val) where date is a date object or string in YYYY-MM-DD format
                and val is the value/counts for that date
        """
        # clear any past test data values
        self._clearVal("testData")
        for (date, val) in inputDataArr:
            assert isinstance(val, (int, float)), "Value is expected to be a number"
            dateStr = None
            if isinstance(val, datetime.date):
                dateStr = val.isoformat()
            elif isinstance(val, datetime.datetime):
                dateStr = val.date().isoformat()
            elif isinstance(val, six.string_types):
                assert re.match("\d{4}-\d{2}-\d{2}", date)
                dateStr = date
            else:
                assert False, "First argument in the tuple is not a valid date"
            self._addArrayVal("testData", {"date": dateStr, "count": val})


    def loadInputDataWithQuery(self, queryArticles):
        """
        use the queryArticles to find articles that match the criteria. For the articles that match
        criteria in queryArticles compute the time-series (number of resulting articles for each date)
        an use the time series as the input data

        @param queryArticles: an instance of QueryArticles class, containing the conditions that are use to
            find the matching time-series. You don't need to specify any requested result.
        """
        # clear any past test data values
        self._clearVal("testData")

        assert isinstance(queryArticles, QueryArticles), "'queryArticles' excpected to be an instance of QueryArticles"
        queryArticles.addRequestedResult(RequestArticlesTimeAggr())
        res = self._er.execQuery(queryArticles)
        if "timeAggr" in res:
            for obj in res["timeAggr"]:
                self._addArrayVal("testData", json.dumps(obj))

    def loadInputDataWithCounts(self, getCounts):
        """
        use GetCounts class to obtain daily counts information for concept/category of interest
        @param getCounts: an instance of GetCounts class
        """
        # clear any past test data values
        self._clearVal("testData")

        assert isinstance(getCounts, GetCounts), "'getCounts' is expected to be an instance of GetCounts"
        res = self._er.execQuery(getCounts)
        assert len(list(res.keys())) <= 1, "The returned object had multiple keys. When creating the GetCounts instance use only one uri."
        assert len(list(res.keys())) != 0, "Obtained an empty object"
        assert "error" not in res, res.get("error")
        key = list(res.keys())[0]
        assert isinstance(res[key], list), "Expected a list"
        for obj in res[key]:
            self._addArrayVal("testData", json.dumps(obj))

    def hasValidInputData(self):
        """do we have valid input data (needed before we can compute correlations)"""
        return self._hasVal("testData")

    #
    # computing correlations
    #
    def getTopConceptCorrelations(self,
            candidateConceptsQuery = None,
            candidatesPerType = 1000,
            conceptType = None,
            exactCount = 10,
            approxCount = 0,
            returnInfo = ReturnInfo()):
        """
        compute concepts that correlate the most with the input data. If candidateConceptsQuery is provided we first identify the
        concepts that are potentially returned as top correlations. Candidates are obtained by making the query and analyzing the
        concepts that appear in the resulting articles. The top concepts are used as candidates among which we return the top correlations.
        If conceptType is provided then only concepts of the specified type can be provided as the result.

        @param candidateConceptsQuery: optional. An instance of QueryArticles that can be used to limit the space of concept candidates
        @param candidatesPerType: If candidateConceptsQuery is provided, then this number of concepts for each valid type will be return as candidates
        @param conceptType: optional. A string or an array containing the concept types that are valid candidates on which to compute top correlations
            valid values are "person", "org", "loc" and/or "wiki"
        @param exactCount: the number of returned concepts for which the exact value of the correlation is computed
        @param approxCount: the number of returned concepts for which only an approximate value of the correlation is computed
        @param returnInfo: specifies the details about the concepts that should be returned in the output result
        """

        self._clearVal("contextConceptIds")

        # generate all necessary parameters (but don't update the params of the self)
        params = QueryParamsBase.copy(self)

        # compute the candidates
        if candidateConceptsQuery != None:
            assert isinstance(candidateConceptsQuery, QueryArticles), "'candidateConceptsQuery' is expected to be of type QueryArticles"
            candidateConceptsQuery.addRequestedResult(RequestArticlesConceptAggr())
            candidateConceptsQuery._setVal("conceptAggrConceptCountPerType", candidatesPerType)
            candidateConceptsQuery._setVal("conceptAggrConceptIdOnly", True)
            ret = self._er.execQuery(candidateConceptsQuery)
            if ret and "conceptAggr" in ret:
                params._setVal("contextConceptIds", ",".join([str(x) for x in ret["conceptAggr"]]))
            else:
                print("Warning: Failed to compute a candidate set of concepts")

        if conceptType:
            params._setVal("conceptType", conceptType)
        params._setVal("exactCount", exactCount)
        params._setVal("approxCount", approxCount)
        params._setVal("sourceType", "news-concept")

        #
        # compute the correlations
        ret = self._er.jsonRequest(self._getPath(), params.queryParams)

        #
        # extend the return information with the details about the concepts (label, ...)
        if returnInfo != None:
            conceptIds = []
            if ret and ret["news-concept"]["exactCorrelations"]:
                conceptIds += [info["id"] for info in ret["news-concept"]["exactCorrelations"]]
            if ret and ret["news-concept"]["approximateCorrelations"]:
                conceptIds += [info["id"] for info in ret["news-concept"]["approximateCorrelations"]]
            conceptInfos = {}
            for i in range(0, len(conceptIds), 500):
                ids = conceptIds[i:i+500]
                q = GetConceptInfo(returnInfo = returnInfo)
                q.queryById(ids)
                info = self._er.execQuery(q)
                conceptInfos.update(info)
            if ret and ret["news-concept"]["exactCorrelations"]:
                for item in ret["news-concept"]["exactCorrelations"]:
                    item["conceptInfo"] = conceptInfos.get(str(item["id"]), {})
            if ret and ret["news-concept"]["approximateCorrelations"]:
                for item in ret["news-concept"]["approximateCorrelations"]:
                    item["conceptInfo"] = conceptInfos.get(str(item["id"]), {})

        # return result
        return ret


    def getTopCategoryCorrelations(self,
            exactCount = 10,
            approxCount = 0,
            returnInfo = ReturnInfo()):
        """
        compute categories that correlate the most with the input data.

        @param exactCount: the number of returned categories for which the exact value of the correlation is computed
        @param approxCount: the number of returned categories for which only an approximate value of the correlation is computed
        @param returnInfo: specifies the details about the categories that should be returned in the output result
        """

        # generate all necessary parameters (but don't update the params of the self)
        params = QueryParamsBase.copy(self)
        # don't send unnecessary data
        params._clearVal("contextConceptIds")
        params._setVal("exactCount", exactCount)
        params._setVal("approxCount", approxCount)
        params._setVal("sourceType", "news-category")

        #
        # compute the correlations
        ret = self._er.jsonRequest(self._getPath(), params.queryParams)

        #
        # extend the return information with the details about the categories (label, ...)
        if returnInfo != None:
            categoryIds = []
            if ret and ret["news-category"]["exactCorrelations"]:
                categoryIds += [info["id"] for info in ret["news-category"]["exactCorrelations"]]
            if ret and ret["news-category"]["approximateCorrelations"]:
                categoryIds += [info["id"] for info in ret["news-category"]["approximateCorrelations"]]
            categoryInfos = {}
            for i in range(0, len(categoryIds), 500):
                ids = categoryIds[i:i+500]
                q = GetCategoryInfo(returnInfo = returnInfo)
                q.queryById(ids)
                info = self._er.execQuery(q)
                categoryInfos.update(info)
            if ret and ret["news-category"]["exactCorrelations"]:
                for item in ret["news-category"]["exactCorrelations"]:
                    item["categoryInfo"] = categoryInfos.get(str(item["id"]), {})
            if ret and ret["news-category"]["approximateCorrelations"]:
                for item in ret["news-category"]["approximateCorrelations"]:
                    item["categoryInfo"] = categoryInfos.get(str(item["id"]), {})

        # return result
        return ret
