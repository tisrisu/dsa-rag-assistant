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
| A-raw-2 | 47.1% | 52.9% | 82.4% | 0.542 | 7 |
| A-title-2 | 52.9% | 76.5% | 88.2% | 0.647 | 2 |
| A-strip-2 | 29.4% | 52.9% | 82.4% | 0.432 | 4 |
| A-strip-title-2 | 52.9% | 70.6% | 94.1% | 0.644 | 3 |

These numbers come only from the -2 reruns. My first strip run was scored under the label A-raw by mistake. I edited that label in eval_log.csv by hand (label text only, no numbers) and then changed it back, so A-raw now appears twice in eval_log.csv: once with the baseline numbers and once with the strip numbers. eval_details.csv has 34 rows under A-raw. My first A-strip-title run gave numbers identical to strip, probably because of a stale index. I stopped trusting the old rows, so I reran all four variants with a -2 label and checked the index stamp each time. The old rows are still in both files.

### What changed per question
Title moved six questions up: single_number (not in top 10 to 8), sorted_arr_rotated (not in top 10 to 1), two sum (not in top 10 to 1), subarray sum k (5 to 1), count inversions (5 to 2) and merge sorted arrays (4 to 3). Five of those six ended in the top 3. single_number is still a miss at rank 8.

It also cost me three questions. The leader question and the n/2 question both fell out of the top 10 (they were at rank 9). The n/3 question went from 3 to 5, the only top-3 loss. That n/3 question got worse in every variant: 3 in raw, 5 with title, 7 with strip, 10 with strip-title.

Strip lost two top-3 questions (pairs 1 to 10, n/3 3 to 7) and gained two (subarray sum k 5 to 3, two sum from missing to 2), so it ends level on hit@3.

### Prediction check
1. Right. A-raw-2 matched the baseline exactly.
2. Right. All three misses entered the top 10 with A-title-2. hit@10 only went from 14 to 15 because the leader and n/2 questions dropped out.
3. Half right. hit@3 stayed at 9/17. I can't judge the single_number part, because it was already outside the top 10 in A-raw-2 and stayed out in A-strip-2. Strip cut hit@1 from 8 to 5 and MRR from 0.542 to 0.432, which I did not expect.
4. Wrong, narrowly. A-strip-title-2 is behind A-title-2 on hit@3 (12 vs 13) and MRR (0.644 vs 0.647), and ahead on hit@10 (16 vs 15). One question either way.
5. Half right. reverse_pairs was in the top 3 for 7 questions in A-raw-2, 2 in A-title-2 and 3 in A-strip-title-2, so the title variants dropped it as I guessed. But A-strip-2 also dropped it, to 4, and I expected it to stay within 1 of raw. I haven't checked why strip matters here.

### What surprised me
Strip kept hit@3 the same but dropped hit@1 from 8 to 5. I thought removing boilerplate would be close to neutral. Title helped the short questions (two sum, "sorted and rotated") but pushed two long descriptive ones out of the top 10, though with 17 questions that could be chance. Strip also lowered the reverse_pairs count, which I didn't predict, and I don't know the reason yet. The first strip-title run being identical to strip was a bad run, not a result.

### Decision
Adopt A-title. It wins 4 questions net on hit@3 and loses 1, which passes my rules. A-strip-title also passes (net +3, loses 1) and has the best hit@10, but it is one question behind title on hit@3, so I keep the simpler one. Strip alone loses two passing questions and hurts hit@1 and MRR, so I reject it. The title gain may be overstated, because I wrote the questions while looking at the filenames. The held-out check should say more.

### Held-out result
I ran the 5 held-out questions once for each variant, after the decision to adopt title was already committed.

| label | hit@1 | hit@3 | hit@10 | MRR |
|---|---|---|---|---|
| A-raw-heldout | 3/5 | 3/5 | 5/5 | 0.649 |
| A-title-heldout | 4/5 | 4/5 | 4/5 | 0.800 |

Title was one question ahead on hit@3, which is the number the agent's user feels. Raw was one question ahead on hit@10. Title moved "one number appears twice and another is missing" from rank 7 to rank 1, but it lost "walk through a grid layer by layer" (raw had it at rank 10, title put it outside the top 10). The other three questions were rank 1 in both. I haven't looked into why title lost that one. With 5 questions, one question is 20 points, so this is a rough check, not proof. I'm keeping title, with thin evidence.

I also ran A-title-final once against the strip_title index by mistake, so I reran it as A-title-final-2 after rebuilding and checking the stamp. A-title-final-2 matched A-title-2 exactly.