"""Simple XML parser using only standard library."""

import xml.etree.ElementTree as ET
from typing import Dict, Any


def parse_xml_to_dict(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string to dictionary structure.

    This function replaces xmltodict functionality using only standard library.
    """
    root = ET.fromstring(xml_string)
    # Remove namespace from root tag
    root_tag = root.tag
    if '}' in root_tag:
        root_tag = root_tag.split('}')[1]
    return {root_tag: _element_to_dict(root)}


def _element_to_dict(element: ET.Element) -> Dict[str, Any]:
    """Convert XML element to dictionary."""
    result = {}

    # Add attributes with @ prefix
    if element.attrib:
        for key, value in element.attrib.items():
            # Handle special attribute names
            if key == 'for':
                result['@for'] = value
            else:
                result[f'@{key}'] = value

    # Handle text content
    if element.text and element.text.strip():
        result['#text'] = element.text.strip()

    # Handle child elements
    children = list(element)
    if children:
        for child in children:
            child_dict = _element_to_dict(child)

            # Remove namespace from tag name
            tag_name = child.tag
            if '}' in tag_name:
                tag_name = tag_name.split('}')[1]

            if tag_name in result:
                # Multiple children with same tag - make it a list
                if not isinstance(result[tag_name], list):
                    result[tag_name] = [result[tag_name]]
                result[tag_name].append(child_dict)
            else:
                result[tag_name] = child_dict

    return result


def _convert_numeric_values(data: Any) -> Any:
    """Convert string values to appropriate numeric types where possible."""
    if isinstance(data, dict):
        return {key: _convert_numeric_values(value) for key,
                value in data.items()}
    elif isinstance(data, list):
        return [_convert_numeric_values(item) for item in data]
    elif isinstance(data, str):
        # Try to convert to float
        try:
            if '.' in data:
                return float(data)
            else:
                return int(data)
        except ValueError:
            return data
    return data


def parse(xml_string: str) -> Dict[str, Any]:
    """
    Main parse function that mimics xmltodict.parse().

    Args:
        xml_string: XML content as string

    Returns:
        Dictionary representation of XML
    """
    result = parse_xml_to_dict(xml_string)
    return _convert_numeric_values(result)
