"""
Тест запуска машины состояний из файла TestImpulse.graphml с пустым списком сигналов.
"""
from state_machine_sim.cgml_signal import run_state_machine

GRAPHML_PATH = "tests/TestImpulse.graphml"

if __name__ == "__main__":
    # Читаем XML-файл
    with open(GRAPHML_PATH, "r", encoding="utf-8") as f:
        xml_string = f.read()

    # Пустой список сигналов
    signals = []

    run_state_machine(xml_string, signals, {})
    print("State machine impulse test completed.")
