# 03 — Our results against published numbers

*Novelty review, written 2026-10-29. Our numbers come only from committed files under `results/`
(selection rules and exclusions in 01_project.md §5); published numbers from the sources in
02_literature.md (IDs like A1, B2 refer to that file). Bootstrap CIs below were computed by me
from the committed per-patient probabilities / per-volume Dice (2,000 paired resamples, seed 0);
they capture test-set sampling only, **not** training-seed variance.*

**[V]** = checked against a file or source. **[I]** = my inference.

---

## 1. Like-for-like checklist

Before any table: what is and is not comparable between our runs and the CineMA paper (A1/A2),
which is the only published work on the same three datasets with the same test sets.

| Aspect | CineMA paper | Ours | Comparable? |
| --- | --- | --- | --- |
| Test sets | ACDC 50, M&Ms 105, M&Ms-2 108 patients (classification); 682 ED/ES volumes (segmentation) | identical counts and class distributions **[V]** | **Yes** — very likely the same patients, since we load data through CineMA's own dataset class **[I]** |
| Train / val | ACDC 90/10 (2 per class); M&Ms 150/31; M&Ms-2 156/28 | ACDC: logreg uses 10-fold CV on all 100, segmentation carves a seeded 10; M&Ms/M&Ms-2: README says 150/33 and 156/38 | Close but **not verified identical** — README val counts differ from CineMA Table 2 (possibly patients with excluded labels) **[I]** |
| Backbone training | full fine-tuning (all weights), augmentation (gamma, scaling, affine), label smoothing | **frozen**; heads trained on cached features, so effectively **no augmentation** **[I]** | No — this is the variable under study, but it is confounded with the recipe |
| Classification input | ED + ES as a 2-channel 3D SAX input, linear head on mean-pooled tokens | per-slice (DINOv3/SAM) or per-volume (CineMA) embedding, ED and ES each mean-pooled, concatenated | No — and CineMA's frozen ED and ES embeddings are reported to be > 0.99 cosine-similar (A6), so our concatenation may carry little ED→ES signal |
| AUROC | macro **OVO** (code) | macro OVR in JSON; OVO recomputed by me | **Yes after recomputation.** ACDC OVO ≡ OVR (balanced). |
| Accuracy-type metric | "F1 (%)" = sklearn **micro-F1** in code | accuracy, macro-F1 | Micro-F1 equals accuracy for single-label multi-class, so their "F1" ≈ our accuracy — **but** their values are bootstrap means over a 3-seed average/ensemble **[I]** |
| Seeds | 3 seeds; arXiv v2 = mean over seed models; published = predictions averaged across seeds (ensemble) | **single unseeded run** | No. The published (ensemble) value is a stronger reference than v2 for a single model **[I]** |
| Config selection | fixed hyper-parameters, no search | best of {head} × {pooling} per backbone **chosen on the test set** in our summary tables | Ours is optimistically biased; §3 also gives a fixed-config view |
| Segmentation Dice | mean of RV/MYO/LV per 3D volume, averaged over volumes | per-volume macro Dice (recomputed from `_per_stack` / `_per_sample`); committed `summary.csv` is pooled voxel Dice, 0.01–0.04 higher | **Yes** for the per-volume numbers used below |
| Segmentation decoder | UNETR-style decoder, encoder fine-tuned | frozen encoder; linear / conv / UNETR heads; CineMA UNETR also gets its pretrained conv-stem skips | Partly |

## 2. Segmentation

Per-volume mean Dice (%), RV/MYO/LV averaged. Published rows from CineMA Suppl. Table 3 (A1) **[V]**;
ours recomputed from committed CSVs **[V]**.

