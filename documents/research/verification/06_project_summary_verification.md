# Verification report: 06_project_summary.md

- **Document:** [`documents/research/06_project_summary.md`](../06_project_summary.md) at commit `1b57851`
  ("Update project summary with WIP results"). This replaces the report for the earlier version at
  `a8f872f` (see git history).
- **Run:** 2026-11-16, `verify-claims` skill. Claims table: [06_project_summary_claims.md](06_project_summary_claims.md)
  (40 checkable claims, 10 opinions).
- **Verifiers:** one repo verifier (results, code, git history, refreshers) and two literature
  verifiers (one for papers and plan premises, one for the six novelty claims). They ran as
  general-purpose agents given the `.claude/agents/*-claim-verifier.md` instructions, because those
  agent types were not registered when the session started. None saw the draft. All are Claude, so
  this is not a fully independent check.
- **Spot checks by the orchestrator:**
  - **R11:** read `cache_sam_cls_features` and the 2026-10-23 refresher, and checked the dates of
    `a020ad4` and `4728304`.
  - **R9:** recomputed every UNETR macro Dice from the JSONs.
  - **R8:** recomputed the ACDC CineMA vs DINOv3-B metrics from the JSONs.
  - **L9:** re-extracted the SAM paper text.
  - **L3:** re-read the CineMA PDF in `documents/papers/`.
  - **L11:** looked at CMR-CLIP Fig. 3h.
  - **N1–N4:** re-extracted the Pix2Rep-v2 PDF (and its arXiv comment) and the CMRVision PDF.
  - **N5/N6:** checked the JCMR 2025 quotes.

  No verifier quote was found to be wrong. One verifier argument was corrected: for N1, the novelty
  verifier treated CMR-CLIP itself as the counterexample, but CMR-CLIP is the one study the claim
  names. The real counterexample is Pix2Rep-v2. The verdict stands.

  Not hand-checked: MR-JEPA, Decipher-MR, the retina "Generalist vs Specialist" paper, and secondary
  reports on UK Biobank access status.

> **10 of 40 checkable claims (25%) are not SUPPORTED.** That is exactly the skill's one-quarter
> threshold. Six are contradicted:
> - R11, about which results need re-running;
> - L9, "SAM is neither DINO- nor MAE-pretrained";
> - N1–N4, all four novelty claims in the literature paragraph, as worded.
>
> The project's own results (R1–R10, R12–R14) mostly hold. The main problems are in the literature
> positioning: CineMA has already been compared with DINOv3 and SAM, but only under fine-tuning or
> prompting, never frozen.

## Summary counts

