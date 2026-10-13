# Retrieval experiments

## Setup
- 40 C++ array solutions, one file per document
- Embedding model: BAAI/bge-small-en-v1.5 (normalized), top-k = 10
- 17 questions in `EVAL_SET`, scored by `eval_retrieval.py`
- 5 more questions are held out and I won't run them until the very end
- Metrics: hit@1, hit@3, hit@10 and MRR
- The agent gives the top 3 files to the LLM, so hit@3 is the number a user actually feels

To reproduce a run: set `INDEX_VARIANT` in `config.py`, delete `chroma_db`, run `python ingest.py`, then `python eval_retrieval.py --label <name>`.

## Baseline
| label | hit@1 | hit@3 | hit@10 | MRR |
|---|---|---|---|---|
| baseline-dense | 47.1% | 52.9% | 82.4% | 0.542 |

8 of 17 questions fail (right file ranked below 3rd). Three of those are not in the top 10 at all: single_number, sorted_arr_rotated, two_sum_optimal. The other five sit at ranks 4 to 9.

reverse_pairs.cpp is in the top 3 for five of the eight failures, and none of my questions are about it. So it keeps showing up where it doesn't belong.

## What I noticed before running anything
I read single_number.cpp again. The real logic is about ten lines (the `xorr` loop). The rest is includes, `using namespace std` and a `main()` that reads input and prints.

Nothing in the file says "appears once" or "twice". The method name is `singleNumber`, one joined word. The only place "single number" shows up as normal English is the print line in `main()`: "The single number is: ". The filename also has it.

I haven't checked the other 39 files this closely, so I don't know if they look the same.

## Experiment A: what gets embedded

| Variant | Text embedded |
|---|---|
| A-raw | the whole file |
| A-title | title made from the filename + the whole file |
| A-strip | file without `#include`, `using namespace` and `main()` |
| A-strip-title | title + stripped file |

### Predictions
I haven't run any A variant yet. Nothing with an `A-` label is in `eval_log.csv`, and no .cpp file has code-fence lines in it.

1. A-raw should give exactly the baseline numbers. If it doesn't, something is wrong with my setup and I stop there.

2. I think the title fixes most of the three "not in top 10" questions. single_number.cpp has no words that match what a person would type, but its filename does. My guess is at least 2 of the 3 get into the top 10 with A-title. If fewer do, then the filename is not where the missing words were.

3. Stripping should leave hit@3 about where it is (within one question). The exception is single_number, which might get worse, because `main()` holds the only plain-English "single number" in the file and strip removes it.

4. A-strip-title should be at least as good as A-title. Title puts the words back, and strip removes noise.

5. I'll count how many of the 17 questions have reverse_pairs.cpp in the top 3. I expect the title variants to have a lower count than A-raw, since the title gives the right files a better match. For A-strip alone I expect about the same count as A-raw (within 1). If the count doesn't drop with title, then the filename doesn't help with this problem.

### Something unfair in my test
I wrote the questions while looking at the filenames. So the title variants have an edge that a real user wouldn't give them. If a title variant wins, I have to say that in the write-up. I may ask a friend to write 5 questions from a list of problem names, without seeing my filenames.

### Things I'm not sure about
- 17 questions is small. One question is about 6 points, so a one-question change is probably noise.
- I don't know why reverse_pairs matches so much. I have a guess but haven't checked it.
- The title is built from the filename, so some titles may come out odd.

### Results
| label | hit@1 | hit@3 | hit@10 | MRR | reverse_pairs in top 3 |
|---|---|---|---|---|---|
| A-raw | pending | pending | pending | pending | pending |
| A-title | pending | pending | pending | pending | pending |
| A-strip | pending | pending | pending | pending | pending |
| A-strip-title | pending | pending | pending | pending | pending |

### What changed per question
pending

### What surprised me
pending

### Decision
pending