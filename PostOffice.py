class PostOffice:
    def __init__(self):
        self._eventListeners = {}
        self._mail_map = {}

    def register_event_listener(self, event_name, event_listener):
        if self._eventListeners.get(event_name) is None:  # New Event
            self._eventListeners[event_name] = [event_listener]
        else:  # Add listener to an existing event
            self._eventListeners[event_name].append(event_listener)

    def delete_event_listener(self, event_name):
        del (self._eventListeners[event_name])

    def trigger_event(self, *args):
        event_name = args[0]
        for listener in self._eventListeners[event_name]:
            listener(*args)
