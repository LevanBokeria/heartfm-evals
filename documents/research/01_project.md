# 01 — What the project does

*Research note for the novelty review (branch `research/novelty-review`, written 2026-10-29,
`main` at `1519638`). Numbers are taken only from committed files under `results/`, and
recomputed from the per-run JSON/CSV files where the committed summaries are stale. Nothing was
installed or re-run.*

Legend used throughout: **[V]** = checked against a source file in this repo (path given);
**[I]** = my inference.

---

## 1. Research question

> Do the **frozen** representations of a general-purpose vision foundation model already encode
> enough cardiac anatomy and function, or is a cardiac-pretrained model needed?
> — `AGENTS.md`, `scripts/classification/README.md` **[V]**

The backbone is never trained. All comparisons are frozen-encoder + trainable head. The only
full fine-tune that appears anywhere is the published CineMA number, used as an external
reference **[V: 2026-10-29-classification.md §1]**.

## 2. Models

| Backbone | What it is | Input as used here | Tokens | Variants run |
| --- | --- | --- | --- | --- |
| **CineMA** (Fu et al. 2026) | Conv-stem + ViT-B MAE, pretrained on 74,916 UK Biobank cine studies (SAX + LAX 2C/3C/4C), 126 M params | 3D SAX volume 192×192×16 (1×1×10 mm) | 12×12×16 ViT grid, + conv skips at 48² and 24² | `cinema_pretrained` |
| **DINOv3** (Siméoni et al. 2025) | Self-supervised ViT on natural images (LVD-1689M) | each 2D SAX slice, grey→3-ch, ImageNet-normalised, **192×192** | 12×12 per slice | ViT-S/16, B/16, L/16 (7B appears only in stale significance matrices) |
| **SAM v1** (Kirillov et al. 2023) | Supervised promptable-segmentation ViT image encoder, run at 1024² | each 2D SAX slice at 1024² | 64×64, bilinearly downsampled to 12×12 | ViT-B, L, H |

**[V: `src/heartfm_evals/constants.py`, `features.py`, `decoders.py`, `classification_probe.py`]**
SAM2 (Hiera) was in the grid until 2026-09-08 and was removed (`documents/prompts/sam2_decisions.md`).

## 3. Tasks, heads and protocol

### Segmentation (per-pixel BG/RV/MYO/LV, ED + ES frames)

| Decoder | What it sees | Trainable params (ACDC) | Notes |
| --- | --- | --- | --- |
| `linear_probe` | last-layer 12×12 features → Dropout→BN→1×1 conv → bilinear upsample (DINOv3 protocol) | 2.3 k–6 k | |
| `conv_decoder` | 4 layers concatenated (CineMA: 1 layer only) → upsample → 2×(3×3 conv) | 1.0–4.9 M | CineMA gets 768 ch, DINOv3-B 3072 ch — not like-for-like |
| `unetr` (3D) | 4 frozen feature maps stacked along z as skips **plus the raw 192×192 image through a trainable conv block**; CineMA additionally gets its own pretrained conv-stem skips at 48² and 24² | 31–48 M | the image path and the native high-res skips are a large confound (§6) |

100 epochs, AdamW lr 1e-3, wd 1e-3, batch 16, CE+Dice loss, best epoch on val macro Dice.
Macro Dice = mean of RV/MYO/LV (BG excluded) **[V: `run_segmentation.py`, `metrics.py`,
2026-08-09-segmentation.md]**.

### Classification (patient-level pathology)

One embedding per slice (DINOv3/SAM) or per 3D volume (CineMA), CLS or GAP pooling; ED slices
mean-pooled, ES slices mean-pooled, concatenated → `2·d` vector. Heads: `logreg`
(StandardScaler + L2 logistic regression, C swept over 45 values by 10-fold CV on ACDC or the
val split on M&Ms/M&Ms-2) and `linear` (torch `nn.Linear`, AdamW, lr sweep) on the same cached
features. A binary NOR-vs-disease score is derived as 1 − P(NOR) without retraining
**[V: 2026-08-09-classification.md §1]**.

## 4. Datasets and splits

| Dataset | Classes (classification) | Test patients (cls) | Test volumes (seg, ED+ES) |
| --- | --- | --- | --- |
| ACDC | NOR, DCM, HCM, MINF, RV (5) | 50 (10/class) | 100 |
| M&Ms | NOR, DCM, HCM, ARV, HHD (5) | 105 (31/35/23/6/10) | 268 |
| M&Ms-2 | NOR, HCM, ARR, CIA, FALL, LV (6) | 108 (30/23/10/10/10/25) | 314 |

**[V]** test counts recomputed from `true_labels` in the classification JSONs and row counts of
the segmentation `_per_stack`/`_per_sample` CSVs. These match the CineMA paper exactly: its
Table 2 test columns give 10×5 / 31+23+35+6+10 = 105 / 30+23+10+10+10+25 = 108, and its
Fig. 2 segmentation test set is n = 682 = 100 + 268 + 314 **[V: CineMA PDF pp. 3, 9]**. The
data is loaded through CineMA's own `EndDiastoleEndSystoleDataset`, so the splits are very
likely CineMA's official ones **[I]**. Training sets are small: ACDC 90 + 10 val, M&Ms ~150 + ~33
val, M&Ms-2 ~156 + ~38 val (README; HHD has **1** training patient in M&Ms per CineMA Table 2).

