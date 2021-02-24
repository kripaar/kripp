class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f"{self.tok}"


class BinOpNode:
    def __init__(self, lnode, op_tok, rnode):
        self.lnode = lnode
        self.op_tok = op_tok
        self.rnode = rnode

    def __repr__(self):
        return f"({self.lnode}, {self.op_tok}, {self.rnode})"


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"
