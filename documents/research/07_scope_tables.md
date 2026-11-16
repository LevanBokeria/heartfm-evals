# heartfm-evals — scope at a glance: done vs proposed

*November 2026. Companion to [06_project_summary.md](06_project_summary.md), which gives the
reasoning and caveats behind each item.*

## Overview

M1–M3 = month of the proposed work · ⭐ = stretch goal

| Factor | ✅ Done so far | 🆕 Proposed |
|---|---|---|
| **Backbones** | CineMA (ViT-B)<br>DINOv3 (S, B, L)<br>SAM (B, L, H), classification only | Seeded re-runs limited to CineMA, DINOv3 ViT-B and one SAM size (M1)<br>SAM v1 segmentation, one size (M1)<br>Random-init control, CineMA architecture (M1)<br>MAE ViT-B, natural images (M2)<br>DINOv3 ViT-B → UK Biobank (M2)<br>MAE ViT-B → UK Biobank (M2) |
| **Continued pretraining on cardiac MRI** | None: natural-image models used as released | DINOv3 ViT-B and MAE ViT-B on UK Biobank cine MRI (M2) |
| **Backbone adaptation** | Frozen | LoRA (M3)<br>Full fine-tuning ⭐ |
| **Segmentation heads** | Linear probe<br>Conv decoder<br>UNETR | — |
| **Classification heads** | Logistic regression<br>Linear | kNN / nearest centroid (M1) |
| **Regression heads** | — | Linear probe (M1) |
| **Tasks** | Segmentation (LV, RV, myocardium)<br>Disease classification (patient-level) | Ejection fraction and ventricular volumes (M1)<br>UK Biobank cardiac measurements, with label-efficiency curves (M3) |
| **Datasets** | ACDC<br>M&Ms<br>M&Ms-2 | UK Biobank cine MRI: continued pretraining (M2); evaluation on scans after 6 Nov 2023 (M3) |
| **Baselines and reliability** | From-scratch UNet cited from the CineMA paper<br>All results single unseeded runs<br>6 CineMA linear/conv segmentation runs invalid | From-scratch UNet run in this repo (M1)<br>Random-init backbone control (M1)<br>Classifier on segmentation-derived measurements (M1)<br>Re-run with several fixed seeds: CineMA, DINOv3 ViT-B, one SAM size (M1) |

## Part 1. Work done so far

**Backbones.** All are frozen. None of the natural-image models was further pretrained on cardiac
data.

| Backbone | Sizes | Pretraining data | Pretraining method | Continued pretraining on cardiac MRI | Segmentation | Classification |
|---|---|---|---|---|---|---|
| CineMA | ViT-B | UK Biobank cine MRI (~75k studies) | MAE | n/a (cardiac from the start) | ✅ | ✅ |
| DINOv3 | S, B, L | Natural images | DINO self-distillation | ❌ used as released | ✅ | ✅ |
| SAM | B, L, H | Natural images (SA-1B) | Supervised segmentation (MAE-initialised encoder) | ❌ used as released | ❌ not in committed results | ✅ |

**Backbone adaptation.**

| Adaptation | Status |
|---|---|
| Frozen backbone | ✅ |

**Heads trained on frozen features.**

| Task | Head | Trainable params | Notes |
|---|---|---|---|
| Segmentation | Linear probe | 2–6k | 1×1 conv on patch tokens |
| Segmentation | Conv decoder | 1–5M | 2D CNN on multi-layer features |
| Segmentation | UNETR | 31–48M | Also sees the raw image; CineMA's also gets its own conv-stem skips |
| Classification | Logistic regression | small | On pooled patient-level features |
| Classification | Linear | small | On pooled patient-level features |

**Datasets.**

| Dataset | Used for | Segmentation test patients | Classification test patients | Disease classes |
|---|---|---|---|---|
| ACDC | Evaluation | 50 | 50 | 5 |
| M&Ms | Evaluation | 134 (CineMA: 160) | 105 | 5 |
| M&Ms-2 | Evaluation | 157 (CineMA: 160) | 108 | 6 |

**Downstream tasks.**

| Task | Target | Metric | Status |
|---|---|---|---|
| Segmentation | LV, RV, myocardium | Dice | ✅ |
| Disease classification | Patient-level diagnosis | Macro-F1, AUROC (one-vs-rest) | ✅ |

**Baselines and reliability.**

| Item | Status |
|---|---|
| From-scratch UNet | Cited from the CineMA paper, not run here |
| Random-init backbone control | None |
| Seeds | Seeding disabled; all results are single unseeded runs |
| CineMA linear/conv segmentation | Invalid (since-fixed slice-misalignment bug) |

## Part 2. Proposed work

The same tables, with proposed additions next to the existing work.

Legend: ✅ done · 🔁 re-run with fixed seeds (CineMA, DINOv3 ViT-B, one SAM size only) · 🆕 proposed · ⭐ stretch goal · M1–M3 = month

