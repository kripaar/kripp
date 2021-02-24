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
    def __init__(self, char, reply, grammer_item):
        self.char = char
        self.reply = reply
        self.grammer_item = grammer_item

    def __repr__(self):
        return self.reply


types = [
    TokenType("INT", "INT", "factor"),
    TokenType("FLOAT", "FLOAT", "factor"),
    TokenType("+", "PLUS", "op"),
    TokenType("-", "MINUS", "op"),
    TokenType("*", "MUL", "op"),
    TokenType("/", "DIV", "op"),
    TokenType("(", "LPAREN", "brac"),
    TokenType(")", "RPAREN", "brac"),
    TokenType("EOF", "EOF", "eof"),
]


def get(grammer_item):
    return [i for i in types if i.grammer_item == grammer_item]


def get_chars_of(grammer_item):
    return {t.char: t for t in get(grammer_item)}


def get_replies_of(grammer_item):
    return {t.reply: t for t in get(grammer_item)}


def get_types_from_replies(*replies):
    return [t for t in types if t.reply in replies]


def get_types_from_chars(*chars):
    return [t for t in types if t.char in chars]

def get_eof_token(pos_start=None):
    return Token(get("eof")[0], pos_start=pos_start)
