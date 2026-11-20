# Novelty review — final report

*heartfm-evals, branch `research/novelty-review`, 2026-10-29. Supporting notes:
[01_project.md](01_project.md) (what the project does, which results are valid),
[02_literature.md](02_literature.md) (~30 works, each marked by how it was verified),
[03_positioning.md](03_positioning.md) (our numbers vs published ones),
[BLOCKERS.md](BLOCKERS.md). Throughout, **[V]** = verified against a source or file;
**[I]** = my inference.*

---

## 1. Verdict

**Incremental as it stands — publishable at workshop level at best, and only after the
validity problems are fixed. Confidence: moderate (≈ 70 %).** The exact study — frozen CineMA vs
frozen DINOv3 vs frozen SAM v1 on ACDC, M&Ms and M&Ms-2, with a decoder ladder and pathology
probes — has not been published. Four parallel searches and the citation lists of both CineMA
records found nothing [V]. But every *message* the current results support has a close precedent:

- general FMs rival domain FMs when frozen (C2, C10, C11);
- decoder or readout dominates backbone (C3, C4, C12);
- scaling is non-monotonic (C2, C3);
- DINO beats SAM (C3, C13);
- a cardiac FM beats natural DINOv3 by about a Dice point on cine SAX (B2).

The results that would be new are not yet trustworthy:

- **CineMA:** the linear and conv segmentation cells are invalid (bug).
- **SAM v1:** there is no valid segmentation result.
- **Classification:** every number is a single unseeded run, with the configuration picked on the test set.
- **Frozen vs scratch:** frozen performance sits *below a from-scratch UNet* on segmentation.

The project becomes worth a full paper if it stops being a leaderboard and answers a sharper
question. The best candidate is ***why* a cardiac MAE does not beat a natural-image DINO when
frozen**: domain or objective, and readout or representation. That needs the controls listed in
§5. [I]

## 2. Closest prior work and exactly how we differ

| Prior work | What it did | How we differ | Overlap risk |
| --- | --- | --- | --- |
| **CMRVision** (Jacob, Sharma, Rueckert; arXiv 2609.01308, MedAGI@MICCAI 2026) [V] | Natural-image DINOv3-S vs CineMA vs CMR-DINOv2/v3 vs SAM2/MedSAM2. **All fully fine-tuned** with UNETR. ACDC reduced to one basal slice per frame. Segmentation and view classification only. NI-DINOv3 trails CineMA by 0.4–1.3 Dice. | We test the **frozen** regime, on full 3D SAX volumes, on all three datasets, plus SAM v1, a DINOv3 size sweep, three decoder capacities and patient-level pathology. | **High.** Same research question and the same backbones, by an active, well-resourced group. A frozen or LoRA follow-up from them is plausible. |
| **CineMA** (Fu et al., Commun Med 2026; arXiv 2506.00679) [V] | Fine-tuned CineMA vs from-scratch CNNs and nnUNet on our exact test sets. Never freezes the encoder on these datasets. | We measure the cost of freezing and compare against general FMs. | Low on our specific question. It is the reference we must match protocol-wise. |
| **Kundu et al.** (FIMH 2025) [V] | Frozen DINOv2 B/L/g, SAM-H and MedSAM × {linear, UNet} decoders on left-atrium MRI. Finds DINO > SAM ≈ MedSAM, decoder adds 2–5 Dice, size scaling non-monotonic. | Ventricles on cine SAX instead of the atrium. We add a *cardiac* FM to the grid, and classification. | **High for the segmentation message.** Our backbone × decoder pattern replicates theirs. |
| **Liu et al. "Does DINOv3 set a new medical vision standard?"** (arXiv 2509.06467) [V] | Frozen DINOv3 across many medical tasks; non-monotonic scaling. ACDC appears only for registration. | We cover cine SAX segmentation and pathology, against a cardiac FM. | Medium. They own the general "frozen DINOv3 in medicine" claim. |
| **DINO-AugSeg** (arXiv 2601.08078) [V] | Frozen DINOv3 + U-Net on ACDC, including a few-shot curve. | Our DINOv3 segmentation on ACDC is not new on its own. | Medium for any label-efficiency addition. |
| **Med-DualLoRA** (arXiv 2603.10967) [V] | Frozen CineMA linear probe for **binary** disease detection on ACDC + M&Ms: balanced accuracy 0.81, *above* full fine-tuning at 0.745. | We do multi-class and add general-FM comparators. | Low–medium. |

