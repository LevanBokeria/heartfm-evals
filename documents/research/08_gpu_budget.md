# 08 — GPU-hour budget for the proposed 3-month work

*November 2026. Estimates the compute for the plan in [06_project_summary.md](06_project_summary.md)
and [07_scope_tables.md](07_scope_tables.md). Every number comes from
[08_gpu_budget_model.py](08_gpu_budget_model.py), which holds all the assumptions in one place.
Change a parameter there and re-run it.
Conventions as in [04_followups.md](04_followups.md):*
- *Status markers:*
  - ***V*** *= the number was read in the primary source by a research sub-agent.*
  - ***D*** *= derived by arithmetic from V numbers.*
  - ***[I]*** *= my assumption or inference.*
- *Not re-checked by hand: every literature number below is sub-agent-verified. I did not re-open each source myself.*
- *Not accessed: nature.com (login redirect) and ukbiobank.ac.uk (403).*

## Bottom line

**Units:**
- **GPU-hours** means hours on one GH200 (Isambard-AI). We will run on Isambard-AI, so this is what gets charged.
- **A100-equivalents** are for comparison with papers that report A100 hours: 1 A100-h ≈ 0.5 GH200-h.
- **Node-hours** = GPU-hours / 4, since Isambard-AI allocates whole nodes of 4 GH200.

| | Low | **Central** | High |
|---|---|---|---|
| Month 1: hardening, new heads, nnU-Net, SAM segmentation | 155 | **250** | 510 |
| Month 2: continued pretraining (2 arms + data-scaling curve) and evaluation | 130 | **520** | 1,905 |
| Month 3: UKB label-efficiency curves | 15 | **45** | 115 |
| Debugging / failed-run contingency (+15 / +30 / +50 %) | 45 | **245** | 1,265 |
| **Core plan, GH200-hours** | **~350** | **~1,050** | **~3,800** |
| Core plan, A100-80GB-equivalent hours | ~700 | ~2,100 | ~7,600 |
| Core plan, Isambard-AI node-hours | ~90 | ~265 | ~950 |
| *Stretch goals (separable): LoRA + full fine-tuning, incl. contingency* | *~190* | *~600* | *~2,600* |
| *Core + stretch, GH200-hours* | *~540* | *~1,650* | *~6,400* |

**What drives the total:**
- **The data-scaling curve is the largest item:** about 335 of 1,050 central hours. Each subset model is trained for the same number of images as the full-data model (see §2.3). Training each subset for a fixed number of epochs instead would cut this item several-fold.
- **nnU-Net (~170 h central)** is the next largest.
- **SAM v1 is expensive to train decoders on.** Its encoder runs at 1024 px, so with online augmentation SAM segmentation costs about 40 h central and 150 h high.
- **The two main continued-pretraining runs are cheap: ~65 h central for both arms together.**
- **The range is wide (~10× low to high).** It mostly reflects how long continued pretraining needs to run (15M–100M images for DINOv3, 50M–400M for MAE) and real throughput on GH200. A one-hour throughput benchmark on Isambard-AI in week 1 of Month 2 would narrow it a lot.

**Comparison with the earlier estimate.** [04_followups.md](04_followups.md) Q2 guessed "a few hundred H100-hours per ViT-B run". The central estimate here is ~45 GH200-h per DINOv3 run and ~25 h per MAE run. The two cardiac anchors that estimate drew on cost far more per image because they process many more tokens:
- Jacob et al. used ViT-S/8: 784 tokens per 224 px image.
- RAD-DINO used 518 px input: about 1,370 tokens per image.
- A ViT-B/16 at 224 px processes 196 tokens.

Calibrating on the DINOv3 repo's own ViT-L recipe on H100s (§2.1) gives the lower figure. The high scenario (≈140 h DINOv3, ≈95 h MAE per run) is close to the old guess.

---

## 1. Hardware and unit conversions

