# 05 — Study lookup tables

*Quick reference for meetings (2026-11-09). One row per study, two views:
**Table 1** is at-a-glance; **Table 2** has the details. IDs (A1, B2, C3 …) point to fuller
entries in [02_literature.md](02_literature.md); follow-ups are in [04_followups.md](04_followups.md).*

**Legend:** ✓ yes · ✗ no · ◐ partly / with caveats · ? not checked.
**Source:** V = verified against the paper · V-abs = abstract verified, details from a sub-agent ·
A = sub-agent only. **NI** = natural images. **FT** = full fine-tuning.

---

## Table 1 — at a glance

| # | Study | Objective | Pretraining domain | Init | Evaluation | Seg | Disease cls | View cls | Function / regression | Outcomes | Other tasks | Overlap with us |
| --- | --- | --- | --- | --- | --- | :-: | :-: | :-: | :-: | :-: | --- | --- |
| 1 | **heartfm-evals — current** | MAE (CineMA), DINO (DINOv3), supervised seg (SAM; MAE-initialised encoder) | NI + cardiac (unmatched) | as released | **frozen** | ✓ | ✓ | ✗ | ✗ | ✗ | — | — |
| 2 | **heartfm-evals — proposed** | MAE vs DINO (matched), CineMA as anchor | NI vs NI→UKB cardiac (matched) | **continued from NI** | frozen vs LoRA / FT | ✓ | ✓ | ✗ | ✓ (EF, volumes, UKB phenotypes) | ◐ (UKB incident, stretch) | kNN / retrieval; optional QC head, click-seg, ED→ES propagation | — |
| 3 | CineMA (Fu et al., Commun Med 2026) — A1 | MAE | cardiac (UKB) | scratch | FT (UKB systemic: last block only) | ✓ | ✓ | ✗ | ✓ (EF, MAPSE/GLS, BMI, age) | ✓ (UKB prevalent disease, 1–3-yr survival) | landmarks | **High** — our reference model and test splits |
| 4 | CMRVision (Jacob, Sharma, Rueckert, arXiv 2026) — B2 | DINO (DINOv3-style; DINOv2 ablation) | NI vs cardiac (36M imgs incl. UKB) | **continued from NI** | FT (+ LoRA for NI) | ✓ | ✗ | ✓ | ✗ | ✗ | — | **High** — same question, but fine-tuned, ViT-S, no pathology |
| 5 | Jacob et al. (JCMR 2025) — B1 | DINO v1 (+ MAE ablation) | cardiac (same 36M) + NI ablation | **continued from NI** | FT; cls frozen-or-FT per task; frozen few-shot | ✓ | ✓ (ACDC 0.70 acc) | ✓ | ✗ | ✗ | landmarks, LGE detection | **High-medium** |
| 6 | MR-JEPA (Jacob et al., arXiv 2026) — B3 | JEPA (video) | cardiac vs NI video (V-JEPA2) | from 2D CMR-DINOv3 | **frozen** | ✗ | ✓ (private 4-class) | ✗ | ✓ (LVEF, RVEF, strain) | ✗ | — | Medium — frozen + cardiac vs natural, but video, private data |
| 7 | Pix2Rep-v2 (Sifaoui et al., arXiv 2026) — A4 | own dense SSL | cardiac | scratch | FT baselines; linear probe only for own model; in-context | ✓ | ✗ | ✗ | ✗ | ✗ | in-context seg, mask propagation | Medium — **same 3 datasets**, FT CineMA + DINOv3 baselines |
| 8 | Med-DualLoRA (Perramon-Llussà et al., arXiv 2026) — A3 | MAE (uses CineMA) | cardiac | CineMA | frozen head vs LoRA vs FT (federated) | ✗ | ◐ (binary only) | ✗ | ✗ | ✗ | federated learning | Low-medium — only frozen-CineMA probe published |
| 9 | CMR-CLIP (Nakashima et al., Nat Commun 2026) — B6 | contrastive video–report (CLIP) | cardiac (Cleveland Clinic) | ? | **frozen** + FC; zero/few-shot | ✗ | ✓ (ACDC per-class AUC) | ✗ | ✗ | ✗ | retrieval, report generation | Low-medium |
| 10 | ViTa (Zhang et al., MedIA 2025) — B4 | MAE + tabular CLIP | cardiac (UKB 42k) | ? | FT | ✓ | ✓ (UKB ICD) | ✗ | ✓ (UKB phenotypes) | ◐ (prevalent vs incident unclear) | — | Low |
| 11 | Shad et al. (Nat BME 2026) — B5 | contrastive video–report | cardiac (US centres) | from Kinetics-400 (NI video) | **frozen** + linear / MIL head | ✗ | ✓ (39 conditions) | ✗ | ✓ (LVEF) | ✗ | ACDC only as a t-SNE plot | Low |
| 12 | Kundu et al. (FIMH 2025) — C3 | DINO (DINOv2), supervised seg (SAM, MedSAM) | NI vs medical (MedSAM) | as released | **frozen** | ✓ (left atrium) | ✗ | ✗ | ✗ | ✗ | — | **Medium-high** — same backbone × decoder design, other structure |
| 13 | Liu et al. "Does DINOv3 set a new medical standard?" (arXiv 2025) — C2 | DINO | NI (vs medical FMs as baselines) | as released | **frozen** | ✓ (MSD incl. LA) | ✓ (CXR, CT, pathology) | ✗ | ✗ | ✗ | registration (ACDC ED→ES) | Medium — general "frozen DINOv3 in medicine" claim |
| 14 | DINO-AugSeg (Xu et al., arXiv 2026) — C7 | DINO (DINOv3) | NI | as released | **frozen** | ✓ (ACDC) | ✗ | ✗ | ✗ | ✗ | few-shot seg | Medium — frozen DINOv3 on ACDC already done |
| 15 | RETFound generalist vs specialist (Zhou et al., arXiv 2025) | MAE vs DINO | NI vs retina | DINOv2 variant **continued from NI** | frozen linear + FT | ✗ | ✓ (ocular + systemic) | ✗ | ✗ | ✗ | — | Medium — **3 of 4 cells of our 2×2**, in retina |
| 16 | RAD-DINO (Pérez-García et al., Nat Mach Intell 2025) — C9 | DINO (DINOv2) | NI vs chest X-ray | **continued from NI** and scratch | **frozen** probes + decoders | ✓ | ✓ | ✗ | ✗ | ✗ | report generation | Low-medium — continued-pretraining precedent |

