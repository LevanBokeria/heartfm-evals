# Verification report: 06_project_summary.md

- **Document:** [`documents/research/06_project_summary.md`](../06_project_summary.md) at commit `a8f872f`
- **Run:** 2026-11-16, `verify-claims` skill. Claims table: [06_project_summary_claims.md](06_project_summary_claims.md)
- **Verifiers:** `repo-claim-verifier` (results, code, git history, refreshers) and
  `literature-claim-verifier` (primary papers, model cards, UK Biobank showcase). Neither saw the
  draft. Both are Claude, so this is not a fully independent check.
- **Spot checks by the orchestrator:** five key findings were re-checked by hand (seeding disabled,
  no SAM v1 segmentation JSONs, no UNet baseline, UNETR parameter counts, CMR-CLIP Fig. 3h). One
  misattributed quote was found and corrected (N2, see below).

> **⚠ 13 of 26 checkable claims (50%) are not fully supported.** Three are contradicted: the
> segmentation target, and both novelty claims. Treat 06 as a draft until it is revised.

## Summary counts

| Verdict | Count | Claims |
|---|---|---|
| SUPPORTED | 12 | R4, R8, R11, R12, L1, L2, L3, L4, L7, L9, P1, P3 |
| SUPPORTED, but depends on task | 1 | L8 |
| OVERSTATED | 7 | R1, R2, R6, R7, L5, L6, P2 |
| UNDERSTATED | 1 | R10 |
| CONTRADICTED | 3 | R3, N1, N2 |
| UNVERIFIABLE | 2 | R5, R9 |

## Problems, in the order they appear in 06

### N1: CONTRADICTED. "No published frozen comparison of a cardiac model against general-purpose models on these datasets"

> *Draft:* "A literature review (~30 studies) found no published frozen comparison of a cardiac
> model against general-purpose models on these datasets."