| Fact | Value | Status |
|---|---|---|
| Isambard-AI node | 4 × GH200 (Grace CPU + H100 GPU, 96 GB HBM3 each), 72 Grace cores per GPU, 460 GB CPU RAM per node; each GH200 capped at 660 W shared between CPU and GPU | V ([docs.isambard.ac.uk/specs](https://docs.isambard.ac.uk/specs/), [arXiv 2410.11199](https://arxiv.org/abs/2410.11199)) |
| GH200 GPU peak | 990 TFLOPS dense BF16, 4 TB/s | V (NVIDIA GH200 datasheet) |
| H100 / A100 ViT-B training speed-up | 2.2× (NeMo ViT-B/16 bf16 benchmark) | V |
| GH200 / A100 | 1.7–2.45× (ViT-L fine-tuning; GPT training, [CARAML](https://arxiv.org/html/2409.12994v1)) | V |
| Conversion used | 1 A100-h ≈ **0.50** (0.42–0.63) GH200-h; 1 H100 SXM-h ≈ **1.05** (0.90–1.15) GH200-h; 1 V100-h ≈ 0.22 GH200-h | D |

No published benchmark compares GH200 with H100 directly. The H100 factor is above 1 because of the 660 W shared power cap. CARAML measured a similar 4-per-node layout running about 20 % slower per device.

## 2. Design choices taken from the literature

### 2.1 Continued-pretraining length (Month 2)

**Literature anchors for continued pretraining:**

| Work | Model, initialisation | Images seen | Compute (native → GH200-equivalent) | Status |
|---|---|---|---|---|
| RAD-DINO, paper ([2401.10815](https://arxiv.org/abs/2401.10815)) | ViT-B/14 from DINOv2, 518 px | 38M (60k steps × 640) | not reported | V |
| RAD-DINO, released weights | same | 90M (35k × 2,560) | 2,560 A100-h → ~1,280 GH200-h | V / D |
| MedDINOv3 ([2509.02379](https://arxiv.org/abs/2509.02379)) | ViT-B/16 from DINOv3, CT | 61M (120k × 512) | not reported | V |
| Jacob et al. JCMR 2025 ([PMC12745146](https://pmc.ncbi.nlm.nih.gov/articles/PMC12745146/)) | ViT-S/8 from natural-image DINO, CMR incl. 16k UKB | not stated (36M-image set) | 8×H100×7 d = 1,344 H100-h → ~1,410 GH200-h | V |
| CMRVision ([2609.01308](https://arxiv.org/abs/2609.01308)) | ViT-S/8 and /16 from DINOv3, same data | not stated; "7 days" | GPU type and count not stated | V |
| RETFound (Nature 2023, [PMC10550819](https://pmc.ncbi.nlm.nih.gov/articles/PMC10550819/)) | MAE ViT-L from ImageNet MAE | 723M (800 ep × 904k) | 8×A100×14 d ≈ 2,690 A100-h → ~1,340 GH200-h | V |
| Ma et al. 2022 ([PMC9646404](https://pmc.ncbi.nlm.nih.gov/articles/PMC9646404/)) | SimMIM Swin-B from ImageNet | ~93M (100 ep × 926k) | not reported | V |
| CineMA ([2506.00679](https://arxiv.org/abs/2506.00679), repo) | MAE ViT-B + conv stem, **from scratch**, 3D SAX + LAX | 60M multi-view samples (800 ep) | 8×A6000×18 d ≈ 3,460 A6000-h → very roughly 400–500 GH200-h | V / D (rough) |
| Ilse et al. ([2509.12818](https://arxiv.org/abs/2509.12818)) | RAD-DINO/MI2 continued, 30k → 3.5M images | 15 epochs at each size | 11 → 1,307 H100-h; compute ∝ data size | V / D |

**Throughput calibration.** The DINOv3 repo trains a ViT-L on ImageNet-1k (256M samples, 2×224 + 8×96 crops) in about 14 h on 32 H100s. That is about 159 img/s per H100 (V/D). A ViT-B is about 3.5× cheaper in FLOPs but uses the GPU less efficiently. I therefore use **250 / 350 / 480 img/s per GH200** for DINOv3-style ViT-B training. For MAE ViT-B (75 % masking) I use **1,500 / 2,000 / 2,600 img/s**, which data loading will probably limit.

**Proposed training lengths [I]:**

| | Low | **Central** | High | GH200-h per run (low / central / high) |
|---|---|---|---|---|
| DINOv3 ViT-B/16 → UKB, 224 px | 15M images (~30k iterations at batch 512) | **50M (~100k iterations)** | 100M (~200k iterations) | 9 / **44** / 139 |
| MAE ViT-B/16 → UKB, 224 px | 50M | **150M** | 400M | 6 / **23** / 93 |

- The DINOv3 central value sits between RAD-DINO's paper run and MedDINOv3.
- The MAE central value is higher because MAE is usually trained for more images seen. RETFound's 723M is the upper anchor; the 50M–93M runs (CineMA, Ma et al.) are the lower anchors.

**Scaling efficiency.** Multi-GPU scaling efficiency is set at 95 / 90 / 80 %. In practice a central DINOv3 run takes about 11 h wall-clock on one node (4 GPUs), or about 3 h on 4 nodes.

**Gram anchoring and high-resolution adaptation (out of scope as requested).** Prior literature does use them:

| Work | Gram anchoring | High-resolution adaptation |
|---|---|---|
| **CMRVision**, the closest CMR precedent | **Yes**: "early Gram anchoring, enabled by NI initialisation", Gram teacher refreshed every 20k iterations. Not ablated. | No ≥512 px stage. It trains at half resolution (112 px) and then at 224 px. Jacob et al. do the same. |
| **MedDINOv3** | **Yes**, but **no gain** (AMOS 86.58 → 86.54) | **Yes**: +0.84 DSC, measured at 896 px input |
| **DINOv3 itself** | Applied only to the 7B teacher. **The released ViT-B was distilled and never Gram-trained.** | Yes, the released ViT-B had a high-resolution phase |

- Leaving Gram out is consistent with how the starting checkpoint was made.
- If added later as an ablation, a 10–20k-iteration Gram phase costs roughly +10–20 % per DINOv3 run.
- Adopting the half-then-full resolution schedule (112 px then 224 px) would cut DINOv3 cost by roughly 30 % [I]. It is not assumed here.

### 2.2 Pretraining data [I, from literature]

- **Participants.** Use UKB first-visit participants scanned **before 6 Nov 2023**: about 75k, matching CineMA's 74,916 studies.
  - This matches the largest prior CMR pretraining set.
  - It also keeps the Month-3 post-cut-off test cohort unseen by **every** backbone, not only CineMA.
  - Using all ~96k SAX studies would contaminate the Month-3 evaluation.
- **Views: SAX + LAX 2/3/4-chamber, as 2D frames.** CineMA, ViTa, Jacob et al. and CMRVision all pretrain on SAX plus LAX. ViTa reports that joint views help. M&Ms-2 evaluation includes LAX 4ch.
- **Phases: sample from all 50, one random phase per (participant, slice) per pass.**
  - This is CineMA's scheme (`t = rng.integers(50)`).
  - MR-JEPA samples 8 frames, and ViTa uses 5 evenly spaced frames.
  - Restricting pretraining to ED/ES only (Hager) is the exception.
  - If storage is tight, keep every 5th phase plus ED and ES.
- **Cost.** Neither the view choice nor the phase choice changes the cost: cost scales with images seen, not with dataset size.

### 2.3 Data-scaling curve

- **Subsets:** nested **1k / 5k / 20k / ~75k (= main run) participants**, with **3 random draws at 1k**, the noisiest point. That is 5 extra runs per arm, for both arms.
- **Precedents:**
  - Ilse et al.: 30k / 50k / 100k / 1M / 3.5M images, nested, 3 draws at the small sizes. They found 30k–100k in-domain images already beat the open weights.
  - Xiao et al.: 75k → 510k chest X-rays; ViT-S saturated at 266k.
  - Neither Jacob et al. nor CMRVision ran a data-scaling study.
- **Budget rule:** every subset is trained for the **same images seen** as the main run, so data is the only variable. This is conservative.
  - Ilse et al. instead held epochs fixed, so compute grows with data size.
  - That would cut this line from ~335 h to roughly 25 h central: the five subsets together hold about 0.4× the main run's data.

### 2.4 Evaluation grid (Months 1–2)

- **Backbones on the full grid:**
  - CineMA, DINOv3 ViT-B and SAM v1 ViT-B (re-seeded);
  - random-init (CineMA architecture);
  - MAE ViT-B (natural images);
  - DINOv3 → UKB and MAE → UKB;
  - the 10 data-scaling checkpoints.
- **Full grid** = 3 segmentation decoders × 3 datasets × **3 seeds**, plus logreg / linear / kNN / attentive-probe classification and EF/volume regression.
- **Online augmentation [I]:** because you plan image augmentation, I assume the frozen backbone runs on every training step instead of reading cached features. This is what makes SAM at 1024 px expensive (cost 10 / 15 / 25 × a ViT-B at 224 px).
  - If SAM features were cached without augmentation, the SAM line would mostly disappear.
  - Running SAM at 512 px would cut it about 4×.
- **Workload:** about 8,100 training slices per epoch across ACDC + M&Ms + M&Ms-2 (ED + ES; from cache file counts in `documents/refreshers/2026-09-11-segmentation.md`). Up to 100 epochs, with early stopping at patience 20 (repo defaults).
- **Decoder / augmentation pilot sweep:** included, since the augmentation pipeline is new.
- **Attentive probe:** 15–20 heads (5 learning rates × 3–4 weight decays) trained jointly for about 20 epochs, which is the low end of V-JEPA 2 (20 heads) and CAPI (30 heads) (V).

### 2.5 nnU-Net baseline

- **What is budgeted:** **2d and 3d_fullres, 5 folds each, on all 3 datasets = 30 trainings** of 1000 epochs × 250 iterations.
  - This is what the nnU-Net paper reports for ACDC: 5-fold CV for each configuration, with the 2d + 3d ensemble best.
  - The M&Ms winner also used a 5×2D + 5×3D ensemble.
- **Cost per fold:** about 4.5 h (2d) and 6 h (3d_fullres) on a GH200.
  - Derived from nnU-Net's own benchmark sheet: MSD Heart, 22–31 s per epoch on H100 PCIe (V/D). ACDC is not in the sheet.
  - Cost per fold does not depend on dataset size (fixed 250 iterations per epoch).
- **Seeds:** the 5 folds stand in for the 3 seeds. Repeating the full 5-fold training 3 times would triple this line to about 500 h central.
- **Risk:** data augmentation on ARM Grace CPUs is untested. Raise `nnUNet_n_proc_DA` above the default.

### 2.6 Month 3: UK Biobank label-efficiency curves

- **Cohort:** first imaging visit after 6 Nov 2023. About **21k participants** have SAX cine. This is derived from Showcase field 20209 (95,937 SAX studies) minus CineMA's 74,916. Field 53 deciles put about 24 % of imaging visits after the cut-off (V/D).
- **Inputs: SAX stack at ED + ES** (about 10 slices × 2 frames per participant, so about 420k 2D images per backbone).
  - This is exactly CineMA's EF/volume regression input (`np.stack([ed_image, es_image])`, V).
  - Hager et al. likewise used ED + ES.
  - All-50-phase inputs are rare (Radhakrishnan; ViTa, which subsamples to 5 frames).
- **Label budgets: 1 %, 10 % and 100 % of the training split, with 3 random nested subsets per budget.**
  - This is the low end of accepted practice: Hager et al. (UKB, 1 % / 10 % / 100 %); Shad et al. (UKB LVEF, 1 % / 10 %, 5 replicates); CineMA (3 seeds); V-JEPA and MSN (3 splits) (all V).
  - With about 15k training participants, 1 % is about 150 labels.
- **Heads:** linear (ridge), kNN and the attentive probe, all on cached features. Features fit in a node's 460 GB of RAM; patch tokens for 420k images at ViT-B size are about 125 GB per backbone in bf16.
- **Backbones:** the four 2×2 models, CineMA, SAM and random-init (7).
  - Scaling checkpoints are not run on UKB in this budget.
  - Adding them at linear + kNN only would cost under 10 h.
- **⚠ Label availability (unverified).** The automated Bai-pipeline phenotypes (fields 24100–24107) cover **80,974 participants**. That is close to the pre-cut-off imaged cohort, so the post-cut-off participants may **not have phenotypes yet**. The budget includes a conditional 5–30 h to segment that cohort ourselves (e.g. with the nnU-Net models above) and derive volumes and EF. This should be checked on the Showcase or the Research Analysis Platform before Month 3.

### 2.7 Stretch goals (separable)

- **Scope:** **LoRA and full fine-tuning** of the four 2×2 models, CineMA and SAM:
  - on segmentation (one decoder), classification and EF regression;
  - on all 3 public datasets;
  - 3 learning-rate pilots plus 3 seeds.
- **Epochs:** up to **200, with early stopping**, as in CMRVision, MeLo and SAMed (V).
  - CineMA itself fine-tuned for 4,000 (segmentation) and 800 (classification) epochs (V).
  - Matching CineMA would multiply this block 5–20×.
- **LoRA cost:** LoRA ≈ 0.85× the time of full fine-tuning. LoRA saves memory more than time: 7–23 % faster for dense prediction ([E3VA](https://arxiv.org/abs/2306.09729), V).
- **Optional UKB line:** fine-tuning on UKB at the 1 % and 10 % budgets.
- **SAM at 1024 px is again most of the cost:** about 270 of the ~460 h central before contingency.

## 3. Line-item budget (GH200-hours)

| Item | Low | Central | High |
|---|---|---|---|
| M1 segmentation: CineMA, DINOv3-B, random-init (ViT-B class) × 3 decoders × 3 seeds | 7 | 15 | 34 |
| M1 segmentation: SAM v1 ViT-B at 1024 px × 3 decoders × 3 seeds | 11 | 38 | 151 |
| M1 decoder / augmentation pilot sweep | 9 | 20 | 45 |
| M1 classification + regression heads (incl. attentive probe, kNN, EF) | 3 | 8 | 23 |
| M1 nnU-Net (2d + 3d_fullres, 5 folds, 3 datasets) | 126 | 170 | 256 |
| M2 continued pretraining: main runs (DINOv3 + MAE) | 15 | 67 | 231 |
| M2 pilots and hyperparameter sweeps (0.3 / 0.6 / 1.5 × main runs) | 4 | 40 | 347 |
| M2 data-scaling runs (5 per arm, fixed images seen) | 74 | 336 | 1,157 |
| M2 evaluation: 3 new backbones, full grid | 8 | 18 | 40 |
| M2 evaluation: 10 scaling checkpoints, full grid | 28 | 60 | 132 |
| M3 UKB feature extraction (7 backbones, ~420k images each) | 5 | 11 | 29 |
| M3 UKB label-efficiency heads (3 heads × 9 subsets × 7 backbones) | 7 | 21 | 57 |
| M3 label generation for post-cut-off cohort (conditional) | 5 | 15 | 30 |
| Debugging / failed-run contingency (+15 / +30 / +50 %) | 45 | 246 | 1,266 |
| **Core total** | **347** | **1,066** | **3,797** |
| Stretch: full fine-tuning, 5 ViT-B-class backbones | 34 | 74 | 187 |
| Stretch: full fine-tuning, SAM at 1024 px | 44 | 145 | 676 |
| Stretch: LoRA, 5 ViT-B-class backbones | 31 | 67 | 167 |
| Stretch: LoRA, SAM at 1024 px | 38 | 124 | 576 |
| Stretch: fine-tuning on UKB at the 1 % / 10 % budgets (optional) | 20 | 50 | 120 |
| Stretch contingency (+15 / +30 / +50 %) | 25 | 138 | 863 |
| **Stretch total** | **192** | **597** | **2,590** |

## 4. Ways to cut the budget, in order of hours saved [I]

1. **Data-scaling runs at fixed epochs instead of fixed images seen:** −310 h central (−1,070 h high). This changes the question slightly: data size and compute then vary together, as in Ilse et al.
2. **Cache SAM features (no augmentation) or run SAM at 512 px:** −35 h central, −145 h high. Stretch fine-tuning saves another −200 h central.
3. **nnU-Net 3d_fullres only, no 2d / ensemble:** −75 h central.
4. **Evaluate scaling checkpoints on one decoder (UNETR) plus the classification heads:** −35 h central.
5. **A one-hour DINOv3 / MAE throughput benchmark on Isambard-AI before committing:** it saves no hours itself, but it collapses most of the low-to-high range for Month 2.

## 5. Not included

- **CPU-only work:** UKB DICOM → 2D frame conversion and sharding, nnU-Net preprocessing, logreg/kNN fitting.
- **Storage:** roughly 125 GB of patch tokens per backbone for UKB, plus the public-dataset caches already estimated at ~640 GB (see `documents/refreshers/2026-09-11-segmentation.md`, B1).
- **Development and interactive debugging:** partly covered by the contingency line.
- **DINOv3 S and L, and the other SAM sizes:** not re-run, per [07_scope_tables.md](07_scope_tables.md).
- **The Q3 tasks from [04_followups.md](04_followups.md):** out of scope.