| Model | Training | ACDC | M&Ms | M&Ms-2 | Pooled (682) |
| --- | --- | --- | --- | --- | --- |
| nnUNet | from scratch, auto-configured | 91.26 | 87.39 | 90.17 | 89.24 |
| CineMA | **fine-tuned** | 90.88 | 87.32 | 89.23 | 88.72 |
| UNet (5-level, residual) | **from scratch** | 89.54 | 86.01 | 88.00 | — |
| CineMA architecture | **from scratch** | 89.57 | 85.03 | 85.96 | — |
| **Ours: CineMA frozen + UNETR** | frozen | **88.69** | **83.48** | **85.25** | **85.06** |
| Ours: DINOv3-L frozen + conv decoder | frozen | 85.71 | 82.43 | 84.56 | 83.89 |
| Ours: DINOv3-B frozen + UNETR | frozen | 85.84 | 81.69 | 83.83 | — |
| Ours: DINOv3-L frozen + linear probe | frozen | 74.84 | 72.59 | 73.10 | — |
| CMRVision paper (B2): NI DINOv3-S fine-tuned | fine-tuned, **ACDC basal slices only** | LV/MYO/RV 95.3 / 89.2 / 92.4 | — | — | — |

Paired bootstrap, CineMA-UNETR minus DINOv3-L-conv: ACDC **+2.98** [2.48, 3.56], M&Ms +1.05
[0.44, 1.65], M&Ms-2 +0.69 [0.13, 1.20] Dice points **[V, computed]**. Run-to-run noise between
two independent April/May runs of the same config is up to 0.7 points (01 §6.1), so only the
ACDC gap is clearly larger than training noise **[I]**.

What this means:

1. **Every frozen configuration is below a plain UNet trained from scratch** on the same
   splits — by 0.9 (ACDC), 2.5 (M&Ms) and 2.8 (M&Ms-2) points for the *best* frozen model, and by
   3.7 / 3.6 / 3.4 points for the best DINOv3 cell. The best frozen model is also below CineMA's
   own *randomly initialised* architecture on all three datasets (by 0.9 / 1.6 / 0.7).
   **[V numbers; I interpretation]** Freezing any of these
   backbones costs accuracy compared with not using a foundation model at all. The paper's
   framing ("do frozen features already encode enough anatomy?") gets the answer "enough for
   ~0.84–0.89 Dice, not enough to match a from-scratch UNet".
2. The cost of freezing CineMA is **3.7 points pooled** (88.72 → 85.06). The CineMA paper
   never measured this; it is a number our project can uniquely contribute (with the caveat that
   our recipe has no augmentation).
3. CineMA's frozen advantage over DINOv3 is real on ACDC (+3) and small elsewhere (+0.7 to +1.8).
   It is confounded by CineMA's UNETR receiving pretrained 48² and 24² conv-stem skips while
   DINOv3 gets only 12² features plus the raw image (01 §3). CMRVision (B2) finds the fine-tuned
   gap NI-DINOv3 → CineMA on ACDC basal slices is only 0.7 / 1.3 / 0.4 (LV/MYO/RV) — similar size
   to ours on M&Ms/M&Ms-2.
4. No published frozen-CineMA or frozen-SAM-v1 segmentation exists on these datasets. Frozen
   DINOv3 on ACDC exists (C7, few-shot, different split); frozen DINOv2/SAM/MedSAM on LA MRI exists
   (C3) with the same "decoder ≫ backbone, DINO > SAM" pattern.

## 3. Pathology classification

### 3.1 Multi-class AUROC (macro OVO)

Published rows from CineMA arXiv v2 Table 5 (seed-mean) and Suppl. Table 8 (seed-ensemble) **[V]**.
Ours recomputed from committed probabilities **[V]**. Bracketed: 95 % bootstrap CI.

