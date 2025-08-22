class EventLoop:
    events: list[str] = []
    called_events: list[str] = []
    current_event_idx = 0
    insert_event_idx = 0

    @staticmethod
    def add_event(event: str, is_called=False):
        """Добавляет событие в цикл событий."""
        EventLoop.insert_event_idx += 1
        EventLoop.events.insert(
            EventLoop.insert_event_idx,
            event
            )
        if is_called:
            EventLoop.called_events.append(event)

    @staticmethod
    def clear():
        EventLoop.current_event_idx = 0
        EventLoop.events.clear()
        EventLoop.called_events.clear()

    @staticmethod
    def get_event():
        # обнулять где-то надо
        if EventLoop.current_event_idx < len(EventLoop.events):
            event = EventLoop.events[EventLoop.current_event_idx]
            EventLoop.current_event_idx += 1
            EventLoop.insert_event_idx = EventLoop.current_event_idx
            return event
        return None