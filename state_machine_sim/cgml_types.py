"""Module contains types for CyberiadaML scheme using standard library only."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, DefaultDict, Literal
from collections import defaultdict


# Type aliases
CGMLVertexType = Literal['choice', 'initial', 'final', 'terminate', 'shallowHistory']
CGMLNoteType = Literal['formal', 'informal']
AvailableKeys = DefaultDict[str, List['CGMLKeyNode']]


@dataclass
class Point:
    """Point data class."""
    x: float
    y: float


@dataclass
class Rectangle:
    """Rectangle data class."""
    x: float
    y: float
    width: float
    height: float


@dataclass
class CGMLRectNode:
    """The type represents <rect> node."""
    x: float
    y: float
    width: float
    height: float


@dataclass
class CGMLPointNode:
    """The type represents <point> node."""
    x: float
    y: float


@dataclass
class CGMLDataNode:
    """The type represents <data> node."""
    key: str
    content: Optional[str] = None
    rect: Optional[CGMLRectNode] = None
    point: Optional[Union[CGMLPointNode, List[CGMLPointNode]]] = None


@dataclass
class CGMLKeyNode:
    """The type represents <key> node."""
    id: str
    for_: str
    attr_name: Optional[str] = None
    attr_type: Optional[str] = None


@dataclass
class CGMLEdge:
    """The type represents <edge> node."""
    id: str
    source: str
    target: str
    data: Optional[Union[List[CGMLDataNode], CGMLDataNode]] = None


@dataclass
class CGMLGraph:
    """The type represents <graph> node."""
    id: str
    data: Union[List[CGMLDataNode], CGMLDataNode] = field(default_factory=list)
    edgedefault: Optional[str] = None
    node: Optional[Union[List['CGMLNode'], 'CGMLNode']] = None
    edge: Optional[Union[List[CGMLEdge], CGMLEdge]] = None


@dataclass
class CGMLNode:
    """The type represents <node> node."""
    id: str
    graph: Optional[Union[CGMLGraph, List[CGMLGraph]]] = None
    data: Optional[Union[List[CGMLDataNode], CGMLDataNode]] = None


@dataclass
class CGMLGraphml:
    """The type represents <graphml> node."""
    data: Union[CGMLDataNode, List[CGMLDataNode]]
    xmlns: str
    key: Optional[Union[List[CGMLKeyNode], CGMLKeyNode]] = None
    graph: Optional[Union[List[CGMLGraph], CGMLGraph]] = None


@dataclass
class CGML:
    """Root type of CyberiadaML scheme."""
    graphml: CGMLGraphml


@dataclass
class CGMLBaseVertex:
    """
    The type represents pseudo-nodes.
    
    type: content from nested <data>-node with key 'dVertex'.
    data: content from nested <data>-node with key 'dName'.
    position: content from nested <data>-node with key 'dGeometry'.
    parent: parent node id.
    """
    type: str
    data: Optional[str] = None
    position: Optional[Union[Point, Rectangle]] = None
    parent: Optional[str] = None


@dataclass
class CGMLState:
    """
    Data class with information about state.
    
    State is <node>, that not connected with meta node,
    doesn't have data node with key 'dNote'
    
    Parameters:
    name: content of data node with key 'dName'.
    actions: content of data node with key 'dData'.
    bounds: x, y, width, height properties of data node with key 'dGeometry'.
    parent: parent state id.
    color: content of data node with key 'dColor'.
    unknown_datanodes: all datanodes, whose information is not included in the type.
    """
    name: str
    actions: str
    unknown_datanodes: List[CGMLDataNode]
    parent: Optional[str] = None
    bounds: Optional[Union[Rectangle, Point]] = None
    color: Optional[str] = None


@dataclass
class CGMLComponent:
    """
    Data class with information about component.
    
    Component is formal note, that includes <data>-node with key 'dName'
    and content 'CGML_COMPONENT'.
    parameters: content of data node with key 'dData'.
    """
    id: str
    type: str
    parameters: Dict[str, str]


@dataclass
class CGMLInitialState(CGMLBaseVertex):
    """
    Data class with information about initial state (pseudo node).
    
    Initial state is <node>, that contains data node with key 'dVertex'
    and content 'initial'.
    """
    pass


@dataclass
class CGMLShallowHistory(CGMLBaseVertex):
    """
    Data class with information about shallow history node (pseudo node).
    
    Choice is <node>, that contains data node with key 'dVertex'
    and content 'shallowHistory'.
    """
    pass


@dataclass
class CGMLChoice(CGMLBaseVertex):
    """
    Data class with information about choice node (pseudo node).
    
    Choice is <node>, that contains data node with key 'dVertex'
    and content 'choice'.
    """
    pass


@dataclass
class CGMLTransition:
    """
    Data class with information about transition(<edge>).
    
    Parameters:
    source: <edge> source property's content.
    target: <edge> target property's content.
    actions: content of data node with 'dData' key.
    color: content of data node with 'dColor' key.
    position: x, y properties of data node with 'dGeometry' key.
    unknown_datanodes: all datanodes, whose information is not included in the type.
    """
    id: str
    source: str
    target: str
    actions: str
    unknown_datanodes: List[CGMLDataNode]
    color: Optional[str] = None
    position: List[Point] = field(default_factory=list)
    label_position: Optional[Point] = None
    pivot: Optional[str] = None


@dataclass
class CGMLNote:
    """
    Dataclass with information about note.
    
    Note is <node> containing data node with key 'dNote'
    type: content of <data key="dNote">
    text: content of <data key="dData">
    name: content of <data key="dName">
    position: properties <data key="dGeometry">'s child <point> or <rect>
    unknown_datanodes: all datanodes, whose information is not included in the type.
    """
    name: str
    position: Union[Point, Rectangle]
    text: str
    type: str
    unknown_datanodes: List[CGMLDataNode]
    parent: Optional[str] = None


@dataclass
class CGMLMeta:
    """
    The type represents meta-information from formal note with 'dName' CGML_META.
    
    id: meta-node id.
    values: information from meta node, exclude required parameters.
    """
    id: str
    values: Dict[str, str]


@dataclass
class CGMLFinal(CGMLBaseVertex):
    """
    The type represents final-states.
    
    Final state - <node>, that includes dVertex with content 'final'.
    """
    pass


@dataclass
class CGMLTerminate(CGMLBaseVertex):
    """
    The type represents terminate-states.
    
    Final state - <node>, that includes dVertex with content 'terminate'.
    """
    pass


@dataclass
class CGMLStateMachine:
    """
    The type represents state machine <graph>.
    
    Contains dict of CGMLStates, where the key is state's id.
    Also contains transitions, components, available keys, notes.
    
    States doesn't contain components nodes and pseudo-nodes.
    transitions doesn't contain component's transitions.
    """
    platform: str
    meta: CGMLMeta
    standard_version: str
    states: Dict[str, CGMLState]
    transitions: Dict[str, CGMLTransition]
    components: Dict[str, CGMLComponent]
    notes: Dict[str, CGMLNote]
    initial_states: Dict[str, CGMLInitialState]
    finals: Dict[str, CGMLFinal]
    choices: Dict[str, CGMLChoice]
    terminates: Dict[str, CGMLTerminate]
    shallow_history: Dict[str, CGMLShallowHistory]
    unknown_vertexes: Dict[str, CGMLBaseVertex]
    name: Optional[str] = None


@dataclass
class CGMLElements:
    """
    Dataclass with elements of parsed scheme.
    
    Parameters:
    meta: content of data node with key 'dData' inside meta-node.
    format: content of data node with key 'gFormat'.
    platform: content of meta-data
    keys: dict of KeyNodes, where the key is 'for' attribute.
        Example: { "node": [KeyNode, ...], "edge": [...] }
    """
    state_machines: Dict[str, CGMLStateMachine]
    format: str
    keys: AvailableKeys


# Union type for vertices
Vertex = Union[
    CGMLFinal,
    CGMLChoice,
    CGMLInitialState,
    CGMLTerminate,
    CGMLShallowHistory,
    CGMLBaseVertex
]

defaultSignals = ['unconditionalTransition', 'break']