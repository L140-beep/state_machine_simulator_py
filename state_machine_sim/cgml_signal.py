from dataclasses import dataclass
from .qhsm import Q_SUPER, QHsm, Q_UNHANDLED, Q_HANDLED, Q_TRAN, SIMPLE_DISPATCH
from .cgml_types import (
    CGMLComponent,
    CGMLState,
    CGMLTransition,
    CGMLStateMachine,
    CGMLInitialState,
    CGMLFinal,
    CGMLChoice
)

from .event_loop import EventLoop
from . import components
from functools import partial
from typing import Callable
from abc import ABC
import time
import re
from .simple_parser import CGMLParser

@dataclass
class Component:
    id: str
    type: str
    obj: object


@dataclass
class Action:
    component: str
    action: str
    args: list[str]

@dataclass
class Signal:
    condition: str
    action: str
    status: Callable[..., int]

    def __str__(self):
        cond = f"[{self.condition}]" if self.condition else ""
        return f"Signal{cond}/ {self.action}"  # статус не выводим, он всегда функция

@dataclass
class ChoiceSignal(Signal):
    target: str

class StateMachine:
    def __init__(
        self,
        sm: CGMLStateMachine,
        sm_parameters: dict
    ):
        self.components = init_components(sm.components, sm_parameters)
        self.inital_states = init_initial_states(
            self, sm.initial_states, sm.transitions)
        self.final_states = init_final_states(self, sm.finals)
        self.choice_states = init_choice_states(self, sm.choices, sm.transitions)
        self.qhsm = QHsm()
        self.states = init_states(
            self.qhsm,
            self,
            self.inital_states,
            self.final_states,
            self.choice_states,
            sm.states,
            sm.transitions
        )
        post_init_choice_states(self, self.choice_states, self.states, self.inital_states, self.final_states)
        self.initial = find_highest_level_initial_state(self.inital_states)
        if self.initial is None:
            raise ValueError("No initial state found in the state machine.")
        self.qhsm.post_init(self.initial.execute_signal)

    def intepreter_condition(self, condition: str) -> bool:
        """
        Интерпретирует простые условные выражения вида:
        timer.difference > 0
        12 > 0
        3 == timer.difference
        timer.difference == timer.difference
        """
        if not condition or condition.strip() == "":
            return True
        # Поддержка: <, >, ==, !=, <=, >=
        import operator
        ops = {
            '>': operator.gt,
            '<': operator.lt,
            '==': operator.eq,
            '!=': operator.ne,
            '>=': operator.ge,
            '<=': operator.le,
        }
        # Поиск оператора
        for op_str in sorted(ops.keys(), key=len, reverse=True):
            if op_str in condition:
                left, right = condition.split(op_str, 1)
                left = left.strip()
                right = right.strip()
                op_func = ops[op_str]
                # Попытка привести к числу

                def resolve(val):
                    try:
                        return float(val) if '.' in val else int(val)
                    except ValueError:
                        # Попытка получить значение из компонента
                        if '.' in val:
                            comp_name, attr = val.split('.', 1)
                            comp = self.components.get(comp_name)
                            if comp and hasattr(comp.obj, attr):
                                return getattr(comp.obj, attr)
                        return val
                left_val = resolve(left)
                right_val = resolve(right)
                return op_func(left_val, right_val)
        # Если не найден оператор, просто сравниваем на True
        return bool(condition)

    def __parse_action(self, actions: str) -> list[Action]:
        """
        Парсит строку или строки вида
        'компонент.действие(арг1, ...)'\n'компонент2.действие2(...)'\n...
        в список объектов Action.
        """
        result = []
        for action in actions.strip().splitlines():
            action = action.strip()
            if not action:
                continue
            pattern = r'^(?P<component>\w+)\.(?P<method>\w+)\((?P<args>.*)\)$'
            match = re.match(pattern, action)
            if not match:
                raise ValueError(f"Invalid action format: {action}")
            component = match.group('component')
            method = match.group('method')
            args_str = match.group('args').strip()
            if args_str:
                args = [arg.strip() for arg in re.split(r',\s*', args_str)]
            else:
                args = []
            result.append(Action(
                component=component, action=method, args=args))
        return result

    def intepreter_action(self, action: str):
        # если не компонентная структура кода, то просто делаем eval здесь
        actions_obj = self.__parse_action(action)
        for action_obj in actions_obj:
            component = self.components.get(action_obj.component)
            if component:
                method = getattr(component.obj, action_obj.action, None)
                if callable(method):
                    method(*action_obj.args)
                else:
                    raise ValueError(
                        f"Action {action_obj.action} not \
                            callable on {component.type}")


