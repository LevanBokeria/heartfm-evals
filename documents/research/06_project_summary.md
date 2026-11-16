# heartfm-evals — summary and proposed next steps

*November 2026, revised after [verification](verification/06_project_summary_verification.md).
Supporting detail: [REPORT.md](REPORT.md), [03_positioning.md](03_positioning.md),
[04_followups.md](04_followups.md), [05_study_lookup.md](05_study_lookup.md).*

## Background and work to date:

**Cardiac foundation models.** Foundation models have been increasingly pretrained on multi-modal imaging datasets (MRI, CT, PET etc.) and used for various clinically relevant downstream tasks including tissue segmentation, disease classification, and others. One such recent foundation model, CineMA ([Fu et al., *Commun Med* 2026](https://doi.org/10.1038/s43856-026-01636-0); [code](https://github.com/mathpluscode/CineMA)), was pretrained on UK Biobank cardiac MRI images in a self-supervised manner, and shown to have SOTA performance on various tasks on various open datasets after full fine-tuning. 

**What has been done in HeartFM project.** This project asks whether the frozen features of a general-purpose vision foundation model already capture enough cardiac anatomy and pathology for such clinical tasks, or whether a cardiac-specific model such as CineMA is needed. Tasks are _segmentation_ of cardiac structures and patient-level _disease classification_. We freeze a pretrained natural-image or cardiac backbone and train different task heads on top. For the segmentation task, we use three decoders: a linear probe, a 2D conv decoder and a UNETR. The classification task uses either logistic-regression or a linear head on pooled features. We evaluate on three publicly available datasets: ACDC, M&Ms, and M&Ms-2. The model backbones are: **CineMA**, a masked-autoencoder (MAE); **DINOv3** (sizes: S/B/L), trained on natural images; **SAMv1** (sizes: B/L/H), trained for natural-image segmentation. We use SAM v1 rather than SAM2 because its non-hierarchical ViT encoder is closer to DINOv3 and to CineMA's ViT-B transformer than SAM2's hierarchical Hiera encoder.

Current WIP results:
- **Benchmarking infrastructure**: codebase set up for loading different backbones+decoder combinations and fine-tuning the decoders on various datasets for both segmentation and classification.
- **Classification:** frozen CineMA shows no consistent advantage over frozen DINOv3 (leads on ACDC, mixed on M&Ms and trails on M&Ms-2).
- **Segmentation:** with the UNETR decoder, CineMA leads DINOv3 by +1.1 to +2.3 Dice.

Note: these results are from a single unseeded run, so multi-seed runs are needed. Some backbone+decoder combinations need a rerun after bug-fix. SAMv1 segmentation hasn't been run yet.

**Position in the literature.** The study addresses a narrow gap in the literature, and is incremental. A review of ~30 foundation-model studies ([02_literature.md](02_literature.md)) found no study that applies the same frozen readout to a cardiac foundation model and to general-purpose models on these datasets. The nearest are CMR-CLIP ([Nakashima et al., *Nat Commun* 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13194963/)), which evaluates frozen embeddings on ACDC disease classification against CLIP-family baselines, and Pix2Rep-v2 ([Sifaoui et al., MICCAI 2026](https://arxiv.org/abs/2609.01427)), which linear-probes a cardiac self-supervised U-Net on ACDC, M&Ms and M&Ms-2 against in-context ProtoSAM and zero-shot SAM 3. CineMA has been compared with DINOv3 and SAM2 only under fine-tuning or prompting (CMRVision; Pix2Rep-v2; [Jacob et al., *JCMR* 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12745146/)). Frozen general models rivalling domain models has precedents in other imaging domains, though the result depends on the task (e.g. [Liu et al., arXiv 2509.06467](https://arxiv.org/abs/2509.06467)). The closest cardiac work, CMRVision ([Jacob, Sharma, Rueckert, 2026](https://arxiv.org/abs/2609.01308)), finds that cardiac-pretrained models consistently beat natural-image ones. But it evaluates only fine-tuned or LoRA-adapted encoders, compares natural vs cardiac pretraining only at ViT-S (not ViT-B), and has no disease classification.

## Proposed future work (2–3 months):

We propose to turn the benchmark into a controlled study of *why*
frozen cardiac features do or do not help. Does any advantage come from the training data
(cardiac vs natural images) or from the training method (MAE vs DINO-style self-distillation)?
Prior cardiac work has varied one factor at a time, under fine-tuning and at ViT-S. No study has run a matched
2×2 of data × method with frozen evaluation as opposed to fine-tuning. This proposal strengthens the existing study, although it remains incremental in nature. 

### The core 2×2 design: pretraining data × pretraining method, all ViT-B, evaluated frozen.

| | MAE | DINO |
|---|---|---|
| **Natural images, as released** | MAE ViT-B | DINOv3 ViT-B |
| **Natural images, then UK Biobank cine MRI** | MAE → UK Biobank | DINOv3 → UK Biobank |

- **Month 1: harden the evaluation pipeline.**
  - Re-run with several seeds; Run a from-scratch UNet baseline in this repo; Add a randomly-initialised-backbone control, to show how much performance comes from pretraining at all.
  - Add kNN / nearest-centroid classifiers as a second readout for disease classification.
  - Add an attentive probe over patch tokens for disease classification. Linear readouts are known to understate MAE features, which would bias the MAE vs DINO comparison in the 2×2.
  - Add a _regression_ task for predicting ejection fraction (EF) and ventricular volumes.
- **Month 2: the core 2×2 experiment** at CineMA-matched model size (ViT-B).
  - Take public natural-image DINOv3 and MAE ViT-B models and continue pretraining both on UK Biobank cine MRI.
  - Evaluate all four models frozen, using several readouts. CineMA and SAM models stay as reference points: CineMA is an MAE but differs in architecture and input (conv stem, 3D input), and SAM's encoder is MAE-initialised but then trained with supervision.
- **Month 3: label-efficiency curves.**
  - Use UK Biobank's large set of cardiac measurements (e.g. LV volumes for ~81k participants)
    for label-efficiency curves at scale, for the four 2×2 models and the CineMA and SAM
    references, all frozen.
  - *Stretch goal:* LoRA and full fine-tuning of the same models, as an upper bound on what freezing
    costs (this might take considerable time).

## Scope at a glance: done vs proposed

M1–M3 = month of the proposed work · ⭐ = stretch goal

| Factor | ✅ Done so far | 🆕 Proposed |
|---|---|---|
| **Backbones** | CineMA (ViT-B)<br>DINOv3 (S, B, L)<br>SAM (B, L, H), classification only | SAM v1 segmentation, one size (M1)<br>Random-init control, CineMA architecture (M1)<br>MAE ViT-B, natural images (M2)<br>DINOv3 ViT-B → UK Biobank (M2)<br>MAE ViT-B → UK Biobank (M2) |
| **Continued pretraining on cardiac MRI** | None: natural-image models used as released | DINOv3 ViT-B and MAE ViT-B on UK Biobank cine MRI (M2) |
| **Backbone adaptation** | Frozen | LoRA ⭐<br>Full fine-tuning ⭐ |
| **Segmentation heads** | Linear probe<br>Conv decoder<br>UNETR | — |
| **Classification heads** | Logistic regression<br>Linear | kNN / nearest centroid (M1)<br>Attentive probe over patch tokens (M1) |
| **Regression heads** | — | Linear probe (M1) |
| **Tasks** | Segmentation (LV, RV, myocardium)<br>Disease classification (patient-level) | Ejection fraction and ventricular volumes (M1)<br>UK Biobank cardiac measurements, with label-efficiency curves (M3) |
| **Datasets** | ACDC<br>M&Ms<br>M&Ms-2 | UK Biobank cine MRI: continued pretraining (M2)<br>UK Biobank cardiac measurements: evaluation (M3) |
| **Baselines and reliability** | From-scratch UNet cited from the CineMA paper<br>All results single unseeded runs<br>Certain results need re-running post bug-fix | From-scratch UNet run in this repo (M1)<br>Random-init backbone control (M1)<br>Re-run with several fixed seeds: CineMA, DINOv3 ViT-B, one SAM size (M1) |
