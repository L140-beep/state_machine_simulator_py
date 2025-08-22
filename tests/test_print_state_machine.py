import os
import sys
from state_machine_sim.simple_parser import CGMLParser
from state_machine_sim.cgml_signal import StateMachine
from state_machine_sim.cgml_types import CGMLStateMachine


GRAPHML_PATH = "tests/CyberiadaFormat-Blinker.graphml"


def main():
    # Читаем XML-файл
    with open(GRAPHML_PATH, "r", encoding="utf-8") as f:
        xml_string = f.read()
    # Парсим CGML
    parser = CGMLParser()
    elements = parser.parse_cgml(xml_string)
    sm_data: CGMLStateMachine = elements.state_machines[next(
        iter(elements.state_machines))]
    # Инициализируем StateMachine
    sm = StateMachine(sm_data)
    # Выводим все состояния и их сигналы
    print("States:")
    for state_id, state in sm.states.items():
        print(f"State: {state_id}")
        for signal_name, signal in state.signals.items():
            print(f"  Signal: {signal_name}")
            print(f"    Condition: {signal.condition}")
            print(f"    Action: {signal.action}")
            print(f"    Status: {signal.status}")


if __name__ == "__main__":
    main()
