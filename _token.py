class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        return f"{self.type}({self.value})" if self.value else f"{self.type}"


class TokenType:
    def __init__(self, char, reply, grammer_item, func=None, op_lvl=0):
        self.char = char
        self.reply = reply
        self.grammer_item = grammer_item
        self.func = func
        self.lvl = op_lvl

    def __repr__(self):
        return self.reply


types = [
    TokenType("INT", "INT", "factor"),
    TokenType("FLOAT", "FLOAT", "factor"),
    TokenType("+", "PLUS", "op", "__add__", 4),
    TokenType("-", "MINUS", "op", "__sub__", 4),
    TokenType("*", "MUL", "op", "__mul__", 3),
    TokenType("/", "DIV", "op", "__div__", 3),
    TokenType("(", "LPAREN", "brac", 1),
    TokenType(")", "RPAREN", "brac", 1),
    TokenType("EOF", "EOF", "eof"),
    TokenType("^", "POW", "op", "__pow__", 2)
]

max_prio = 4

def get(grammer_item):
    return [i for i in types if i.grammer_item == grammer_item]


def get_chars_of(grammer_item):
    return {t.char: t for t in get(grammer_item)}


def get_replies_of(grammer_item):
    return {t.reply: t for t in get(grammer_item)}


def get_tokens_by_replies(*replies):
    return [t for t in types if t.reply in replies]


def get_types_from_chars(*chars):
    return [t for t in types if t.char in chars]


def get_eof_token(pos_start=None):
    return Token(get("eof")[0], pos_start=pos_start)


def get_token_by_priority(priority):
    return [t for t in types if t.lvl == priority]