| Verdict | Count | Claims |
|---|---|---|
| SUPPORTED | 24 | R1–R7, R10, R12–R14, L1, L2, L4–L7, L10, L12, L14–L16, P2, P3 |
| SUPPORTED, with a caveat that should change the wording | 6 | R8, R9, L11, L13, P1, P4 |
| OVERSTATED | 3 | L3, L8, N5 |
| CONTRADICTED | 6 | R11, L9, N1, N2, N3, N4 (N1–N4 only as worded: see below) |
| NOT REFUTED (novelty) | 1 | N6 |
| UNDERSTATED / UNVERIFIABLE | 0 | (R11's second half is also UNDERSTATED) |

## Problems first

### R11: CONTRADICTED (SAM part) and UNDERSTATED (the rest)

> "SAM results need a re-run after bug-fixes." (Current WIP results) · "Certain results need
> re-running post bug-fix" (scope table)

**The SAM v1 bug fix does not affect the committed SAM results.**
- The fix in question is #66 (merged `4728304`, 2026-09-08). It changed how a block index is
  resolved through `hidden_states`.
- SAM classification features come from `cache_sam_cls_features`
  (`src/heartfm_evals/classification_probe.py:354-423`). That function runs `patch_embed` and
  `pos_embed`, loops over every block in `ve.layers`, and pools the last block's output. It never
  touches `hidden_states`.
- The refresher `documents/refreshers/2026-10-23-classification.md` (§1) says the same: "The SAM v1
  fix does not touch classification, and the committed SAM classification results remain valid."
- No SAM v1 segmentation results exist on this branch. SAM segmentation therefore needs a first
  valid run, not a re-run.

**The document misses the results that do need re-running.**
- All three CineMA `linear_probe` and `conv_decoder` segmentation JSONs are dated 2026-04-18. They
  predate `a020ad4` (2026-08-28), "Fix CineMA 2D cache misaligning features and labels along z",
  which says each cached slice was paired "with a different slice's features".
- Still open: the linear head keeps the last epoch, not the best (`linear_head.py:333-345`), and
  seeding (#59) affects every linear-head row.

**Suggested:**

> "SAM v1 classification results are unaffected by the #66 fix; SAM v1 segmentation has not yet
> been run on the current code. The CineMA linear-probe and conv-decoder segmentation results
> predate the CineMA z-alignment fix (`a020ad4`) and must be re-run."

### L9: CONTRADICTED

> "SAM is neither DINO- nor MAE-pretrained."

**Evidence:** the SAM paper (Kirillov et al. 2023, https://arxiv.org/abs/2304.02643).
- §3: "we use an MAE [47] pre-trained Vision Transformer (ViT)"
- App. A: "We initialize SAM from an MAE [47] pre-trained ViT-H."

SAM's encoder is initialised from ImageNet MAE weights and then trained with supervision for
promptable segmentation on SA-1B. This matters for the 2×2 design: SAM is an MAE-initialised model,
so it is not a clean "neither" reference.

**Suggested:**

> "SAM's encoder is MAE-initialised and then trained with supervision for promptable segmentation,
> so it is a reference point outside the 2×2 rather than a third pretraining method."

### N1–N4: CONTRADICTED as worded (the narrower, frozen-and-matched version is NOT REFUTED)

> "A review of ~28 foundation-model studies found one published frozen comparison on these
> datasets: CMR-CLIP … No study covers M&Ms or M&Ms-2, frozen segmentation, or a cardiac MAE
> against DINOv3 or SAM."

**Pix2Rep-v2** (Sifaoui et al., arXiv 2609.01427, arXiv comment "Accepted at MICCAI 2026") is a
second frozen comparison on these datasets, and it includes M&Ms, M&Ms-2 and segmentation.
- Its cardiac SSL U-Net is pretrained on "the combined ACDC, M&Ms and M&Ms-2 training sets".
- It is evaluated by linear probe ("In linear probing, the backbone is frozen", §3).
- It is compared with in-context ProtoSAM, which uses frozen DINOv2 + SAM (Fig. 2), and with
  zero-shot SAM 3 video propagation (Fig. 4).
- The readouts are not matched: the general models are run in-context or by prompting, not by
  linear probe. Pix2Rep-v2 is also a U-Net, not a ViT foundation model.

**N4 (a cardiac MAE against DINOv3 or SAM):** CineMA has already been compared with both, though
always fine-tuned and with SAM always prompted.
- **CMRVision** (arXiv 2609.01308, §4.2) compares "SAM2 [21] and MedSAM2 [30] (box prompting) …
  and CineMA (publicly available encoder retrained in the segment-all setting…)". Table 1a also has
  natural-image DINOv3 ViT-S/16.
- **Pix2Rep-v2** (§4) includes "recent foundation models fine-tuned on the tasks, specifically
  DINOv3 [6], as well as the MAE-based CineMA [9]", on ACDC, M&Ms and M&Ms-2.
- **Jacob et al.**, *JCMR* 2025 (PMC12745146), Table 5, has SAM2 and CineMA on cine SAX.

**Suggested:**

> "We found no study that applies the same frozen readout to a cardiac foundation model and to
> general-purpose models on these datasets. The nearest are CMR-CLIP (frozen embeddings, ACDC
> classification, against CLIP-family video/vision-language baselines) and Pix2Rep-v2 (Sifaoui et
> al., MICCAI 2026: a linear-probed cardiac self-supervised U-Net on ACDC, M&Ms and M&Ms-2, against
> in-context ProtoSAM and zero-shot SAM 3). CineMA has been compared with DINOv3 and SAM2 only
> under fine-tuning or prompting (CMRVision; Pix2Rep-v2; Jacob et al., JCMR 2025)."

Also add Pix2Rep-v2 and Jacob et al. 2025 to `02_literature.md`. Both are directly relevant and
neither is cited in the summary.

### L3: OVERSTATED

> "[CineMA was] shown to have SOTA performance on various tasks on various open datasets after full
> fine-tuning."

**Evidence:** the CineMA paper (Fu et al., *Commun Med* 2026, PDF in `documents/papers/`).
- The paper never uses "state-of-the-art".
- Results: "it achieved performance competitive with the nnUNet framework (89.24%), narrowing the
  gap to 0.52 percentage points" (CineMA 88.72%).
- Disease classification "consistently outperformed baseline models across all three datasets",
  but those baselines are randomly initialised CNNs.
- Some downstream tasks froze all but the last encoder block, so not every task was fully
  fine-tuned.

**Suggested:**

> "After fine-tuning, CineMA was competitive with nnU-Net on ACDC, M&Ms and M&Ms-2 segmentation
> (88.7 vs 89.2 Dice) and outperformed randomly initialised CNN baselines on disease
> classification and several other tasks."

### L8: OVERSTATED

> "We use SAM v1 rather than SAM2 because its plain-ViT encoder matches DINOv3 and CineMA."

The SAM v1 and SAM 2 parts are correct:
- SAM v1 uses a non-hierarchical ViT with windowed plus global attention (SAM App. A).
- SAM 2 uses "an MAE … pre-trained Hiera … image encoder, which is hierarchical" (arXiv
  2408.00714, §4).

CineMA, though, is not a plain ViT. It is "encoded using convolutional downsampling as in MCMAE"
before the shared ViT (CineMA PDF, Methods). The document itself says so later (line 44, "conv
stem, 3D input").

**Suggested:**

> "…because its non-hierarchical ViT encoder is closer to DINOv3 and to CineMA's ViT-B transformer
> than SAM2's hierarchical Hiera encoder."

### N5: OVERSTATED

> "Prior cardiac work has varied one factor at a time, under fine-tuning and at ViT-S."

**True for cardiac image self-supervised work:**
- Jacob et al. JCMR 2025 §2.6: "we compared our proposed model to two other pretraining options: a
  ResNet50 pretrained through DINO and a ViTS/8 pretrained through MAE"; "the model was initialized
  with the weights of a ViT-S/8 pretrained on natural images [4] and then finetuned".
- CMRVision: ViT-S, "full end-to-end finetuning".

**Not true of all prior cardiac work.** Some studies compare natural with cardiac pretraining under
frozen evaluation at ViT-B scale, though those comparisons are confounded:
- CMR-CLIP freezes embeddings and compares its cardiac model with natural-video Frozen in Time and
  CLIP.
- MR-JEPA (arXiv 2608.30975, verifier-reported, not hand-checked) is frozen and includes a
  natural-video V-JEPA2 ViT-B baseline.

Neither of these isolates MAE vs DINO.

**Suggested:**

> "Prior cardiac image self-supervised work has varied data or method one at a time, under
> fine-tuning, at ViT-S (Jacob et al. 2025; CMRVision); frozen natural-vs-cardiac comparisons exist
> only for video-text or JEPA models, which do not separate MAE from DINO."

### N6: NOT REFUTED

> "No study has run a matched 2×2 of data × method with frozen evaluation as opposed to
> fine-tuning."

No counterexample was found in 13 search strands (web, PubMed, arXiv API, Semantic Scholar citers of
CineMA, CMRVision and JCMR 2025).

**Closest work:** Jacob et al. JCMR 2025 has three of the four cells: cardiac DINO, cardiac MAE and
natural-image DINO, all ViT-S/8. All three are fine-tuned, and the cardiac MAE was itself
initialised from natural-image weights. The document should cite it as the nearest design.

**Outside cardiac:** "Generalist vs Specialist" (arXiv 2509.03421, not hand-checked) compares DINOv2
and DINOv3 with RETFound-MAE and RETFound-DINOv2 on retina, using linear probe and fine-tuning. This
is a partial cross-domain precedent.

### Supported, but the wording should carry the caveat

**R8, classification: "leads on ACDC, mixed on M&Ms and trails on M&Ms-2".** The overall claim holds,
with two caveats about ACDC (recomputed from the JSONs):
- CineMA beats DINOv3-B on 5-way accuracy and macro-F1 in all four head/pooling settings, but trails
  it on macro AUC in all four (0.880–0.905 vs 0.902–0.911).
- No ACDC difference is significant (exact McNemar p ≥ 0.096, n = 50).

On M&Ms-2, CineMA trails DINOv3 in all 11 available pairs, but only one pair reaches uncorrected
p < 0.05.

The committed `summary.csv` files and the linear-head McNemar matrices are stale, so quote the JSONs,
not these files.

Suggested: "leads on ACDC in accuracy and F1 (not AUC; not significant, n = 50)".

**R9, segmentation: "+1.1 to +2.3 Dice".** Exact against the best DINOv3 size: ACDC +2.27, M&Ms
+1.56, M&Ms-2 +1.13 (macro Dice from the JSONs). Three caveats:
- Against every DINOv3 size the gap is +1.1 to +2.7.
- A rerun of the same configurations on `origin/sam2-classification` gives +0.8 to +1.8.
- The comparison is not like-for-like. CineMA's UNETR receives multi-scale skips from CineMA's
  frozen conv stem, while DINOv3's UNETR upsamples 12×12 tokens. Normalisation and dropout defaults
  also differ (`decoders.py:123-262` vs `264-402`).

Suggested: "+1.1 to +2.3 Dice over the best DINOv3 size, in one run (a rerun gives +0.8 to +1.8);
part of the gap may come from CineMA's conv-stem skips."

**L11 (CMR-CLIP):**
- The frozen-embedding evaluation also includes a private Cleveland Clinic cohort, so "ACDC only" is
  true only of the public data.
- Besides the CLIP-family models, the baselines include an "Amyloid-Targeted" model (Fig. 3h).
- There is no DINO, SAM or image-MAE baseline.

**L13 (CMRVision "consistently beat").** "Consistently" is the paper's own word. Caveats:
- It holds for every segmentation Dice cell and for average view-classification accuracy.
- Natural-image models still win on SAX-view accuracy (0.961/0.953 vs 0.930–0.945).
- All models are ViT-S and fully fine-tuned.
- The "cardiac" models are continued pretraining from natural-image weights, which is exactly what
  the proposal's 2×2 design does.

**P1 (MAE ViT-B weights).** Weights including the decoder are public, but only via HF
`facebook/vit-mae-base`.
- The MAE README's paper checkpoint `mae_pretrain_vit_base.pth` is encoder-only.
- The HF config has `norm_pix_loss: false`, so it may not be the paper's norm-pix model.
- The GitHub licence is CC-BY-NC 4.0.

**P4 (UK Biobank cine MRI).** Cine MRI exists for about 96k participants (field 20209 SAX: 96,120;
field 20208 LAX: 96,366), and the CineMA paper says it is available to bona fide researchers by
application. Current practical access is unconfirmed:
- the UK Biobank access pages returned HTTP 403;
- secondary reports describe a UKB-RAP pause during 2026.

Confirm the project's access route before Month 2.

## Full table

| ID | Verdict | Evidence pointer |
|---|---|---|
| R1 | SUPPORTED | `constants.py:18-19` (BG/RV/MYO/LV); `classification_probe.py:425-465` one row per patient (ED+ES). M&Ms-2 has 6 classes. |
| R2 | SUPPORTED | `backbones.py:86-91` `_freeze()` applied to all three backbones; optimisers see only decoder/head params. |
| R3 | SUPPORTED | `run_segmentation.py:66` choices; all 3 decoders have JSONs for CineMA and DINOv3 S/B/L × 3 datasets. |
| R4 | SUPPORTED | `run_classification.py:64,68` (`logreg`/`linear`, `cls`/`gap`); committed linear runs are labelled `ftfrozen`. |
| R5 | SUPPORTED | 12/12/12 segmentation and 22/22/21 classification JSONs (M&Ms-2 is missing `dinov3_vits16_logreg_cls`). |
| R6 | SUPPORTED | Classification has CineMA, DINOv3 S/B/L, SAM B/L/H; segmentation has no SAM JSONs. The segmentation `summary.csv` files still hold 9 orphan SAM2 rows. |
| R7 | SUPPORTED | `choices=` in both drivers; SAM+cls is rejected. |
| R8 | SUPPORTED, caveat | See above: ACDC lead is accuracy/F1 only and not significant. |
| R9 | SUPPORTED, caveat | +2.27/+1.56/+1.13 vs best DINOv3 (orchestrator recomputed); one run; not like-for-like. |
| R10 | SUPPORTED | `set_seed` commented out since `0b5d350` (2026-04-16); one JSON per config. Logreg is effectively deterministic, linear-head results are not. |
| R11 | CONTRADICTED / UNDERSTATED | `classification_probe.py:354-423`; refresher 2026-10-23 §1; `a020ad4` postdates the CineMA linear/conv JSONs. |
| R12 | SUPPORTED | Released DINOv3 `.pth`, `facebook/sam-vit-*`, `CineMA.from_pretrained()`; no pretraining code. |
| R13 | SUPPORTED | No scratch UNet or regression code or results in the repo. |
| R14 | SUPPORTED | 28 distinct FM studies in sections A–C of `02_literature.md` (37 tabulated in total). |
| L1 | SUPPORTED | PMID 42129472; *Commun Med* 6:408 (2026); GitHub README. |
| L2 | SUPPORTED | "CineMA adopts a masked autoencoder architecture"; 74,916 UKB cine studies. |
| L3 | OVERSTATED | Competitive with, but below, nnUNet; the paper never says "SOTA". |
| L4 | SUPPORTED | "'base' configuration from He et al."; 768-d, 12 layers (126 M params including conv stem and decoder). |
| L5 | SUPPORTED | Conv downsampling "as in MCMAE"; SAX 3D (192×192×16) plus 2D LAX. |
| L6 | SUPPORTED | DINOv3 §5.2 distillation to S/B/L from a 7B model trained on LVD-1689M. |
| L7 | SUPPORTED | SA-1B: 11M licensed images, 1.1B masks; promptable segmentation. |
| L8 | OVERSTATED | SAM v1 non-hierarchical ViT and SAM 2 Hiera are correct; CineMA is a conv-stem hybrid, not a plain ViT. |
| L9 | CONTRADICTED | "We initialize SAM from an MAE [47] pre-trained ViT-H." |
| L10 | SUPPORTED | MAE §4.3: "MAE representations are less linearly separable"; DINOv2 Table 4; Psomas et al. 2506.10178. |
| L11 | SUPPORTED, caveat | Frozen FC on ACDC plus a private cohort; Fig. 3h baselines; no M&Ms or segmentation. |
| L12 | SUPPORTED | Liu et al. 2509.06467: frozen DINOv3 beats some medical FMs and degrades on WSI/EM/PET. (It also uses some cardiac data.) |
| L13 | SUPPORTED, caveat | CMRVision §5 "consistently outperformed"; NI wins SAX-view accuracy; ViT-S, fine-tuned. |
| L14 | SUPPORTED | "full end-to-end finetuning"; only qualitative PCA of frozen features. |
| L15 | SUPPORTED | "We pretrained a ViT-S backbone"; no ViT-B anywhere. |
| L16 | SUPPORTED | Tasks are segmentation and cine view classification only. |
| N1 | CONTRADICTED as worded | Pix2Rep-v2 (2609.01427): linear-probe cardiac SSL vs in-context ProtoSAM / zero-shot SAM 3 on ACDC/M&Ms/M&Ms-2. |
| N2 | CONTRADICTED as worded | Pix2Rep-v2 covers M&Ms and M&Ms-2. |
| N3 | CONTRADICTED as worded | Pix2Rep-v2 segmentation; no matched frozen-decoder comparison of cardiac vs general foundation models found. |
| N4 | CONTRADICTED as worded | CMRVision, Pix2Rep-v2 and JCMR 2025 compare CineMA with DINOv3 and/or SAM2/SAM 3 (fine-tuned or prompted). |
| N5 | OVERSTATED | JCMR 2025 and CMRVision fit the claim; CMR-CLIP and MR-JEPA are frozen natural-vs-cardiac comparisons. |
| N6 | NOT REFUTED | 13 search strands; closest is JCMR 2025 (3 of 4 cells, fine-tuned, ViT-S/8). |
| P1 | SUPPORTED, caveat | HF `facebook/vit-mae-base` includes the decoder; the README checkpoint is encoder-only; licence CC-BY-NC. |
| P2 | SUPPORTED | DINOv3 ViT-B public after access request; licence allows derivatives; backbone only (heads re-initialised). |
| P3 | SUPPORTED | UKB fields 24100–24103: 80,974 participants (Bai et al. automated pipeline). |
| P4 | SUPPORTED, caveat | Field 20209: 96,120 participants; current access status unconfirmed. |

## Other things a reader should know

- **Stale classification outputs.** The committed classification `summary.csv` files and
  significance matrices predate the April sweep and include phantom entries (`ft-full`, `vit7b16`).
  Quote numbers from the JSONs.
- **Two Dice definitions.** JSON Dice is pooled over voxels. Per-volume mean Dice
  (`_per_sample.csv`) is about 1.5 points lower and gives larger CineMA−DINOv3 gaps (+1.4 to +3.1).
  Don't mix them.
- **Superseded segmentation runs.** The 2026-08-09 segmentation refresher calls this branch's 04-18
  and 04-21 segmentation runs superseded by the `sam2-classification` reruns. Neither set is merged
  here.

## Opinions not checked

O1 field framing (foundation models increasingly multi-modal) · O2 "narrow gap", "incremental" ·
O3 results need confirmation · O4 SAM2 would add a confound (factual core is L8) · O5 the "why"
framing · O6 Month 1 plan · O7 linear readout would bias MAE vs DINO (factual core is L10) · O8 Month 2
plan · O9 Month 3 plan and stretch goal · O10 which models get seeded re-runs.