## 5. Which results are current and valid

### Segmentation — `results/segmentation/` on `main` is the April 2026 generation

| Rows | Status | Used? | Why |
| --- | --- | --- | --- |
| CineMA `linear_probe`, `conv_decoder` (all 3 datasets) | **Invalid** | **Excluded** | z-misalignment bug in `cache_cinema_2d_features` paired each label with features from a different slice; fixed in `a020ad4` (PR #65). A 2-epoch smoke run on the fixed cache already gave 0.827 vs the committed 0.739 on ACDC (2026-09-01 refresher §1). No corrected 100-epoch run is committed. |
| SAM2 rows in `summary.csv` / `summary_aggregated.csv` | **Orphaned** | **Excluded** | Their JSONs were deleted with the SAM2 removal (2026-09-08); the summaries were never regenerated. SAM2 is out of scope. |
| SAM v1 segmentation | **Absent** on `main` | — | Only on `sam2-classification` (not fetched; pre-dates the #66 off-by-one fix, so invalid anyway). |
| CineMA `unetr`; DINOv3-S/B/L × all three decoders | **Provisionally valid** | **Used, with caveats** | No known bug. But: single unseeded run (`set_seed` commented out; cross-run noise 0.001–0.005 Dice), and issue #74 is re-running ACDC precisely to check reproducibility — nothing regenerated yet (2026-10-22 refresher). The DINOv3-S 2D cache contamination found on 10-22 is in the *new* local cache, not demonstrably in the April one **[I]**. |

### Classification — `results/classification/` (April 2026 runs, unchanged since)

All 65 JSONs (22 ACDC, 22 M&Ms, 21 M&Ms-2) are **used**. Caveats: single runs; `linear` head
unseeded and keeps the last-epoch head (issue 8); `mnm2/dinov3_vits16_logreg_cls` missing;
committed `summary.csv` and significance matrices are stale (5/5/4 rows, phantom methods) so I
**did not use** them — I recomputed every metric from the per-run `probabilities` /
`true_labels`. `.json.bak` files **excluded**.

## 6. Headline numbers

### 6.1 Segmentation, valid rows only (per-volume mean macro Dice, RV/MYO/LV; n = 100 / 268 / 314)

Per-volume mean is the CineMA-paper convention; the committed `summary.csv` reports *pooled*
voxel Dice, which is 0.01–0.04 higher. Both recomputed from files **[V]**.

| Backbone | Decoder | ACDC | M&Ms | M&Ms-2 | Pooled (summary.csv) ACDC / M&Ms / M&Ms-2 |
| --- | --- | --- | --- | --- | --- |
| DINOv3-S | linear | 0.720 | 0.695 | 0.692 | 0.758 / 0.728 / 0.715 |
| DINOv3-B | linear | 0.747 | 0.722 | 0.725 | 0.783 / 0.751 / 0.747 |
| DINOv3-L | linear | 0.748 | 0.726 | 0.731 | 0.783 / 0.753 / 0.753 |
| DINOv3-S | conv | 0.848 | 0.816 | 0.839 | 0.869 / 0.836 / 0.849 |
| DINOv3-B | conv | 0.849 | 0.819 | 0.843 | 0.871 / 0.839 / 0.853 |
| DINOv3-L | conv | 0.857 | 0.824 | 0.846 | 0.877 / 0.844 / 0.856 |
| DINOv3-S | UNETR | 0.856 | 0.818 | 0.836 | 0.874 / 0.838 / 0.850 |
| DINOv3-B | UNETR | 0.858 | 0.817 | 0.838 | 0.878 / 0.837 / 0.852 |
| DINOv3-L | UNETR | 0.858 | 0.819 | 0.838 | 0.877 / 0.839 / 0.850 |
| **CineMA** | **UNETR** | **0.887** | **0.835** | **0.853** | 0.901 / 0.855 / 0.863 |
| *(CineMA linear / conv — invalid, excluded)* | | | | | |

Pooled over the 682 test volumes: CineMA-UNETR **0.851**, DINOv3-L-conv 0.839, DINOv3-L-UNETR 0.833
**[V, computed]**. The CineMA paper's full fine-tune on the same 682 volumes is **88.72 %** mean
Dice (nnUNet 89.24 %) **[V: CineMA PDF p. 7]**.

**Run-to-run noise [V, computed].** `origin/sam2-classification` (commit `6d71694`, 2026-04-30 →
05-05) holds an independent re-run of every CineMA and DINOv3 cell above with identical code
for these backbones. Per-volume macro Dice differs from `main` by **≤ 0.007** in every cell
(e.g. CineMA-UNETR ACDC 0.887 vs 0.883; DINOv3-B-UNETR ACDC 0.858 vs 0.862). I use those
re-runs only as a noise estimate, not as results. The same branch's SAM v1 segmentation rows
pre-date the #66 fix (taps on windowed blocks 1/4/7/10) and are **excluded**; for the record
they are 0.01–0.09 below DINOv3-B/L in every cell.

What these say **[I]**:
1. Decoder capacity dominates: linear → conv is +0.10–0.13 for every DINOv3 size; size S→L is
   ≤ 0.01 at fixed decoder.
2. CineMA's only valid row (UNETR) beats every DINOv3 cell by 0.03 on ACDC and ~0.01–0.02
   elsewhere — but its UNETR receives pretrained high-resolution conv skips (48², 24²) that the
   DINOv3 UNETR does not, so the comparison mixes "cardiac pretraining" with "native 4×/8×
   feature resolution".
3. DINOv3 UNETR ≈ DINOv3 conv despite ~10× more parameters and a raw-image skip, i.e. the 3D
   decoder adds nothing for DINOv3.
4. Frozen CineMA-UNETR is ~3.7 points below the published CineMA fine-tune on the same test
   volumes. That gap is the cost of freezing (mixed with decoder/recipe differences).
5. There is no "decoder on raw image only / random-init backbone" control, so it is unknown
   how much of the 0.83–0.89 UNETR Dice comes from the frozen features at all.

### 6.2 Classification (multi-class macro AUROC; best of {logreg, linear} × {cls, gap} per backbone)

I recomputed macro one-vs-rest **and** one-vs-one AUROC (the CineMA paper's metric per issue
#82) and multi-class MCC from the stored per-patient probabilities. OVR recomputation matches the
JSONs to 4 d.p. On ACDC the test set is perfectly balanced, and for balanced classes macro OVO
and macro OVR AUROC are algebraically identical — so the OVO/OVR question in refresher N5 is
moot for ACDC; on M&Ms/M&Ms-2 they differ by ≤ 0.01 **[V, computed]**.

| Backbone (best config) | ACDC AUROC / acc / MCC | M&Ms AUROC(OVO) / acc / MCC | M&Ms-2 AUROC(OVO) / acc / MCC |
| --- | --- | --- | --- |
| CineMA | 0.906 / 0.64 / 0.55 (logreg·gap) | 0.684 / 0.50 / 0.33 (logreg·gap) | 0.709 / 0.33 / 0.20 (linear·cls) |
| DINOv3-S | 0.859 / 0.52 / 0.41 | 0.701 / 0.45 / 0.26 (logreg·cls) | 0.794 / 0.45 / 0.34 (linear·cls) |
| DINOv3-B | **0.911** / 0.62 / 0.53 (logreg·gap) | 0.679 / 0.41 / 0.20 | 0.766 / 0.40 / 0.26 |
| DINOv3-L | 0.879 / 0.54 / 0.44 | 0.671 / 0.47 / 0.26 | 0.781 / 0.44 / 0.31 |
| SAM-B | 0.869 / 0.60 / 0.51 | 0.675 / 0.38 / 0.17 | 0.734 / 0.43 / 0.30 |
| SAM-L | 0.809 / 0.52 / 0.41 | **0.731** / 0.44 / 0.23 (logreg) | 0.740 / 0.44 / 0.31 |
| SAM-H | 0.836 / 0.54 / 0.43 | 0.723 / 0.47 / 0.27 | 0.722 / 0.38 / 0.24 |
| *Published CineMA full fine-tune* | 0.980 or 0.992 | 0.774 or 0.810 | 0.772 or 0.801 |

"Best config" selected on the test set — this is optimistic for every row and is how the
committed tables also do it **[I]**. The two published values per dataset are the two conflicting
transcriptions of CineMA Suppl. Table 8 (refresher N5); the supplement is not in the PDF and I
could not open it (see BLOCKERS.md).

What these say **[I]**:
1. Every frozen probe is well below the published fine-tune (ACDC ~0.91 vs ≥0.98).
2. Absolute performance on M&Ms/M&Ms-2 is weak: accuracy 0.33–0.54 on 5–6 classes, MCC
   0.07–0.38; several probes are degenerate (binary specificity 0.0).
3. No backbone family wins consistently: CineMA ≈ DINOv3-B on ACDC, SAM-L best on M&Ms,
   DINOv3-S best on M&Ms-2. With 50–108 test patients and single runs, most differences are
   within noise (≈ ±0.05 AUROC is a reasonable bootstrap half-width at n = 50) **[I]**.
4. CineMA's frozen embedding is not obviously better than a natural-image model for
   pathology — the most interesting (if fragile) observation in the classification results.

## 7. What is *not* in the results

- No seeds/variance for anything; no CIs in committed segmentation outputs on `main`.
- No random-init / no-pretraining baseline, no raw-image (pixel) baseline for classification,
  no segmentation-derived handcrafted-feature baseline (volumes, EF, mass) for classification.
- No label-efficiency curves, no cross-dataset (train ACDC → test M&Ms) transfer, no
  per-vendor/per-centre breakdown.
- No in-house fine-tune of any backbone (#28 open).
