from _token import Token, get_chars_of, get as get_tt, get_types_from_replies, get_eof_token
from _constant import DIGITS
from _error import IllegalCharError, InvalidSyntaxError
from _node import NumberNode, BinOpNode, UnaryOpNode

class Lexer:
    def __init__(self, fn, text: str = ""):
        self.fn = fn
        self.text = text

        self.pos = Position(-1, 0, -1, fn, text)
        self.char_now = None

        self.advance()

    def advance(self):
        self.pos.advance(self.char_now)
        self.char_now = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.char_now is not None:
            if self.char_now in " \t":  # skip spaces and tabs
                self.advance()
            elif self.char_now in DIGITS:
                tokens.append(self.make_number())
            elif self.char_now in get_chars_of("op"):  # operators e.g. + - * /
                tokens.append(Token(get_chars_of("op")[self.char_now], pos_start=self.pos))
                self.advance()
            elif self.char_now in get_chars_of("brac"):  # brackets e.g. ( )
                tokens.append(Token(get_chars_of("brac")[self.char_now], pos_start=self.pos))
                self.advance()
            else:  # Illegal Character
                pos_start = self.pos.copy()
                char = self.char_now
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}' is not implemented.")

        tokens.append(get_eof_token(self.pos.copy()))
        return tokens, None  # None for no error

    def make_number(self):
        number_str = ""
        has_dot = False
        pos_start = self.pos.copy()

        while self.char_now is not None and self.char_now in DIGITS + ".":
            if self.char_now == ".":
                if has_dot: break
                number_str += "."
                has_dot = True
            else:
                number_str += self.char_now

            self.advance()

        if has_dot:
            return Token(get_chars_of("factor")["FLOAT"], float(number_str), pos_start, self.pos)
        else:
            return Token(get_chars_of("factor")["INT"], int(number_str), pos_start, self.pos)


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, char_now=None):
        self.idx += 1
        self.col += 1
        if char_now == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1

        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.tok_now = self.tokens[self.tok_idx]
        return self.tok_now

    def parse(self):
        res = self.expr()
        if not res.error and self.tok_now.type != get_eof_token().type:
            return res.failure(InvalidSyntaxError(self.tok_now.pos_start, self.tok_now.pos_end, f"Expected {get_tt('op')}"))
        return res

    # Nodes building
    def bin_op_(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.tok_now.type in get_types_from_replies(*ops):
            op_tok = self.tok_now
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)  # set it back to left to allow chained ops of same types

        return res.success(left)

    def factor(self):
        res = ParseResult()
        tok = self.tok_now

        if tok.type in get_types_from_replies("PLUS", "MINUS"):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in get_types_from_replies("LPAREN"):
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.tok_now.type in get_types_from_replies("RPAREN"):
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.tok_now.pos_start, self.tok_now.pos_end, f"Expected {get_types_from_replies('RPAREN')}"))


        elif tok.type in get_tt("factor"):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, f"Expected {get_tt('factor')}"))

    def term(self):
        return self.bin_op_(self.factor, ["MUL", "DIV"])

    def expr(self):
        return self.bin_op_(self.term, ["PLUS", "MINUS"])


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


def run(fn, text):
    tokens, error = Lexer(fn, text).make_tokens()
    if error: return None, error

    ast = Parser(tokens).parse()
    return ast.node, ast.error
