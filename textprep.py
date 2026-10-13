import re
from pathlib import Path

VARIANTS = ("raw", "strip", "title", "strip_title")

_INCLUDE = re.compile(r"^\s*#\s*include\b.*$", re.MULTILINE)
_USING = re.compile(r"^\s*using\s+namespace\s+std\s*;\s*$", re.MULTILINE)
_MAIN = re.compile(r"^\s*(?:int|signed)\s+main\s*\(", re.MULTILINE)


def title_from_filename(filename):
    return Path(filename).stem.replace("_", " ").strip()


def split_main(code):
    """Return (before, main_block, after). main_block is '' when no main() is found."""
    m = _MAIN.search(code)
    if not m:
        return code, "", ""

    open_brace = code.find("{", m.end())
    if open_brace == -1:
        return code[:m.start()], code[m.start():], ""

    depth = 0
    for i in range(open_brace, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return code[:m.start()], code[m.start():i + 1], code[i + 1:]

    return code[:m.start()], code[m.start():], ""


def strip_boilerplate(code):
    before, _main_block, after = split_main(code)
    text = before + after
    text = _INCLUDE.sub("", text)
    text = _USING.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_index_text(filename, code, variant):
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; choose from {VARIANTS}")

    text = strip_boilerplate(code) if variant in ("strip", "strip_title") else code
    if variant in ("title", "strip_title"):
        text = f"{title_from_filename(filename)}\n\n{text}"
    return text


SAMPLE = """#include <iostream>
#include<vector>
using namespace std;

class Solution {
public:
  int f(int x) { return x; }
};

int main() {
  cout << "hi";
  return 0;
}
"""


def self_test():
    assert title_from_filename("two_sum_optimal.cpp") == "two sum optimal"
    assert title_from_filename("3_sum.cpp") == "3 sum"

    stripped = strip_boilerplate(SAMPLE)
    assert "#include" not in stripped
    assert "using namespace" not in stripped
    assert "main" not in stripped
    assert "class Solution" in stripped
    assert "int f(int x)" in stripped

    with_tail = "int main() { return 0; }\nvoid helper() {}\n"
    assert "helper" in strip_boilerplate(with_tail)
    assert "main" not in strip_boilerplate(with_tail)

    assert build_index_text("a.cpp", SAMPLE, "raw") == SAMPLE
    assert build_index_text("two_sum.cpp", SAMPLE, "title").startswith("two sum\n\n#include")
    assert build_index_text("two_sum.cpp", SAMPLE, "strip_title").startswith("two sum\n\nclass Solution")
    print("textprep tests passed")


if __name__ == "__main__":
    self_test()