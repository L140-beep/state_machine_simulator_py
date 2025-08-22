import os
from bundle import StateMachine, run_state_machine, StateMachineResult
from bundle import CGMLParser
from bundle import (
    CGMLComponent,
    CGMLState,
    CGMLTransition,
    CGMLStateMachine,
    CGMLInitialState,
    CGMLFinal,
    CGMLChoice
)
TEST_GRAPHML_PATH = os.path.join(os.path.dirname(__file__), "from_ide.graphml")


def check_reader(result: StateMachineResult, answer_signals: list[str]) -> tuple[str, bool]:
    if result.timeout:
        return ('Машина состояний работает слишком долго!', False)

    if len(answer_signals) != len(result.called_signals):
        return ('Вызвано неверное количество событий!', False)

    for i in range(len(answer_signals)):
        if answer_signals[i] != result.called_signals[i]:
            return (f'Неверное событие {result.called_signals[i]}', False)
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
    check_result = check_reader(result, answer_signals)
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
              'impulseA', 'impulseA'], True), ('АААБББАВС', ['impulseA', 'impulseA',
                                                              'impulseA', 'impulseA', 'impulseA'], False)]

    for test in tests:
        result = auto_test_reader(
            list(
                cgml_state_machines.state_machines.values())[0],
            {'message': test[0]},
            [], test[1], ['char_accepted', 'line_finished']
        )
        assert result == test[2]


if __name__ == "__main__":
    test_reader()
