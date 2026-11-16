# Claims table: 06_project_summary.md

Extracted by the `verify-claims` skill (step 1) from `06_project_summary.md` at commit `1b57851`.
Each claim is rewritten to stand alone and keeps the draft's strength words. (The table for the
earlier run, at commit `a8f872f`, is in this file's git history.)

## Checkable claims

| ID | Claim | Type | Draft's stated basis | Check question |
|---|---|---|---|---|
| R1 | The project's two tasks are segmentation of cardiac structures (LV, RV and myocardium) and patient-level disease classification. | internal-method | — | Which classes does the segmentation pipeline predict, and is classification done per patient (not per slice/frame)? |
| R2 | In both tasks the pretrained backbone is frozen and only task heads are trained on top. | internal-method | — | Do the segmentation and classification pipelines freeze every backbone parameter (all three backbones), training only the decoder/head? |
| R3 | Segmentation uses three decoders: a linear probe, a 2D conv decoder and a UNETR. | internal-method | — | Which decoders does `run_segmentation.py` support, and which appear in committed segmentation results? |
| R4 | Classification uses either logistic regression or a linear head on pooled features. | internal-method | — | Which classification heads and pooling options exist in code and in committed results? |
| R5 | The project evaluates on ACDC, M&Ms and M&Ms-2 (for both tasks). | internal-method | — | Do committed results exist for every task × dataset combination (segmentation and classification × ACDC, M&Ms, M&Ms-2)? |
| R6 | The backbones evaluated so far are CineMA (ViT-B), DINOv3 at sizes S, B and L, and SAM v1 at sizes B, L and H; SAM is evaluated for classification only (no SAM v1 segmentation results). | internal-method | — | Which backbone/size combinations appear in committed results for each task and dataset? Are there any SAM segmentation results? |
| R7 | The codebase can load different backbone + decoder/head combinations and train the decoders/heads on the different datasets, for both segmentation and classification. | internal-method | — | Do the unified entry points accept all backbones × decoders/heads × datasets via `choices=`, for both tasks? |
| R8 | For disease classification, frozen CineMA shows no consistent advantage over frozen DINOv3: CineMA leads on ACDC, is mixed on M&Ms, and trails on M&Ms-2. | internal-result | — | Per dataset, across heads/poolings/DINOv3 sizes, how do frozen CineMA and frozen DINOv3 classification scores compare? Does CineMA lead on ACDC, give a mixed picture on M&Ms and trail on M&Ms-2? What do McNemar/bootstrap outputs say? |
| R9 | For segmentation with the UNETR decoder, CineMA leads DINOv3 by +1.1 to +2.3 Dice points (across the datasets). | internal-result | — | For the UNETR decoder, per dataset, what is CineMA's mean Dice minus DINOv3's (each DINOv3 size, and the best DINOv3)? Does the range equal +1.1 to +2.3? Any CIs/significance? |
| R10 | All current results come from a single, unseeded run (no repeated seeds). | internal-method | — | Are there multiple runs/seeds per configuration in committed results? Was seeding enabled when the committed results were produced (check `set_seed` usage and git history vs result timestamps)? |
| R11 | SAM results need re-running after bug fixes (and certain other results also need re-running post bug-fix). | internal-method | — | Which bugs affecting SAM (or other) results were fixed after the committed results' timestamps? Which committed results are affected? |
| R12 | No continued pretraining on cardiac MRI has been done so far: the natural-image models are used as released. | internal-method | — | Does the code or any result use DINOv3/SAM weights other than the released checkpoints? |
| R13 | There is no from-scratch UNet run in this repo; the UNet baseline is cited from the CineMA paper. No regression task (e.g. EF/volumes) exists yet. | internal-method | — | Is there any from-scratch UNet code or result in the repo? Is there any regression task/head? |
| R14 | The literature review in `02_literature.md` covered about 28 foundation-model studies. | internal-method | `02_literature.md` | How many distinct studies are tabulated/discussed in `documents/research/02_literature.md`? (Counting the notes' contents is allowed for this claim only.) |
| L1 | CineMA is published as Fu et al., *Communications Medicine* 2026 (doi 10.1038/s43856-026-01636-0), with code at github.com/mathpluscode/CineMA. | literature | DOI + GitHub link | Do the DOI and repo resolve to the CineMA paper/code, with Fu as first author, in Commun Med, 2026? |
| L2 | CineMA was pretrained self-supervised, as a masked autoencoder (MAE), on UK Biobank cardiac MRI. | literature | CineMA paper | What does the CineMA paper say about the pretraining objective and data source? |
| L3 | CineMA was shown to have state-of-the-art performance on various tasks on various open datasets after full fine-tuning. | literature | CineMA paper | Does the CineMA paper report fine-tuned results on multiple tasks and public datasets, and does it claim/show best performance versus baselines (on all, or only some, tasks)? |
| L4 | CineMA's model size is ViT-B. | literature | — | What encoder size (embed dim, depth, params) does CineMA use, and does it match ViT-B? |
| L5 | CineMA differs in architecture and input from a standard MAE ViT-B: it has a convolutional stem and takes 3D input. | literature | — | Does CineMA's architecture use a convolutional stem / conv patch embedding and 3D (or multi-view 2D+3D) input? |
| L6 | DINOv3 is available at sizes S, B and L, trained on natural images. | literature | — | What data were DINOv3 ViT-S/B/L trained on (directly or via distillation), and are these sizes released? |
| L7 | SAM v1 (sizes B/L/H) was trained for natural-image segmentation. | literature | — | What is SAM v1's training data (SA-1B) and objective? |
| L8 | SAM v1's image encoder is a plain ViT (like DINOv3 and CineMA), whereas SAM2's encoder is the hierarchical Hiera architecture. | literature | — | What encoder architectures do SAM v1 and SAM 2 use? Is CineMA's encoder a plain ViT? |
| L9 | SAM is neither DINO- nor MAE-pretrained. | literature | — | Was SAM v1's image encoder initialised from MAE (or DINO) pretraining? |
| L10 | Linear readouts are known to understate the quality of MAE features (relative to non-linear / attentive readouts). | literature | — | Do primary sources (e.g. the MAE paper, attentive-probing papers) report that MAE features score poorly under linear probing compared with fine-tuning or attentive probing, and compared with DINO-style models? |
| L11 | CMR-CLIP (Nakashima et al., *Nat Commun* 2026, PMC13194963) is a published frozen-feature comparison that covers ACDC disease classification only, against CLIP-family baselines. | literature | PMC link | Does CMR-CLIP evaluate frozen features? On which datasets and tasks (only ACDC classification? any segmentation, M&Ms, M&Ms-2)? Which baselines (only CLIP-family, or also DINO/SAM/MAE)? |
| L12 | Precedents exist in other (non-cardiac) imaging domains of frozen general-purpose models rivalling domain-specific models, though the result depends on the task (e.g. Liu et al., arXiv 2509.06467). | literature | arXiv 2509.06467 | What does arXiv 2509.06467 compare and find? Are there other primary papers with frozen general vs domain-specific comparisons, and is the outcome task-dependent? |
| L13 | CMRVision (Jacob, Sharma, Rueckert, 2026, arXiv 2609.01308) finds that cardiac-pretrained models consistently beat natural-image-pretrained ones. | literature | arXiv 2609.01308 | Do the paper's authors/year match? Does it report cardiac-pretrained models beating natural-image ones consistently (every task/dataset) or only on some? |
| L14 | CMRVision evaluates only fine-tuned or LoRA-adapted encoders (no frozen evaluation). | literature | arXiv 2609.01308 | Does CMRVision report any frozen / linear-probe / feature-extraction evaluation anywhere, including the appendix? |
| L15 | CMRVision compares natural-image vs cardiac pretraining only at ViT-S (not ViT-B). | literature | arXiv 2609.01308 | At which model sizes does CMRVision compare natural-image vs cardiac pretraining? |
| L16 | CMRVision has no disease classification task. | literature | arXiv 2609.01308 | Does CMRVision evaluate any disease/pathology classification task? |
| N1 | Only one published study (CMR-CLIP) compares a frozen cardiac model against frozen general-purpose models on ACDC, M&Ms or M&Ms-2. | novelty | ~28-study review | Search for any paper (2023–2026) evaluating frozen/linear-probe features of a cardiac-pretrained model alongside a general-purpose model (DINOv2/v3, SAM, CLIP, ImageNet-MAE) on ACDC, M&Ms or M&Ms-2. |
| N2 | No study has a frozen cardiac-vs-general-model comparison on M&Ms or M&Ms-2. | novelty | ~28-study review | Search for frozen-backbone evaluations on M&Ms / M&Ms-2 that include both a cardiac-pretrained and a general-purpose model. |
| N3 | No study compares frozen backbones (cardiac vs general) for cardiac MRI segmentation on these datasets. | novelty | ~28-study review | Search for frozen-encoder / linear-probe segmentation benchmarks on ACDC/M&Ms/M&Ms-2 that include a cardiac-pretrained and a general-purpose foundation model. |
| N4 | No study compares a cardiac MAE (e.g. CineMA) against DINOv3 or SAM. | novelty | ~28-study review | Search for papers evaluating CineMA or another cardiac MAE alongside DINOv3 or SAM (any evaluation protocol). |
| N5 | Prior cardiac work has varied pretraining data or pretraining method one factor at a time, under fine-tuning and at ViT-S. | novelty | — | In cardiac pretraining comparisons (e.g. CMRVision), was data or method varied one at a time, under fine-tuning, at ViT-S only? Is there any cardiac work comparing these factors at ViT-B or frozen? |
| N6 | No study has run a matched 2×2 of pretraining data (natural vs cardiac) × pretraining method (MAE vs DINO-style self-distillation), with frozen evaluation, for cardiac imaging. | novelty | — | Search for cardiac (or medical) imaging papers that pretrain both MAE and DINO-style methods on both natural and cardiac data in a controlled comparison and evaluate frozen. |
| P1 | Public natural-image MAE ViT-B weights are available to continue pretraining from. | plan-premise | — | Are the official MAE ViT-B (ImageNet) pretrained weights — including the decoder needed to continue MAE pretraining — publicly released? |
| P2 | Public natural-image DINOv3 ViT-B weights are available to continue pretraining from on UK Biobank cine MRI. | plan-premise | — | Are DINOv3 ViT-B weights public, and does the release include what is needed for continued self-distillation (e.g. DINO head / teacher)? Does the licence permit it? |
| P3 | UK Biobank provides cardiac measurements such as LV volumes for ~81k participants, usable for label-efficiency curves. | plan-premise | — | Which UK Biobank showcase fields hold LV volumes/EF from CMR, and how many participants have values? |
| P4 | UK Biobank cine MRI is available for continued pretraining of DINOv3 and MAE models. | plan-premise | — | Is UK Biobank cardiac cine MRI (e.g. field 20208/20209) available to approved researchers, and at what scale? |

## Opinions and plans (not checked)

| ID | Statement |
|---|---|
| O1 | Foundation models have increasingly been pretrained on multi-modal imaging datasets (MRI, CT, PET etc.) and used for clinically relevant downstream tasks. (General framing.) |
| O2 | The study addresses a narrow gap in the literature and is incremental; the proposal strengthens the study but remains incremental. |
| O3 | The WIP results need further work, confirmation and replication with multiple seeded runs. |
| O4 | Using SAM2's Hiera encoder would add an architectural confound (factual core checked in L8). |
| O5 | The proposed study asks *why* frozen cardiac features do or do not help, separating training data from training method. |
| O6 | Month 1 plan: re-run with several seeds; from-scratch UNet; random-init backbone control (CineMA architecture); kNN / nearest-centroid; attentive probe; EF/volume regression with a linear probe. |
| O7 | A linear readout would bias the MAE vs DINO comparison in the 2×2 (follows from L10). |
| O8 | Month 2 plan: continue pretraining DINOv3 and MAE ViT-B on UK Biobank; evaluate all four frozen with several readouts; CineMA and SAM as reference points. |
| O9 | Month 3 plan: label-efficiency curves on UK Biobank measurements; stretch goal LoRA / full fine-tuning, which "might take considerable time". |
| O10 | Re-runs with several fixed seeds limited to CineMA, DINOv3 ViT-B and one SAM size. |