class Element(ABC):
    def execute_signal(self, qhsm: QHsm, signal_name: str) -> int:
        raise NotImplementedError("Subclasses should implement this method.")


class InitialState(Element):
    def __init__(
        self,
        sm: StateMachine,
        target: str,
        parent: str | None = None
    ):
        self.sm = sm
        self.target = target
        self.parent = parent

    def execute_signal(self, qhsm: QHsm, signal_name: str) -> int:
        if signal_name == 'entry':
            EventLoop.add_event('noconditionTransition')
            return Q_HANDLED()
        return Q_TRAN(qhsm, self.sm.states[self.target].execute_signal)

class ChoiceState(Element):
    def __init__(self, sm: StateMachine, parent: str | None = None):
        self.sm = sm
        self.parent = parent
        self.conditions: list[ChoiceSignal] = []

    def execute_signal(self, qhsm: QHsm, signal_name: str) -> int:
        if signal_name == 'entry':
            EventLoop.add_event('noconditionTransition')
            return Q_HANDLED()
        else_signal = None
        for signal in self.conditions:
            signal_condition = signal.condition
            signal_action = signal.action
            if (signal_condition == "else"):
                else_signal = signal
                continue
            if self.sm.intepreter_condition(signal_condition):
                self.sm.intepreter_action(signal_action)
                status = signal.status()
                return status
        if else_signal is not None:
            self.sm.intepreter_action(else_signal.action)
            status = else_signal.status()
            return status
        return Q_UNHANDLED()

class FinalState(Element):
    def __init__(self, sm: StateMachine, parent: str | None = None):
        self.sm = sm
        self.parent = parent

    def execute_signal(self, qhsm: QHsm, signal_name: str) -> int:
        if signal_name == 'entry':
            EventLoop.add_event('break')
            return Q_HANDLED()
        # Final state does not handle any other signals
        return Q_UNHANDLED()


class State(Element):
    def __init__(
        self,
        sm: StateMachine,
        signals: dict[str, list[Signal]],
        parent: str | None = None
    ):
        self.signals = signals
        self.parent = parent
        self.sm = sm

    def __str__(self):
        signals_str = []
        for event, siglist in self.signals.items():
            for sig in siglist:
                signals_str.append(f"  {event}: {sig}")
        parent_str = f", parent={self.parent}" if self.parent else ""
        return f"State(signals=[\n" + "\n".join(signals_str) + f"\n]{parent_str})"

    def execute_signal(self, qhsm: QHsm, signal_name: str) -> int:
        signals = self.signals.get(signal_name)
        if signals:
            else_signal = None
            for signal in signals:
                if signal.condition == "else":
                    else_signal = signal
                    continue
                if self.sm.intepreter_condition(signal.condition):
                    self.sm.intepreter_action(signal.action)
                    status = signal.status()
                    return status
            if else_signal is not None:
                self.sm.intepreter_action(else_signal.action)
                status = else_signal.status()
                return status
        if self.parent:
            return Q_SUPER(qhsm, self.sm.states[self.parent].execute_signal)
        return Q_UNHANDLED()