**Evidence:** CMR-CLIP (Nakashima et al., *Nat Commun* 2026, 17:4416;
[PMC13194963](https://pmc.ncbi.nlm.nih.gov/articles/PMC13194963/)): "we freeze the visual
embeddings learned during pretraining" and train a classifier on them. Fig. 3h ("supervised
transfer learning") plots **ACDC** MI/HCM/DCM/Abn RV/Normal AUCs for CMR-CLIP against OpenAI
CLIP, BiomedCLIP, VideoMAE-CLIP and others. The orchestrator checked the figure image directly.
Its limits: a random 70/30 split of 132 ACDC patients, disease classification only, results
only as a radar plot, no M&Ms/M&Ms-2, no segmentation, and none of CineMA, DINOv2/v3 or SAM.

**Suggested wording:** "We found one published frozen comparison on these datasets (CMR-CLIP,
ACDC classification only, against CLIP-family baselines). None covers M&Ms or M&Ms-2, frozen
segmentation, or a cardiac MAE against DINOv3/SAM."

### R3: CONTRADICTED (segmentation half). "Ventricle segmentation"

> *Draft:* "Tasks are ventricle segmentation and patient-level disease classification…"

**Evidence:** `src/heartfm_evals/constants.py:18-19` defines classes BG/RV/MYO/LV. Macro Dice
averages RV, MYO and LV, and MYO is the lowest class everywhere (e.g. ACDC CineMA UNETR: RV
0.898, MYO 0.859, LV 0.945). Classification is patient-level, as stated. It has 5 classes for
ACDC and M&Ms, and **6** for M&Ms-2.

**Suggested wording:** "segmentation of the LV, RV and LV myocardium".

### R5: UNVERIFIABLE in the repo, but the literature half is SUPPORTED (L9). "The same test sets as the CineMA paper"

**Evidence:** Splits come from `../data/heartfm/processed/{dataset}/*_metadata.csv`, which is outside
the repo (`data.py:103-118`). Nothing in the repo links them to CineMA. The CineMA paper uses the
official challenge test splits: segmentation 50/160/160, classification 50/105/108 after
excluding classes absent from training. The repo's classification test counts match exactly
(50/105/108). The **segmentation counts do not match** for M&Ms and M&Ms-2: the repo has
50/**134/157**, against the paper's 50/160/160. The CineMA README notes that part of M&Ms
requires an application to access.

**Suggested wording:** "using the official challenge test splits, as in CineMA (classification
test sets identical, 50/105/108 patients; segmentation test sets slightly smaller on M&Ms and
M&Ms-2, 134/157 vs 160/160)." Record the provenance of the metadata CSVs in the repo.

### R2 and R1: OVERSTATED. Which backbones were evaluated, and "only lightweight task heads"

> *Draft:* "…freezes three backbones and trains only lightweight task heads… CineMA…; DINOv3
> (S/B/L)…; and SAM (B/L/H)."

**Evidence (R2):** All 7 backbones appear in the classification results. The committed
segmentation results contain **no SAM v1**: only CineMA and DINOv3 S/B/L, 27 JSONs. The "SAM"
rows in `results/segmentation/*/summary.csv` and `summary_aggregated.csv` are **SAM2** Hiera
models, whose JSONs were deleted (012221d) and whose backbone was removed from the code
(93a55e5). SAM v1 segmentation numbers exist only on the `sam2-classification` branch,
according to the 2026-08-09 refresher, and they predate the SAM v1 tap fix.

**Evidence (R1):** Backbones are frozen (`backbones.py:86-91`). But the UNETR decoders have
**31–48M trainable parameters**, comparable to the backbones themselves, and take the raw image
as a skip input (`decoders.py:162, 304`). The linear and conv heads are light: 2–6k and
1–5M parameters.

**Suggested wording:** "…freezes the backbone and trains task heads, ranging from linear probes
to a UNETR decoder (31–48M parameters, which also sees the raw image). SAM is currently
evaluated for classification only; SAM v1 segmentation needs re-running."

### R6: OVERSTATED. "Frozen CineMA is no better than frozen DINOv3 for disease classification"

**Evidence:** The result depends on the dataset. Macro-F1, from the JSONs, across all heads
and poolings:
- **ACDC:** every CineMA configuration (0.637–0.658) beats every DINOv3 configuration (best 0.616).
  Only 4 of 48 paired bootstrap CIs exclude 0.
- **M&Ms:** mixed, from −0.25 to +0.18. 16 of 48 CIs exclude 0, in both directions.
- **M&Ms-2:** every DINOv3 configuration beats every CineMA one, with AUC 0.75–0.79 vs 0.69–0.70.

All of these are single unseeded runs, with no correction for multiple comparisons. The
committed `mcnemar_*`/`bootstrap_*` CSVs are stale: they include methods with no current JSON.

**Suggested wording:** "Frozen CineMA shows no consistent advantage over frozen DINOv3 for
disease classification: it leads on ACDC (mostly not significant), is mixed on M&Ms, and trails
on M&Ms-2."

### R7: OVERSTATED. "CineMA has a modest segmentation advantage (+1–3 Dice)"

**Evidence:** This holds only for the UNETR decoder, and only against DINOv3. CineMA minus the
best DINOv3: ACDC +2.3, M&Ms +1.6, M&Ms-2 +1.1 Dice. A patient-level paired bootstrap excludes
0 for every DINOv3 size. With the linear and conv decoders, CineMA is 4–19 Dice **below**
DINOv3, but those 6 CineMA results are invalid because of the z-misalignment bug, fixed in
a020ad4 after they were run. The SAM comparison can't be checked in this repo (see R2).

**Suggested wording:** "With a UNETR decoder, CineMA leads DINOv3 by +1.1 to +2.3 Dice
(significant on single runs). The linear and conv-decoder comparisons must be re-run, and SAM
v1 segmentation is not yet in the committed results."

### R9: UNVERIFIABLE. "Every frozen model performs below a UNet trained from scratch"

**Evidence:** There is no from-scratch UNet or nnU-Net result, script or config anywhere in
`results/`, `src/`, `scripts/` or the refreshers (confirmed by the orchestrator). The baseline
must come from a published paper, most likely CineMA's own comparisons, and 06 does not cite it.

**Suggested wording:** Cite the source and its numbers, e.g. "below the from-scratch UNet
reported in the CineMA paper (X/Y/Z Dice)". Better still, add the baseline to this repo so it
uses the same splits and metric. Note the metric mismatch: `summary.csv` Dice is pooled over
voxels, while per-volume means are about 0.015 lower.

### R10: UNDERSTATED. "Several results also need re-running with fixed seeds"

**Evidence:** `set_seed()` has been commented out since 0b5d350 (2026-04-16) and **is still
disabled at HEAD** (`run_segmentation.py:195`, `run_classification.py:224`,
`linear_head.py:249`; issue #59 is open). **All** committed results (65 classification JSONs
and 27 segmentation JSONs, dated 2026-04-18 to 04-21) are unseeded single runs. Separately, the
6 CineMA linear/conv segmentation results are invalid regardless of seed (z-misalignment). Run-to-run noise is
0.001–0.005 Dice: enough to swamp differences between DINOv3 sizes, but not the CineMA UNETR
margin.

**Suggested wording:** "All committed results are single unseeded runs (seeding is currently
disabled), and six CineMA segmentation results are invalid because of a since-fixed slice
misalignment bug. The full grid needs re-running with fixed seeds and multiple repeats."

### L5 and L6: OVERSTATED. CMRVision "only with full fine-tuning, small ViT-S models"

**Evidence:** CMRVision (Jacob, Sharma, Rueckert, [arXiv 2609.01308](https://arxiv.org/abs/2609.01308)):
"Both tasks used full end-to-end finetuning". It also evaluates **LoRA-adapted** natural-image
DINOv3, zero-shot transfer and PCA of pretrained features, though it has no frozen or linear-probe
numbers. All the encoders it trains are ViT-S (patch 8 or 16), but it benchmarks
against larger baselines, including CineMA, SAM2 and MedSAM2. Its conclusion is directly
relevant: "CMR-pretrained models consistently outperformed NI-pretrained counterparts".

**Suggested wording:** "…but evaluates only fine-tuned or LoRA-adapted encoders (no frozen
readout), compares natural vs cardiac pretraining only at ViT-S, and has no disease
classification."

### N2: CONTRADICTED. "Neither CMRVision nor any other cardiac study has separated the two"

> *Draft:* "The key question is whether the advantage comes from the training data… or from the
> training method… Neither CMRVision nor any other cardiac study has separated the two."

**Evidence:** Jacob et al., *JCMR* 2025, 27:101967
([PMC12745146](https://pmc.ncbi.nlm.nih.gov/articles/PMC12745146/)), varies one factor at a time:
- **Method:** §2.6.2, "To tease apart the effect of encoder architecture and pretraining method",
  compares MAE vs DINO, both ViT-S/8, on the same CMR subset of about 360k images.
- **Data:** §2.6.3 compares natural-image vs CMR initialisation within DINO ViT-S/8.

CMRVision also varies the data, within the DINO family.

*Orchestrator correction:* the literature verifier cited "the encoder was kept frozen across
all experiments" as describing §2.6.3. That sentence is actually in §2.6.4 (few-shot). The
natural-image vs CMR comparison was **fine-tuned**. The verdict stands, but the comparisons
were not frozen.

**What remains new:** a full matched 2×2 (natural vs cardiac data × MAE vs DINO method),
evaluated with **frozen** readouts, at ViT-B.

**Suggested wording:** "Prior cardiac work has varied pretraining data or method one factor at
a time, under fine-tuning and at ViT-S (Jacob et al. 2025; CMRVision 2026). No study has run a
matched 2×2 of data × method with frozen evaluation."

### P2: OVERSTATED. "Participants scanned after CineMA's pretraining cut-off"

**Evidence:** CineMA documents only "74,916 unlabelled cine CMR studies from UKB (up to 6 November
2023)", from fields 20208/20209, instances 2 and 3. It publishes no participant list. Scans after
6 Nov 2023 are guaranteed unseen. Data acquired earlier but released later is ambiguous. Field 20209 now
covers 96,120 participants, so there should be a sizeable post-cut-off pool.

**Suggested wording:** "…participants whose cine CMR was acquired after CineMA's data cut-off
(6 Nov 2023)." Check with the CineMA authors whether instance-3 repeat scans count.

## Supported, with notes worth knowing

- **L1:** the "~75k" figure counts **studies**, not participants, because repeat visits are
  included (74,916 studies). The arXiv v2 abstract wrongly says "subjects".
- **L3:** SAM's image encoder was **initialised from an MAE-pretrained ViT**. That makes SAM a
  partly MAE-trained model, which matters for the planned MAE-vs-DINO framing.
- **L8:** Precedents exist (Liu et al. [2509.06467](https://arxiv.org/abs/2509.06467), frozen
  DINOv3 beats BiomedCLIP/CT-Net on several tasks; Raptor; AnyMC3D, the last two checked from
  the abstract only). But the result depends on the task: in Liu et al., general models lose
  on pathology WSI, EM and PET.
- **P1:** DINOv3 ViT-B weights are gated (approval required). No DINO/iBOT projection heads are
  released, so continued self-supervised pretraining needs new heads. The public MAE ViT-B
  checkpoint appears to be encoder-only.
- **R11:** test sets have 50/105/108 patients, with as few as 6 per class (M&Ms ARV). Pairwise
  F1 CIs on ACDC are about ±0.16.
- **R12:** about 28 foundation-model studies in `02_literature.md` sections A–C. The tables
  list about 38 distinct works in total.

## Other issues found that 06 does not mention

- `results/segmentation/*summary*.csv` still contain SAM2 rows. Anyone quoting "SAM"
  segmentation numbers from these files is quoting SAM2.
- The classification `summary.csv` files are stale (5/5/4 rows vs 22/22/21 JSONs).
- Binary NOR-vs-rest on M&Ms/M&Ms-2 is dominated by class prevalence: several models predict
  all-positive and still score F1 ≈ 0.83.
- Classification AUROC here is one-vs-rest. CineMA reports one-vs-one, so the numbers are not
  directly comparable.
- CineMA's own UK Biobank downstream test participants overlap its pretraining set (temporal
  split before 2019 / 2019 / after 2019, while pretraining runs to Nov 2023). Don't cite those
  results as clean held-out results.

## Full table

| ID | Verdict | Evidence pointer |
|---|---|---|
| R1 | OVERSTATED | UNETR 31–48M params, raw-image skip (`summary.csv`, `decoders.py:162,304`) |
| R2 | OVERSTATED | No SAM v1 segmentation JSONs; `summary.csv` "SAM" = SAM2 |
| R3 | CONTRADICTED | `constants.py:18-19`: RV/MYO/LV |
| R4 | SUPPORTED | Results for both tasks on all 3 datasets (segmentation: CineMA and DINOv3 only) |
| R5 | UNVERIFIABLE | Split CSVs outside repo; classification counts match CineMA, segmentation counts do not |
| R6 | OVERSTATED | CineMA leads on ACDC, mixed on M&Ms, trails on M&Ms-2 |
| R7 | OVERSTATED | +1.1 to +2.3 with UNETR vs DINOv3 only; SAM not in results |
| R8 | SUPPORTED | CineMA: 3D input and its own conv skips (`decoders.py:264-279`) |
| R9 | UNVERIFIABLE | No UNet baseline in repo |
| R10 | UNDERSTATED | All results unseeded; `set_seed` disabled at HEAD; 6 CineMA results invalid |
| R11 | SUPPORTED | 50/105/108 test patients |
| R12 | SUPPORTED | about 28 foundation-model studies, about 38 total |
| L1 | SUPPORTED | CineMA Methods: 74,916 studies, MAE (studies, not participants) |
| L2 | SUPPORTED | DINOv3 README: S/B/L distilled, LVD-1689M |
| L3 | SUPPORTED | SAM: SA-1B; encoder initialised from MAE |
| L4 | SUPPORTED | arXiv 2609.01308 |
| L5 | OVERSTATED | Also LoRA, zero-shot, PCA; no frozen numbers |
| L6 | OVERSTATED | Trained encoders ViT-S; larger baselines compared |
| L7 | SUPPORTED | View classification only |
| L8 | SUPPORTED, task-dependent | Liu et al. 2509.06467; Raptor; AnyMC3D |
| L9 | SUPPORTED | Official challenge splits |
| N1 | CONTRADICTED | CMR-CLIP, *Nat Commun* 2026, Fig. 3h |
| N2 | CONTRADICTED | Jacob et al., *JCMR* 2025 §2.6.2–2.6.3 (fine-tuned) |
| P1 | SUPPORTED, with caveats | Gated DINOv3 weights; no SSL heads |
| P2 | OVERSTATED | Date cut-off only, no participant list |
| P3 | SUPPORTED | UK Biobank field 24100 LVEDV, 80,974 participants |

## Novelty searches (from the literature verifier)

**N1:** 5 web and PubMed searches plus full-text checks of CMR-CLIP, MoViD, Pix2Rep-v2,
DINO-MVR, MRI-CORE and Hashmi et al. Near-misses:
- Jacob 2025: a ResNet50 ImageNet baseline, frozen or fine-tuned depending on the run.
- Med-DualLoRA: frozen CineMA only.
- Pix2Rep-v2: CineMA and DINOv3 fine-tuned.
- MoViD: fine-tuned, not on ACDC.
- Liu et al.: ACDC used for registration only.

**N2:** 5 searches plus full text of CMRVision and de Mooij et al. 2024. Near-misses:
- de Mooij et al. 2024: SimCLR/PCL/DINO/MIM on the same M&Ms data, but with a CNN and no
  natural-image arm.
- MetaCLIP-CMR: seen only as a search snippet.

## Opinions not checked

- "the study is incremental"
- the 3-month plan items
- the risk list, including the "few hundred GPU-hours" estimate
