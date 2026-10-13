import sys
import config
from textprep import split_main, strip_boilerplate


def main():
    if len(sys.argv) > 1:
        path = config.DATA_DIR / sys.argv[1]
        print(strip_boilerplate(path.read_text(encoding="utf-8", errors="replace")))
        return

    print(f"{'file':38} {'raw':>6} {'stripped':>9}  notes")
    for p in sorted(config.DATA_DIR.glob(config.FILE_GLOB)):
        code = p.read_text(encoding="utf-8", errors="replace")
        _before, main_block, after = split_main(code)
        stripped = strip_boilerplate(code)

        notes = []
        if not main_block:
            notes.append("NO MAIN")
        if after.strip():
            notes.append("CODE AFTER MAIN")
        if "```" in code:
            notes.append("CODE FENCE")
        if "#include" in stripped or "using namespace" in stripped:
            notes.append("BOILERPLATE LEFT")
        if len(stripped) < 150:
            notes.append("VERY SHORT")

        print(f"{p.name:38} {len(code):6} {len(stripped):9}  {', '.join(notes)}")


if __name__ == "__main__":
    main()