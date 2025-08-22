"""Simple CyberiadaML parser using only standard libraries."""

from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, List, Optional, Union

from .xml_parser import parse
from .utils import to_list, is_vertex_type, is_note_type
from .cgml_types import (
    CGMLDataNode, CGMLKeyNode, CGMLPointNode,
    CGML, CGMLEdge, CGMLGraph, CGMLNode,
    CGMLBaseVertex, CGMLChoice, CGMLFinal, CGMLMeta, CGMLShallowHistory,
    CGMLStateMachine, CGMLTerminate, CGMLComponent, CGMLElements,
    AvailableKeys, CGMLInitialState, CGMLNote, CGMLState, CGMLTransition,
    Point, Rectangle, CGMLRectNode, CGMLGraphml
)


class CGMLParserException(Exception):
    """Logical errors during parsing CGML scheme."""
    pass


def create_empty_elements() -> CGMLElements:
    """Create CGMLElements with empty fields."""
    return CGMLElements(
        state_machines={},
        format='',
        keys=defaultdict(list)
    )


def create_empty_state_machine() -> CGMLStateMachine:
    """Create CGMLStateMachine with empty fields."""
    return CGMLStateMachine(
        standard_version='',
        platform='',
        meta=CGMLMeta(id='', values={}),
        states={},
        transitions={},
        finals={},
        choices={},
        terminates={},
        initial_states={},
        components={},
        notes={},
        shallow_history={},
        unknown_vertexes={}
    )


def _is_empty_meta(meta: CGMLMeta) -> bool:
    return meta.values == {} and meta.id == ''


def _parse_data_node(data_dict: dict) -> CGMLDataNode:
    """Parse dictionary into CGMLDataNode."""
    key = data_dict.get('@key', '')
    content = data_dict.get('#text')

    rect = None
    if 'rect' in data_dict:
        rect_data = data_dict['rect']
        rect = CGMLRectNode(
            x=rect_data.get('@x', 0.0),
            y=rect_data.get('@y', 0.0),
            width=rect_data.get('@width', 0.0),
            height=rect_data.get('@height', 0.0)
        )

    point = None
    if 'point' in data_dict:
        point_data = data_dict['point']
        if isinstance(point_data, list):
            point = [CGMLPointNode(
                x=p.get('@x', 0.0), y=p.get('@y', 0.0)) for p in point_data]
        else:
            point = CGMLPointNode(x=point_data.get(
                '@x', 0.0), y=point_data.get('@y', 0.0))

    return CGMLDataNode(key=key, content=content, rect=rect, point=point)


def _parse_key_node(key_dict: dict) -> CGMLKeyNode:
    """Parse dictionary into CGMLKeyNode."""
    return CGMLKeyNode(
        id=key_dict.get('@id', ''),
        for_=key_dict.get('@for', ''),
        attr_name=key_dict.get('@attr.name'),
        attr_type=key_dict.get('@attr.type')
    )


def _parse_edge(edge_dict: dict) -> CGMLEdge:
    """Parse dictionary into CGMLEdge."""
    data = None
    if 'data' in edge_dict:
        data_list = edge_dict['data']
        if isinstance(data_list, list):
            data = [_parse_data_node(d) for d in data_list]
        else:
            data = _parse_data_node(data_list)

    return CGMLEdge(
        id=edge_dict.get('@id', ''),
        source=edge_dict.get('@source', ''),
        target=edge_dict.get('@target', ''),
        data=data
    )


def _parse_node(node_dict: dict) -> CGMLNode:
    """Parse dictionary into CGMLNode."""
    data = None
    if 'data' in node_dict:
        data_list = node_dict['data']
        if isinstance(data_list, list):
            data = [_parse_data_node(d) for d in data_list]
        else:
            data = _parse_data_node(data_list)

    graph = None
    if 'graph' in node_dict:
        graph_data = node_dict['graph']
        if isinstance(graph_data, list):
            graph = [_parse_graph(g) for g in graph_data]
        else:
            graph = _parse_graph(graph_data)

    return CGMLNode(
        id=node_dict.get('@id', ''),
        graph=graph,
        data=data
    )


def _parse_graph(graph_dict: dict) -> CGMLGraph:
    """Parse dictionary into CGMLGraph."""
    data = []
    if 'data' in graph_dict:
        data_list = graph_dict['data']
        if isinstance(data_list, list):
            data = [_parse_data_node(d) for d in data_list]
        else:
            data = _parse_data_node(data_list)

    node = None
    if 'node' in graph_dict:
        node_data = graph_dict['node']
        if isinstance(node_data, list):
            node = [_parse_node(n) for n in node_data]
        else:
            node = _parse_node(node_data)

    edge = None
    if 'edge' in graph_dict:
        edge_data = graph_dict['edge']
        if isinstance(edge_data, list):
            edge = [_parse_edge(e) for e in edge_data]
        else:
            edge = _parse_edge(edge_data)

    return CGMLGraph(
        id=graph_dict.get('@id', ''),
        data=data,
        edgedefault=graph_dict.get('@edgedefault'),
        node=node,
        edge=edge
    )


