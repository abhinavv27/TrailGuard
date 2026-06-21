from pydantic import BaseModel, Field


class GraphExploreRequest(BaseModel):
    account_id: str = ""
    hops: int = Field(default=2, ge=1, le=5, alias="depth")
    max_nodes: int = Field(default=50, ge=1, le=500)
    filters: dict = {}

    model_config = {"populate_by_name": True}


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    risk: str = ""
    metadata: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    type: str = "normal"
    metadata: dict = {}


class GraphExploreResponse(BaseModel):
    nodes: list[GraphNode] = []
    links: list[GraphEdge] = []


class TraceRequest(BaseModel):
    account_id: str
    direction: str = "source"
    max_hops: int = Field(default=3, ge=1, le=10, alias="depth")
    max_nodes: int = Field(default=50, ge=1, le=500)

    model_config = {"populate_by_name": True}


class TraceResponse(BaseModel):
    path_nodes: list[GraphNode] = []
    path_edges: list[GraphEdge] = []
