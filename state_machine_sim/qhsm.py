from typing import Callable, Optional

# qhsm.py

Q_MAX_DEPTH = 8

# Signals as string names
QEP_EMPTY_SIG_ = "QEP_EMPTY_SIG"
Q_ENTRY_SIG = "entry"
Q_EXIT_SIG = "exit"
Q_INIT_SIG = "Q_INIT_SIG"
Q_VERTEX_SIG = "Q_VERTEX_SIG"
Q_USER_SIG = "Q_USER_SIG"

# Return codes
Q_RET_SUPER = 0
Q_RET_UNHANDLED = 1
Q_RET_HANDLED = 2
Q_RET_IGNORED = 3
Q_RET_TRAN = 4


class QHsm:
    def __init__(self, initial: Optional[Callable[["QHsm", str], int]] = None):
        if initial is None:
            return
        self.current_: Callable[["QHsm", str], int] = initial
        self.effective_: Callable[["QHsm", str], int] = initial
        self.target_: Optional[Callable[["QHsm", str], int]] = None

    def post_init(self, initial: Callable[["QHsm", str], int]):
        self.current_: Callable[["QHsm", str], int] = initial
        self.effective_: Callable[["QHsm", str], int] = initial
        self.target_: Optional[Callable[["QHsm", str], int]] = None


def QHsm_top(me: "QHsm", event: str) -> int:
    return Q_RET_IGNORED


standard_events = [
    QEP_EMPTY_SIG_,
    Q_ENTRY_SIG,
    Q_EXIT_SIG,
    Q_INIT_SIG,
]


def do_transition(me: QHsm) -> None:
    source = me.current_
    effective = me.effective_
    target = me.target_

    while source != effective:
        source(me, standard_events[2])  # Q_EXIT_SIG
        source(me, standard_events[0])  # QEP_EMPTY_SIG
        source = me.effective_

    if source == target:
        source(me, standard_events[2])  # Q_EXIT_SIG
        target(me, standard_events[1])  # Q_ENTRY_SIG
        me.current_ = target
        me.effective_ = target
        me.target_ = None
        return

    path: list[Optional[Callable[[QHsm, str], int]]] = [None] * Q_MAX_DEPTH
    top = 0
    lca = -1

    path[0] = target
    while target != QHsm_top:
        if target is not None:
            target(me, standard_events[0])  # QEP_EMPTY_SIG
            target = me.effective_
            top += 1
            path[top] = target
            if target == source:
                lca = top
                break
        else:
            break

    while lca == -1:
        source(me, standard_events[2])  # Q_EXIT_SIG
        source(me, standard_events[0])  # QEP_EMPTY_SIG
        source = me.effective_
        for i in range(top + 1):
            if path[i] == source:
                lca = i
                break

    target = path[lca]
    if lca == 0 and target is not None:
        target(me, standard_events[1])  # Q_ENTRY_SIG
    for i in range(lca - 1, -1, -1):
        target = path[i]
        if target is not None:
            target(me, standard_events[1])  # Q_ENTRY_SIG

    me.current_ = target
    me.effective_ = target
    me.target_ = None


def QHsm_ctor(me: QHsm, initial: Callable[[QHsm, str], int]) -> None:
    me.current_ = initial
    me.effective_ = initial
    me.target_ = None


def QMsm_init(me: QHsm, event: str) -> None:
    me.current_(me, event)
    me.effective_ = QHsm_top
    do_transition(me)


def QMsm_dispatch(me: QHsm, event: str) -> int:
    result = me.current_(me, event)
    while result == Q_RET_SUPER:
        result = me.effective_(me, event)
    if result == Q_RET_TRAN:
        do_transition(me)
    elif result in (Q_RET_HANDLED, Q_RET_UNHANDLED, Q_RET_IGNORED):
        me.effective_ = me.current_
    return result


def QMsm_simple_dispatch(me: QHsm, signal: str) -> int:
    return QMsm_dispatch(me, signal)

# --- Macro equivalents from qhsm.hpp as Python functions ---


def Q_UNHANDLED() -> int:
    return Q_RET_UNHANDLED


def Q_HANDLED() -> int:
    return Q_RET_HANDLED


def Q_TRAN(me: QHsm, target: Callable[[QHsm, str], int]) -> int:
    me.target_ = target
    return Q_RET_TRAN


def Q_SUPER(me: QHsm, super_handler: Callable[[QHsm, str], int]) -> int:
    me.effective_ = super_handler
    return Q_RET_SUPER


def QMSM_INIT(me: QHsm, event: str) -> None:
    QMsm_init(me, event)


def QMSM_DISPATCH(me: QHsm, event: str) -> int:
    return QMsm_dispatch(me, event)


def SIMPLE_DISPATCH(me: QHsm, sig: str) -> None:
    QMsm_dispatch(me, sig)


def SIGNAL_DISPATCH(me: QHsm, sig: str) -> None:
    QMsm_dispatch(me, sig)


def PASS_EVENT_TO(obj: QHsm, e: str) -> None:
    QMsm_dispatch(obj, e)