| Model | Training | ACDC (n=50) | M&Ms (n=105) | M&Ms-2 (n=108) |
| --- | --- | --- | --- | --- |
| CineMA (published, ensemble) | fine-tuned | 0.992 | 0.810 | 0.801 |
| CineMA (arXiv v2, seed-mean) | fine-tuned | 0.980 | 0.774 | 0.772 |
| ResNet-50 3D (published / v2) | from scratch | 0.847 / 0.811 | 0.682 / 0.633 | 0.716 / 0.691 |
| CineMA arch. (published / v2) | from scratch | 0.629 / 0.631 | 0.575 / 0.582 | 0.622 / 0.616 |
| **Ours, fixed config `logreg·gap`** | | | | |
| CineMA frozen | frozen | 0.906 [0.85, 0.96] | 0.684 [0.60, 0.77] | 0.698 [0.62, 0.77] |
| DINOv3-B frozen | frozen | 0.911 [0.85, 0.96] | 0.679 [0.61, 0.75] | 0.766 [0.73, 0.81] |
| DINOv3-L frozen | frozen | 0.850 | 0.636 | 0.777 |
| SAM-B frozen | frozen | 0.858 [0.78, 0.93] | 0.675 [0.61, 0.73] | 0.730 [0.68, 0.78] |
| **Ours, best config per backbone (test-selected, optimistic)** | | 0.911 (DINOv3-B) | 0.731 (SAM-L) | 0.794 (DINOv3-S) |

Paired differences, DINOv3-B − CineMA (`logreg·gap`): ACDC +0.005 [−0.05, +0.07]; M&Ms −0.005
[−0.07, +0.06]; M&Ms-2 +0.068 [−0.001, +0.14] **[V, computed]**. With `logreg·cls`, DINOv3-B −
CineMA on M&Ms is +0.075 [+0.001, +0.15].

What this means:

1. **Frozen probes are far below the fine-tuned CineMA on ACDC** (0.91 vs 0.98–0.99) and below it
   on M&Ms (0.68–0.73 vs 0.77–0.81). On **M&Ms-2, frozen DINOv3 + a linear readout
   (logreg 0.76–0.78; linear head up to 0.79) is level with fine-tuned CineMA's seed-mean (0.772)** and within ~0.02–0.03 of its
   ensemble (0.801). That is the most surprising comparison in the project — but it rests on a
   single run, a test-selected config for the 0.794, and n = 108 **[I]**.
2. **Frozen probes are at or above a ResNet-50 trained from scratch.** Under the fixed config,
   all four rows are ≥ the published ResNet-50 on ACDC (+0.00 to +0.06; +0.04 to +0.10 vs v2) and
   within ±0.05 of it on M&Ms; on M&Ms-2 DINOv3-B/L beat it by 0.05–0.06 while CineMA is level.
   So for classification, frozen FM features are no worse than training a CNN from scratch —
   unlike segmentation (§2, point 1) **[I]**.
3. **Frozen CineMA is never significantly better than frozen DINOv3**, and is nominally worse on
   M&Ms-2. Its pretraining advantage, visible after fine-tuning (A1, B2) and in fine-tuned
   follow-ups (A7), does not show under linear readouts. This matches the known weakness of MAE
   features under linear probes (D1–D3) and the near-identical ED/ES embeddings (A6) — so our
   result is more likely a statement about *readout* than about *cardiac pretraining* **[I]**.
4. Independent evidence agrees that frozen CineMA is weak on multi-class M&Ms / M&Ms-2: MoViD
   (A5) reports CineMA baselines of 0.553 / 0.619 under its own protocol. Med-DualLoRA (A3) shows
   a frozen CineMA linear probe does fine on the **binary** task (balanced acc 0.81).

### 3.2 Accuracy

| | ACDC | M&Ms | M&Ms-2 |
| --- | --- | --- | --- |
| CineMA fine-tuned "F1" = micro-F1 ≈ accuracy (published / v2) | 0.878 / 0.843 | 0.398 / 0.399 | 0.501 / 0.477 |
| ResNet-50 from scratch (published / v2) | 0.582 / 0.503 | 0.257 / 0.265 | 0.334 / 0.353 |
| Ours, frozen, range over backbones (best) | 0.48–0.66 (CineMA 0.66) | 0.33–0.54 (DINOv3-S 0.54) | 0.33–0.45 (DINOv3-S 0.45) |
| Khened et al. 2019 (E1), segmentation-derived features | **1.00** (official test) | — | — |
| Isensee et al. 2017 (E2) | 0.92 | — | — |
| Jacob et al. 2025 (B1), fine-tuned CMR ViT-S/8, 75/25/50 split | 0.70 | — | — |

