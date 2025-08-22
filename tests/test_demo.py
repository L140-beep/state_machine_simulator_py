"""Test the simple parser with a real demo file."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state_machine_sim.simple_parser import CGMLParser, CGMLParserException


def test_demo_file():
    """Test parsing a real demo file."""
    demo_path = "demos/CyberiadaFormat-Blinker.graphml"
    
    try:
        with open(demo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = CGMLParser()
        elements = parser.parse_cgml(content)
        
        print("Demo file parsing successful!")
        print(f"Format: {elements.format}")
        print(f"Number of state machines: {len(elements.state_machines)}")
        
        for sm_id, sm in elements.state_machines.items():
            print(f"\nState Machine '{sm_id}':")
            print(f"  Name: {sm.name}")
            print(f"  Platform: {sm.platform}")
            print(f"  Standard Version: {sm.standard_version}")
            print(f"  States: {len(sm.states)}")
            print(f"  Transitions: {len(sm.transitions)}")
            print(f"  Initial states: {len(sm.initial_states)}")
            print(f"  Final states: {len(sm.finals)}")
            print(f"  Choice states: {len(sm.choices)}")
            print(f"  Components: {len(sm.components)}")
            print(f"  Notes: {len(sm.notes)}")
            
            if sm.states:
                print(f"  State names: {[state.name for state in sm.states.values()]}")
        
        return True
        
    except FileNotFoundError:
        print(f"Demo file not found at {demo_path}")
        return False
    except Exception as e:
        print(f"Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_demo_file() 