def _parse_graphml(graphml_dict: dict) -> CGMLGraphml:
    """Parse dictionary into CGMLGraphml."""
    data = []
    if 'data' in graphml_dict:
        data_list = graphml_dict['data']
        if isinstance(data_list, list):
            data = [_parse_data_node(d) for d in data_list]
        else:
            data = _parse_data_node(data_list)

    key = None
    if 'key' in graphml_dict:
        key_data = graphml_dict['key']
        if isinstance(key_data, list):
            key = [_parse_key_node(k) for k in key_data]
        else:
            key = _parse_key_node(key_data)

    graph = None
    if 'graph' in graphml_dict:
        graph_data = graphml_dict['graph']
        if isinstance(graph_data, list):
            graph = [_parse_graph(g) for g in graph_data]
        else:
            graph = _parse_graph(graph_data)

    return CGMLGraphml(
        data=data,
        xmlns=graphml_dict.get('@xmlns', ''),
        key=key,
        graph=graph
    )


class CGMLParser:
    """Class that contains functions for parsing CyberiadaML."""

    def __init__(self) -> None:
        self.elements: CGMLElements = create_empty_elements()

    def parse_cgml(self, graphml: str) -> CGMLElements:
        """
        Parse CyberiadaGraphml scheme.

        Args:
            graphml (str): CyberiadaML scheme.

        Returns:
            CGMLElements: notes, states, transitions, initial state and components
        """
        self.elements = create_empty_elements()
        parsed_dict = parse(graphml)

        # Create CGML object manually
        graphml_data = parsed_dict['graphml']
        cgml = CGML(graphml=_parse_graphml(graphml_data))

        graphs: List[CGMLGraph] = to_list(cgml.graphml.graph)
        format_str: str = self._get_format(cgml)

        for graph in graphs:
            keys: AvailableKeys = self._get_available_keys(cgml)
            platform = ''
            standard_version = ''
            meta: CGMLMeta = CGMLMeta(id='', values={})
            states: Dict[str, CGMLState] = {}
            transitions: Dict[str, CGMLTransition] = {}
            notes: Dict[str, CGMLNote] = {}
            terminates: Dict[str, CGMLTerminate] = {}
            finals: Dict[str, CGMLFinal] = {}
            choices: Dict[str, CGMLChoice] = {}
            initials: Dict[str, CGMLInitialState] = {}
            unknown_vertexes: Dict[str, CGMLBaseVertex] = {}
            components: Dict[str, CGMLComponent] = {}
            shallow_history: Dict[str, CGMLShallowHistory] = {}

            vertex_dicts = {
                'initial': (initials, CGMLInitialState),
                'choice': (choices, CGMLChoice),
                'final': (finals, CGMLFinal),
                'terminate': (terminates, CGMLTerminate),
                'shallowHistory': (shallow_history, CGMLShallowHistory)
            }

            states = self._parse_graph_nodes(graph)
            transitions = self._parse_graph_edges(graph)

            for state_id in list(states.keys()):
                state = self._process_state_data(states[state_id])
                if isinstance(state, CGMLNote):
                    note = state
                    del states[state_id]
                    if note.type == 'informal':
                        notes[state_id] = state
                        continue
                    if note.name == 'CGML_META':
                        if not _is_empty_meta(meta):
                            raise CGMLParserException('Double meta nodes!')
                        meta.id = state_id
                        meta.values = self._parse_meta(note.text)
                        try:
                            platform = meta.values['platform']
                            standard_version = meta.values['standardVersion']
                        except KeyError:
                            raise CGMLParserException(
                                'No platform or standardVersion.')
                    elif note.name == 'CGML_COMPONENT':
                        component_parameters: Dict[str, str] = self._parse_meta(
                            note.text)
                        try:
                            component_id = component_parameters['id'].strip()
                            component_type = component_parameters['type'].strip(
                            )
                            del component_parameters['id']
                            del component_parameters['type']
                        except KeyError:
                            raise CGMLParserException(
                                "Component doesn't have type or id.")
                        components[state_id] = CGMLComponent(
                            id=component_id,
                            type=component_type,
                            parameters=component_parameters
                        )
                elif isinstance(state, CGMLState):
                    states[state_id] = state
                elif isinstance(state, CGMLBaseVertex):
                    vertex = state
                    del states[state_id]
                    if is_vertex_type(vertex.type):
                        vertex_dict, vertex_type = vertex_dicts[vertex.type]
                        vertex_dict[state_id] = vertex_type(
                            type=vertex.type,
                            data=vertex.data,
                            position=vertex.position,
                            parent=vertex.parent
                        )
                    else:
                        unknown_vertexes[state_id] = CGMLBaseVertex(
                            type=vertex.type,
                            data=vertex.data,
                            position=vertex.position,
                            parent=vertex.parent
                        )
                else:
                    raise CGMLParserException(
                        'Internal error: Unknown type of node')

            component_ids: List[str] = []
            for transition in list(transitions.values()):
                processed_transition: CGMLTransition = self._process_edge_data(
                    transition)
                if transition.source == meta.id:
                    component_ids.append(transition.id)
                else:
                    transitions[transition.id] = processed_transition

            for component_id in component_ids:
                del transitions[component_id]

            self.elements.state_machines[graph.id] = CGMLStateMachine(
                states=states,
                transitions=transitions,
                components=components,
                initial_states=initials,
                finals=finals,
                unknown_vertexes=unknown_vertexes,
                terminates=terminates,
                notes=notes,
                choices=choices,
                name=self._get_state_machine_name(graph),
                meta=meta,
                shallow_history=shallow_history,
                platform=platform,
                standard_version=standard_version,
            )

        self.elements.keys = keys
        self.elements.format = format_str
        return self.elements

    def _get_state_machine_name(self, graph: CGMLGraph) -> Optional[str]:
        graph_datas = to_list(graph.data)
        name: Optional[str] = None
        is_state_machine = False
        for graph_data in graph_datas:
            if graph_data.key == 'dName':
                name = graph_data.content
            if graph_data.key == 'dStateMachine':
                is_state_machine = True
        if not is_state_machine:
            raise CGMLParserException(
                "First level graph doesn't contain <data> with dStateMachine key!")
        return name

    def _parse_meta(self, meta: str) -> Dict[str, str]:
        splited_parameters: List[str] = meta.split('\n\n')
        parameters: Dict[str, str] = {}
        for parameter in splited_parameters:
            if '/' in parameter:
                parameter_name, parameter_value = parameter.split('/', 1)
                parameters[parameter_name.strip()] = parameter_value.strip()
        return parameters

    def _get_data_content(self, data_node: CGMLDataNode) -> str:
        return data_node.content if data_node.content is not None else ''

    def _process_edge_data(self, transition: CGMLTransition) -> CGMLTransition:
        new_transition = CGMLTransition(
            position=[],
            id=transition.id,
            source=transition.source,
            target=transition.target,
            actions=transition.actions,
            unknown_datanodes=[]
        )
        for data_node in transition.unknown_datanodes:
            if data_node.key == 'dData':
                new_transition.actions = self._get_data_content(data_node)
            elif data_node.key == 'dGeometry':
                if data_node.point is None:
                    raise CGMLParserException(
                        'Edge with key dGeometry doesnt have <point> node.')
                points: List[CGMLPointNode] = to_list(data_node.point)
                for point in points:
                    new_transition.position.append(Point(x=point.x, y=point.y))
            elif data_node.key == 'dColor':
                new_transition.color = self._get_data_content(data_node)
            elif data_node.key == 'dLabelGeometry':
                if data_node.point is None:
                    raise CGMLParserException(
                        'Edge with key dGeometry doesnt have <point> node.')
                if isinstance(data_node.point, list):
                    raise CGMLParserException(
                        'dLabelGeometry with several points!')
                point = data_node.point
                new_transition.label_position = Point(x=point.x, y=point.y)
            else:
                new_transition.unknown_datanodes.append(data_node)
        return new_transition

    def _get_note_type(self, value: str) -> str:
        if is_note_type(value):
            return value
        raise CGMLParserException(
            f'Unknown type of note! Expect formal or informal.')

    def _process_state_data(self, state: CGMLState) -> Union[CGMLState, CGMLNote, CGMLBaseVertex]:
        """Return CGMLState, CGMLNote, or CGMLBaseVertex."""
        new_state = CGMLState(
            name=state.name,
            actions=state.actions,
            unknown_datanodes=[],
            bounds=state.bounds,
            parent=state.parent
        )
        note_type: Optional[str] = None
        vertex_type: Optional[str] = None
        is_note = False
        is_vertex = False

        for data_node in state.unknown_datanodes:
            if data_node.key == 'dName':
                new_state.name = self._get_data_content(data_node)
            elif data_node.key == 'dGeometry':
                if data_node.rect is None and data_node.point is None:
                    raise CGMLParserException(
                        'Node with key dGeometry doesnt have rect or point child')
                if data_node.point is not None:
                    if isinstance(data_node.point, list):
                        raise CGMLParserException(
                            "State doesn't support several points.")
                    new_state.bounds = Point(
                        x=data_node.point.x, y=data_node.point.y)
                    continue
                if data_node.rect is not None:
                    new_state.bounds = Rectangle(
                        x=data_node.rect.x,
                        y=data_node.rect.y,
                        width=data_node.rect.width,
                        height=data_node.rect.height
                    )
            elif data_node.key == 'dVertex':
                is_vertex = True
                vertex_type = self._get_data_content(data_node)
            elif data_node.key == 'dData':
                new_state.actions = self._get_data_content(data_node)
            elif data_node.key == 'dNote':
                is_note = True
                if data_node.content is None:
                    note_type = 'informal'
                else:
                    note_type = self._get_note_type(
                        self._get_data_content(data_node))
            elif data_node.key == 'dColor':
                new_state.color = self._get_data_content(data_node)
            else:
                new_state.unknown_datanodes.append(data_node)

        if is_note and note_type is not None:
            bounds: Optional[Union[Rectangle, Point]] = new_state.bounds
            x = 0.0
            y = 0.0
            if bounds is None:
                if note_type == 'informal':
                    raise CGMLParserException('No position for note!')
            else:
                x = bounds.x
                y = bounds.y
            return CGMLNote(
                parent=new_state.parent,
                name=new_state.name,
                position=Point(x=x, y=y),
                type=note_type,
                text=new_state.actions,
                unknown_datanodes=new_state.unknown_datanodes
            )

        if is_vertex and vertex_type is not None:
            return CGMLBaseVertex(
                type=vertex_type,
                position=new_state.bounds,
                parent=new_state.parent
            )

        return new_state

    def _parse_graph_edges(self, root: CGMLGraph) -> Dict[str, CGMLTransition]:
        def _parse_edge(edge: CGMLEdge, cgml_transitions: Dict[str, CGMLTransition]) -> None:
            cgml_transitions[edge.id] = CGMLTransition(
                id=edge.id,
                source=edge.source,
                target=edge.target,
                actions='',
                unknown_datanodes=to_list(edge.data),
            )

        cgml_transitions: Dict[str, CGMLTransition] = {}
        if root.edge is not None:
            if isinstance(root.edge, Iterable) and not isinstance(root.edge, str):
                for edge in root.edge:
                    _parse_edge(edge, cgml_transitions)
            else:
                _parse_edge(root.edge, cgml_transitions)
        return cgml_transitions

    def _parse_graph_nodes(self, root: CGMLGraph, parent: Optional[str] = None) -> Dict[str, CGMLState]:
        def parse_node(node: CGMLNode) -> Dict[str, CGMLState]:
            cgml_states: Dict[str, CGMLState] = {}
            cgml_states[node.id] = CGMLState(
                name='',
                actions='',
                unknown_datanodes=to_list(node.data),
            )
            if parent is not None:
                cgml_states[node.id].parent = parent
            graphs: List[CGMLGraph] = to_list(node.graph)
            for graph in graphs:
                cgml_states = cgml_states | self._parse_graph_nodes(
                    graph, node.id)
            return cgml_states

        cgml_states: Dict[str, CGMLState] = {}
        if root.node is not None:
            if isinstance(root.node, Iterable) and not isinstance(root.node, str):
                for node in root.node:
                    cgml_states = cgml_states | parse_node(node)
            else:
                cgml_states = cgml_states | parse_node(root.node)
        return cgml_states

    def _get_available_keys(self, cgml: CGML) -> AvailableKeys:
        key_node_dict: AvailableKeys = defaultdict(list)
        if cgml.graphml.key is not None:
            if isinstance(cgml.graphml.key, Iterable) and not isinstance(cgml.graphml.key, str):
                for key_node in cgml.graphml.key:
                    key_node_dict[key_node.for_].append(key_node)
            else:
                key_node_dict[cgml.graphml.key.for_].append(cgml.graphml.key)
        return key_node_dict

    def _get_format(self, cgml: CGML) -> str:
        if isinstance(cgml.graphml.data, Iterable) and not isinstance(cgml.graphml.data, str):
            for data_node in cgml.graphml.data:
                if data_node.key == 'gFormat':
                    if data_node.content is not None:
                        return data_node.content
                    raise CGMLParserException(
                        'Data node with key "gFormat" is empty')
        else:
            if cgml.graphml.data.key == 'gFormat':
                if cgml.graphml.data.content is not None:
                    return cgml.graphml.data.content
                raise CGMLParserException(
                    'Data node with key "gFormat" is empty')
        raise CGMLParserException('Data node with key "gFormat" is missing')
