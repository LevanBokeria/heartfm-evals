# heartfm-evals — summary and proposed next steps

*November 2026, revised after [verification](verification/06_project_summary_verification.md).
Supporting detail: [REPORT.md](REPORT.md), [03_positioning.md](03_positioning.md),
[04_followups.md](04_followups.md), [05_study_lookup.md](05_study_lookup.md).*

**What has been done.** The project asks whether the frozen features of a general-purpose vision
foundation model already capture enough cardiac anatomy and pathology for clinical tasks, or
whether a cardiac-specific model is needed. We built a benchmark that freezes a pretrained
backbone and trains task heads on top. The heads range from linear probes (a few thousand
parameters) to a UNETR decoder (31–48M parameters, which also sees the raw image). The backbones
are:
- **CineMA**, a masked-autoencoder (MAE) model pretrained on ~75k UK Biobank cine MRI studies;
- **DINOv3** (S/B/L), distilled from a model trained on natural images;
- **SAM** (B/L/H), trained for natural-image segmentation, with an MAE-initialised encoder.

Tasks are segmentation of the LV, RV and myocardium, and patient-level disease classification
(5 classes on ACDC and M&Ms, 6 on M&Ms-2). We use the official challenge test splits, as CineMA
does. The classification test sets match CineMA's exactly (50/105/108 patients); the
segmentation test sets for M&Ms and M&Ms-2 are slightly smaller (134/157 vs 160/160). SAM has so
far been evaluated for classification only.

Current results:
- **Classification:** frozen CineMA shows no consistent advantage over frozen DINOv3. It leads on
  ACDC (mostly not significant), is mixed on M&Ms, and trails on M&Ms-2.
- **Segmentation:** with the UNETR decoder, CineMA leads DINOv3 by +1.1 to +2.3 Dice. This is
  partly confounded by architecture: CineMA gets 3D input and its own pretrained conv skips.
- **Frozen vs from scratch:** the best frozen model (CineMA + UNETR; 88.7 / 83.5 / 85.3
  per-volume Dice on ACDC / M&Ms / M&Ms-2) is below the from-scratch UNet reported in the CineMA
  paper (89.5 / 86.0 / 88.0). That baseline is not run in this repo, and its test sets differ
  slightly from ours.

None of these results is reliable yet:
- Seeding has been disabled since April 2026 (issue #59), so every committed result is a single
  unseeded run. Run-to-run noise (up to ~0.7 Dice points) can swamp differences between DINOv3
  sizes, though not the CineMA–DINOv3 UNETR margin.
- Six CineMA linear/conv segmentation results are invalid because of a since-fixed slice
  misalignment bug.
- SAM v1 segmentation needs re-running. The "SAM" rows in the committed segmentation summary
  CSVs are SAM2, a backbone since removed. The classification summary and significance-test CSVs
  are stale.
- Our classification AUROC is one-vs-rest; CineMA reports one-vs-one, so the two are not
  directly comparable.

**Position in the literature.** A review of ~28 foundation-model studies found one published
frozen comparison on these datasets: CMR-CLIP (Nakashima et al., *Nat Commun* 2026), which covers
ACDC disease classification only, against CLIP-family baselines. No study covers M&Ms or
M&Ms-2, frozen segmentation, or a cardiac MAE against DINOv3 or SAM. The gap is real but narrow,
and on its own the study is incremental. Frozen general models rivalling domain models has
precedents in other imaging domains, though the result depends on the task (e.g. Liu et al.,
arXiv 2509.06467: frozen DINOv3 loses on pathology, EM and PET). The closest cardiac work,
CMRVision (Jacob, Sharma, Rueckert, 2026), finds that cardiac-pretrained models consistently
beat natural-image ones. But it evaluates only fine-tuned or LoRA-adapted encoders, compares
natural vs cardiac pretraining only at ViT-S, and has no disease classification.

**Proposed work (2–3 months).** We propose to turn the benchmark into a controlled study of *why*
frozen cardiac features do or do not help. Does any advantage come from the training data
(cardiac vs natural images) or from the training method (MAE vs DINO-style self-distillation)?
Prior cardiac work has varied one factor at a time, under fine-tuning and at ViT-S. Jacob et al.
(*JCMR* 2025) compare MAE vs DINO on the same cardiac data, and natural vs cardiac
initialisation within DINO; CMRVision varies the data within DINO. No study has run a matched
2×2 of data × method with frozen evaluation.

- **Month 1: make the existing results trustworthy, then add cheap analyses.**
  - Re-enable seeding and re-run the full grid with several seeds. This includes SAM v1
    segmentation and the invalid CineMA linear/conv runs. Regenerate the summary and
    significance CSVs.
  - Run a from-scratch UNet baseline in this repo, on the same splits and metric. Record where
    the split metadata comes from.
  - Add kNN / nearest-centroid classifiers as a second readout.
  - Add a randomly-initialised-backbone control, to show how much performance comes from
    pretraining at all.
  - Probe ejection fraction and ventricular volumes directly.
  - Add a classifier on segmentation-derived measurements as the clinical baseline.
- **Month 2: the core 2×2 experiment** at matched model size (ViT-B).
  - Take public natural-image DINOv3 and MAE ViT-B models and continue pretraining both on UK
    Biobank cine MRI. DINOv3 ViT-B weights are gated (approval needed), and the DINO projection
    heads and, it appears, the MAE decoder are not released, so both need new heads.
  - Evaluate all four models frozen, using several readouts.
  - Keep CineMA and its random-init control as reference points. SAM's MAE-initialised
    encoder makes it a mixed reference, not a clean "natural-image, non-MAE" arm.
- **Month 3: label-efficiency curves and write-up.**
  - Compare frozen vs lightly fine-tuned (LoRA) models on a subset of tasks, to test whether
    cardiac pretraining matters most when labels are scarce.
  - Use UK Biobank's large set of cardiac measurements (e.g. LV volumes for ~81k participants)
    for label-efficiency curves at scale.
  - Keep disease classification as a secondary task; the public test sets are small (as few as
    6 patients per class).

To keep the comparison fair, all UK Biobank evaluation will use participants whose cine MRI was
acquired after CineMA's data cut-off (6 Nov 2023). CineMA publishes no participant list, so we
will check with its authors how repeat scans were handled. For the same reason, CineMA's own UK
Biobank downstream results should not be treated as clean held-out results. The main risks:
- **Timing of UK Biobank access.** If it slips, we fall back to public cine data for pretraining.
- **Small effect sizes.** Mitigated by multiple seeds and confidence intervals.
- **Compute.** A few hundred GPU-hours per pretraining run (an estimate).
