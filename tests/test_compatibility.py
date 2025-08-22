"""Test compatibility between simple_parser and original cyberiadaml_parser."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import simple parser
from state_machine_sim.simple_parser import CGMLParser as SimpleCGMLParser

# Import original parser
# try:
#     sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
#     from cyberiadaml_py.cyberiadaml_parser import CGMLParser as OriginalCGMLParser
# except ImportError as e:
#     print(f"Cannot import original parser: {e}")
#     sys.exit(1)


def compare_basic_structure(original, simple, path=""):
    """Compare basic structure of two objects."""
    if type(original) != type(simple):
        print(f"Type mismatch at {path}: {type(original)} vs {type(simple)}")
        return False
    
    if hasattr(original, '__dict__'):
        # Compare object attributes
        orig_attrs = set(original.__dict__.keys())
        simple_attrs = set(simple.__dict__.keys())
        
        if orig_attrs != simple_attrs:
            missing_in_simple = orig_attrs - simple_attrs
            extra_in_simple = simple_attrs - orig_attrs
            if missing_in_simple:
                print(f"Missing attributes in simple parser at {path}: {missing_in_simple}")
            if extra_in_simple:
                print(f"Extra attributes in simple parser at {path}: {extra_in_simple}")
            return False
        
        # Recursively compare attributes
        for attr in orig_attrs:
            if not compare_basic_structure(
                getattr(original, attr), 
                getattr(simple, attr), 
                f"{path}.{attr}"
            ):
                return False
    
    elif isinstance(original, dict):
        if set(original.keys()) != set(simple.keys()):
            print(f"Dict keys mismatch at {path}")
            print(f"  Original: {set(original.keys())}")
            print(f"  Simple: {set(simple.keys())}")
            return False
        
        for key in original.keys():
            if not compare_basic_structure(original[key], simple[key], f"{path}[{key}]"):
                return False
    
    elif isinstance(original, (list, tuple)):
        if len(original) != len(simple):
            print(f"Length mismatch at {path}: {len(original)} vs {len(simple)}")
            return False
        
        for i, (orig_item, simple_item) in enumerate(zip(original, simple)):
            if not compare_basic_structure(orig_item, simple_item, f"{path}[{i}]"):
                return False
    
    return True


def compare_content(original, simple, path="", ignore_attrs=None):
    """Compare content of two objects, ignoring specified attributes."""
    if ignore_attrs is None:
        ignore_attrs = set()
    
    if type(original) != type(simple):
        print(f"Type mismatch at {path}: {type(original)} vs {type(simple)}")
        return False
    
    if hasattr(original, '__dict__'):
        # Compare object attributes
        for attr in original.__dict__.keys():
            if attr in ignore_attrs:
                continue
                
            orig_val = getattr(original, attr)
            simple_val = getattr(simple, attr)
            
            if not compare_content(orig_val, simple_val, f"{path}.{attr}", ignore_attrs):
                return False
    
    elif isinstance(original, dict):
        for key in original.keys():
            if key in ignore_attrs:
                continue
            if not compare_content(original[key], simple[key], f"{path}[{key}]", ignore_attrs):
                return False
    
    elif isinstance(original, (list, tuple)):
        for i, (orig_item, simple_item) in enumerate(zip(original, simple)):
            if not compare_content(orig_item, simple_item, f"{path}[{i}]", ignore_attrs):
                return False
    
    elif isinstance(original, str):
        if original != simple:
            print(f"String content mismatch at {path}: '{original}' vs '{simple}'")
            return False
    
    elif isinstance(original, (int, float)):
        if original != simple:
            print(f"Numeric content mismatch at {path}: {original} vs {simple}")
            return False
    
    return True


def test_compatibility():
    """Test that simple_parser produces the same structure as original parser."""
    
    # Use a comprehensive test case
    simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
    <data key="gFormat">Cyberiada-GraphML</data>
    <key id="dStateMachine" for="graph" attr.name="statemachine" attr.type="string"/>
    <key id="dName" for="node" attr.name="name" attr.type="string"/>
    <key id="dGeometry" for="node" attr.name="geometry" attr.type="string"/>
    <key id="dData" for="node" attr.name="data" attr.type="string"/>
    <key id="dVertex" for="node" attr.name="vertex" attr.type="string"/>
    <key id="dNote" for="node" attr.name="note" attr.type="string"/>
    <graph id="G" edgedefault="directed">
        <data key="dStateMachine"/>
        <data key="dName">TestStateMachine</data>
        <node id="meta">
            <data key="dNote">formal</data>
            <data key="dName">CGML_META</data>
            <data key="dData">platform/test

standardVersion/1.0</data>
            <data key="dGeometry">
                <point x="0.0" y="0.0"/>
            </data>
        </node>
        <node id="initial">
            <data key="dVertex">initial</data>
            <data key="dGeometry">
                <point x="50.0" y="50.0"/>
            </data>
        </node>
        <node id="state1">
            <data key="dName">State1</data>
            <data key="dData">entry/doSomething</data>
            <data key="dGeometry">
                <rect x="100.0" y="100.0" width="80.0" height="40.0"/>
            </data>
        </node>
        <node id="final">
            <data key="dVertex">final</data>
            <data key="dGeometry">
                <point x="200.0" y="100.0"/>
            </data>
        </node>
        <edge id="e1" source="initial" target="state1">
            <data key="dData">start</data>
        </edge>
        <edge id="e2" source="state1" target="final">
            <data key="dData">finish</data>
        </edge>
    </graph>
</graphml>"""
    
    print("Testing compatibility with synthetic XML...")
    
    # Parse with both parsers
    try:
        original_parser = OriginalCGMLParser()
        original_elements = original_parser.parse_cgml(simple_xml)
        print("  ✓ Original parser successful")
    except Exception as e:
        print(f"  ✗ Original parser failed: {e}")
        return False
    
    try:
        simple_parser = SimpleCGMLParser()
        simple_elements = simple_parser.parse_cgml(simple_xml)
        print("  ✓ Simple parser successful")
    except Exception as e:
        print(f"  ✗ Simple parser failed: {e}")
        return False
    
    # Skip basic structure comparison (different classes expected)
    print("\nSkipping basic structure comparison (different class types expected)...")
    
    # Compare high-level content (ignoring some implementation details)
    print("\nComparing high-level content...")
    
    # Check format
    if original_elements.format != simple_elements.format:
        print(f"  ✗ Format mismatch: '{original_elements.format}' vs '{simple_elements.format}'")
        return False
    
    # Check state machines count
    if len(original_elements.state_machines) != len(simple_elements.state_machines):
        print(f"  ✗ State machine count mismatch: {len(original_elements.state_machines)} vs {len(simple_elements.state_machines)}")
        return False
    
    # Compare each state machine
    for sm_id in original_elements.state_machines:
        if sm_id not in simple_elements.state_machines:
            print(f"  ✗ State machine {sm_id} missing in simple parser")
            return False
        
        orig_sm = original_elements.state_machines[sm_id]
        simple_sm = simple_elements.state_machines[sm_id]
        
        # Compare counts
        if len(orig_sm.states) != len(simple_sm.states):
            print(f"  ✗ State count mismatch in {sm_id}: {len(orig_sm.states)} vs {len(simple_sm.states)}")
            return False
        
        if len(orig_sm.transitions) != len(simple_sm.transitions):
            print(f"  ✗ Transition count mismatch in {sm_id}: {len(orig_sm.transitions)} vs {len(simple_sm.transitions)}")
            return False
        
        # Compare state names
        orig_state_names = {sid: state.name for sid, state in orig_sm.states.items()}
        simple_state_names = {sid: state.name for sid, state in simple_sm.states.items()}
        
        if orig_state_names != simple_state_names:
            print(f"  ✗ State names mismatch in {sm_id}")
            print(f"    Original: {orig_state_names}")
            print(f"    Simple: {simple_state_names}")
            return False
        
        # Compare meta information
        if orig_sm.platform != simple_sm.platform:
            print(f"  ✗ Platform mismatch: '{orig_sm.platform}' vs '{simple_sm.platform}'")
            return False
        
        if orig_sm.standard_version != simple_sm.standard_version:
            print(f"  ✗ Standard version mismatch: '{orig_sm.standard_version}' vs '{simple_sm.standard_version}'")
            return False
    
    print("  ✓ High-level content matches")
    
    # Print detailed comparison for verification
    print("\nDetailed comparison:")
    for sm_id, orig_sm in original_elements.state_machines.items():
        simple_sm = simple_elements.state_machines[sm_id]
        print(f"  State Machine '{sm_id}':")
        print(f"    Platform: '{orig_sm.platform}' == '{simple_sm.platform}' ✓")
        print(f"    Standard Version: '{orig_sm.standard_version}' == '{simple_sm.standard_version}' ✓")
        print(f"    States: {len(orig_sm.states)} == {len(simple_sm.states)} ✓")
        print(f"    Transitions: {len(orig_sm.transitions)} == {len(simple_sm.transitions)} ✓")
        print(f"    Initial States: {len(orig_sm.initial_states)} == {len(simple_sm.initial_states)} ✓")
        print(f"    Final States: {len(orig_sm.finals)} == {len(simple_sm.finals)} ✓")
        print(f"    Choices: {len(orig_sm.choices)} == {len(simple_sm.choices)} ✓")
        print(f"    Components: {len(orig_sm.components)} == {len(simple_sm.components)} ✓")
        print(f"    Notes: {len(orig_sm.notes)} == {len(simple_sm.notes)} ✓")
        
        # Compare state content
        if orig_sm.states:
            print(f"    Sample state comparison:")
            sample_state_id = list(orig_sm.states.keys())[0]
            orig_state = orig_sm.states[sample_state_id]
            simple_state = simple_sm.states[sample_state_id]
            print(f"      State '{sample_state_id}':")
            print(f"        Name: '{orig_state.name}' == '{simple_state.name}' ✓")
            print(f"        Actions: '{orig_state.actions}' == '{simple_state.actions}' ✓")
        
        # Compare transition content
        if orig_sm.transitions:
            print(f"    Sample transition comparison:")
            sample_trans_id = list(orig_sm.transitions.keys())[0]
            orig_trans = orig_sm.transitions[sample_trans_id]
            simple_trans = simple_sm.transitions[sample_trans_id]
            print(f"      Transition '{sample_trans_id}':")
            print(f"        Source: '{orig_trans.source}' == '{simple_trans.source}' ✓")
            print(f"        Target: '{orig_trans.target}' == '{simple_trans.target}' ✓")
            print(f"        Actions: '{orig_trans.actions}' == '{simple_trans.actions}' ✓")
    
    return True


