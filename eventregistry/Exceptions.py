"""
exceptions raised when a request to Event Registry fails.

All of them derive from EventRegistryError (which derives from Exception), so a single
`except EventRegistryError` catches every failed request, and code that catches Exception keeps working.

    EventRegistryError
     +-- NoDataError            204: the request succeeded, but the requested information is not available
     +-- InvalidRequestError    400 and the other 4xx codes: invalid or missing parameters, unknown endpoint, ...
     +-- AccessError
     |    +-- UnauthorizedError 401: the API key is not valid, or the user reached the limit of the tokens in the account
     |    +-- ForbiddenError    403: the user's IP or account is disabled, or all the tokens have been used
     +-- RateLimitError         429: too many simultaneous requests (at most 5 are allowed)
     +-- ServerError            5xx: internal error or the service is temporarily unavailable
     +-- InvalidResponseError   the server returned a response that is not valid json
     +-- QueryError             the server processed the request, but returned an error instead of the results
     +-- NetworkError           the request could not be made or timed out (the requests exception is in __cause__)

RateLimitError, ServerError, InvalidResponseError and NetworkError are temporary - EventRegistry repeats such
requests (see the repeatFailedRequestCount parameter) before raising the error. Requests rejected with 429 are
repeated until they succeed, so EventRegistry does not raise RateLimitError.
"""
from typing import Optional

__all__ = ["EventRegistryError", "NoDataError", "InvalidRequestError", "AccessError", "UnauthorizedError", "ForbiddenError",
           "RateLimitError", "ServerError", "InvalidResponseError", "NetworkError", "QueryError"]


class EventRegistryError(Exception):
    """
    base class of the errors raised when a request to Event Registry fails

    Attributes:
        statusCode: the HTTP status code of the response (None if there was no response)
        responseText: the text of the response returned by the server (usually explains the error)
        url: the url of the request
        retryAfter: the number of seconds after which the request can be repeated, if the server said so (Retry-After header)
    """
    # can repeating the same request later succeed?
    isTemporary = False

    def __init__(self,
                 message: str,
                 statusCode: Optional[int] = None,
                 responseText: Optional[str] = None,
                 url: Optional[str] = None,
                 retryAfter: Optional[int] = None):
        super().__init__(message)
        self.statusCode = statusCode
        self.responseText = responseText
        self.url = url
        self.retryAfter = retryAfter


class NoDataError(EventRegistryError):
    """status 204: the request succeeded, but the requested information is not available"""


class InvalidRequestError(EventRegistryError):
    """status 400 (and the other 4xx codes without a more specific class): the request was invalid"""


class AccessError(EventRegistryError):
    """the user is not allowed to make the request (401 or 403)"""


class UnauthorizedError(AccessError):
    """status 401: the API key is not recognized, or the user reached the limit of the tokens in the account"""


class ForbiddenError(AccessError):
    """status 403: the user's IP or account is disabled, or all the tokens have been used"""


class RateLimitError(EventRegistryError):
    """status 429: the user is making too many simultaneous requests"""
    isTemporary = True


class ServerError(EventRegistryError):
    """status 5xx: an internal error occurred or the service is temporarily unavailable"""
    isTemporary = True


class InvalidResponseError(EventRegistryError):
    """the server returned a response that is not valid json (for example a truncated response)"""
    isTemporary = True


class QueryError(EventRegistryError):
    """
    the server processed the request (status 200), but returned an error message instead of the results - for example
    because of an invalid uri or a condition that the account is not allowed to use. Raised by the iterator classes
    (QueryArticlesIter, ...) and by EventRegistry.execQuery() when called with raiseOnError=True
    """


class NetworkError(EventRegistryError):
    """the request could not be made (connection problem) or it timed out"""
    isTemporary = True


def getErrorClassForStatusCode(statusCode: int) -> type:
    """the EventRegistryError subclass that describes a response with the given (non 200) status code"""
    if statusCode == 204:
        return NoDataError
    if statusCode == 401:
        return UnauthorizedError
    if statusCode == 403:
        return ForbiddenError
    if statusCode == 429:
        return RateLimitError
    if statusCode >= 500:
        return ServerError
    return InvalidRequestError
