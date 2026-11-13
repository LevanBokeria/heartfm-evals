# heartfm-evals — summary and proposed next steps

*November 2026. Supporting detail: [REPORT.md](REPORT.md), [04_followups.md](04_followups.md),
[05_study_lookup.md](05_study_lookup.md).*

**What has been done.** The project asks whether the frozen features of a general-purpose vision
foundation model already capture enough cardiac anatomy and pathology for clinical tasks, or
whether a cardiac-specific model is needed. We built a benchmark that freezes three backbones and
trains only lightweight task heads on top. The backbones are CineMA, a masked-autoencoder model
pretrained on ~75k UK Biobank cardiac MRI studies; DINOv3 (S/B/L), trained on natural images;
and SAM (B/L/H), trained for natural-image segmentation. Tasks are ventricle segmentation and
patient-level disease classification on the three public cine MRI datasets ACDC, M&Ms and M&Ms-2,
using the same test sets as the CineMA paper.

The current results show three things:
- Frozen CineMA is no better than frozen DINOv3 for disease classification.
- CineMA has a modest segmentation advantage (+1–3 Dice), partly confounded by architecture.
- For segmentation, every frozen model performs below a UNet trained from scratch.

A literature review (~30 studies) found no published frozen comparison of a cardiac model against
general-purpose models on these datasets. On its own, though, the study is incremental: the
general message that frozen general models rival domain models has precedents in other imaging
domains. The closest cardiac work (CMRVision, Jacob/Rueckert, 2026) answers a related question,
but only with full fine-tuning, small ViT-S models, and no disease classification. Several
results also need re-running with fixed seeds before they can be relied on.

**Proposed work (2–3 months).** We propose to turn the benchmark into a controlled study of *why*
frozen cardiac features do or do not help. The key question is whether the advantage comes from
the training data (cardiac vs natural images) or from the training method (masked-autoencoder vs
DINO-style self-distillation). Neither CMRVision nor any other cardiac study has separated the two.

- **Month 1: consolidate and add cheap analyses that need no new data.**
  - Fix seeding and re-run the invalid results.
  - Add kNN / nearest-centroid classifiers as a second readout.
  - Add a randomly-initialised-backbone control, to show how much performance comes from
    pretraining at all.
  - Probe ejection fraction and ventricular volumes directly.
  - Add a classifier on segmentation-derived measurements as the clinical baseline.
- **Month 2: the core 2×2 experiment** at matched model size (ViT-B).
  - Take public natural-image DINOv3 and masked-autoencoder models and continue pretraining both
    on UK Biobank cardiac MRI.
  - Evaluate all four models frozen, using several readouts.
  - Keep CineMA and its random-init control as reference points.
- **Month 3: label-efficiency curves and write-up.**
  - Compare frozen vs lightly fine-tuned (LoRA) models on a subset of tasks, to test whether
    cardiac pretraining matters most when labels are scarce.
  - Use UK Biobank's large set of cardiac measurements for label-efficiency curves at scale.
  - Keep disease classification as a secondary task; the public test sets are small.

To keep the comparison fair, all UK Biobank evaluation will use participants scanned after
CineMA's pretraining cut-off. The main risks:
- **Timing of UK Biobank access.** If it slips, we fall back to public cine data for pretraining.
- **Small effect sizes.** Mitigated by multiple seeds and confidence intervals.
- **Compute.** A few hundred GPU-hours per pretraining run.
