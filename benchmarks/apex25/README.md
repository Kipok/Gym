# APEX 2025

Math problems from [MathArena](https://matharena.ai/?comp=apex--apex_2025)'s
APEX 2025 finals, sourced from `MathArena/apex_2025` on HuggingFace (12
problems). Companion to the larger `apex_shortlist` benchmark.

## Verification

Uses `math_with_judge`: **symbolic-first with a dedicated Luna medium fallback**.
The final response must contain a nonempty, complete `\boxed{...}`. Missing or
empty boxes receive zero without a judge call. `math-verify` checks symbolic
equivalence first; only misses reach Luna with the raw boxed answer, reference,
and question. A positive judgment is checked again with the answers swapped,
and both judgments must be positive for credit.

The judge is separate from the policy model.

MathArena grades final-answer math symbolically without an LLM fallback.
Gym's parser and fallback differ, so its scores are not an exact reproduction
of the leaderboard's grading methodology.

## Prompt

Byte-aligned with MathArena's own APEX prompt
(`configs/competitions/apex/apex_2025.yaml`):

```
Put your final answer within \boxed{}.

<question>
```

## Data preparation

```bash
gym eval prepare --benchmark apex25
```

Writes `data/apex25_benchmark.jsonl` with one row per problem:
`{"question": "...", "expected_answer": "..."}`. The HuggingFace dataset
revision is pinned in `prepare.py` (`HF_REVISION`) for reproducibility.

## Running servers

```bash
gym env start \
    --model-type inference_provider \
    --benchmark apex25
```

## Collecting rollouts

```bash
gym eval run --no-serve \
    --agent apex25_math_with_judge_simple_agent \
    --input benchmarks/apex25/data/apex25_benchmark.jsonl \
    --output results/apex25_rollouts.jsonl \
    --num-repeats 32
```

The judge needs `OPENAI_API_KEY` (or `JUDGE_API_KEY`) in the environment.
The shared [judge config](../judge_luna.yaml) uses the public OpenAI Responses
API. For another compatible provider, set `JUDGE_BASE_URL`, `JUDGE_MODEL`, and
`JUDGE_API_KEY` together. It must support medium reasoning through the Responses
API. The example supplies all repeats at collection time; do not also repeat
the prepared dataset.

With only 12 problems the per-run variance is high — use several repeats
(`--num-repeats`) and report `avg@k`.
