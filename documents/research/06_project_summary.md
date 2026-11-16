# heartfm-evals — summary and proposed next steps

*November 2026, revised after [verification](verification/06_project_summary_verification.md).
Supporting detail: [REPORT.md](REPORT.md), [03_positioning.md](03_positioning.md),
[04_followups.md](04_followups.md), [05_study_lookup.md](05_study_lookup.md).*

## Background and work to date:

**Cardiac foundation models.** In the domain of cardiovascular modelling, foundation models have been increasingly trained on multi-modal imaging datasets (such as MRI scans, CT scans, PET scans, etc.) and used for various clinically relevant downstream tasks including tissue segmentation in MRI images, disease classification from MRI images, and others. One such recent foundation model, CineMA ([Fu et al., *Commun Med* 2026](https://doi.org/10.1038/s43856-026-01636-0); [code](https://github.com/mathpluscode/CineMA)), was pretrained on UK Biobank cardiac MRI images and was shown to have SOTA performance on various tasks on various open datasets after full fine-tuning. 

**What has been done in HeartFM project.** This project asks whether the frozen features of a general-purpose vision foundation model already capture enough cardiac anatomy and pathology for such clinical tasks, or whether a cardiac-specific model such as CineMA is needed. Tasks are _segmentation_ of various anatomical structures of the heart and patient-level _disease classification_.

We built a benchmark that freezes a pretrained natural-image or cardiac backbone and trains task heads on top. For the segmentation task, we use three decoders: a linear probe, a 2D conv decoder and a UNETR. The classification task uses either logistic-regression or linear heads on pooled features. The
backbones are:
- **CineMA**, a masked-autoencoder (MAE) model pretrained on ~75k UK Biobank cine MRI studies;
- **DINOv3**, (sizes: S/B/L), distilled from a model trained on natural images;
- **SAMv1**, (sizes: B/L/H), trained for natural-image segmentation.

Following CineMA, we have been evaluating on three publicly available datasets: ACDC, M&Ms, and M&Ms-2.

Current WIP results:
- **Classification:** frozen CineMA shows no consistent advantage over frozen DINOv3. It leads on
  ACDC (mostly not significant), is mixed on M&Ms, and trails on M&Ms-2.
- **Segmentation:** with the UNETR decoder, CineMA leads DINOv3 by +1.1 to +2.3 Dice.
- **Frozen vs from scratch:** the best frozen model (CineMA + UNETR; 88.7 / 83.5 / 85.3
  per-volume Dice on ACDC / M&Ms / M&Ms-2) is below the from-scratch UNet reported in the CineMA
  paper (89.5 / 86.0 / 88.0). That baseline is not yet run in this repo.

These results are from a single unseeded run. They need further work and replication with multiple seeded runs.

**Position in the literature.** The study so far addresses a real but narrow gap, and is incremental. A review of ~28 foundation-model studies ([02_literature.md](02_literature.md)) found one published frozen comparison on these datasets: CMR-CLIP ([Nakashima et al., *Nat Commun* 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13194963/)), which covers ACDC disease classification only, against CLIP-family baselines. No study covers M&Ms or M&Ms-2, frozen segmentation, or a cardiac MAE against DINOv3 or SAM. Frozen general models rivalling domain models has precedents in other imaging domains, though the result depends on the task (e.g. [Liu et al., arXiv 2509.06467](https://arxiv.org/abs/2509.06467)). The closest cardiac work, CMRVision ([Jacob, Sharma, Rueckert, 2026](https://arxiv.org/abs/2609.01308)), finds that cardiac-pretrained models consistently beat natural-image ones. But it evaluates only fine-tuned or LoRA-adapted encoders, compares natural vs cardiac pretraining only at ViT-S, and has no disease classification.

## Proposed future work (2–3 months):

We propose to turn the benchmark into a controlled study of *why*
frozen cardiac features do or do not help. Does any advantage come from the training data
(cardiac vs natural images) or from the training method (MAE vs DINO-style self-distillation)?
Prior cardiac work has varied one factor at a time, under fine-tuning and at ViT-S. Jacob et al.
([*JCMR* 2025](https://doi.org/10.1016/j.jocmr.2025.101967)) compare MAE vs DINO on the same cardiac data, and natural vs cardiac
initialisation within DINO; CMRVision varies the data within DINO. No study has run a matched
2×2 of data × method and specifically with frozen evaluation as opposed to fine-tuning.

- **Month 1: replicate existing results, then add cheap analyses.**
  - Enable seeding and re-run the full grid with several seeds. 
  - Run a from-scratch UNet baseline in this repo.
  - Add kNN / nearest-centroid classifiers as a second readout.
  - Add a randomly-initialised-backbone control, to show how much performance comes from
    pretraining at all.
  - Add a _regression_ task for predicting clinically relevant indices such as ejection fraction (EF) and ventricular volumes.
  - Add a classifier on segmentation-derived measurements as the clinical baseline.
- **Month 2: the core 2×2 experiment** at CineMA-matched model size (ViT-B).
  - Take public natural-image DINOv3 and MAE ViT-B models and continue pretraining both on UK
    Biobank cine MRI.
  - Evaluate all four models frozen, using several readouts. 
  - CineMA and SAM models stay as reference points.
- **Month 3: label-efficiency curves.**
  - Compare frozen vs lightly fine-tuned (LoRA) models on a subset of tasks, to test whether
    cardiac pretraining matters most when labels are scarce.
  - *Stretch goal:* full fine-tuning of the same models, as an upper bound on what freezing
    costs (this might take considerable time).
  - Use UK Biobank's large set of cardiac measurements (e.g. LV volumes for ~81k participants)
    for label-efficiency curves at scale.
  - Analyse disease classification alongside segmentation throughout. Caveat: the public test
    sets are small (as few as 6 patients per class), so they have little power to detect
    differences between models.

The main risks:
- **Timing of UK Biobank access.** If it slips, public cine data is likely not sufficient for proper continued pretraining.
- **Small effect sizes.** Mitigated by multiple seeds and confidence intervals.