**Backbones.** Three new pretrained models complete a matched 2×2 at ViT-B, plus a random-init
control.

| Backbone | Sizes | Pretraining data | Pretraining method | Continued pretraining on cardiac MRI | Segmentation | Classification | 🆕 UK Biobank measurements |
|---|---|---|---|---|---|---|---|
| CineMA | ViT-B | UK Biobank cine MRI (~75k studies) | MAE | n/a (cardiac from the start) | ✅ 🔁 | ✅ 🔁 | 🆕 |
| DINOv3 | S, B, L | Natural images | DINO self-distillation | ❌ used as released | ✅ (🔁 ViT-B only) | ✅ (🔁 ViT-B only) | 🆕 (ViT-B) |
| SAM | B, L, H | Natural images (SA-1B) | Supervised segmentation (MAE-initialised encoder) | ❌ used as released | 🆕 SAM v1, one size (M1) | ✅ (🔁 one size only) | — |
| 🆕 MAE (M2) | ViT-B | Natural images (ImageNet) | MAE | ❌ used as released | 🆕 | 🆕 | 🆕 |
| 🆕 DINOv3 → UK Biobank (M2) | ViT-B | Natural images, then UK Biobank cine MRI | DINO self-distillation | 🆕 yes | 🆕 | 🆕 | 🆕 |
| 🆕 MAE → UK Biobank (M2) | ViT-B | Natural images, then UK Biobank cine MRI | MAE | 🆕 yes | 🆕 | 🆕 | 🆕 |
| 🆕 Random init (M1) | ViT-B (CineMA architecture) | None | None | — | 🆕 | 🆕 | 🆕 |

**The core 2×2 (M2): pretraining data × pretraining method, all ViT-B, evaluated frozen.**

| | MAE | DINO self-distillation |
|---|---|---|
| **Natural images, as released** | 🆕 MAE ViT-B | ✅ DINOv3 ViT-B |
| **Natural images, then UK Biobank cine MRI** | 🆕 MAE → UK Biobank | 🆕 DINOv3 → UK Biobank |
| *Reference: cardiac only* | ✅ CineMA | — |

**Backbone adaptation.**

| Adaptation | Status |
|---|---|
| Frozen backbone | ✅ 🔁 |
| 🆕 LoRA adapters | 🆕 subset of tasks, with label-efficiency curves (M3) |
| 🆕 Full fine-tuning | ⭐ upper bound on the cost of freezing (M3); fair tuning per model may take considerable time |

**Heads trained on frozen features.**

| Task | Head | Trainable params | Notes |
|---|---|---|---|
| Segmentation | Linear probe | 2–6k | ✅ 🔁 |
| Segmentation | Conv decoder | 1–5M | ✅ 🔁 |
| Segmentation | UNETR | 31–48M | ✅ 🔁 |
| Classification | Logistic regression | small | ✅ 🔁 |
| Classification | Linear | small | ✅ 🔁 |
| Classification | 🆕 kNN / nearest centroid | none | 🆕 second readout (M1) |
| 🆕 Regression | 🆕 Linear probe | small | 🆕 ejection fraction, ventricular volumes (M1); UK Biobank measurements (M3) |

**Datasets.**

| Dataset | Used for | Segmentation test patients | Classification test patients | Disease classes |
|---|---|---|---|---|
| ACDC | Evaluation | 50 | 50 | 5 |
| M&Ms | Evaluation | 134 (CineMA: 160) | 105 | 5 |
| M&Ms-2 | Evaluation | 157 (CineMA: 160) | 108 | 6 |
| 🆕 UK Biobank cine MRI | 🆕 Continued pretraining (M2); evaluation on participants scanned after CineMA's cut-off, 6 Nov 2023 (M3) | — | — | — |

**Downstream tasks.**

| Task | Target | Metric | Status |
|---|---|---|---|
| Segmentation | LV, RV, myocardium | Dice | ✅ 🔁 |
| Disease classification | Patient-level diagnosis | Macro-F1, AUROC (one-vs-rest) | ✅ 🔁 |
| 🆕 Cardiac function | Ejection fraction, ventricular volumes (public datasets) | Regression error | 🆕 M1 |
| 🆕 UK Biobank measurements | Cardiac measurements (e.g. LV volumes, ~81k participants) | Regression error, label-efficiency curves | 🆕 M3 |

**Baselines and reliability.**

| Item | Status | Proposed |
|---|---|---|
| From-scratch UNet | Cited from the CineMA paper, not run here | 🆕 run in this repo on the same splits and metric (M1) |
| Random-init backbone control | None | 🆕 added (M1) |
| 🆕 Classifier on segmentation-derived measurements | — | 🆕 clinical baseline (M1) |
| Seeds | Seeding disabled; all results are single unseeded runs | 🔁 re-run with several fixed seeds: CineMA, DINOv3 ViT-B, one SAM size (M1) |
| CineMA linear/conv segmentation | Invalid (since-fixed slice-misalignment bug) | 🔁 re-run (M1) |
