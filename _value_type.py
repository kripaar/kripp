from _error import RTError

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, start=None, end=None):
        self.pos_start = start
        self.pos_end = end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def __div__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, "Divided by zero", self.context)
            return Number(self.value / other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)
