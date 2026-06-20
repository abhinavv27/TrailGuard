from pydantic import BaseModel, Field


class GraphExploreRequest(BaseModel):
    account_id: str
    hops: int = Field(default=2, ge=1, le=5)
    filters: dict = {}


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    metadata: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    metadata: dict = {}


class GraphExploreResponse(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class TraceRequest(BaseModel):
    account_id: str
    direction: str = "source"
    max_hops: int = Field(default=3, ge=1, le=10)


class TraceResponse(BaseModel):
    path_nodes: list[GraphNode] = []
    path_edges: list[GraphEdge] = []
