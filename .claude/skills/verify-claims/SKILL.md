---
name: verify-claims
description: Fact-check a research document (summary, report, proposal) claim by claim. Splits it into atomic claims, sends claims about this project to a repo verifier (results, code) and claims about published work to a literature verifier (primary papers), neither of which sees the draft, and writes a verification report with a verdict and quoted evidence per claim.
argument-hint: <path to document> [--literature-only | --repo-only]
disable-model-invocation: true
---

# Verify the claims in a document

Input: `$ARGUMENTS`, the path of a document to check (usually under `documents/research/`).

Rules for the whole run:
- **The draft is not evidence, and neither are other notes Claude wrote.** Files in
  `documents/research/` are notes Claude wrote, so they don't count as evidence. A claim is
  supported only by results files, code, or a primary source (the paper itself).
- **The verifiers never see the draft.** They get the claims table only. They should not
  see the draft's wording, its reasoning or its confidence.
- Do not edit the draft. The output is a separate report. The user decides what to change.

## 1. Extract claims

Read the document and write a claims table. Each claim is one checkable assertion,
rewritten to stand alone: resolve pronouns, add the dataset, metric or paper it is about,
and keep the draft's strength words ("no better", "every", "significantly", "first").
Split compound sentences. One sentence often holds two or three claims.

Columns:

| ID | Claim | Type | Draft's stated basis | Check question |
|---|---|---|---|---|

Types:
- `internal-result`: a number, ranking or comparison from this project's results.
- `internal-method`: what the code, data or pipeline does (backbones, splits, heads, seeds).
- `literature`: what a published paper, model or dataset is or reported.
- `novelty`: "no prior work has…", "first to…", "nobody has separated…". These are
  absence claims, which a search can contradict but never prove.
- `plan-premise`: a factual premise the proposed work depends on (e.g. a dataset field
  exists, a model's weights are public, a cut-off date is documented).
- `opinion`: judgements, plans and estimates with no factual core. List them, but don't
  send them for checking.

The check question is one concrete question that the evidence alone can answer, e.g.
"In `results/classification/*/summary.csv` and the McNemar/bootstrap outputs, is frozen CineMA
worse than, equal to, or better than frozen DINOv3, per dataset, and is any difference
significant?"

Save the table to `<doc-dir>/verification/<doc-stem>_claims.md`.

## 2. Verify, in parallel

Launch both verifiers in a single message with the Agent tool. Give each one only its rows
of the claims table (ID, Claim, Type, Check question; leave out "Draft's stated basis" for
the repo verifier). Do not give either verifier the draft's path or its text.

- `repo-claim-verifier` gets `internal-result`, `internal-method`, and the internal half of
  any mixed claim.
- `literature-claim-verifier` gets `literature`, `novelty` and `plan-premise`.

If the agent types are not registered in this session (they load at session start), launch
`general-purpose` agents and paste the body of `.claude/agents/<name>.md` as the start of
the prompt.

## 3. Reconcile and report

Merge both returns into `<doc-dir>/verification/<doc-stem>_verification.md`:

1. **Header**: document checked, its git commit (`git log -1 --format=%h -- <doc>`), date,
   and which verifiers ran. Note that both are Claude, so the check is not fully
   independent.
2. **Summary counts** by verdict.
3. **Problems first**: every claim marked CONTRADICTED, OVERSTATED or UNVERIFIABLE, plus every
   novelty claim. For each, give the claim as written in the draft (quote the sentence), the
   verdict, the evidence (file:line, value, or quoted passage with URL), and a suggested
   rewording that the evidence supports.
4. **Full table**: all claims with verdict and a one-line evidence pointer.
5. **Opinions not checked**: the `opinion` rows, listed.

Verdicts (shared with the verifiers):
- `SUPPORTED`: the evidence says this, at this strength.
- `OVERSTATED`: the evidence supports a weaker or narrower version (fewer datasets, not
  significant, "some" not "every", a range that is too tight).
- `CONTRADICTED`: the evidence says otherwise.
- `UNVERIFIABLE`: the evidence needed is not accessible (paywall, data not in the repo, result
  not run). Say what would settle it.
- `NOT REFUTED`: novelty claims only. The searches found no counterexample. List the searches.

If more than a quarter of the checkable claims are not SUPPORTED, say so in the header.

## 4. Report back

Tell the user the counts, the problem claims in one line each, and the report path. Ask
before committing anything.
