"""Simple test for the CyberiadaML parser."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simple_parser import CGMLParser, CGMLParserException


def test_basic_parsing():
    """Test basic XML parsing functionality."""
    simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
    <data key="gFormat">Cyberiada-GraphML</data>
    <key id="dStateMachine" for="graph" attr.name="statemachine" attr.type="string"/>
    <key id="dName" for="node" attr.name="name" attr.type="string"/>
    <key id="dGeometry" for="node" attr.name="geometry" attr.type="string"/>
    <graph id="G" edgedefault="directed">
        <data key="dStateMachine"/>
        <data key="dName">TestStateMachine</data>
        <node id="n0">
            <data key="dName">TestState</data>
            <data key="dGeometry">
                <rect x="100.0" y="100.0" width="80.0" height="40.0"/>
            </data>
        </node>
    </graph>
</graphml>"""
    
    parser = CGMLParser()
    try:
        elements = parser.parse_cgml(simple_xml)
        print("Parsing successful!")
        print(f"Format: {elements.format}")
        print(f"State machines: {list(elements.state_machines.keys())}")
        
        # Check if we have a state machine
        if elements.state_machines:
            sm = list(elements.state_machines.values())[0]
            print(f"States in state machine: {list(sm.states.keys())}")
            if sm.states:
                state = list(sm.states.values())[0]
                print(f"State name: {state.name}")
        
        return True
    except Exception as e:
        print(f"Parsing failed: {e}")
        return False


if __name__ == "__main__":
    test_basic_parsing() 