## 3. What is genuinely new in our findings

Ranked by how much I would defend each one today.

1. **The cost of freezing CineMA on its own benchmark.** On the same 682 test volumes, frozen
   CineMA + UNETR reaches **85.1** mean Dice, against 88.7 fine-tuned. That is also **below a
   from-scratch UNet** (89.5 / 86.0 / 88.0) and below CineMA's own random-init architecture on
   all three datasets [V numbers; 03 §2]. Nobody has published this. It has a clear practical
   message: for cine segmentation, freezing a foundation model is worse than not using one.
   *Caveat:* our decoders train on cached features without augmentation, so part of the gap is
   the recipe.
2. **Frozen CineMA is not a better pathology representation than frozen DINOv3.** Paired
   differences are within noise on ACDC and M&Ms, and nominally favour DINOv3 on M&Ms-2 (+0.07,
   CI [−0.00, +0.14]) [V; 03 §3.1]. This runs against the counter-evidence of RAD-DINO (C9) and
   MR-JEPA (B3), where domain pretraining clearly wins when frozen. It is interesting *because*
   it disagrees, but the obvious explanation is that MAE features read out poorly through linear
   heads (D1–D3), not that cardiac pretraining is useless. [I]
3. **On M&Ms-2, frozen DINOv3 with a linear readout (0.76–0.79 OVO AUROC) is level with
   fine-tuned CineMA's seed-mean (0.772).** It is within 0.01–0.04 of the seed-ensemble (0.801).
   This is fragile: one run, n = 108, and the 0.79 config was selected on the test set.
4. **The bookkeeping that makes CineMA comparisons possible** [V]:
   - Our test sets match CineMA's exactly.
   - CineMA reports macro **one-vs-one** AUROC, which on balanced ACDC equals one-vs-rest.
   - The two "published CineMA" baselines in circulation are arXiv v2's seed-mean
     (97.98 / 77.41 / 77.20) and the journal's seed-ensemble (0.992 / 0.810 / 0.801).

   This is useful internally; it is not a contribution.

**Not new** (frame these as replication, with citations):
- decoder ≫ backbone;
- DINOv3 > SAM v1;
- non-monotonic size scaling;
- "general FMs ≈ medical FMs when frozen" in general;
- cardiac FM slightly better than natural DINOv3 on cine segmentation.

## 4. Strongest argument that this is NOT worth pursuing

The question has already been answered in neighbouring settings, and the answer in ours is
unflattering to the premise:

- **The general claim is taken.** Liu et al. (C2), AnyMC3D (C10), CardioBench (C11) and Kundu et al. (C3)
  already report the same nuanced answer: frozen general FMs are competitive when the readout is
  adequate, and fall short on fine-grained tasks. On cine CMR specifically, the Rueckert/Siemens
  group has three 2025–26 papers (B1–B3) comparing natural against cardiac pretraining. They have 36 M
  private CMR images and a CMR-DINO model we cannot obtain (Jacob et al. state the weights will
  not be released) [V].
- **Our own numbers say "don't freeze".** Every frozen segmentation configuration is below a
  from-scratch UNet [V]. On ACDC classification, frozen embeddings reach 0.48–0.66 accuracy,
  while a classifier on segmentation-derived volumes and EF reached **0.92–1.00 in 2017–2019**
  (E1, E2) [V]. A reviewer will ask why anyone should use frozen FM embeddings for a task that
  EF + volumes already solve.
- **The classification benchmark is barely well-posed.** M&Ms has **one** HHD training patient
  and 6 ARV test patients [V]. Test sets of 50–108 give 95 % CI half-widths of ±0.04–0.09 AUROC [V], larger than
  most between-backbone differences.
- **The evidence is not yet admissible.**
  - CineMA linear/conv cells: invalid.
  - SAM v1 segmentation: no valid result.
  - Single unseeded runs, with the linear head keeping its last epoch.
  - Configurations selected on test.
  - Committed summaries stale.

  Fixing all of this is weeks of compute (≈ 640 GiB of caches, about 4 days of SAM extraction;
  refreshers) just to reach the starting line.
