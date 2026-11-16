# Claims table: 06_project_summary.md

Extracted by the `verify-claims` skill (step 1). Each claim is rewritten to stand alone and
keeps the draft's strength words.

| ID | Claim | Type | Draft's stated basis | Check question |
|---|---|---|---|---|
| R1 | The benchmark keeps all backbones frozen and trains only lightweight task heads on top. | internal-method | — | Do the segmentation and classification pipelines freeze every backbone parameter, and are all heads/decoders (incl. `unetr`) "lightweight"? |
| R2 | The backbones evaluated are CineMA, DINOv3 at sizes S, B and L, and SAM at sizes B, L and H. | internal-method | — | Which backbone/size combinations does the code support, and which actually appear in committed results for each task and dataset? |
| R3 | The tasks are ventricle segmentation and patient-level disease classification. | internal-method | — | Which classes are segmented (only ventricles, or also myocardium)? Is classification patient-level? |
| R4 | Both tasks are run on all three datasets ACDC, M&Ms and M&Ms-2. | internal-method | — | Do committed results exist for every task × dataset combination? |
| R5 | The benchmark uses the same test sets as the CineMA paper. | internal-method (+literature) | — | How are the test splits defined in this repo (code/metadata/docs), and is there evidence they match CineMA's splits? |
| R6 | Frozen CineMA is no better than frozen DINOv3 for disease classification. | internal-result | — | Per dataset, how do frozen CineMA and frozen DINOv3 classification scores compare (all heads/poolings/sizes), and what do the significance tests say? |
| R7 | CineMA has a modest segmentation advantage over the other frozen backbones of +1 to +3 Dice points. | internal-result | — | Per dataset and decoder, what is CineMA's Dice difference from the best DINOv3 and best SAM model? Does it fall in +1–3 everywhere? Are any differences significant / CIs non-overlapping? |
| R8 | CineMA's segmentation advantage is partly confounded by architecture. | internal-method | — | Does CineMA differ architecturally from the other backbones in the pipeline (e.g. 3D input, patch size, feature resolution, decoder used) in a way that could explain a Dice gap? |
| R9 | For segmentation, every frozen model performs below a UNet trained from scratch. | internal-result | — | Is there a from-scratch UNet result in this repo? If so, is every frozen backbone/decoder combination below it on every dataset? If not, where would the UNet number come from? |
| R10 | Several committed results need re-running with fixed seeds before they can be relied on. | internal-method | — | Which committed results predate seeding/determinism fixes or are otherwise flagged invalid? How many and which ones? |
| R11 | The public disease-classification test sets are small. | internal-method | — | How many test patients per dataset for classification, and per class? |
| R12 | The literature review covered about 30 studies. | internal-method | `05_study_lookup.md` | How many distinct studies are tabulated in `documents/research/05_study_lookup.md` and `02_literature.md`? (Counting the notes' contents is allowed here; this claim is about the notes.) |
| L1 | CineMA is a masked-autoencoder model pretrained on about 75,000 UK Biobank cardiac MRI studies. | literature | CineMA paper | What does the CineMA paper/model card say about pretraining objective, data source, and number of studies/subjects? |
| L2 | DINOv3 is available at sizes S, B and L, trained on natural images. | literature | DINOv3 paper | What data were DINOv3 ViT-S/B/L trained on (directly or via distillation), and are these sizes released? |
| L3 | SAM (B/L/H) was trained for natural-image segmentation. | literature | SAM paper | What is SAM's training data and objective, and were its image encoders initialised from another pretraining (e.g. MAE)? |
| L4 | CMRVision (Jacob, Rueckert et al., 2026) addresses a related question to this project. | literature | REPORT.md | Does a paper called CMRVision exist with these authors and year, and what question does it address? |
| L5 | CMRVision evaluates only with full fine-tuning (no frozen-backbone evaluation). | literature | REPORT.md | Does CMRVision report any frozen / linear-probe / feature-extraction evaluation anywhere, including appendix? |
| L6 | CMRVision uses only small ViT-S models. | literature | REPORT.md | Which model sizes does CMRVision train/evaluate? |
| L7 | CMRVision does not include disease classification. | literature | REPORT.md | Does CMRVision evaluate any disease/pathology classification task? |
| L8 | In other imaging domains there are precedents showing that frozen general-purpose models rival domain-specific models. | literature | REPORT.md | Name 2+ primary papers (non-cardiac medical imaging) that compare frozen general-purpose vs domain-pretrained backbones and find the general model comparable or better. |
| L9 | (Literature half of R5.) The CineMA paper evaluates ACDC, M&Ms and M&Ms-2 on specific, identifiable test sets. | literature | — | Which test splits (official challenge test sets? sizes?) does the CineMA paper use for ACDC, M&Ms and M&Ms-2 segmentation and classification? |
| N1 | No published study has compared a frozen cardiac foundation model against frozen general-purpose models on ACDC, M&Ms or M&Ms-2. | novelty | ~30-study review | Search for any paper (2023–2026) evaluating frozen/linear-probe features of a cardiac-pretrained model alongside a general-purpose model (DINOv2/v3, SAM, CLIP, MAE-ImageNet) on ACDC, M&Ms or M&Ms-2. |
| N2 | No cardiac study (CMRVision included) has separated the effect of pretraining data (cardiac vs natural images) from pretraining method (MAE vs DINO-style self-distillation). | novelty | — | Search for cardiac imaging papers that pretrain the same method on cardiac and natural data, or different methods on the same cardiac data, in a controlled comparison. |
| P1 | Public natural-image pretrained DINOv3 and masked-autoencoder ViT-B weights exist that could be continued-pretrained on cardiac MRI. | plan-premise | — | Are DINOv3 ViT-B and MAE ViT-B weights publicly released, and is DINOv3's training code released (needed for continued pretraining)? |
| P2 | CineMA has a documented pretraining cut-off (set of UK Biobank participants/scan dates), so participants scanned after it can be selected for clean evaluation. | plan-premise | — | Does the CineMA paper or repo document which UK Biobank participants or which date range/data release were used for pretraining? |
| P3 | UK Biobank provides a large set of cardiac MRI-derived measurements usable as regression labels. | plan-premise | — | Does UK Biobank release cardiac MRI imaging-derived phenotypes (e.g. LV/RV volumes, EF, mass), and for roughly how many participants? |

## Opinions and plans (not sent for checking)

- "On its own, though, the study is incremental."
- The 3-month plan items (seeding fixes, kNN readout, random-init control, EF probing,
  measurement-based classifier, 2×2 experiment, LoRA label-efficiency, keep classification
  secondary).
- Risks and mitigations: UK Biobank access timing, small effect sizes, compute "a few hundred
  GPU-hours per pretraining run" (an estimate).
