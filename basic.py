from _token import Token, get_chars_of, get as get_tgi, get_tokens_by_replies as get_ttr, get_eof_token, get_token_by_priority as get_ttp, max_prio
from _constant import DIGITS
from _error import IllegalCharError, InvalidSyntaxError, RTError
from _node import NumberNode, BinOpNode, UnaryOpNode
from _value_type import Number
from _context import Context

##############################################
# Lexer: Inidcates keywords, convert to tokens
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
            elif self.char_now in get_chars_of("op"):  # operators e.g. + - * / ^
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

####################################################################
# Parser: Accept tokens, add brackets to indicate order of operation
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
        res = self.expr(max_prio)
        if not res.error and self.tok_now.type != get_eof_token().type:
            return res.failure(InvalidSyntaxError(self.tok_now.pos_start, self.tok_now.pos_end, f"Expected {get_tgi('op')}"))
        return res

    def expr(self, prio):
        res = ParseResult()

        if prio >= 2:  # Bin Op
            left = res.register(self.expr(prio-1))
            if res.error: return res

            while self.tok_now.type in get_ttp(prio):
                op_tok = self.tok_now
                res.register(self.advance())
                right = res.register(self.expr(prio-1))
                if res.error: return res
                left = BinOpNode(left, op_tok, right)  # set it back to left to allow chained ops of same types

            return res.success(left)

        elif prio == 1:  # Paren
            tok = self.tok_now
            if tok.type in get_ttr("LPAREN"):
                res.register(self.advance())
                inside = res.register(self.expr(max_prio))
                if res.error: return res
                if self.tok_now.type in get_ttr("RPAREN"):
                    res.register(self.advance())
                    return res.success(inside)
                else:
                    return res.failure(InvalidSyntaxError(self.tok_now.pos_start, self.tok_now.pos_end, f"Expected {get_ttr('RPAREN')}"))
            else:
                return res.register(self.expr(0))

        elif prio == 0:  # Number / Directed number
            tok = self.tok_now
            if tok.type in get_ttp(max_prio):
                res.register(self.advance())
                factor = res.register(self.expr(0))
                if res.error: return res
                return res.success(UnaryOpNode(tok, factor))
            elif tok.type in get_tgi("factor"):
                res.register(self.advance())
                return res.success(NumberNode(tok))
            return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, f"Expected {get_tgi('factor')}"))


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


########################################################################################
# Interpreter: Accept correctly ordered tokens, perform the actions instructed by tokens
class Interpreter:
    def visit(self, node, context):
        method_name = f"_visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"Visit method _visit_{type(node).__name__} undefined")

    def _visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))  # 100% success as no opertion is done

    def _visit_BinOpNode(self, node, context):
        res = RuntimeResult()

        l = res.register(self.visit(node.lnode, context))
        if res.error: return res
        r = res.register(self.visit(node.rnode, context))
        if res.error: return res

        func = getattr(l, node.op_tok.type.func)
        result, error = func(r)
        return res.failure(error) if error else res.success(result.set_pos(node.pos_start, node.pos_end))

    def _visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None
        if node.op_tok.type in get_ttr("MINUS"): number, error = number * Number(-1)
        return res.failure(error) if error else res.success(number.set_pos(node.pos_start, node.pos_end))


class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


def run(fn, text):
    # Text -> List of tokens
    tokens, error = Lexer(fn, text).make_tokens()
    if error: return None, error

    # List of tokens -> Ordered list of tokens
    ast = Parser(tokens).parse()
    if ast.error: return None, ast.error

    # Ordered list of tokens -> Result
    context = Context("<program>")
    result = Interpreter().visit(ast.node, context)

    return result.value, result.error
