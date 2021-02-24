class Error:
    def __init__(self, pos_start, pos_end, err_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.err_name = err_name
        self.details = details

    def as_string(self):
        return f"In file {self.pos_start.fn}, line {self.pos_start.ln + 1}\n" \
               f"{self.err_name}: {self.details}\n" \
               f"{string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)}"


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)


def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')