def parse_actions_block(actions: str) -> dict[str, list[Signal]]:
    """Парсит блок событий и действий из строки actions. Поддерживает несколько условий для одного события."""
    signals: dict[str, list[Signal]] = {}
    if not actions:
        return signals
    blocks = actions.strip().split('\n\n')
    for block in blocks:
        lines = [line for line in block.strip().splitlines() if line.strip()]
        if not lines:
            continue
        header = lines[0]
        body = lines[1:]
        # событие[условие]/
        if '/' in header:
            event_part, _ = header.split('/', 1)
            if '[' in event_part and ']' in event_part:
                event_name = event_part.split('[')[0].strip()
                condition = event_part.split('[')[1].split(']')[0].strip()
            else:
                event_name = event_part.strip()
                condition = ""
        else:
            event_name = header.strip()
            condition = ""
        action = '\n'.join(body)
        signal = Signal(
            condition=condition, action=action, status=Q_HANDLED)
        if event_name not in signals:
            signals[event_name] = []
        signals[event_name].append(signal)
    return signals

def init_choice_states(
    sm: StateMachine,
    cgml_choice_states: dict[str, CGMLChoice],
    cgml_transitions: dict[str, CGMLTransition]
) -> dict[str, ChoiceState]:
    """Initialize choice states from CGMLChoice data. Для каждого состояния выбора ищет все исходящие переходы и парсит их в список Signal."""
    initialized_states: dict[str, ChoiceState] = {}
    for state_id, cgml_choice in cgml_choice_states.items():
        choice_state = ChoiceState(sm, parent=cgml_choice.parent)
        conditions: list[ChoiceSignal] = []
        for trans in cgml_transitions.values():
            if trans.source != state_id:
                continue
            trigger = trans.actions
            condition = ""
            action = ""
            if '/' in trigger:
                cond_part, action_part = trigger.split('/', 1)
                if '[' in cond_part and ']' in cond_part:
                    condition = cond_part.split('[')[1].split(']')[0].strip()
                else:
                    condition = ""
                action = action_part.strip()
            else:
                condition = ""
                action = ""
            signal = ChoiceSignal(
                condition=condition,
                action=action,
                status=Q_HANDLED,
                target=trans.target
            )
            conditions.append(signal)
        choice_state.conditions = conditions
        initialized_states[state_id] = choice_state
    return initialized_states

def post_init_choice_states(
    sm: StateMachine,
    choice_states: dict[str, ChoiceState],
    states: dict[str, State],
    initials: dict[str, 'InitialState'],
    finals: dict[str, FinalState]
):
    """
    Для каждого ChoiceState обновляет status у Signal в conditions на partial(Q_TRAN, qhsm, target_func),
    где target_func — execute_signal целевого состояния (State, InitialState, FinalState, ChoiceState).
    """
    qhsm = sm.qhsm
    for choice_state in choice_states.values():
        for signal in choice_state.conditions:
            # Определяем целевое состояние по target
            target_func = None
            if signal.target in states:
                target_func = states[signal.target].execute_signal
            elif signal.target in initials:
                target_func = initials[signal.target].execute_signal
            elif signal.target in finals:
                target_func = finals[signal.target].execute_signal
            elif signal.target in choice_states:
                target_func = choice_states[signal.target].execute_signal
            else:
                raise ValueError(f"Target state '{signal.target}' not found for choice transition.")
            signal.status = partial(Q_TRAN, qhsm, target_func)

def init_states(
        qhsm: QHsm,
        sm: 'StateMachine',
        initials: dict[str, 'InitialState'],
        finals: dict[str, FinalState],
        choices: dict[str, ChoiceState],
        cgml_states: dict[str, CGMLState],
        cgml_transition: dict[str, CGMLTransition],
) -> dict[str, 'State']:
    """Initialize states from CGMLState data."""
    initialized_states: dict[str, 'State'] = {}
    for state_id, cgml_state in cgml_states.items():
        signals = parse_actions_block(cgml_state.actions)
        initialized_states[state_id] = State(sm, signals, cgml_state.parent)
    # transitions
    for trans in cgml_transition.values():
        trigger = trans.actions
        condition = ""
        action = ""
        if '/' in trigger:
            event_part, action_part = trigger.split('/', 1)
            if '[' in event_part and ']' in event_part:
                event_name = event_part.split('[')[0].strip()
                condition = event_part.split('[')[1].split(']')[0].strip()
            else:
                event_name = event_part.strip()
                condition = ""
            action = action_part.strip()
        else:
            event_name = trigger.strip()
            condition = ""
            action = ""
        if trans.source in initialized_states:
            target = initialized_states.get(trans.target) or initials.get(
                trans.target) or finals.get(trans.target) or choices.get(trans.target)
            if target is None:
                continue
            target_func = target.execute_signal
            status_func = partial(Q_TRAN, qhsm, target_func)
            signal = Signal(
                condition=condition,
                action=action,
                status=status_func
            )
            if event_name not in initialized_states[trans.source].signals:
                initialized_states[trans.source].signals[event_name] = []
            initialized_states[trans.source].signals[event_name].append(signal)
    return initialized_states

