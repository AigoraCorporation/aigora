from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MasteryLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MASTERY_LEVEL_UNSPECIFIED: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_UNEXPOSED: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_RECOGNISES: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_GUIDED: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_INDEPENDENT: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_EFFICIENT: _ClassVar[MasteryLevel]
    MASTERY_LEVEL_TRANSFERABLE: _ClassVar[MasteryLevel]

class PrerequisiteKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PREREQUISITE_KIND_UNSPECIFIED: _ClassVar[PrerequisiteKind]
    PREREQUISITE_KIND_HARD: _ClassVar[PrerequisiteKind]
    PREREQUISITE_KIND_SOFT: _ClassVar[PrerequisiteKind]
MASTERY_LEVEL_UNSPECIFIED: MasteryLevel
MASTERY_LEVEL_UNEXPOSED: MasteryLevel
MASTERY_LEVEL_RECOGNISES: MasteryLevel
MASTERY_LEVEL_GUIDED: MasteryLevel
MASTERY_LEVEL_INDEPENDENT: MasteryLevel
MASTERY_LEVEL_EFFICIENT: MasteryLevel
MASTERY_LEVEL_TRANSFERABLE: MasteryLevel
PREREQUISITE_KIND_UNSPECIFIED: PrerequisiteKind
PREREQUISITE_KIND_HARD: PrerequisiteKind
PREREQUISITE_KIND_SOFT: PrerequisiteKind

class RequestContext(_message.Message):
    __slots__ = ("request_id", "graph_version")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    graph_version: str
    def __init__(self, request_id: _Optional[str] = ..., graph_version: _Optional[str] = ...) -> None: ...

class MasteryCriterion(_message.Message):
    __slots__ = ("level", "description")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    level: MasteryLevel
    description: str
    def __init__(self, level: _Optional[_Union[MasteryLevel, str]] = ..., description: _Optional[str] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("id", "name", "domain", "description", "mastery_criteria", "error_taxonomy", "prerequisite_ids", "regression_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MASTERY_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    ERROR_TAXONOMY_FIELD_NUMBER: _ClassVar[int]
    PREREQUISITE_IDS_FIELD_NUMBER: _ClassVar[int]
    REGRESSION_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    domain: str
    description: str
    mastery_criteria: _containers.RepeatedCompositeFieldContainer[MasteryCriterion]
    error_taxonomy: _containers.RepeatedScalarFieldContainer[str]
    prerequisite_ids: _containers.RepeatedScalarFieldContainer[str]
    regression_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., domain: _Optional[str] = ..., description: _Optional[str] = ..., mastery_criteria: _Optional[_Iterable[_Union[MasteryCriterion, _Mapping]]] = ..., error_taxonomy: _Optional[_Iterable[str]] = ..., prerequisite_ids: _Optional[_Iterable[str]] = ..., regression_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ErrorDetail(_message.Message):
    __slots__ = ("code", "message", "request_id", "graph_version")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    request_id: str
    graph_version: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., request_id: _Optional[str] = ..., graph_version: _Optional[str] = ...) -> None: ...

class GetGraphMetadataRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ...) -> None: ...

class GetGraphMetadataResponse(_message.Message):
    __slots__ = ("graph_version", "node_count", "edge_count", "profile_count", "profile_ids", "domains")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    NODE_COUNT_FIELD_NUMBER: _ClassVar[int]
    EDGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    PROFILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    PROFILE_IDS_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    node_count: int
    edge_count: int
    profile_count: int
    profile_ids: _containers.RepeatedScalarFieldContainer[str]
    domains: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, graph_version: _Optional[str] = ..., node_count: _Optional[int] = ..., edge_count: _Optional[int] = ..., profile_count: _Optional[int] = ..., profile_ids: _Optional[_Iterable[str]] = ..., domains: _Optional[_Iterable[str]] = ...) -> None: ...

class GetNodeRequest(_message.Message):
    __slots__ = ("context", "node_id")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    node_id: str
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ..., node_id: _Optional[str] = ...) -> None: ...

