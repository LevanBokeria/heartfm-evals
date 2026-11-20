# 04 — Follow-up questions (2026-11-05)

*Four follow-up questions from the PI after REPORT.md. Each was researched by a separate
sub-agent; I re-checked the claims the recommendations depend on. Same conventions as
02_literature.md: **V** = I opened the source and checked the claim; **V-abs** = I checked the
abstract only (numbers from the sub-agent); **A** = sub-agent only. **[I]** = my inference.
No site behind a login/bot check was accessed this round (agents were told not to work around
any; the UK Biobank guidance and fees pages returned 403 and are unread).*

---

## Q1. UK Biobank cardiac data: what does it allow, and does it change novelty?

**Short answer: yes, but only if the project moves from ACDC-style tasks to population-scale
tasks — phenotype regression at large n, incident outcomes, and genetics. UKB does not fix the
small-pathology-set problem (the cohort is mostly healthy), and it creates a new one: CineMA was
pretrained on it.**

### What is there

- ~100,000 imaged participants; a repeat imaging phase (target 60,000) is under way. CMR protocol:
  SAX + LAX cines (50 phases), LVOT cine, tagging, aortic flow, native T1 (ShMOLLI)
  ([Petersen et al. JCMR 2016](https://doi.org/10.1186/s12968-016-0227-4), **V** via PubMed).
- Showcase counts (agent, field pages Aug–Sep 2025, **A**): SAX cine 96,120 participants; automated
  LVEF (Bai pipeline) 80,974; global circumferential / longitudinal strain ~80k; linked hospital
  ICD-10, death and primary-care records; genotypes for the whole cohort.

### What has already been done with UKB CMR representations

| Work | Frozen? | General-vision FM baseline? | Relevance |
| --- | --- | --- | --- |
| CineMA (A1) — prevalent self-reported hypertension/diabetes/cancer, 1–3-yr survival | all but last block | **none** | authors list incident disease / MACE as future work (**V**, PDF) |
| Ometto et al., *Nat Commun* 17 (2026), [doi:10.1038/s41467-026-74575-y](https://doi.org/10.1038/s41467-026-74575-y) — 3D diffusion-autoencoder latents of 71,017 participants; h² 4–18 %, GWAS 89 variants / 42 loci (7 novel) | unsupervised latents | none | genetics of learned CMR embeddings is **already done** for a bespoke model (**V**, PubMed abstract) |
| Hager et al. CVPR 2023; ViTa (MedIA 2025); Radhakrishnan et al. *Nat Commun* 2023; Bonazzola et al. *NMI* 2024; Shad et al. *Nat BME* 2026 | mixed; Hager / Radhakrishnan / Shad use frozen probes | **none** use DINO/SAM | prior UKB representation work (**A**, except Shad **V**) |
| CARDIAC-FM (medRxiv 2026) — incident AF/HF at 5 yr | fine-tuned heads, CNN-LSTM MRI encoder | none | MRI adds < 1 AUROC point for AF, ~+1 for HF (**A**) — a warning that imaging may add little to outcomes |
| Raptor (An et al., ICML 2025, arXiv [2507.08254](https://arxiv.org/abs/2507.08254)) — frozen natural-image 2D FM, train-free 3D embeddings | frozen | it *is* the general FM | beats medical-volume FMs (SuPreM, Merlin) on 10 tasks (**V-abs**; brain-UKB details **A**). The closest "general beats medical, frozen, at biobank scale" precedent, outside cardiac. |

**Gap [I]:** I found no comparison of frozen general-vision FMs (DINOv2/v3, SAM) with a cardiac FM
on UKB CMR — for phenotypes, outcomes or heritability.

### The CineMA overlap problem (must be designed around)

- CineMA was pretrained on 74,916 UKB studies up to **6 Nov 2023**, instances 2 and 3, with no
  no held-out participants described (**V**, CineMA PDF p. 2 and p. 4) and no released ID list
  (agent check of paper + README, **A**). CMRVision and
  Jacob et al. used 16,230 UKB participants in pretraining (**V**, CMRVision PDF).
- Any UKB evaluation of CineMA on pre-cutoff participants is in-cohort: it has seen the test
  images (no label leakage, but transductive). A fair design [I]:
  1. primary test set = participants whose first CMR is **after the cutoff** (agent estimate
     ~15–20k from Showcase counts; must be checked on the Research Analysis Platform);
  2. report the pre- vs post-cutoff **"membership gap"** for CineMA on matched samples — itself
     a new measurement of how much a medical FM's pretraining-set membership inflates results;
  3. incident-outcome analyses will need long follow-up, hence pre-cutoff participants; state
     those CineMA numbers as upper bounds.

### What UKB access would let us do (ranked by novelty × feasibility) [I]

1. **Label-efficiency curves on image-derived phenotypes** (EF, EDV/ESV, mass, strain; ~80k
   labels): frozen linear and kNN probes at 10 → 50k labels for each backbone. Answers directly
   whether the general-vs-cardiac gap closes as labels grow. High feasibility. Caveat: labels come
   from the automated Bai pipeline, so they carry its errors.
2. **Incident HF / AF / MACE / death from frozen embeddings, on top of Bai phenotypes + clinical
   risk factors** (Cox / discrete-time heads). High usefulness, medium feasibility; CARDIAC-FM
   suggests the imaging increment may be small.
3. **Heritability of each backbone's embeddings** (LDSC / GREML on principal components or probe
   outputs). Novel for a general-vs-cardiac FM comparison; needs genetics fields and careful
   covariates (ImageNet features in brain UKB mostly encoded brightness and body size —
   Rakowski et al. 2024, **A**).
4. **Visit-2 vs visit-3 stability** of embeddings and predictions (~5–6k pairs, ~3 years apart —
   not test–retest; for true test–retest use the public Rescan set CineMA used).
5. **Train on UKB, test on ACDC / M&Ms** (EF / volume regression) — modest novelty; test sets stay small.
6. Prevalent-disease classification — low novelty (Hager, ViTa, CineMA did it).

### Practical constraints

- UKB is cloud-only (Research Analysis Platform) since 2024; cost per GPU-day is a real budget line
  (agent, **A**). The UKB guidance on sharing models trained on UKB returned 403; search snippets
  say trained-model parameters are returned to UKB as derived data and third-party sharing needs
  a leakage assessment (**unverified**). CineMA, Ometto et al. and CARDIAC-FM all released
  UKB-trained weights publicly, so it is done in practice.
- For our frozen benchmark only the small heads are UKB-trained — low risk [I]. Per-participant
  embeddings are participant-level derived data: return them to UKB, do not publish them.

---

## Q2. Continued pretraining of NI-DINOv3 on UKB CMR — interesting / novel?

**Short answer: as stated, it is not novel — it has been done twice, by the same group, including
UKB data. It becomes novel as one arm of a matched-data {domain} × {objective} experiment with
frozen evaluation, which nobody has run on CMR.**

### Already done

- **CMRVision** (arXiv [2609.01308](https://arxiv.org/abs/2609.01308)): "Models were initialized
  from NI weights"; DINO + iBOT + KoLeo + **Gram anchoring** ("early Gram anchoring, enabled by NI
  initialization"); 36 M images from ~27k studies including **16,230 UK Biobank** participants
  (**V**, PDF lines quoted). ViT-S only; **all evaluation is full fine-tuning**; no frozen
  probes; no weights release statement.
- **Jacob et al. JCMR 2025** (B1): DINO ViT-S/8 "initialized with DINO weights pretrained on
  natural images", same 36 M images; 8 × H100 × 7 days; weights explicitly **not** releasable
  (**V**, PMC full text).
- **MR-JEPA** (B3) already extends a 2D CMR-DINOv3 to video, with frozen EF/strain evaluation —
  pre-empts a "temporal" extension (**V**, text).

### Evidence that the domain × objective question is live

- **RETFound generalist vs specialist** (Zhou et al., arXiv [2509.03421](https://arxiv.org/abs/2509.03421)):
  retinal DINOv2 (continued from natural DINOv2) "consistently outperforms" natural DINOv2/DINOv3
  (**V-abs**). Agent-read linear-probe means: RETFound-MAE 0.761 < natural DINOv2-g 0.776 ≈
  natural DINOv3-L 0.778 < RETFound-DINOv2 0.787 (**A**). That ordering — *domain-MAE < natural-DINO
  < domain-DINO* — is exactly what our CineMA < NI-DINOv3 result would predict if the objective,
  not the domain, is holding CineMA back [I].
- **RAD-DINO** (C9): continued-from-DINOv2 beats random-init domain DINO and natural DINOv2 under
  frozen probes on chest X-ray (**V-abs**; numbers **A**).
- **Ilse et al.** "Data scaling laws for radiology FMs" (arXiv [2509.12818](https://arxiv.org/abs/2509.12818)):
  continued pretraining of RAD-DINO / MedImageInsight on up to 3.5 M CXRs; "as few as 30k in-domain
  samples are sufficient to surpass open-weights foundation models" for some tasks (**V-abs**).
- **Tayebi Arasteh et al.** (arXiv [2601.19618](https://arxiv.org/abs/2601.19618), DP medical
  imaging): changing the pretraining *domain* improved AUC 2.2–3.7× more than changing the
  *objective* (**V-abs**) — the opposite emphasis, in a different setting; the agent reports they
  had only three of the four cells.
- I found no medical-imaging study with the full 2 × 2 (agent search, **A**; consistent with my
  own reading of the above).

### What would be novel [I]

1. **Matched-data 2 × 2 at ViT-B, frozen evaluation:** {natural, natural→UKB} × {MAE, DINOv3}.
   Natural MAE ViT-B and NI-DINOv3-B are public; continue each on the *same* UKB frames with the
   same iteration budget. CineMA stays as an external reference (its conv-stem, multi-view
   architecture is not matched). This is the cleanest test of the review's main hypothesis.
2. **Data-scaling curve** for the DINOv3 arm (e.g. 1k / 5k / 20k / 75k participants): how much
   UKB data until frozen CMR-DINOv3 beats NI-DINOv3 on our benchmark? Watch for forgetting.
3. **Function readouts** inside the 2 × 2: ED/ES separability and EF probes — frozen CineMA ED and ES
   embeddings are reported to be > 0.99 cosine-similar (A6, **V**).
4. **Open weights** — there are no public CMR-DINO weights (Jacob: unreleasable; CMRVision: no
   statement). A resource, not a finding. The DINOv3 licence permits derivative weights if
   redistributed under the same licence with acknowledgement (**V**, `LICENSE-DINOv3.md` §1.a–b);
   UKB's own policy must be checked (403 above).

**Feasibility [I]:** a few hundred H100-hours per ViT-B run at 224 px (Jacob: ~1,340 H100-h for
ViT-S/8 on 36 M images; RAD-DINO ~2,560 A100-h for ViT-B/14 — agent figures, **A**). UKB holds
roughly 50–65 M 2D cine frames, highly redundant — subsample. The official DINOv3 repo has training
code including Gram anchoring and high-res adaptation; MedDINOv3 is a working continued-pretraining
precedent (**A**). Main risk: the effect is small (CMRVision's fine-tuned NI→CMR gain on ACDC
cine SAX is ~+0.8 Dice; **V**, Table 1).

---

## Q3. Tasks beyond segmentation and disease classification

**Short answer: three task families fit "frozen vs fine-tuned" well, have public cardiac labels,
and have no FM comparison yet: interactive (click) segmentation, training-free cross-frame
correspondence / mask propagation, and quality-control heads (the defensible RLHF analogue).
"Click-based classification" is not an established task. RLHF proper is a weak fit for judging
vision backbones on fully labelled segmentation.**

| # | Task | Why frozen-vs-fine-tuned matters | Prior work (access) | Public cardiac labels | Novelty × feasibility [I] |
| --- | --- | --- | --- | --- | --- |
| 1 | **Click-based interactive segmentation** (simulated clicks at the largest error; NoC@85/90, Dice after k clicks) | Clicks add information the frozen features may lack: does the frozen-vs-fine-tuned gap close with 1, 3, 5 clicks? | **VerSe** (Guo et al., arXiv [2412.16381](https://arxiv.org/abs/2412.16381)): click-prompted versatile cardiac MRI segmentation, from-scratch backbone, no FM comparison (**V-abs**; dataset list incl. ACDC/M&Ms/M&Ms-2 **A**). **Havrylov et al.** (arXiv [2505.02075](https://arxiv.org/abs/2505.02075)): proposes interactive segmentation "as a novel benchmark" for vision-FM features (**V-abs**). **Stein et al.** (C5): frozen SAM encoders on ACDC/M&Ms cap at Dice 0.69 zero-shot, 0.84 with a trained decoder (**V**). | ACDC, M&Ms, M&Ms-2 masks (clicks simulated from GT) | **High × high** — click maps as extra input channels to our conv decoder |
| 2 | **Training-free correspondence:** ED→ES mask propagation by nearest-neighbour feature matching; feature-guided registration | Isolates the spatial fidelity of the features, no decoder in the way | **Kögl et al.** (WBIR@MICCAI 2024, arXiv [2407.13311](https://arxiv.org/abs/2407.13311)): frozen DINOv2 / SAM / MedSAM ViT-B as an extra term in 2D ED→ES registration of an ACDC mid-slice; NCC baseline 0.836 → 0.833–0.845, within the ±0.05 SD; feature-only losses worse than baseline (**V**, HTML). **Liu et al.** (C2): frozen DINOv3 3D ACDC registration ≈ VoxelMorph (**V**). **Pix2Rep-v2** (A4): training-free 3D+t propagation on our three datasets, but no frozen CineMA/DINOv3 propagation baseline (**A**). | ED and ES masks in ACDC / M&Ms / M&Ms-2 | **Medium-high × high** — no training; reuses cached 12² features |
| 3 | **Quality-control / "reward-model" heads:** predict per-slice Dice or flag failures from frozen features; image-quality (motion) classification | A QC head on frozen features is the natural reward model for any best-of-N or RL-style refinement; tests whether general features encode "plausible anatomy" | UKB QC: Tarroni et al. TMI 2019, Ruijsink et al. JACC CVI 2020, Robinson et al. JCMR 2019 (**A**). **RL4Seg** (Judge et al., arXiv [2406.17902](https://arxiv.org/abs/2406.17902)): RL domain adaptation for echo segmentation with a reward network that doubles as an uncertainty estimate; no manual review (**V-abs**). **CMRxMotion** (public, 320 series with induced motion; **A**). No CMR QC work with FM features found (**A**). | CMRxMotion; our own models' predicted masks + GT give Dice targets on all three datasets | **High × high** — scales to UKB |
| 4 | **Scribble / point-supervised segmentation** with frozen features (partial CE on labelled pixels) | Frozen features should help most when labels are weak | ACDC expert scribbles (Valvano et al. TMI 2021), MSCMRseg scribbles (CycleMix) (**A**); no frozen-FM scribble work found (**A**) | ACDC scribbles (public) | **Medium-high × high** |
| 5 | Regression: EF / volumes / mass; ED/ES frame detection; slice-level (basal/mid/apical) | Direct test of "encodes function" | CineMA fine-tunes EF/BMI/age (**V**); Majchrowska & Teare (C12) frozen DINOv3 EF on echo (**V-abs**) | derivable from masks; UKB IDPs | Low novelty alone; essential as a row (REPORT §5 #5) |
| 6 | One-shot / in-context segmentation; cold-start active learning | Nearest-neighbour prototypes on cached features | Pix2Rep-v2 in-context mode (**A**); MedCAL-Bench: DINO features best for cold-start selection (**A**) | our datasets | Medium × high |
| 7 | Vision-language (VQA, report generation) | Frozen vs tuned vision tower in a VLM | **CineMR** (Li et al., arXiv [2610.01166](https://arxiv.org/abs/2610.01166), Oct 2026): Qwen3-VL-8B, SFT then **GRPO**; VQA benchmark of 11,531 QA pairs built from **ACDC, M&Ms, M&Ms-2**; segmentation tool "fine-tuned from CineMA" (**V**, HTML) | no public CMR reports | Low × low for us — and CineMR has just claimed the obvious version |

### On the RLHF analogy [I]

- With dense ground truth, Dice is already a direct, differentiable loss; RL replaces an exact
  gradient with a noisy estimate. The agent reports GRPO post-training of DINOv2 gives only
  0.2–0.5 mIoU on segmentation (GRPO-RM, arXiv [2511.15256](https://arxiv.org/abs/2511.15256);
  method **V-abs**, numbers **A**).
- RL is justified when the reward is **non-decomposable or label-free**: anatomical plausibility
  (RL4Seg), clinical consistency (LV and RV stroke volumes should match), or cheap clinician
  accept/reject on UKB. Preferences simulated from GT are just supervision; an RLHF claim needs
  real human or label-free signals.
- The clean mapping onto our question: **a QC/reward head on frozen features** (row 3), then
  best-of-N reranking of candidate masks, before any RL. Where RL has landed on our datasets is
  the language side (CineMR's GRPO), not the vision backbone.

---

## Q4. kNN disease classification on frozen features

**Short answer: not done on ACDC / M&Ms / M&Ms-2 with these backbones, but kNN is a standard SSL
readout, so the novelty is small. Its real value is as a readout-bias check with a predicted
direction: kNN should hurt the MAE-trained models (CineMA, and SAM, whose encoder is
MAE-initialised) relative to DINOv3.**

### Literature

- **Cardiac MRI:** no kNN or nearest-centroid disease classification on frozen embeddings of
  ACDC / M&Ms / M&Ms-2 found. Closest: CMR-CLIP prototype (class-centroid) few-shot on private data
  and 1-NN report retrieval (B6, PMC, **A** for these details); EchoPrime's sklearn kNN vs logistic
  regression on echo study embeddings (arXiv [2410.09704](https://arxiv.org/abs/2410.09704), **A**).
- **Protocol:** DINO's standard is L2-normalised features, cosine similarity, weighted 20-NN with
  exp(s/0.07) votes (Caron et al. 2021; **A**).
- **Bias against MAE:** DINOv2 paper Table 4 — ImageNet kNN vs linear: MAE ViT-H 49.4 vs 76.6;
  DINOv2-L 83.5 vs 86.3 (**A**). Marks et al. (arXiv [2407.12210](https://arxiv.org/abs/2407.12210),
  preprint): in-domain linear and kNN probes are the best predictors of transfer (**V-abs**);
  agent reports feature normalisation recovers much of MAE's kNN deficit (**A**).
- **Medical counter-evidence:** on CheXpert, MAE ViT-L kNN beat DINOv2-L (Baharoon et al., C4; **A**)
  — the MAE penalty is not universal.
- **Corrections to 02_literature.md:** Huix et al. say kNN results are "largely in line" with
  linear/fine-tune results (**V**, ar5iv), not that kNN is unreliable; MedMNIST+ reports kNN
  72.1 vs linear 76.7 median accuracy, non-significant after correction but a large effect (**A**).
  Both entries are now corrected in 02.

### Recommended protocol for our tiny, imbalanced sets [I]

- Fit standardisation / centring on the training fold only; L2-normalise **ED and ES halves
  separately** before concatenation; cosine similarity; optional PCA inside the fold.
- Choose k by repeated stratified CV (or leave-one-out) on the training set — never on test;
  temperature-weighted soft votes, divided by class prior; report macro OVO AUROC from soft votes,
  balanced accuracy and per-class recall, with paired bootstrap CIs.
- Add **nearest-centroid** (SimpleShot-style: centre + L2-normalise): no k to tune, and it is the
  only kNN-family readout that can predict the M&Ms HHD class, which has a single training patient.
- Report kNN next to logreg and an attentive / patch-mean readout (REPORT §5 #2), with CLS and GAP
  pooling. Pre-register the prediction: if CineMA's deficit grows under kNN and shrinks under
  normalisation / patch-mean pooling, the deficit is a readout effect.

### Extra uses [I]

- **Few-shot curve** with nearest-centroid (1 → all training patients per class).
- **Interpretability:** show each test patient's nearest training patients ("this looks like that").
- **Cross-dataset retrieval** (ACDC bank → M&Ms queries) for shared classes (NOR, DCM, HCM) — a
  shift test that needs no retraining.

**Effort:** hours. Pooled embeddings are already cached per patient by `classification_probe.py`;
kNN / nearest-centroid is a new `--head` choice next to `logreg` and `linear`.

---

## How the four fit together [I]

The strongest next-stage paper is one question asked four ways: **is it the cardiac domain or the
pretraining objective that makes frozen CMR features useful?**

1. Backbones: NI-MAE, NI-DINOv3, UKB-continued MAE, UKB-continued DINOv3 (Q2), plus CineMA and
   SAM as references.
2. Readouts: logreg, **kNN / nearest-centroid** (Q4), attentive probe — so the answer is not an
   artefact of one readout.
3. Tasks: ACDC / M&Ms / M&Ms-2 segmentation and pathology; **UKB phenotype label-efficiency curves
   and incident outcomes on a post-CineMA-cutoff test cohort** (Q1); **click-based segmentation,
   ED→ES propagation and a QC head** as non-standard tasks (Q3).
4. Hygiene from REPORT §5 (seeds, fixed configs, re-run invalid cells) still comes first.

Cheapest first steps, needing no UKB access: kNN / nearest-centroid heads (hours), ED→ES
propagation with cached features (days), the QC head on existing predicted masks (days).
