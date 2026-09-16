<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Judge defaults for APEX25 and the May ArXiv benchmarks

`apex25`, `arxivmath_0526`, and `brokenarxiv_0526` use a dedicated
GPT-5.6 Luna judge with medium reasoning. Both the default and system-prompt
configurations select the same grader. Dataset revisions and policy prompts
are unchanged; the April benchmarks retain their existing configurations.

## Grading behavior

| Benchmark | Resource server | What the judge evaluates |
| --- | --- | --- |
| APEX25 | `math_with_judge` | Mathematical equivalence of the final boxed answer and reference, with the question for context |
| ArXivMath May | `math_with_judge` | The same final-answer equivalence check |
| BrokenArXiv May | `false_statement_judge` | The full final response to the false statement, using the true reference and MathArena's 0/1/2 rubric |

The two final-answer benchmarks require a nonempty, complete `\boxed{...}`.
An empty, unboxed, or incomplete boxed answer receives zero without a judge
call. Otherwise, `math-verify` runs first. Only symbolic misses reach Luna,
using the raw contents of the last complete box. A positive first judgment
triggers a second judgment with the answers swapped; both must be positive.
This checks answer equivalence, not the correctness of the proof or derivation.
The implementation, prompt and verdict parser are the existing
`math_with_judge` ones, rather than a new grader.

The historical `*_math_with_autograder_*` instance names are retained for
existing commands and metric consumers. Their underlying implementation is now
`math_with_judge`; overrides of its settings must use
`resources_servers.math_with_judge`.

BrokenArXiv keeps its full-response rubric, including partial credit and its
contradiction-deduction exceptions. It cannot be replaced by binary mathematical
answer equivalence. Its prove-the-statement policy prompt is unchanged.

## Endpoint and request settings

The shared [judge configuration](judge_luna.yaml) defaults to OpenAI's public
Responses API with `gpt-5.6-luna`, medium reasoning, and concurrency 16. Set
`OPENAI_API_KEY`, or use `JUDGE_API_KEY` for a separate judge credential.
For another OpenAI-compatible provider, set `JUDGE_BASE_URL`, `JUDGE_MODEL`,
and `JUDGE_API_KEY` together. The provider must support Responses API requests
with `reasoning: {effort: medium}`; its model identifier may differ.

There is no explicit judge output cap, temperature, or top-p override. In
BrokenArXiv these settings explicitly clear the inherited Ultra parameters.
Provider defaults and limits still apply. The policy model remains separate
from the judge; this configuration does not set policy serving or output limits.

## Validation and decision

The decision used judge-only replays of saved responses from an internal model.
No policy answers were regenerated. Each replay checked complete coverage,
unchanged policy responses, valid verdicts, and individual reward differences.
These are contributor-reported checks on one model, not a public gold-label
dataset or a claim of general judge accuracy. The replays used a compatible
provider; the public OpenAI endpoint itself was not exercised in those runs.

| Benchmark | Saved responses | Comparison | Outcome |
| --- | ---: | --- | --- |
| APEX25 | 384 (12 problems × 32 repeats) | `math_with_autograder` + Luna versus `math_with_judge` + Luna | All final rewards agreed; no judge failures |
| ArXivMath May | 640 (40 × 16) | `math_with_autograder` + Ultra versus `math_with_judge` + Luna | All final rewards agreed, including 135 symbolic misses recovered by the judge; no judge failures |
| BrokenArXiv May | 800 (50 × 16) | Same rubric with Luna, Ultra, Terra medium/high, Sol medium and Gemini 3.1 Pro medium | Luna completed all 800 verdicts without serving or parsing failures; exact-grade agreement with alternatives was approximately 96% |

The APEX25 sample had no positive LLM-only recoveries, so separate live controls
checked equivalent fractions and unequal integers. ArXivMath supplied positive
benchmark cases: 137 first judgments were positive and 135 remained positive
after swapping. One rejected first acceptance compared `k=3` against `4`.
This supports retaining the two-positive-judgments rule; the experiment does
not distinguish answer-order effects from sampling variability.

For BrokenArXiv, Luna's mean score differed from Terra medium by -0.25 percentage
points, Sol medium by -0.0625 points, and Gemini medium by +1.625 points.
A paired bootstrap over problems, retaining all 16 responses per problem,
found exploratory 95% intervals of [-1.31, +0.63], [-1.06, +0.81], and
[+0.69, +2.75] points, respectively (100,000 resamples). These are intervals for
score differences, not judge accuracy or proof of equivalence. Among responses
where either judge gave credit, disagreements were more frequent (24–30%);
similar aggregate scores can hide offsetting grading differences.

Targeted, unblinded review found errors in every judge. Luna sometimes confused
the false statement with its true reference. Conversely, other judges sometimes
deducted a point after recognizing a reinterpreted definition, despite the
rubric explicitly forbidding that deduction; Luna followed the rule in those
cases. These examples do not establish an overall accuracy ranking.

Luna was selected as a practical cost/reliability tradeoff. Recorded usage at
published rates put it roughly 10–20 times below the tested Terra, Sol and
Gemini settings, without evidence quantifying a corresponding accuracy benefit
from those alternatives. This is a workload-specific estimate, not a provider
billing comparison. See the published model pricing for
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), and
[Gemini](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-pro-preview).

## Reporting and comparability

Report the combined mean `reward`, judge model, reasoning effort, grader,
repeat count, and missing-verdict count. Symbolic and fallback-judge accuracies
are diagnostics over different subsets, not substitutes for the overall score.
Require complete scoring; do not silently omit failed judgments or substitute
a different judge within one result.

MathArena uses symbolic grading without an LLM fallback for APEX/ArXivMath and
[Gemini 3.1 Pro medium for BrokenArXiv](https://github.com/eth-sri/matharena/blob/main/configs/judges/arxiv_judge_post_march.yaml).
The Gym defaults therefore do not exactly reproduce its grading methodology.
Keep the judge fixed across model comparisons and retain the original grader
attribution on historical results. Independent blinded adjudication and more
policy models would be needed to establish relative judge accuracy.