class GetNodeResponse(_message.Message):
    __slots__ = ("graph_version", "node")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    node: Node
    def __init__(self, graph_version: _Optional[str] = ..., node: _Optional[_Union[Node, _Mapping]] = ...) -> None: ...

class ListNodesRequest(_message.Message):
    __slots__ = ("context", "domain", "profile_id", "page_size", "page_token")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PROFILE_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    domain: str
    profile_id: str
    page_size: int
    page_token: str
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ..., domain: _Optional[str] = ..., profile_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListNodesResponse(_message.Message):
    __slots__ = ("graph_version", "nodes", "next_page_token", "total_size")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    next_page_token: str
    total_size: int
    def __init__(self, graph_version: _Optional[str] = ..., nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ..., next_page_token: _Optional[str] = ..., total_size: _Optional[int] = ...) -> None: ...

class GetPrerequisitesRequest(_message.Message):
    __slots__ = ("context", "node_id", "include_soft")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SOFT_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    node_id: str
    include_soft: bool
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ..., node_id: _Optional[str] = ..., include_soft: bool = ...) -> None: ...

class Prerequisite(_message.Message):
    __slots__ = ("node", "kind")
    NODE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    node: Node
    kind: PrerequisiteKind
    def __init__(self, node: _Optional[_Union[Node, _Mapping]] = ..., kind: _Optional[_Union[PrerequisiteKind, str]] = ...) -> None: ...

class GetPrerequisitesResponse(_message.Message):
    __slots__ = ("graph_version", "prerequisites")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    PREREQUISITES_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    prerequisites: _containers.RepeatedCompositeFieldContainer[Prerequisite]
    def __init__(self, graph_version: _Optional[str] = ..., prerequisites: _Optional[_Iterable[_Union[Prerequisite, _Mapping]]] = ...) -> None: ...

class GetRegressionTargetsRequest(_message.Message):
    __slots__ = ("context", "node_id")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    node_id: str
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ..., node_id: _Optional[str] = ...) -> None: ...

class GetRegressionTargetsResponse(_message.Message):
    __slots__ = ("graph_version", "targets")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    targets: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, graph_version: _Optional[str] = ..., targets: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class GetLearningPathRequest(_message.Message):
    __slots__ = ("context", "start_node_id", "target_node_id", "include_soft")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    START_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SOFT_FIELD_NUMBER: _ClassVar[int]
    context: RequestContext
    start_node_id: str
    target_node_id: str
    include_soft: bool
    def __init__(self, context: _Optional[_Union[RequestContext, _Mapping]] = ..., start_node_id: _Optional[str] = ..., target_node_id: _Optional[str] = ..., include_soft: bool = ...) -> None: ...

class GetLearningPathResponse(_message.Message):
    __slots__ = ("graph_version", "path_found", "path")
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    PATH_FOUND_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    graph_version: str
    path_found: bool
    path: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, graph_version: _Optional[str] = ..., path_found: bool = ..., path: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "graph_version")
    class ServingStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVING_STATUS_UNSPECIFIED: _ClassVar[HealthCheckResponse.ServingStatus]
        SERVING_STATUS_SERVING: _ClassVar[HealthCheckResponse.ServingStatus]
        SERVING_STATUS_NOT_SERVING: _ClassVar[HealthCheckResponse.ServingStatus]
    SERVING_STATUS_UNSPECIFIED: HealthCheckResponse.ServingStatus
    SERVING_STATUS_SERVING: HealthCheckResponse.ServingStatus
    SERVING_STATUS_NOT_SERVING: HealthCheckResponse.ServingStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    GRAPH_VERSION_FIELD_NUMBER: _ClassVar[int]
    status: HealthCheckResponse.ServingStatus
    graph_version: str
    def __init__(self, status: _Optional[_Union[HealthCheckResponse.ServingStatus, str]] = ..., graph_version: _Optional[str] = ...) -> None: ...
