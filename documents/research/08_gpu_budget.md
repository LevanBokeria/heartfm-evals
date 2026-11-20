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
| Month 2: continued pretraining (2 arms + data-scaling curve) and evaluation | 75 | **235** | 880 |
| Month 3: UKB label-efficiency curves | 15 | **45** | 115 |
| Debugging / failed-run contingency (+15 / +30 / +50 %) | 35 | **160** | 755 |
| **Core plan, GH200-hours** | **~285** | **~700** | **~2,250** |
| Core plan, A100-80GB-equivalent hours | ~570 | ~1,400 | ~4,500 |
| Core plan, Isambard-AI node-hours | ~70 | ~175 | ~565 |
| *Stretch goals (separable): LoRA + full fine-tuning, incl. contingency* | *~190* | *~600* | *~2,600* |
| *Core + stretch, GH200-hours* | *~475* | *~1,300* | *~4,850* |
| *High-resolution add-on (separable, §2.8), incl. contingency* | *~25* | *~100* | *~565* |
| *…plus natural-image DINOv3 + MAE also evaluated at 512 px* | *~35* | *~130* | *~665* |

**What drives the total:**
- **nnU-Net (~170 h central) is the largest single item.**
- **Continued pretraining as a whole is ~155 h central:** the two main runs (~65 h), pilots and sweeps (~40 h) and the data-scaling curve (~50 h).
- **The data-scaling curve is cheap because each subset is trained for the same number of epochs as the main run, with a minimum of 15k iterations (central)** (see §2.3). Its evaluation (~60 h central for 10 checkpoints on the full grid) costs more than its training. The earlier design, with every subset trained for the same number of images as the main run, cost ~335 h central.
- **SAM v1 is expensive to train decoders on.** Its encoder runs at 1024 px, so with online augmentation SAM segmentation costs about 40 h central and 150 h high.
- **The range is wide (~8× low to high).** It mostly reflects how long continued pretraining needs to run (15M–100M images for DINOv3, 50M–400M for MAE), how many pilots it needs, and real throughput on GH200. A one-hour throughput benchmark on Isambard-AI in week 1 of Month 2 would narrow it a lot.

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

**Gram anchoring and high-resolution adaptation.** Both are left out of the core plan. A high-resolution stage is costed as an optional add-on in §2.8. Prior literature does use both:

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
- **Frames per participant:** about 10 SAX slices (8 mm slices, 2 mm gap, "approximately ×10") plus 3 LAX cines (2-, 3- and 4-chamber), each with 50 phases (V, [Petersen et al. 2016, Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4736703/), checked by hand). That is about 13 slice positions and ~650 frames per participant, or ~49M frames for 75k participants, consistent with the 50–65M in [04_followups.md](04_followups.md) (D).
- **Phases: sample from all 50, one random phase per (participant, slice) per pass.**
  - This is CineMA's scheme (`t = rng.integers(50)`).
  - MR-JEPA samples 8 frames, and ViTa uses 5 evenly spaced frames.
  - Restricting pretraining to ED/ES only (Hager) is the exception.
  - If storage is tight, keep every 5th phase plus ED and ES.
- **Epoch definition used in this budget:** one pass = one random phase per (participant, slice position), so ~13 images per participant and ~975k images per epoch for 75k participants (D). The central main runs are then ~51 epochs (DINOv3, 50M images) and ~154 epochs (MAE, 150M).
- **Cost.** For the main runs, neither the view choice nor the phase choice changes the cost: cost scales with images seen, not with dataset size. For the data-scaling runs, cost does scale with subset size (§2.3).

### 2.3 Data-scaling curve

- **Subsets:** nested **1k / 5k / 20k / ~75k (= main run) participants**, with **3 random draws at 1k**, the noisiest point. That is 5 extra runs per arm, for both arms.
- **Precedents:**
  - Ilse et al.: 30k / 50k / 100k / 1M / 3.5M images, nested, 3 draws at the small sizes. They found 30k–100k in-domain images already beat the open weights.
  - Xiao et al.: 75k → 510k chest X-rays; ViT-S saturated at 266k.
  - Neither Jacob et al. nor CMRVision ran a data-scaling study.
- **Training length rule [I]: the same number of epochs as the main run, with a minimum of 10k / 15k / 20k iterations (low / central / high) at batch 512.**
  - Fixed epochs follows Ilse et al., who trained every subset size for 15 epochs. Compute then grows with data size, so the curve answers "what does a dataset of this size give, trained in the usual way?" rather than "what does data alone buy at equal compute?". The write-up should say so.
  - **Why a minimum:** at a fixed epoch count alone, the 1k subset would get only ~1,300 iterations in the central DINOv3 scenario (51 epochs × 13k images), too few to move far from the natural-image starting point. The curve would then confound less data with too little training.
  - **Why 10k–20k iterations:** this is the order of the short phases used to adapt an already-trained DINOv3 model: the high-resolution phase (§2.8) and a Gram phase if added (§2.1). At the central 15k iterations (7.7M images) the 1k subset makes about 12 passes over each of its ~650k frames, close to Ilse et al.'s 15 epochs.
  - **Which subsets hit the minimum (central):** DINOv3 at 1k and 5k; MAE at 1k only. The 20k subsets, and MAE at 5k, are above it.
- **Cost:** ~50 h central for both arms (19 / 50 / 132 h low / central / high).
  - The earlier rule, the **same images seen** as the main run for every subset, made data the only variable but cost ~335 h central (74 / 336 / 1,157 h). It also meant ~3,800 passes over the 1k subset's slice positions (~77 over every frame), a real overfitting risk.

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

