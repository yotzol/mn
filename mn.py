import re
import sys

DECL_EXPR   = re.compile(r"^\s*(const|let|var)\s+[^\s]+\s*(?P<colon>:\s*[^\s]+)?\s*(?P<equal>=\s*.*)?;\s*$")
ASSIGN_EXPR = re.compile(r"^\s*[^\s]+\s*(?P<equal>=)\s*.*;\s*$")
OBJ_EXPR    = re.compile(r"^\s*(\^\+\])\s*(?P<colon>:)\s*'.*',\s*$")

def align(code: str):
    lines = code.split("\n")

    max_colon_col    =  0
    max_equal_col    =  0

    last_decl_line   = -1
    last_assign_line = -1
    last_record_line = -1

    selected_lines: list[int] = []

    for i, line in enumerate(lines):
        m = DECL_EXPR.match(line)
        if m:
            if m.group("colon"):
                colon_col     = m.start("colon")
                max_colon_col = max(max_colon_col, colon_col)
                selected_lines.append(i)

            if m.group("equal"):
                equal_col     = m.start("equal")
                max_equal_col = max(max_equal_col, equal_col)
                selected_lines.append(i)

            last_decl_line = i

        if last_decl_line - i > 1 or i == len(lines) - 1:
            for j in selected_lines:
                sel       = lines[j]

                if max_colon_col > 0:
                    colon_col = sel.find(":")

                    if colon_col == -1: 
                        colon_col = sel.find("=")

                    offset    = max_colon_col - colon_col
                    sel       = sel[:colon_col] + " " * offset + sel[colon_col:]

                if max_equal_col > 0:
                    equal_col = sel.find("=")
                    offset    = max_equal_col - equal_col
                    sel       = sel[:equal_col] + " " * offset + sel[equal_col:]

                lines[j] = sel

            selected_lines.clear()
            max_colon_col = 0
            max_equal_col = 0


        m = ASSIGN_EXPR.match(line)

        if m:
            equal_col        = m.start("equal")
            last_assign_line = i
            max_equal_col    = max(max_equal_col, equal_col)
            selected_lines.append(i)

        if last_assign_line - i > 1:
            for j in selected_lines:
                sel       = lines[j]
                equal_col = sel.find("=")
                offset    = max_equal_col - equal_col
                sel       = sel[:equal_col] + " " * offset + sel[equal_col:]
                lines[j]  = sel

            selected_lines.clear()
            max_equal_col = 0

        m = OBJ_EXPR.match(line)
        if m:
            colon_col        = m.start("colon")
            last_record_line = i
            max_colon_col    = max(max_colon_col, colon_col)
            selected_lines.append(i)

        if last_record_line - i > 1:
            for j in selected_lines:
                sel       = lines[j]
                colon_col = sel.find(":")
                offset    = max_colon_col - colon_col
                sel       = sel[:colon_col] + " " * offset + sel[colon_col:]
                lines[j]  = sel

            selected_lines.clear()
            max_colon_col = 0

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mn.py <path>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r") as f:
        code = f.read()

    formatted_code = align(code)

    with open(path, "w") as f:
        f.write(formatted_code)
