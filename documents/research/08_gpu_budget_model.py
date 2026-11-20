"""GPU-hour budget model behind 08_gpu_budget.md.

All quantities are GH200-hours on Isambard-AI. Scenarios: low / central / high.
Run: python documents/research/08_gpu_budget_model.py
"""

S = ["low", "central", "high"]


def tri(lo, c, hi):
    return dict(zip(S, (lo, c, hi), strict=True))


# ---------------- throughput (img/s per GH200) ----------------
dino_tp = tri(480, 350, 250)  # DINOv2/3-style ViT-B, 2x224 + 8x96 crops + teacher
mae_tp = tri(2600, 2000, 1500)  # MAE ViT-B, 75% mask
dist_eff = tri(0.95, 0.90, 0.80)  # multi-GPU / multi-node scaling efficiency
# ---------------- M2 continued pretraining ----------------
dino_imgs = tri(15e6, 50e6, 100e6)
mae_imgs = tri(50e6, 150e6, 400e6)


def run_h(imgs, tp, s):
    return imgs[s] / tp[s] / dist_eff[s] / 3600


pilot_frac = tri(0.3, 0.6, 1.5)  # pilots+HP sweeps, in units of one main run
# Data-scaling curve: nested participant subsets, 3 random draws at 1k.
# Each subset is trained for the SAME NUMBER OF EPOCHS as the main run, so images
# seen scale with subset size, with a floor of `scaling_min_iters` iterations
# (batch 512) so the small subsets still train long enough to move off init.
main_participants = 75_000  # pre-cut-off cohort, ~CineMA's 74,916
scaling_subsets = [1_000] * 3 + [5_000, 20_000]
scaling_runs_per_arm = len(scaling_subsets)
scaling_batch = 512
scaling_min_iters = tri(10e3, 15e3, 20e3)
# One "epoch" = one random phase per (participant, slice position):
# ~10 SAX slices + 3 LAX views (Petersen et al. 2016, JCMR 18:8, Table 1).
slices_per_participant = 13


def scaling_imgs(main_imgs, s):  # total images seen over all subsets of one arm
    floor = scaling_min_iters[s] * scaling_batch
    return sum(
        max(main_imgs[s] * n / main_participants, floor) for n in scaling_subsets
    )


# ---------------- M1 public-dataset grid ----------------
train_slices = 8100  # ACDC ~1.5k + M&Ms ~3.1k + M&Ms-2 ~3.5k train slices (ED+ES)
epochs = tri(60, 80, 100)  # effective epochs incl. early stopping
val_overhead = 1.15
frozen_tp = tri(
    1500, 800, 400
)  # img/s, frozen ViT-B fwd + decoder fwd/bwd + online aug
job_overhead = tri(0.05, 0.1, 0.2)  # h per (dataset) job: load, cache warmup, test eval
sam_factor = tri(10, 15, 25)  # SAM v1 ViT-B @1024 vs ViT-B@224 cost


def seg_unit(s, factor=1.0):  # one (backbone, decoder, seed) over all 3 datasets
    imgs = train_slices * epochs[s] * val_overhead
    return imgs / frozen_tp[s] * factor / 3600 + 3 * job_overhead[s]


