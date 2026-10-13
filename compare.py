import csv
import sys
from collections import defaultdict

import config


def main():
    labels = sys.argv[1:]
    table = defaultdict(dict)

    with open(config.BASE_DIR / "eval_details.csv", newline="", encoding="utf-8") as f :
        for row in csv.DictReader(f):
    
            if row["set"] == "eval" and (not labels or row["label"] in labels) :
                table[row["question"]][row["label"]] = row["rank"] or "-"

    cols = labels or sorted({lab for ranks in table.values() for lab in ranks})
    print(f"{'question' : 60}" + "".join(f"{c:>16}" for c in cols))
    
    for question , ranks in table.items():
        print(f"{question[:58]:60}" + "".join(f"{ranks.get(c , ''):>16}" for c in cols))


if __name__ == "__main__":
    main()