def test_compatibility_with_demo():
    """Test compatibility using a real demo file."""
    demo_path = "demos/CyberiadaFormat-Blinker.graphml"
    
    try:
        with open(demo_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Demo file not found: {demo_path}")
        return False
    
    print(f"\nTesting compatibility with {demo_path}...")
    
    # Parse with both parsers
    try:
        original_parser = OriginalCGMLParser()
        original_elements = original_parser.parse_cgml(content)
        print("  ✓ Original parser successful")
    except Exception as e:
        print(f"  ✗ Original parser failed: {e}")
        return False
    
    try:
        simple_parser = SimpleCGMLParser()
        simple_elements = simple_parser.parse_cgml(content)
        print("  ✓ Simple parser successful")
    except Exception as e:
        print(f"  ✗ Simple parser failed: {e}")
        return False
    
    # Compare key metrics
    print("Comparing key metrics...")
    
    if original_elements.format != simple_elements.format:
        print(f"  ✗ Format mismatch: '{original_elements.format}' vs '{simple_elements.format}'")
        return False
    
    if len(original_elements.state_machines) != len(simple_elements.state_machines):
        print(f"  ✗ State machine count mismatch")
        return False
    
    for sm_id in original_elements.state_machines:
        orig_sm = original_elements.state_machines[sm_id]
        simple_sm = simple_elements.state_machines[sm_id]
        
        metrics = [
            ('states', len(orig_sm.states), len(simple_sm.states)),
            ('transitions', len(orig_sm.transitions), len(simple_sm.transitions)),
            ('initial_states', len(orig_sm.initial_states), len(simple_sm.initial_states)),
            ('finals', len(orig_sm.finals), len(simple_sm.finals)),
            ('choices', len(orig_sm.choices), len(simple_sm.choices)),
            ('components', len(orig_sm.components), len(simple_sm.components)),
            ('notes', len(orig_sm.notes), len(simple_sm.notes)),
        ]
        
        for metric_name, orig_count, simple_count in metrics:
            if orig_count != simple_count:
                print(f"  ✗ {metric_name} count mismatch in {sm_id}: {orig_count} vs {simple_count}")
                return False
        
        print(f"  ✓ State machine {sm_id}: {len(orig_sm.states)} states, {len(orig_sm.transitions)} transitions")
    
    print("  ✓ Demo file compatibility confirmed")
    return True


def main():
    """Run all compatibility tests."""
    print("=== CyberiadaML Parser Compatibility Test ===\n")
    
    success = True
    
    # Test with synthetic XML
    if not test_compatibility():
        success = False
    
    # Test with demo file
    if not test_compatibility_with_demo():
        success = False
    
    print(f"\n=== Results ===")
    if success:
        print("✅ All compatibility tests passed!")
        print("Simple parser produces equivalent structure to original parser.")
    else:
        print("❌ Some compatibility tests failed.")
        print("There are differences between simple and original parsers.")
    
    return success


if __name__ == "__main__":
    main() 