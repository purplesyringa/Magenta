class Event(set):
    def __init__(self, name):
        super()
        self.__name = name

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return f"Event{self.__name}"

    def subscribe(self, f):
        self.add(f)

    def unsubscribe(self, f):
        try:
            self.remove(f)
        except KeyError:
            pass