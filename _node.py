class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class BinOpNode:
    def __init__(self, lnode, op_tok, rnode):
        self.lnode = lnode
        self.op_tok = op_tok
        self.rnode = rnode

        self.pos_start = self.lnode.pos_start
        self.pos_end = self.rnode.pos_end

    def __repr__(self):
        return f"({self.lnode}, {self.op_tok}, {self.rnode})"


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"
