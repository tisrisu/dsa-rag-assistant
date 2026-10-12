import os 
import argparse 
import csv 
from datetime import datetime

import config 
from  eval_set import EVAL_SET , HELD_OUT 
from ask import vectorstore

K = 10
CUTOFFS = (1 , 3 , 10 )
FAIL_RANK = 3 
LOG_PATH = config.BASE_DIR / "eval_log.csv"
LOG_COLUMNS = ["timestamp", "label" , "set" , "n"] + [f"hit@{k}" for k in CUTOFFS] + ["mrr"]

def validate (eval_set) :
    real_files = {p.name for p in config.DATA_DIR.glob(config.FILE_GLOB)}
    problems = []

    for i , items in enumerate(eval_set , start = 1) :
        question = items.get("question", "")
        expected = items.get("expected", [])

        if not isinstance (question , str) or not question.strip() :
            problems.append(f"item {i}: 'question' must be a non-empty string")       

        if not isinstance (expected , list) or not expected :
            problems.append(f"item {i}: 'expected' must be a non-empty list")
            continue

        for name in expected :
            if name not in real_files :
                problems.append(f"item {i}: expected file '{name}' is not in {config.DATA_DIR}")

    if problems :
        raise ValueError("Dataset problems:\n" + "\n".join(problems))



def rankings (retrieved_files , expected) : 
    for pos, name in enumerate (retrieved_files , start = 1) :
        if name in expected  :
            return pos
    return None

def dense_retrieve (question) :
    docs = vectorstore.similarity_search(question , k=K)
    return [os.path.basename(doc.metadata["source"]) for doc in docs]

def run (eval_set , retrieve_func ) :
    results = []
    for item in eval_set : 
        names = retrieve_func(item["question"])
        rank = rankings(names , item["expected"])
        results.append({
            "question": item["question"] ,
            "expected": item["expected"] ,
            "rank": rank ,
            "top3": names[:3] ,
        })

    return results

def compute_metrics (results) :
    n = len (results)
    metrics = {}

    for k in CUTOFFS :
        hits = sum( 1 for r in results if r["rank"] is not None and r["rank"] <= k )
        metrics[f"hit@{k}"] = hits / n if n else 0.0

    reciprocal = [1 / r["rank"] if r["rank"] is not None else 0 for r in results ]
    metrics["mrr"] = sum(reciprocal) / n if n else 0.0

    return metrics

def summary (metrics , n , set_name) :
    print(f"\n Retrieval benchmark .... set: {set_name} .... questions: {n} .... k: {K}")
    for k in CUTOFFS:
        value = metrics[f"hit@{k}"]
        print(f"hit@{k:<2}: {value:6.1%}  ({round(value*n)}/{n})")
    print(f" MRR : {metrics['mrr']:.3f}")

def fail (results) :
    failures = [r for r in results if r["rank"] is None or r["rank"] > FAIL_RANK]
    if not failures:
        print(f"\n no failures : every expected file is in the top {FAIL_RANK}.")
        return

    print(f"\n failures (rank > {FAIL_RANK} or missing) : {len(failures)}")
    
    for r in failures:
        rank_text = r["rank"] if r["rank"] is not None else f"not in top {K}"
        print(f"\nQ: {r['question']}")
        print(f"---expected : {r['expected']}")
        print(f"---rank : {rank_text}----top-3: {r['top3']}")  

def logs (label , set_name , n , metrics) :
    file_existed = LOG_PATH.exists()

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "label": label,
        "set": set_name,
        "n": n,
    }

    for key, value in metrics.items():
        row[key] = round ( value, 4)

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        
        if not file_existed:
            writer.writeheader()
        
        writer.writerow(row)


def test () :
    assert rankings (["a" , "b" , "c"] , ["b"]) == 2
    assert rankings (["a" , "b" , "c"] , ["d"]) is None
    assert rankings (["a" , "b" , "c"] , ["c" ,"a"]) == 1
    assert rankings ([] , ["a"]) is None

    dummy = [{"rank" : r} for r in (1 , 3 , None , 2)]
    m = compute_metrics(dummy)
    assert m["hit@1"] == 0.25
    assert m["hit@3"] == 0.75
    assert m["hit@10"] == 0.75
    assert abs(m["mrr"] - 0.4583) < 0.001
    print("tests passed")

def main () :
    parser = argparse.ArgumentParser(description="retrieval evaluation")
    parser.add_argument("--set" , choices=["eval", "heldout"] , default="eval")
    parser.add_argument("--label" , default="baseline-dense")
    parser.add_argument("--selftest" , action="store_true")
    args = parser.parse_args()

    if args.selftest:
        test()
        return

    eval_set = EVAL_SET if args.set == "eval" else HELD_OUT

    validate(eval_set)
    results = run(eval_set, dense_retrieve)
    metrics = compute_metrics(results)

    summary(metrics, len(results), args.set)
    fail(results)
    logs(args.label, args.set, len(results), metrics)

    if args.set == "heldout":
        print("\nReminder: run the held-out set once, at the end. Tuning against it makes the numbers meaningless.")


if __name__ == "__main__":
    main()