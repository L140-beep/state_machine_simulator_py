import os
from state_machine_sim.cgml_signal import StateMachine
from state_machine_sim.simple_parser import CGMLParser

TEST_GRAPHML_PATH = os.path.join(os.path.dirname(__file__), "test_reader.graphml")

def test_print_state_machine():
    with open(TEST_GRAPHML_PATH, encoding="utf-8") as f:
        xml = f.read()
    parser = CGMLParser()
    cgml_state_machines = parser.parse_cgml(xml)
    assert cgml_state_machines.state_machines, "No state machines found!"
    sm = StateMachine(
        list(cgml_state_machines.state_machines.values())[0],
        sm_parameters={
            'message': 'aaaa'
        }
    )
    print("States:")
    for state_id, state in sm.states.items():
        print(f"  {state_id}: {state}")
    print("Initial states:")
    for init_id, init in sm.inital_states.items():
        print(f"  {init_id}: {init}")
    print("Components:")
    for comp_id, comp in sm.components.items():
        print(f"  {comp_id}: {comp}")

if __name__ == "__main__":
    test_print_state_machine()
