

class Handler:
    active = True

    def __init__(self, handling=None):
        self._handling = dict() if handling is None else dict(handling)

    def handle(self, event_type, event_props):
        if self.active and event_type in self._handling and self._handling[event_type]:
            for condition, *funcs in self._handling[event_type]:
                if condition is True or condition.items() <= event_props.items():
                    for func in funcs:
                        response = func(**event_props)
                        #calling returnes something? stop handling!
                        if response is not None:
                            return response

    def get_handling(self):
        return self._handling

    def update(self, other):
        if isinstance(other, Handler):
            self._handling.update(other.get_handling())
        elif isinstance(other, dict):
            self._handling.update(other)

    def __and__(self, other):
        new = Handler(self._handling)
        new.update(other)
        return new


class HandlersHolder:
    def __init__(self):
        super().__init__()
        self.handlers = []

    def attach_handler(self, handler):
        self.handlers.append(handler)

    def detach_handler(self, handler):
        self.handlers.remove(handler)

    def attach_handler_after(self, reference_handler, handler):
        i = self.handlers.index(reference_handler)
        self.handlers.insert(i + 1, handler)

    def attach_handler_before(self, reference_handler, handler):
        i = self.handlers.index(reference_handler)
        self.handlers.insert(i, handler)

    def handle(self, event_type, event_props):
        for handler in self.handlers:
            response = handler.handle(event_type, event_props)
            # calling returnes True? stop handling for every handler!
            if response is True:
                break

    def all_handlers_before(self, reference_handler):
        i = self.handlers.index(reference_handler)
        return self.handlers[:i]

    def all_handlers_after(self, reference_handler):
        i = self.handlers.index(reference_handler)
        return self.handlers[i:]
