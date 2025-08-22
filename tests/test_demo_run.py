"""
Тест запуска машины состояний из файла CyberiadaFormat-Blinker.graphml.
"""
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../simple_parser')))
from state_machine_sim.cgml_signal import run_state_machine

GRAPHML_PATH = "tests/CyberiadaFormat-Blinker.graphml"

if __name__ == "__main__":
    # Читаем XML-файл
    with open(GRAPHML_PATH, "r", encoding="utf-8") as f:
        xml_string = f.read()

    # Сигналы для теста: три раза timer1.timeout
    signals = [
        "Timer1.timeout",
        "Timer1.timeout",
        "Timer1.timeout"
    ]

    run_state_machine(xml_string, signals)
    print("State machine demo test completed.")