def init_final_states(sm: StateMachine, cgml_final_states: dict[str, CGMLFinal]):
    """Initialize final states from CGMLFinalState data."""
    initialized_states: dict[str, FinalState] = {}
    for state_id, cgml_final in cgml_final_states.items():
        initialized_states[state_id] = FinalState(
            sm,  # StateMachine not needed here, but can be set later
            parent=cgml_final.parent
        )
    return initialized_states

def init_components(
    cgml_components: dict[str, CGMLComponent],
    sm_parameters: dict
) -> dict[str, Component]:
    """Initialize components from CGMLComponent data."""
    initialized_components = {}
    for cgml_comp in cgml_components.values():
        components_obj = getattr(components, cgml_comp.type)
        if components_obj:
            # print(cgml_comp.parameters)
            component_instance = components_obj(cgml_comp.id)
            component_instance.get_sm_options(sm_parameters)
            initialized_components[cgml_comp.id] = Component(
                id=cgml_comp.id,
                type=cgml_comp.type,
                obj=component_instance
            )
        else:
            raise ValueError(f"Component type {cgml_comp.type} not found.")
    return initialized_components


def init_initial_states(
    sm: 'StateMachine',
    cgml_initial_states: dict[str, CGMLInitialState],
    cgml_transitions: dict[str, CGMLTransition]
) -> dict[str, 'InitialState']:
    """Initialize initial states from CGMLInitialState data."""
    initial_states = {}
    for state_id, initial_state in cgml_initial_states.items():
        trans = find_transitions_for_state(state_id, cgml_transitions)
        if len(trans) != 1:
            continue
        initial_states[state_id] = InitialState(
            sm,
            target=trans[0].target,
            parent=initial_state.parent
        )
    return initial_states


def find_transitions_for_state(
    state_id: str,
    cgml_transitions: dict[str, CGMLTransition]
) -> list[CGMLTransition]:
    """Возвращает список переходов, у которых source == state_id."""
    return [
        trans for trans in cgml_transitions.values()
        if trans.source == state_id
    ]

def find_highest_level_initial_state(
    initial_states: dict[str, 'InitialState']
) -> 'InitialState | None':
    """Находит начальное состояние с самым высоким уровнем."""
    for initial_state in initial_states.values():
        if initial_state.parent is None:
            return initial_state

    return None


class StateMachineResult:
    def __init__(self, timeout: bool, signals: list[str], called_signals: list[str], components: dict[str, Component]):
        self.timeout = timeout  # Закончилась ли МС по таймауту
        self.signals = signals  # Сигналы, которые были вызваны (с учетом сигналов по умолчанию)
        self.called_signals = called_signals  # Все, что вызвано пользователем вручную
        self.components = components  # компоненты и их состояния

def run_state_machine(sm: StateMachine,
                      signals: list[str], timeout_sec: float = 10.0) -> StateMachineResult:
    """
    Запускает машину состояний на основе CGML XML и списка сигналов.
    Возвращает StateMachineResult: был ли выход по таймауту, список сигналов, компоненты.
    """
    EventLoop.clear()
    qhsm = sm.qhsm
    qhsm.current_(qhsm, 'entry')

    for event in signals:
        EventLoop.add_event(event)

    timeout = False
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout_sec:
            timeout = True
            break
        event = EventLoop.get_event()
        if event is None or event == 'break':
            break
        SIMPLE_DISPATCH(qhsm, event)
    return StateMachineResult(timeout, EventLoop.events, EventLoop.called_events, sm.components)