**[V]** except Jacob (agent-read table) and the "F1 = accuracy" equivalence, which is my reading of
the CineMA code (`f1_score(average="micro")`) **[I]**.

What this means:

1. On **ACDC**, accuracy 0.48–0.66 from frozen embeddings is far below what is achievable: a
   classifier on segmentation-derived volumes/EF reaches 0.92–1.00. Frozen-FM classification on
   ACDC is not competitive with a 2017 challenge pipeline.
2. On **M&Ms**, if CineMA's "F1" is accuracy, our frozen probes (up to 0.50–0.54) **match or exceed**
   the fine-tuned CineMA (0.40) on accuracy while trailing it on AUROC. With 6 ARV and 10 HHD test
   patients, and **one** HHD training patient, the M&Ms 5-class task is close to ill-posed;
   both numbers are fragile **[I]**.
3. Several of our probes are degenerate on the derived binary task (specificity 0.0; 01 §6.2).
   CineMA's fine-tuned binary specificity is 0.90 / 0.65 / 0.33 per dataset (Suppl. T8). Our
   binary score is never threshold-tuned, so this comparison is not fair either way **[I]**.

## 4. Where our results sit relative to the closest prior work

| Prior work | Their setting | What we add | What they have that we do not |
| --- | --- | --- | --- |
| CineMA (A1/A2) | fine-tuned CineMA vs from-scratch CNNs, 3 datasets | the **frozen** cost of CineMA on the same test sets (−3.7 Dice pooled; −0.07 to −0.13 AUROC across datasets depending on seed-mean vs ensemble reference) and frozen general-FM comparators (DINOv3 is ≈ fine-tuned CineMA's seed-mean on M&Ms-2) | fine-tuning, augmentation, seeds, nnUNet, external sets |
| CMRVision (B2) | **fine-tuned** NI-DINOv3 vs CineMA vs CMR-DINO, ACDC basal slices | frozen regime, full 3D volumes, M&Ms + M&Ms-2, SAM v1, pathology classification, size sweep S/B/L | a CMR-pretrained *DINO* (separates domain from objective), multi-sequence, LoRA |
| Kundu et al. (C3) | frozen DINOv2 / SAM / MedSAM × linear / UNet on LA MRI | cine SAX ventricles, a cardiac FM in the grid, classification | nnUNet comparison, significance tests |
| Liu et al. (C2) | frozen DINOv3 across many medical tasks, incl. MSD Heart | cardiac FM comparator, cine SAX segmentation, pathology | breadth (dozens of datasets) |
| DINO-AugSeg (C7) | frozen DINOv3 + U-Net on ACDC, few-shot curve | CineMA/SAM comparators, M&Ms/M&Ms-2, full-data regime | label-efficiency curve on ACDC |
| Med-DualLoRA (A3) | frozen CineMA linear probe, binary, ACDC+M&Ms | multi-class, general-FM comparators | per-vendor (federated client) breakdown |

## 5. Summary of positioning [I]

- **Segmentation:** our numbers are consistent with the literature: frozen general FMs need a real
  decoder (C3, C4, C12), the backbone matters less than the decoder, and a cardiac FM has a modest
  edge (B2). The new and reportable number is **how much freezing costs** relative to
  CineMA fine-tuning and to from-scratch UNet on identical test sets — and the answer is
  "more than the backbone choice does".
- **Classification:** the frozen probes are weak in absolute terms, beaten by decade-old
  segmentation-feature pipelines on ACDC, and the CineMA-vs-DINOv3 comparison is confounded by
  MAE features being known to read out badly linearly. The one comparison that stands out —
  frozen DINOv3 ≈ fine-tuned CineMA on M&Ms-2 AUROC — needs seeds and a pre-registered config
  before it can be claimed.