### 2.8 Optional add-on: high-resolution stage (separable)

**Design:**
- Add a short high-resolution phase only to the two **full-data** continued-pretraining models (DINOv3 → UKB, MAE → UKB). The scaling checkpoints don't get one.
- Evaluate both models at **512 px and at 224 px** on a reduced grid: the best decoder (likely UNETR) plus the classification heads, on 3 datasets × 3 seeds.
- Report it as a separate ablation: does resolution change the domain-vs-method conclusion?
- *Optional:* also evaluate the natural-image DINOv3 and MAE at 512 px, so that the full 2×2 is compared at 512. Released DINOv3 ViT-B already had a high-resolution phase; MAE did not.

**Recipe and cost assumptions [I]:**
- **DINOv3:** follows the DINOv3 and MedDINOv3 recipe: **5k / 10k / 20k iterations** (low / central / high) at batch 512, global crops 512–768 px and local crops 112–336 px (V for the recipe).
  - Per image this costs about **4 / 6 / 9 ×** the 224 px recipe: about 4–5× the tokens, plus quadratic attention.
  - That gives about **6 / 27 / 128 GH200-h**.
- **MAE:** there is no published high-resolution phase for MAE, so I assume the same number of images at 512 px. That gives about **1 / 5 / 21 GH200-h**, because MAE's encoder sees only 25 % of the tokens.
- **Pilots:** 0.3 / 0.5 / 1.0 × the phase.
- **Evaluation at 512 px:** about 5 / 6 / 8 × the 224 px cost.

| Item (GH200-hours) | Low | Central | High |
|---|---|---|---|
| High-resolution pretraining phase (DINOv3 + MAE) | 7 | 32 | 149 |
| Pilots | 2 | 16 | 149 |
| Evaluation of the 2 models at 512 px, reduced grid | 9 | 23 | 67 |
| Evaluation of the 2 models at 224 px, reduced grid | 3 | 5 | 11 |
| Contingency (+15 / +30 / +50 %) | 3 | 23 | 188 |
| **Add-on total** | **~25** | **~100** | **~565** |
| *Optional: natural-image DINOv3 + MAE at 512 px (incl. contingency)* | *+10* | *+30* | *+100* |

**Try heart-centred cropping first [I].** Cropping around the heart at 224 px raises the effective resolution of the heart at no pretraining cost, and may give most of the same benefit. It is worth testing before committing to this add-on.

**Storage:** at 512 px each image has 1,024 patch tokens rather than 196, so cached features for these models are about 5× larger.

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
| M2 data-scaling runs (5 per arm, fixed epochs, minimum 10k / 15k / 20k iterations) | 19 | 50 | 132 |
| M2 evaluation: 3 new backbones, full grid | 8 | 18 | 40 |
| M2 evaluation: 10 scaling checkpoints, full grid | 28 | 60 | 132 |
| M3 UKB feature extraction (7 backbones, ~420k images each) | 5 | 11 | 29 |
| M3 UKB label-efficiency heads (3 heads × 9 subsets × 7 backbones) | 7 | 21 | 57 |
| M3 label generation for post-cut-off cohort (conditional) | 5 | 15 | 30 |
| Debugging / failed-run contingency (+15 / +30 / +50 %) | 37 | 160 | 753 |
| **Core total** | **284** | **694** | **2,259** |
| Stretch: full fine-tuning, 5 ViT-B-class backbones | 34 | 74 | 187 |
| Stretch: full fine-tuning, SAM at 1024 px | 44 | 145 | 676 |
| Stretch: LoRA, 5 ViT-B-class backbones | 31 | 67 | 167 |
| Stretch: LoRA, SAM at 1024 px | 38 | 124 | 576 |
| Stretch: fine-tuning on UKB at the 1 % / 10 % budgets (optional) | 20 | 50 | 120 |
| Stretch contingency (+15 / +30 / +50 %) | 25 | 138 | 863 |
| **Stretch total** | **192** | **597** | **2,590** |
| High-resolution add-on (§2.8): pretraining phase + pilots | 9 | 48 | 298 |
| High-resolution add-on: evaluation at 512 + 224 px, reduced grid | 12 | 28 | 78 |
| High-resolution add-on contingency | 3 | 23 | 188 |
| **High-resolution add-on total** | **~25** | **~100** | **~565** |
| *Optional: natural-image DINOv3 + MAE at 512 px (incl. contingency)* | *10* | *30* | *100* |

## 4. Ways to cut the budget, in order of hours saved [I]

1. **nnU-Net 3d_fullres only, no 2d / ensemble:** −75 h central.
2. **Cache SAM features (no augmentation) or run SAM at 512 px:** −35 h central, −145 h high. Stretch fine-tuning saves another −200 h central.
3. **Evaluate scaling checkpoints on one decoder (UNETR) plus the classification heads:** −35 h central.
4. **A one-hour DINOv3 / MAE throughput benchmark on Isambard-AI before committing:** it saves no hours itself, but it collapses most of the low-to-high range for Month 2.

## 5. Not included

- **CPU-only work:** UKB DICOM → 2D frame conversion and sharding, nnU-Net preprocessing, logreg/kNN fitting.
- **Storage:** roughly 125 GB of patch tokens per backbone for UKB, plus the public-dataset caches already estimated at ~640 GB (see `documents/refreshers/2026-09-11-segmentation.md`, B1).
- **Development and interactive debugging:** partly covered by the contingency line.
- **DINOv3 S and L, and the other SAM sizes:** not re-run, per [07_scope_tables.md](07_scope_tables.md).
- **The Q3 tasks from [04_followups.md](04_followups.md):** out of scope.
