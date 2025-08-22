"""Test the simple parser with all demo files."""

import sys
import os
import glob

from state_machine_sim.simple_parser import CGMLParser, CGMLParserException


def test_all_demos():
    """Test parsing all demo files."""
    demo_dir = "demos"
    demo_files = glob.glob(f"{demo_dir}/*.graphml")
    
    if not demo_files:
        print(f"No demo files found in {demo_dir}")
        return False
    
    parser = CGMLParser()
    success_count = 0
    total_count = len(demo_files)
    
    print(f"Testing {total_count} demo files...\n")
    
    for demo_file in demo_files:
        print(f"Testing: {demo_file}")
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            elements = parser.parse_cgml(content)
            
            print(f"  ✓ Success!")
            print(f"    Format: {elements.format}")
            print(f"    State machines: {len(elements.state_machines)}")
            
            total_states = sum(len(sm.states) for sm in elements.state_machines.values())
            total_transitions = sum(len(sm.transitions) for sm in elements.state_machines.values())
            
            print(f"    Total states: {total_states}")
            print(f"    Total transitions: {total_transitions}")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        print()
    
    print(f"Results: {success_count}/{total_count} files parsed successfully")
    return success_count == total_count


if __name__ == "__main__":
    test_all_demos() 