- **The venue ceiling is low.** A frozen-probe benchmark on three small public datasets, without
  fine-tuning or LoRA arms, will be read as incomplete. "Why not LoRA / fine-tune / nnUNet?" will
  be the first review comment, and CMRVision already has fine-tune and LoRA arms. [I]

## 5. Additions that would increase novelty or impact

**Before any of these:** fix seeding (#59), run ≥ 3 seeds, fix the configs a priori (no test-set
selection), and re-run CineMA linear/conv (bug fixed in `a020ad4`) and SAM v1 segmentation (#66
fixed). Report paired bootstrap CIs. This is hygiene, not novelty, but none of the additions
below are credible without it.

| # | Addition | Why it is novel (the gap it fills) | Effort | Supported by existing code/results? |
| --- | --- | --- | --- | --- |
| 1 | **Controls that make "frozen features help" testable.** (a) Each backbone with **random frozen weights** under the same decoders. (b) A UNETR with the feature skips zeroed, i.e. raw-image path only. (c) A from-scratch UNet or nnUNet on our splits; CineMA's published UNet numbers can stand in if splits are confirmed. | No frozen-FM medical benchmark found includes a random-init frozen backbone at fixed decoder capacity (02, "searched not found"; also noted by the probing agent). Our UNETR feeds the raw 192² image into a 31–48 M-parameter decoder, so we cannot currently say how much of its 0.83–0.89 Dice comes from the features. | **Low–medium.** Random init is a small change in `load_backbone()` (skip the checkpoint load); zeroing skips is a few lines in `decoders.py`; caches must be re-extracted. | **Yes.** Same drivers, decoders and analysis scripts. |
| 2 | **Readouts that are fair to an MAE.** Mean of patch tokens plus an **attentive probe** over the cached 12×12 patch tokens of every ED/ES slice. Multi-layer CineMA features, since CineMA currently exposes only its final layer. kNN as a third readout. | Linear/CLS readouts are known to understate MIM models (D1–D3), and CineMA is an MAE; no cardiac study has controlled for this. It decides whether finding 3.2 is about cardiac pretraining or about the readout. | **Medium.** The attentive probe is ~100 lines; multi-layer CineMA needs `feature_forward` hooks. | **Partly.** The **segmentation 2D caches already store per-slice 12×12 patch tokens for ED/ES**, reusable for an attentive classification probe without re-extraction. Classification caches store only pooled vectors. |
| 3 | **A 2×2 that separates domain from objective:** {natural, cardiac} × {MAE, DINO-like}. Natural MAE = ImageNet MAE ViT-B (public). Cardiac MAE = CineMA. Natural DINO = DINOv3. Cardiac DINO = a released CMR contrastive or DINO encoder if one exists (CMR-CLIP B6 or Shad et al. B5 — release status unchecked), else a short continued-pretraining of DINOv3-S on public cine data. | RAD-DINO (C9) and MR-JEPA (B3) say domain pretraining wins when frozen; our data say it does not. CMRVision (B2) has the objective-matched comparison but only fine-tuned. Nobody has crossed domain × objective under frozen evaluation on CMR. This is the most *scientific* addition. | **Natural-MAE cell: low.** Cardiac-DINO cell: **high** (compute, data access) unless weights are public. | **Partly.** The backbone factory makes adding ViT families straightforward. CineMA's conv stem makes the MAE comparison imperfect. |
| 4 | **An adaptation ladder on identical splits:** frozen → last-block fine-tune → LoRA → full fine-tune, for CineMA and DINOv3-B, at 10 / 25 / 50 / 100 % labels. | The CineMA paper has only full fine-tuning. CMRVision has fine-tune and LoRA on basal slices. DINO-AugSeg has frozen few-shot on ACDC only. A same-split curve from frozen to fine-tuned for a cardiac vs a general FM, on 3D volumes and three datasets, does not exist. It also pre-empts the first reviewer question (§4). | **Medium–high.** Needs a training loop with the backbone in the graph; the repo is built around cached features. | **Partly.** Issue #28 (`cinema.from_finetuned`), the `fine-tunning` branch and CineMA's own fine-tune code exist; the analysis scripts carry over. |
| 5 | **Probe for function, not just labels.** Regress EF, EDV, ESV and LV mass from frozen embeddings (labels computable from the GT masks already loaded). Measure ED-vs-ES embedding separability per backbone. Add a **segmentation-derived-feature classifier** (Khened-style) as the classification baseline. | The research question is whether frozen features "encode cardiac anatomy and function". Pathology labels test that only indirectly, and ACDC pathology is solved by volumes/EF (E1). A6 reports frozen CineMA ED and ES embeddings at > 0.99 cosine similarity, so function may be exactly what frozen features miss. No paper tests this on frozen general vs cardiac FMs. | **Low.** Ridge/logreg on cached features; masks are already in the data pipeline. | **Yes.** Classification caches and `build_patient_features`, plus our own segmentation predictions for the derived-feature baseline. |
| 6 | **Token-grid and resolution fairness.** DINOv3 at 384 / 512 px (24² / 32² tokens). We currently use 192 px (12²), while the DINOv3 dense protocol uses about 1024 tokens (C1). Give DINOv3's UNETR skips at 48² / 24² as CineMA's stem gets. | MedDINOv3 reports resolution is worth about +2 Dice (sub-agent reading, not re-checked by me). Our CineMA-vs-DINOv3 segmentation gap (+0.7 to +3 Dice) is the same size as this confound, so the current comparison cannot attribute the gap to pretraining. | **Low–medium.** Changing `IMAGE_SIZE` and `GRID_SIZE` is simple, but cache disk grows 4–7×. | **Yes**, subject to disk (B1 in refreshers). |
| 7 | **Shift robustness.** Per-vendor and per-centre breakdown on M&Ms / M&Ms-2, and cross-dataset transfer (train ACDC → test M&Ms SAX segmentation; fit the probe on M&Ms → test M&Ms-2 for shared classes NOR / HCM). | CineMA's claimed advantage is robustness under shift (EF consistency, Rescan). Whether that survives freezing, and whether DINOv3 is more or less shift-robust, is untested. Kundu et al. did cross-dataset for left atrium only. | **Low.** Re-evaluation of existing models; vendor metadata comes with M&Ms. | **Mostly.** Per-volume CSVs exist; vendor columns need joining from metadata. |

