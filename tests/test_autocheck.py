import os
from state_machine_sim.cgml_signal import StateMachine, run_state_machine
from state_machine_sim.simple_parser import CGMLParser

TEST_GRAPHML_PATH = os.path.join(os.path.dirname(__file__), "from_ide.graphml")


def test_print_and_run_state_machine():
    with open(TEST_GRAPHML_PATH, encoding="utf-8") as f:
        xml = f.read()
    parser = CGMLParser()
    cgml_state_machines = parser.parse_cgml(xml)
    assert cgml_state_machines.state_machines, "No state machines found!"
    sm = StateMachine(
        list(cgml_state_machines.state_machines.values())[0],
        sm_parameters={"message": "АААА"}
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

    # Запуск МС с логами
    print("\n--- RUN STATE MACHINE ---")
    signals = []
    result = run_state_machine(xml, signals, {"message": "АААБББВВВ"}, 1000)
    print(f"Timeout: {result.timeout}")
    print(f"Signals: {result.signals}")
    print("Components after run:")
    for comp_id, comp in result.components.items():
        print(f"  {comp_id}: {comp}")


if __name__ == "__main__":
    test_print_and_run_state_machine()
