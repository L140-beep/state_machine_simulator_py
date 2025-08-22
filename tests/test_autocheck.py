import os
from state_machine_sim.cgml_signal import StateMachine, run_state_machine, StateMachineResult
from state_machine_sim.simple_parser import CGMLParser
from state_machine_sim.cgml_types import (
    CGMLComponent,
    CGMLState,
    CGMLTransition,
    CGMLStateMachine,
    CGMLInitialState,
    CGMLFinal,
    CGMLChoice
)
TEST_GRAPHML_PATH = os.path.join(os.path.dirname(__file__), "from_ide.graphml")


def check_reader(result: StateMachineResult, entry_signals: list[str], answer_signals: list[str], ignored_signals: list[str]) -> tuple[str, bool]:
    if result.timeout:
        return ('Машина состояний работает слишком долго!', False)

    answer_i = 0
    entry_i = 0
    # breakpoint()
    for signal in result.signals:
        if signal == 'noconditionTransition':
            continue
        is_ignored = False
        for ignored in ignored_signals:
            if signal.find(ignored) != -1:
                is_ignored = True
                break
        if is_ignored:
            continue
        if entry_i in range(len(entry_signals)) and signal == entry_signals[entry_i]:
            entry_i += 1
            continue
        if answer_i in range(len(answer_signals)) and signal == answer_signals[answer_i]:
            answer_i += 1
            continue
        return (f'Неправильное событие {signal}', False)
    if (answer_i != len(answer_signals)):
        return ('Неверное количество событий!', False)
    return ('', True)


def auto_test_reader(
    cgml_sm: CGMLStateMachine,
    sm_parameters: dict,
    entry_signals: list[str],
    answer_signals: list[str],
    ignored_signals: list[str],
    timeout: int = 10000
):
    sm = StateMachine(
        cgml_sm,
        sm_parameters=sm_parameters,
    )
    result = run_state_machine(sm, entry_signals, timeout)
    check_result = check_reader(result, [], answer_signals, ignored_signals)
    if check_result[1] is False:
        print(check_result[0])
        return False
    print('Машина состояний работает отлично!')
    return True

def test_reader():
    with open(TEST_GRAPHML_PATH, encoding="utf-8") as f:
        xml = f.read()
    parser = CGMLParser()
    cgml_state_machines = parser.parse_cgml(xml)
    assert cgml_state_machines.state_machines, "No state machines found!"
    list(cgml_state_machines.state_machines.values())[0]

    tests = [('АААБББАВС', ['impulseA', 'impulseA',
              'impulseA', 'impulseA'],)]

    for test in tests:
        auto_test_reader(
            list(cgml_state_machines.state_machines.values())[0], 
                        {'message': test[0]},
                        [], test[1], ['char_accepted', 'line_finished']
                        )


if __name__ == "__main__":
    test_reader()
