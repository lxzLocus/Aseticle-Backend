from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchScholarRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class SearchScholarResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SearchResult]
    def __init__(self, results: _Optional[_Iterable[_Union[SearchResult, _Mapping]]] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ("url", "title", "author", "conference", "pages", "date", "abstract", "cite_num", "submitted", "relevant_no", "tier")
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CONFERENCE_FIELD_NUMBER: _ClassVar[int]
    PAGES_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    ABSTRACT_FIELD_NUMBER: _ClassVar[int]
    CITE_NUM_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_FIELD_NUMBER: _ClassVar[int]
    RELEVANT_NO_FIELD_NUMBER: _ClassVar[int]
    TIER_FIELD_NUMBER: _ClassVar[int]
    url: str
    title: str
    author: str
    conference: str
    pages: int
    date: str
    abstract: str
    cite_num: int
    submitted: bool
    relevant_no: int
    tier: int
    def __init__(self, url: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., conference: _Optional[str] = ..., pages: _Optional[int] = ..., date: _Optional[str] = ..., abstract: _Optional[str] = ..., cite_num: _Optional[int] = ..., submitted: bool = ..., relevant_no: _Optional[int] = ..., tier: _Optional[int] = ...) -> None: ...