DEC, SEEDS = 3, 3
core_vitb = 6  # CineMA, DINOv3-B, random-init, MAE-NI, DINOv3->UKB, MAE->UKB
scaling_bb = 2 * scaling_runs_per_arm
seg_hp_units = (
    2 * DEC * 6
)  # decoder/aug sweep: 2 backbones x 3 decoders x 6 configs, 1 seed
cls_per_bb = tri(
    0.5, 1.0, 2.0
)  # extraction (aug views) + logreg/linear/kNN/attentive + EF regression, 3 ds x 3 seeds
nn_2d, nn_3d = tri(3.5, 4.5, 6.5), tri(4.5, 6.0, 9.0)  # h per fold, GH200
nn_extra = tri(1.05, 1.08, 1.10)  # validation/inference
# ---------------- M3 UKB ----------------
m3_bb = 7  # 2x2 (4) + CineMA + SAM + random-init
ukb_extract = tri(
    0.5, 1.0, 2.0
)  # h per ViT-B backbone for ~21k participants x ED/ES SAX (~420k imgs), I/O-bound
ukb_probe_runs = 9  # (1%x3, 10%x3, 100%x3 seeds) per head
ukb_attn_h = tri(
    0.1, 0.3, 0.8
)  # avg h per attentive-probe run (15-20 heads jointly, ~20 epochs, tokens in RAM)
ukb_lin_knn_h = tri(0.01, 0.03, 0.1)  # per run, linear + kNN together (mostly CPU)
label_gen = tri(
    5, 15, 30
)  # conditional: segment post-cutoff cohort if Bai IDPs missing
# ---------------- Stretch: LoRA + full FT ----------------
ft_bb_vitb, ft_bb_sam = 5, 1  # 2x2 + CineMA ; SAM
ft_tasks = 3  # segmentation (one decoder), classification, EF regression
ft_modes = {"full": 1.0, "lora": 0.85}
ft_runs_per = 3 + 3  # 3 lr pilots (1 seed) + 3 seeds at best lr
ft_epochs = tri(80, 120, 200)  # 200 max with early stopping
ft_tp = tri(900, 600, 350)  # img/s fwd+bwd through ViT-B + head + aug


def ft_unit(s, factor=1.0):
    return (
        train_slices * ft_epochs[s] * val_overhead / ft_tp[s] * factor / 3600
        + 3 * job_overhead[s]
    )


ukb_ft = tri(
    20, 50, 120
)  # optional: FT on UKB at 1% & 10% budgets, 6 backbones, 1 seed

# ---------------- Optional add-on: high-resolution stage ----------------
# Applied only to the two full-data continued-pretraining models.
# DINOv3: MedDINOv3 / DINOv3 recipe, ~10k iterations, global crops 512-768,
# local crops 112-336, batch 512. MAE has no published high-res phase: same
# image count at 512 px is assumed.
hr_imgs = tri(2.56e6, 5.12e6, 10.24e6)  # 5k / 10k / 20k iterations x batch 512
hr_cost = tri(4, 6, 9)  # per-image cost vs the 224 px recipe (4-5x tokens + attention)
hr_pilot_frac = tri(0.3, 0.5, 1.0)  # pilots, in units of one high-res phase
f512 = tri(5, 6, 8)  # evaluating at 512 px vs 224 px
HR_DEC = 1  # reduced grid: best decoder (likely UNETR) + classification heads


def hr_eval(s, factor):  # one backbone, reduced grid, 3 datasets, 3 seeds
    return HR_DEC * SEEDS * seg_unit(s, factor) + cls_per_bb[s] * factor


contingency = tri(1.15, 1.30, 1.50)

