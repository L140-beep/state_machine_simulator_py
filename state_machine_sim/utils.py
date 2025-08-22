"""Utility functions for the simple parser."""

from typing import List, TypeVar, Union

ListType = TypeVar('ListType')


def to_list(nodes: Union[List[ListType], None, ListType]) -> List[ListType]:
    """Return list of objects."""
    if nodes is None:
        return []
    if isinstance(nodes, list):
        return nodes
    else:
        return [nodes]


def is_vertex_type(value: str) -> bool:
    """Check if value is a valid vertex type."""
    vertex_types = ['choice', 'initial', 'final', 'terminate', 'shallowHistory']
    return value in vertex_types


def is_note_type(value: str) -> bool:
    """Check if value is a valid note type."""
    note_types = ['formal', 'informal']
    return value in note_types


def create_object_from_dict(cls, data_dict: dict):
    """
    Create an object from a dictionary.
    
    This replaces pydantic's automatic parsing functionality.
    """
    if not isinstance(data_dict, dict):
        return data_dict
    
    # Get the class annotations to understand expected types
    import inspect
    if hasattr(cls, '__annotations__'):
        annotations = cls.__annotations__
        kwargs = {}
        
        for field_name, field_type in annotations.items():
            # Handle field aliasing (like pydantic's Field(alias=...))
            dict_key = field_name
            
            # Handle special field name mappings
            if field_name == 'for_':
                dict_key = '@for'
            elif field_name in ['id', 'source', 'target', 'x', 'y', 'width', 'height', 'key', 'xmlns']:
                dict_key = f'@{field_name}'
            elif field_name == 'content':
                dict_key = '#text'
                
            if dict_key in data_dict:
                value = data_dict[dict_key]
                kwargs[field_name] = value
            elif field_name in data_dict:
                kwargs[field_name] = data_dict[field_name]
        
        # Handle remaining fields that might not be in annotations
        for key, value in data_dict.items():
            if key.startswith('@') and key[1:] in annotations:
                kwargs[key[1:]] = value
            elif key == '#text' and 'content' in annotations:
                kwargs['content'] = value
        
        return cls(**kwargs)
    else:
        return cls(**data_dict) if data_dict else cls() 