---

## Table 2 — details

| # | Study | Backbones / sizes | Input | Pretraining data (UKB?) | Readouts / heads | Downstream datasets | NI vs cardiac compared? | MAE vs DINO compared? | Label-efficiency? | Seeds / CIs | Weights released? | Key result (one line) | Source |
| --- | --- | --- | --- | --- | --- | --- | :-: | :-: | :-: | --- | --- | --- | --- |
| 1 | heartfm-evals — current | CineMA ViT-B (conv stem); DINOv3 S/B/L; SAM B/L/H | CineMA 3D SAX; others 2D slices | public checkpoints (CineMA: 74,916 UKB studies) | seg: linear / conv / UNETR; cls: logreg / linear | ACDC, M&Ms, M&Ms-2 | ◐ (unmatched) | ✗ (confounded) | ✗ | single unseeded run | n/a | Frozen CineMA ≈ DINOv3 for pathology; CineMA +1–3 Dice seg; all frozen < from-scratch UNet | 01, 03 |
| 2 | heartfm-evals — proposed | ViT-B ×4 (2×2) + CineMA + random-init CineMA | 2D (CineMA 3D) | UKB continued pretraining; post-Nov-2023 test cohort | linear, kNN / nearest-centroid, attentive; decoder ladder; LoRA / FT | ACDC, M&Ms, M&Ms-2, UKB | ✓ (matched) | ✓ (matched) | ✓ (frozen vs FT) | ≥3 seeds, bootstrap CIs | planned (UKB policy unverified) | — | REPORT §5, 04 |
| 3 | CineMA | ViT-B + conv stem, 126M | 3D SAX + 2D LAX, multi-view | 74,916 UKB studies (**UKB ✓**, to Nov 2023) | UNETR (seg); linear (cls) | ACDC, M&Ms, M&Ms-2, Kaggle, Rescan, Landmark, EMIDEC, MyoPS, UKB | ✗ (vs random init + CNNs) | ✗ | ✓ (seg / EF) | 3 seeds (ensembled in journal) | ✓ (MIT) | FT seg 88.7 vs nnUNet 89.2 Dice; disease AUROC 0.992 / 0.810 / 0.801 | V |
| 4 | CMRVision | ViT-S/8 (main), ViT-S/16 | 2D | 36M images, ~27k studies; **UKB ✓** (16,230) + 2 clinical centres | UNETR (seg); fine-tuned head (view) | ACDC (one basal slice/frame), Kaggle, EMIDEC, private | ✓ (matched, DINO only) | ◐ (DINOv2 vs v3 only) | ✗ | ? | ✗ (no statement) | CMR > NI by ~+1.7 Dice avg; ACDC cine gap ≤ 1.3; CineMA ≈ CMRVision on cine | V |
| 5 | Jacob et al. 2025 | ViT-S/8 | 2D | same 36M; **UKB ✓** | UNETR (seg); linear (cls) | ACDC (75/25/50), Kaggle, EMIDEC, UKB, private | ◐ (not on ACDC) | ✓ (360k subset) | ✓ (few-shot, frozen) | ? | ✗ (explicitly unreleasable) | CMR up to +70.7 pts cls / +9.1 seg vs NI; ACDC disease 0.70 acc ("lags SoTA") | V |
| 6 | MR-JEPA | ViT-S/16 (video) | cine video | 10,505 pts, 2 centres (UKB not named) | gated-attention pooling + linear | private (+ Kaggle) | ✓ (vs V-JEPA2) | ✗ | ? | ? | ? | Disease AUC 0.868 vs V-JEPA2 0.741; LVEF MAE 4.79 vs 6.70 | V |
| 7 | Pix2Rep-v2 | own (3D UNet-type) | 3D (+t) | dataset training images | linear probe, FT, in-context | ACDC, M&Ms, M&Ms-2 | ◐ (FT baselines only) | ✗ | ✓ (1–100 %) | ? | ? | Strong in low-label regime; flags MedSAM2 as contaminated on these datasets; CineMA/DINOv3 numbers only in a figure | V (text) |
| 8 | Med-DualLoRA | CineMA | 3D SAX ED+ES | — (uses CineMA) | head-only, LoRA, FT; federated | ACDC + M&Ms-1/2 (binary) | ✗ | ✗ | ✗ | mean ± sd over runs | ? | Frozen head 0.810 balanced acc > full FT 0.745 (centralised) | V |
| 9 | CMR-CLIP | ViT-B/16 video transformer | video | ~11–14k studies, cine + LGE (no UKB) | FC on frozen; prototypes; zero-shot | ACDC (132 pts, 70/30), internal | ✓ (vs OpenAI CLIP 0.707 vs 0.961) | ✗ | ✓ (1–32-shot) | ? | ✓ (Hugging Face) | Frozen ACDC per-class AUC 0.93–1.00 (different split) | V |
| 10 | ViTa | ? (3D+T ViT) | 3D + time, SAX + LAX | 42k UKB (**UKB ✓**) | FT heads | UKB only (1,000-subject test) | ✗ | ✗ | ? | ? | ? | UKB CAD AUROC 0.770, diabetes 0.813 | A |
| 11 | Shad et al. | mViT (video) + PubMedBERT | video | Stanford / UCSF / MedStar (no UKB in pretraining) | frozen + linear / MIL attention | private, UKB, Kaggle, ACDC (t-SNE) | ✓ (vs Kinetics) | ✗ | ? | ? | ✓ (gated, CC-BY-NC) | HFrEF AUC 0.880 (UKB) vs Kinetics 0.751 | V |
| 12 | Kundu et al. | DINOv2 B/L/g; SAM-H; MedSAM-B | 2D | as released | linear vs UNet decoder; native mask decoder | LAScarQS, LASC (left atrium) | ✓ (vs MedSAM) | ✗ | ✗ | p-values | n/a | DINOv2-L + UNet 91.5 > nnUNet 88.7; UNet decoder +2–5 Dice; non-monotonic size | V |
| 13 | Liu et al. (DINOv3 medical) | DINOv3 S/B/L | 2D; slice-stacked 3D | as released | linear, kNN, light 2D/3D decoders | CXR, CT, pathology, MSD, ACDC (registration only) … | ✓ (vs medical FMs) | ✗ | ✗ | mostly single runs | n/a | Frozen DINOv3 beats some medical FMs, loses to pathology FMs; non-monotonic scaling | V |
| 14 | DINO-AugSeg | DINOv3 (size ?) | 2D | as released | U-Net-like decoder (+ augmentation) | ACDC (160/40 2D), LA2018, Synapse, others | ✗ | ✗ | ✓ (2–140 samples) | ? | ? | Frozen-DINOv3 Dice collapses below ~20 samples; frozen MAE much worse | V |
| 15 | RETFound generalist vs specialist | ViT-L (+ DINOv2-g, DINOv3-L) | 2D fundus | 904k retinal images | linear probe + FT | 10 ocular / oculomics tasks | ✓ | ✓ (3 of 4 cells) | ? | ? | ✓ (RETFound) | Linear probe: retina-DINO 0.787 > NI-DINO ~0.777 > retina-MAE 0.761 | V-abs (numbers A) |
| 16 | RAD-DINO | ViT-B/14 at 518 px | 2D CXR | 0.88M chest X-rays | linear probes; ViTDet / UPerNet decoders | VinDr-CXR, others | ✓ | ✗ | ? | ? | ✓ (MIT) | VinDr AUPRC 52.8 (continued) vs 45.9 (scratch) vs 33.5 (NI DINOv2-G) | V-abs (numbers A) |

---

### Reading the tables for the meeting

- **No row has both** NI-vs-cardiac **and** MAE-vs-DINO **with frozen evaluation on cardiac MRI.**
  CMRVision (row 4) has the domain axis, fine-tuned only; Jacob 2025 (row 5) adds a partial
  objective ablation, also fine-tuned; RETFound (row 15) has three of four cells, in retina. That
  empty cell is row 2.
- **Pathology classification** with general-vs-cardiac FMs on public cine data appears in no
  overlapping cardiac row except ours (rows 1–2); CMRVision has none.
- **Same three datasets:** CineMA (fine-tuned), Pix2Rep-v2 (fine-tuned baselines), Med-DualLoRA
  (binary, frozen CineMA). None compares frozen general FMs.
- **UKB overlap risk:** CineMA, CMRVision, Jacob 2025 and ViTa all pretrained on UKB — any UKB
  evaluation needs a held-out (post-cutoff) cohort.