rows = {}
for s in S:
    r = {}
    r["M1 seg: 3 core backbones re-seeded + random-init (ViT-B class)"] = (
        3 * DEC * SEEDS * seg_unit(s)
    )
    r["M1 seg: SAM v1 ViT-B @1024"] = DEC * SEEDS * seg_unit(s, sam_factor[s])
    r["M1 seg: decoder/augmentation pilot sweep"] = seg_hp_units * seg_unit(s)
    r["M1 cls+reg heads (4 backbones incl. SAM)"] = (
        3 * cls_per_bb[s] + cls_per_bb[s] * sam_factor[s] / 3
    )
    r["M1 nnU-Net (2d + 3d_fullres, 5 folds, 3 datasets)"] = (
        3 * 5 * (nn_2d[s] + nn_3d[s]) * nn_extra[s]
    )
    dino, mae = run_h(dino_imgs, dino_tp, s), run_h(mae_imgs, mae_tp, s)
    r["M2 pretrain: main runs (DINOv3 + MAE)"] = dino + mae
    r["M2 pretrain: pilots / HP sweeps"] = pilot_frac[s] * (dino + mae)
    sc_dino = run_h({s: scaling_imgs(dino_imgs, s)}, dino_tp, s)
    sc_mae = run_h({s: scaling_imgs(mae_imgs, s)}, mae_tp, s)
    r["M2 pretrain: data-scaling runs (5 per arm, fixed epochs)"] = sc_dino + sc_mae
    r["M2 eval: 3 new backbones, full grid"] = 3 * (
        DEC * SEEDS * seg_unit(s) + cls_per_bb[s]
    )
    r["M2 eval: 10 scaling checkpoints, full grid"] = scaling_bb * (
        DEC * SEEDS * seg_unit(s) + cls_per_bb[s]
    )
    r["M3 UKB feature extraction (7 backbones)"] = (
        6 * ukb_extract[s] + ukb_extract[s] * sam_factor[s] / 3
    )
    r["M3 UKB label-efficiency heads"] = (
        m3_bb * ukb_probe_runs * (ukb_attn_h[s] + ukb_lin_knn_h[s])
    )
    r["M3 UKB label generation (conditional)"] = label_gen[s]
    base = sum(r.values())
    r["Debugging / failed-run contingency"] = base * (contingency[s] - 1)
    r["TOTAL core"] = base * contingency[s]
    st = {}
    for m, f in ft_modes.items():
        st[f"Stretch {m} FT, public datasets (5 ViT-B-class backbones)"] = (
            ft_bb_vitb * ft_tasks * ft_runs_per * ft_unit(s, f)
        )
        st[f"Stretch {m} FT, public datasets (SAM @1024)"] = (
            ft_bb_sam * ft_tasks * ft_runs_per * ft_unit(s, f * sam_factor[s])
        )
    st["Stretch FT on UKB 1%/10% (optional)"] = ukb_ft[s]
    sb = sum(st.values())
    st["Stretch contingency"] = sb * (contingency[s] - 1)
    st["TOTAL stretch"] = sb * contingency[s]
    r.update(st)
    hr = {}
    hr_dino = hr_imgs[s] / (dino_tp[s] / hr_cost[s]) / dist_eff[s] / 3600
    hr_mae = hr_imgs[s] / (mae_tp[s] / hr_cost[s]) / dist_eff[s] / 3600
    hr["High-res: pretraining phase (DINOv3 + MAE, full-data models)"] = (
        hr_dino + hr_mae
    )
    hr["High-res: pilots"] = hr_pilot_frac[s] * (hr_dino + hr_mae)
    hr["High-res: eval of 2 models at 512 px, reduced grid"] = 2 * hr_eval(s, f512[s])
    hr["High-res: eval of 2 models at 224 px, reduced grid"] = 2 * hr_eval(s, 1.0)
    hr["High-res (optional): natural-image DINOv3 + MAE at 512 px"] = 2 * hr_eval(
        s, f512[s]
    )
    hb = sum(hr.values())
    hr["High-res contingency"] = hb * (contingency[s] - 1)
    hr["TOTAL high-res add-on"] = hb * contingency[s]
    r.update(hr)
    rows[s] = r
    rows[s]["_dino"], rows[s]["_mae"] = dino, mae
    rows[s]["_segunit"] = seg_unit(s)
    # For comparison: the earlier design (every subset = main run's images seen).
    rows[s]["_scaling_fixed_imgs_seen"] = scaling_runs_per_arm * (dino + mae)
    epoch = main_participants * slices_per_participant
    rows[s]["_epochs_main_dino"] = dino_imgs[s] / epoch
    rows[s]["_epochs_main_mae"] = mae_imgs[s] / epoch
    rows[s]["_iters_1k_dino_no_floor"] = (
        dino_imgs[s] * 1_000 / main_participants / scaling_batch
    )
    rows[s]["_ftunit"] = ft_unit(s)

keys = [k for k in rows["low"] if not k.startswith("_")]
print(f"{'item':70s} {'low':>8s} {'central':>8s} {'high':>8s}")
for k in keys:
    print(f"{k:70s} " + " ".join(f"{rows[s][k]:8.0f}" for s in S))
for k in [
    "_dino",
    "_mae",
    "_segunit",
    "_ftunit",
    "_scaling_fixed_imgs_seen",
    "_epochs_main_dino",
    "_epochs_main_mae",
    "_iters_1k_dino_no_floor",
]:
    print(k, [round(rows[s][k], 2) for s in S])
for s in S:
    t = rows[s]["TOTAL core"]
    ts = rows[s]["TOTAL stretch"]
    print(
        s,
        "core GH200-h",
        round(t),
        "A100-eq",
        round(t / 0.5),
        "node-h",
        round(t / 4),
        "| core+stretch",
        round(t + ts),
        "A100-eq",
        round((t + ts) / 0.5),
        "node-h",
        round((t + ts) / 4),
    )