If only two can be done: **#1 and #2**. They are cheap, they turn the current results into
interpretable ones, and #2 decides which story the paper tells. **#5** is the cheapest way to
answer the stated research question directly. [I]

## 6. Open questions I could not resolve

1. **Corrected CineMA linear/conv segmentation numbers.** The 2-epoch smoke run (0.827 vs the
   committed 0.739 on ACDC) suggests CineMA may lead at every decoder capacity, which would
   change the segmentation story. No 100-epoch run exists.
2. **Valid SAM v1 segmentation.** None exists after the #66 fix. The pre-fix rows were 0.01–0.09
   below DINOv3-B/L.
3. **Train/val split identity with CineMA.** Test sets match. Our README's val counts (33 / 38)
   differ from CineMA's Table 2 (31 / 28), possibly through excluded labels. This needs a
   patient-ID comparison against CineMA's split files.
4. **What CineMA's "F1 (%)" is.** The code computes micro-F1 (= accuracy), but the values are
   bootstrap means over a seed average or ensemble. I could not confirm which code path produced
   the published table. The M&Ms accuracy comparison in 03 §3.2 depends on it.
5. **Pix2Rep-v2's fine-tuned CineMA and DINOv3 numbers** on all three datasets are only in a bar
   chart. They would give a second, independent fine-tuned reference.
6. **Whether any CMR-DINO or contrastive CMR encoder has public weights** (needed for addition
   #3). Jacob et al. state theirs will not be released [V]. I did not check CMR-CLIP or Shad et al.
7. **Whether our frozen CineMA ED/ES embeddings are as near-identical as A6 reports.** This is
   checkable from the classification caches, but none exist locally (refresher N2).
8. **Very recent preprints.** Citation indexes lag. Anything from Sep–Oct 2026 by the
   Jacob/Rueckert group or the CineMA authors could change the overlap picture.
9. **Provenance of the CineMA supplement.** The copy used was fetched by a sub-agent via a route
   my own fetch was refused on (BLOCKERS B1/B2). The arXiv v2 values give the same comparison
   from an unrestricted source.
