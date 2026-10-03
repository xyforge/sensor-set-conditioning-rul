# Formal Experiment Protocol

合同编号：`FEP-4.1a`  
版本：`0.1.3-wp0`（2026-08-22）

状态：**C2 core/scope 与 execution-state contract 已完成 pre-outcome 修订；数值预算、splits 与 margins 待 precision/design lock**

上游合同：[Formal problem](./formal_problem_spec.md) · [Oracle/cell eligibility](./oracle_and_cell_eligibility_spec.md) · [Claim–metric registry](./claim_metric_registry.md)  
历史证据（pilot only）：[R1–R47 decision bundle](../results/r1_r47_decision_bundle/README.md)

> 本协议将 V4.1a 转为从 WP0 到 lockbox 的执行顺序。正式研究使用 `F0`–`F8` 命名空间，不启动 `R48`。本文件不把内部 gates 写成论文 Results 结构；它们只保证正文中的三项科学发现有可信地基。

---

## 1. 成功条件与执行边界

### 1.1 Protocol 成功，不等于论文 Claim 成功

协议执行成功表示：

- 数据、oracle、模型、统计和 artifacts 均遵守合同；
- 无论结果正负，Claim decision 可由保存的 per-asset data 自动复算；
- 失败按预声明转向，不再通过局部补丁开启探索轮。

论文完整主线成功另需 Gate C–F 按 registry 通过。

### 1.2 第一篇只执行的程序

```text
WP0 contract/schema freeze
  -> WP1 generator + same-information oracle (F0 / Gate A)
  -> WP2 development-only model qualification (F1 / Gate B)
  -> final precision, model, baseline and lockbox freeze
  -> WP3 confirmatory C1–C3 (F2–F4)
  -> explanatory ablations + alternate generator (F5–F6)
  -> WP4 public PHM + TSFM comparator (F7–F8)
  -> WP5 manuscript-facing synthesis + independent audit
```

F0 失败时停在问题世界；F1 失败时停在方法；F2/F3 失败时不能用 F4/F7/F8 挽救。

### 1.3 禁止的范围扩张

正式序列中禁止新增：learned sufficiency/abstention、active sensing、maintenance utility、
通用 ontology、第三种 relation loss、moment/quantile anchor 或 detached widening repair。
任何这类想法进入 backlog，不进入当前 protocol amendment。

### 1.4 科学裁决与执行有效性分离

Formal evaluator 必须先裁决合同有效性与可估计性，再计算科学 gate：

- permission/leakage violation → `INVALID / CONTRACT-VIOLATION`；
- reference、metric evaluator 或 bootstrap numerical failure → `NON-ESTIMABLE / EXECUTION-HOLD`；
- model 自身的 invalid support、collapse/density failure → 相应 Claim 的 scientific failure；
- primary 或 fatal scientific guard 未通过 → 相应 Claim 的 core failure。

前两类不得写成模型失败。修复 execution-only 问题后，只能按原冻结 model、estimand、weights
与 analysis 重算受影响范围，不能借机改变科学合同。

---

## 2. 冻结状态机与 lockbox

### 2.1 四个 freeze points

| Freeze | 必须锁定 | 允许之后改变什么 |
|---|---|---|
| `FRZ-0 SCIENCE` | V4.1a + 四合同的定义、Claims、方向、角色 | 仅 PENDING 数值/实现字段 |
| `FRZ-1 WORLD` | generator laws、\(\Pi_u\)、query law、factor grid、oracle、eligibility rules | development model implementation |
| `FRZ-2 MODEL` | proposed candidate、parameterization、training/tuning rule、baseline pool/selection | 只完成 power 与 exact run manifests |
| `FRZ-3 CONFIRMATORY` | assets/cells/splits、sample sizes、seeds、margins、metrics、bootstrap、code/env、failure policy | 无 outcome-responsive change |

只有 `FRZ-3` 完成并登记 versioned acceptance 后，才能执行 F2–F6 的 test/lockbox evaluation。CMR 中
`CM-T01`–`CM-T11`、`CM-T14`、`CM-T16`–`CM-T19` 必须在首次 F2 evaluation 前一次性纳入
该 bundle；F2/F3/F4 的 fixed sequence 不允许逐阶段补锁后续 Claim 门槛。

### 2.2 Split roles

asset-first 分为四个互斥集合：

| Split | 可见信息与用途 | 明确禁止 |
|---|---|---|
| `development` | generator debugging、normalization、architecture/HPO、oracle design calibration、power pilot | confirmatory claim |
| `validation` | early stopping、direct/relation promotion、baseline selection、一次 parameterization choice | training gradients、final Claim estimate |
| `test` | `FRZ-3` 后的正式 Stage-A effect estimation | tuning、cell/metric/margin selection |
| `lockbox` | 独立 asset/operator/generator seeds 下的 final confirmation | 在正式开启前查看任何 outcome/summary |

split 必须先按 base asset 生成；同一 asset 的所有 latent paths/views/query rows 只能属于一个
split。operator/cell manifest 随 split 生成，但 held-out factor tuple 在所有 split 中保持同一
角色。

`development` 还必须按 asset 分成两个互斥 subpartitions：

- `development/world_design`：generator/oracle calibration、eligibility、threshold scale 与
  power/precision；不进入 model gradient 或 checkpoint selection；
- `development/model_train`：model gradients、HPO 与 normalization fitting；不参与 cell
  eligibility point estimate。

这样 world/cell definition 与训练拟合不会复用同一批 latent trajectories。validation 仍是
第三个独立 asset set，只承担 early stopping、candidate promotion 和 baseline designation。
其中 early stopping 使用 Pgen-blind pooled proper score；需要 oracle-relative
\(R_{\mathrm{excess}}\) 或 \(\bar G\) 的 promotion/designation/guardrail 只能读取
`same_info_selection`，且发生在各 branch checkpoint 已冻结之后。

### 2.3 Test/lockbox combination rule

最终采用哪一种组合方式必须由 precision analysis 在 `FRZ-3` 锁定，且只能从以下两种中选择：

1. **Lockbox-primary（默认）**：test 为冻结后的 Stage-A replication，lockbox 为最终 primary
   Claim decision；test effect 完整并列，不与 lockbox pooled。
2. **Predeclared two-stage meta-estimand**：test 与 lockbox 使用固定 weights 合并，分别报告；
   lockbox point effect 还必须不出现预声明 adverse reversal。

选择依据只能是资源、目标 precision 与独立 replication 需求，不能是 test outcome。若在
`FRZ-3` 未明确写入，自动采用 lockbox-primary。本文档不预先伪造尚未完成的 power 决策。

一旦 Stage-A test 开始，model/cell/metric/margin 均不得修改。`FRZ-3` 还必须预先声明
lockbox 是否无条件执行及唯一允许取消的 fatal-audit/resource 条件；不得因 test effect 不利
而悄悄不打开或重建 lockbox。在默认 lockbox-primary 下，test 不承担 Claim pass/fail，
lockbox 决定 registry gate；但二者出现超过预声明 heterogeneity/reversal limit 的冲突时，
结论进入 `INTERPRETATION-HOLD`，不能只展示 lockbox。two-stage meta 方案则严格按预定
合并式判定，任一 stage 都不得单独 rescue。

### 2.4 Lockbox access

lockbox manifest 至少隐藏：

- asset IDs/seeds；
- operator/cell realization seeds；
- generator stochastic seeds；
- target/reference summaries；
- metric aggregates。

允许自动化 runner 读取 encrypted/permission-restricted manifest，但研究者在 `FRZ-3` 前不能
读取。每次 access 留下时间、命令、revision 与操作者记录。若意外打开，必须立即登记并生成
新 lockbox；不得只口头声明“没有仔细看”。

---

## 3. WP0：合同与 executable schema freeze

### 3.1 WP0 交付

- 本目录四份 contracts；
- machine-readable `problem_manifest` schema；
- `P_obs/P_gen` schema 与 model allowlist；
- reference-role consumer allowlist 与 stream/sample-ID schema；
- `oracle_cell_manifest` schema；
- `claim_metric_registry` machine table；
- baseline eligibility table（Section 8）；
- freeze ledger 与 amendment log；
- artifact directory/naming convention。

### 3.2 WP0 退出条件

- 所有科学对象只有一个 canonical definition；
- 任何 proposed experiment 可映射到 C1/C2/C3、E1/T1 或 required guardrail；
- 无映射实验不启动；
- 所有 PENDING 数值均有 derivation method 和 deadline；
- train/eligibility/selection/metric:test/metric:lockbox 的 producer–consumer mapping 唯一；
- 不需要读取 R1–R47 outcome 才能理解 formal estimand。

WP0 完成后仍不能训练 formal model；先执行 WP1/F0。

---

## 4. WP1 / F0：formal generator 与 oracle

### 4.1 Generator families

至少实现：

1. `GEN-A competing stochastic degradation`：两个相互作用/竞争 degradation coordinates、
   mechanism-dependent failure boundary、direct/proxy/redundant sensors；
2. `GEN-B nonlinear-or-switching`：改变 dynamics、measurement nonlinearity 或 stage
   transition，作为独立 robustness family。

primary/alternate 角色必须在 learned model comparison 前由 oracle tractability、数值成本与
scientific coverage 冻结，不根据哪一个更利于 proposed 决定。

### 4.2 Base-asset artifact

每个 asset 保存：

- latent path、past/future context、\(K_{\mathrm{fail}}\)、\(T_{\mathrm{fail}}\)、censoring；
- full sensor field、native event times 与 common observation randomness；
- asset/generator/operator/seed IDs；
- physically separated \(P_{\mathrm{obs}}\) 与 \(P_{\mathrm{gen}}\)；
- \(\Pi_u\) ID 与 realized future load（private）；
- oracle reconstruction state；
- split/manifest revision IDs。

可重建缓存可另存，但上述 canonical asset record、manifest 与 provenance 不得随空间清理删除。

### 4.3 Factorial design

构造 \(S\times R\times Q\) 候选 grid，使用 parent-first coupling。F0 不是穷举竞赛；只在
oracle audit 后保留足以覆盖：

- compatible sufficient pairs；
- critical/random/redundant matched triplets；
- low/medium/high ambiguity strata；
- sufficient 与 loss composition holdouts；
- 非退化 support。

informative MNAR/nonordered swaps 必须标为 boundary cells，不能混入 Claim 2 primary。

### 4.4 Same-information oracle pipeline

执行顺序：

1. 冻结 generator law、\(\Pi_u\)、target normalization candidate；
2. 为 analytic special case 实现 reference；
3. 实现 primary MC/IS/SMC reference；
4. 分离 train/eligibility/selection/metric:test/metric:lockbox/omniscient roles；
5. 完成 SBC、budget ladder、ESS/degeneracy 与 independent spot-check；
6. 估计 \(\bar B^\star,\mathcal A^\star_{\mathrm{obs}},D^\star\) 及 MC floor；
7. 依据 OCES 状态机生成 eligibility manifest；
8. 生成 Gate-A report；
9. 登记 `FRZ-1 WORLD` artifact revisions 与 acceptance。

### 4.5 F0/Gate A stop rule

若以下任一发生，停止进入模型开发：

- same-information reference 不稳定或误用 hidden labels；
- critical 与 matched controls 的 oracle effect 达不到预冻结 scientific threshold；
- compatible sufficient pairs 不足；
- parent/garbling relation无效；
- oracle MC error 与 scientific effect 同量级；
- cell support 只能靠 near-empty views 建立。

只允许修复 generator/oracle/设计，不允许用 learned model output 定义“好 cells”。Gate A 通过
前的计算属于 world construction，不是 R48，也不是论文确认性结果。

---

## 5. WP2 / F1：development-only model qualification

### 5.1 Proposed candidates

只实现两个 candidate branches：

- `PROP-DIRECT`：observation-process-conditioned joint posterior + direct joint density objective；
- `PROP-RELATION`：同一 model + 预声明 scalar geometry regularization。

architecture、head family、mixture components、learning-rate 等可以在 development budget 内
调节；不能增加第三种 scientific loss。若默认 mixture 在 absolute posterior predictive
checks 触发 parameterization review，只允许执行一次 protocol 中预写的 matched-head
conditional-flow trial；proposed 与 eligible probabilistic baseline 使用相同 flow family、预算与
训练规则。最终 mixture/flow 选择按预声明 validation rule完成，不重开 relation promotion。

### 5.2 Candidate promotion

执行：

1. 两候选使用相同 development/validation rows、supervision、HPO budget 与 seeds；
2. 先检查 absolute learnability ceiling；
3. 按 CMR Section 7.2 的 \(\bar G\) improvement + per-view \(R_{\mathrm{excess}}\) non-inferiority rule；
4. 条件满足则 promotion `PROP-RELATION`；否则 `PROP-DIRECT` 且
   \(\lambda_{\mathrm{geom}}=0\)；
5. 保存全部候选结果与 decision，不因 direct 获胜而隐藏 relation failure；
6. 生成唯一 `promoted_candidate_id`，进入 `FRZ-2 MODEL`。

每个 candidate branch 必须先用 Pgen-blind pooled validation proper score 独立冻结 checkpoint。
promotion evaluator 只读取去除 intervention/mechanism labels 的
`pair_id + same_info_selection D* + validation metric rows` manifest；其 reference artifacts
必须标记 `reference_role=same_info_selection, split_role=validation`。不得把
critical/random/redundant 字段交给 model、optimizer 或 checkpoint epoch selector。

F2/F3/F4 必须使用同一个 promoted checkpoint family。不得为 sufficient 与 critical cells
分别选择模型。

### 5.3 Gate B

Gate B 通过要求：

- seen validation support 上达到 absolute \(\tau_{\mathrm{learn}}\)；
- 对 same-permission standard probabilistic baseline 至少 non-inferior；
- joint/state/failure distributions 无 collapse 或 invalid support；
- point performance 无 catastrophic loss；
- promotion decision完成且冻结。

posterior predictive shape checks 只承担 parameterization trigger、C2 claim-linked scope
diagnostic 与论文表述限制，不属于 Gate B core。若 core 通过但 shape thresholds 未全部达到，
Gate B 状态为 `PASS-CORE / SHAPE-LIMITATION`，可继续执行唯一 parameterization trial 与后续
合同步骤。

coherent target permutation 只检查 pipeline 是否能区别真实 conditioning signal，不能作为
“比随机好所以可学习”的成功门槛。

### 5.4 F1 失败动作

若默认 parameterization 触发 shape review，执行唯一一次 matched-head upgrade trial，并在
asset-disjoint validation `same_info_selection` 上按预声明 rule 固定 mixture 或 flow。只要 Gate B
core endpoints、support、point guardrails 与 candidate uniqueness 继续通过，upgrade 未达到全部
绝对 shape threshold 不自动停止当前方法；shape limitation 向 C2 scope diagnostics 传播。不得
继续进入 geometry/moment/quantile loss 搜索，也不得用 public dataset 先成功再反向声称
controlled posterior 可学习。

---

## 6. Precision、样本量与 final execution lock

### 6.1 Power/precision targets

在 promoted candidate、posterior parameterization 与所有 claim-specific strongest baselines
完成 `FRZ-2` 冻结后，以 validation
`reference_role=same_info_selection, split_role=validation` 的 asset-level effect vectors
估计以下 estimands 的 covariance/variance：

- `C1-P1 ΔG_suf`；
- `C2-P1 ΔR_crit`；
- `C2-P2 ΔG_loss`；
- `C2-P3 I_R`；
- `C3-P1 ΔC_raw`。

样本量设计目标：

- 每个 Claim 的完整 intersection 达到冻结的 target power，默认至少 0.90；
- CI half-width 小于对应 minimum scientific effect；
- oracle MC error 小于 OCES 冻结比例；
- critical/sufficient/held-out strata 均有足够独立 assets；
- worst-cell guard 不因单 cell 极低 n 完全失去意义。

C2 不能以“P1、P2、P3 各自 power ≥ 0.90”替代 joint design。必须从上述 post-checkpoint
validation `same_info_selection` assets 估计 P1/P2/P3 与 fatal scientific guards 的
asset-level joint covariance，在候选 asset count 下模拟完整 paired estimator、CI 与 margin
decision，并锁定：

\[
\Pr\!\left(
C2\text{-}P1\cap C2\text{-}P2\cap C2\text{-}P3
\cap C2\text{-}G0\cap G2\cap G3\text{-MODEL}\cap G4
\right)\ge p_{\mathrm{joint,target}}.
\]

`FP-P09` 记录 \(p_{\mathrm{joint,target}}\)、validation covariance source、reference binding、
simulation law、candidate asset counts、joint pass probability 与 CI precision。validation
observed effects 只用于 covariance/variance 与 numerical-behavior rehearsal；power alternatives
必须以预声明 minimum scientific effects、non-inferiority margins 与 adequacy ceilings 为中心，
不得直接以 observed validation effects 作为预期效应。C2 components 构成
intersection-union decision，不对 core components 机械追加 Bonferroni；individual secondary
families 仍按 CMR 的 multiplicity policy处理。

R1–R47 只可提供保守 variance/resource range；旧 estimand 不同，不直接借用旧 effect size 或
success threshold。

### 6.2 要锁定的 counts

`FRZ-3` 前必须明确：

- 每 generator/split 的 independent asset count；
- query-time strata 与每 asset/query replicates；
- observation realizations；
- oracle samples/repeats/budget ladder；
- optimization seeds；
- bootstrap replicates；
- train/validation/test/lockbox split rule；
- F6 alternate-generator replication count；
- public dataset asset inclusion/exclusion。

更多 query rows 不能替代更多 assets，更多 oracle samples 不能替代数据-level replication，
更多 optimization seeds 不能当统计样本。

### 6.3 Optimization seeds

- 所有 core models 使用相同 seed schedule；
- 每 seed 产生独立 checkpoint 与 per-asset prediction；
- primary 平均 losses，不平均 predictive distributions；
- 报告 per-seed effect、between-seed variance 和 asset-by-seed variation；
- 若某 seed 失败，按 Section 13 的统一 failure policy，不得只重跑 proposed。

### 6.4 Candidate-only C2 claim-alignment dry-run

`FRZ-3` 前允许在 promoted candidate、posterior parameterization 与所有 strongest baselines
完成 `FRZ-2` 冻结后执行一次 C2 claim-alignment audit，用于校验
metric schema、P1/P2/P3 aggregation、modality under-response、G5/G7 scope routing 与 evaluator
numerical health。该 audit：

- 只能使用 checkpoint 冻结后的 validation prediction stores 与
  `reference_role=same_info_selection, split_role=validation`；
- 在 reference allowlist 中归类为 `validation_guardrail`，不得重新选择 checkpoint、candidate、
  posterior parameterization 或 strongest baseline；
- 禁止消费 `same_info_train`、`same_info_eligibility` 作为 oracle-relative metric reference；
- 禁止访问 test/lockbox `same_info_metric`、F2–F6 或 public outcomes；
- 不产生 C2 pass/fail，只能为 `CM-T19`、analysis implementation 与 power covariance/variance
  simulation提供 pre-confirmatory design evidence；observed validation effect 不得作为 power
  alternative。

development-only synthetic rows 可测试 runner/schema，但不能替代上述 validation reference
audit，也不能形成任何 paper-facing effect。

### 6.5 Final lock bundle

`FRZ-3 CONFIRMATORY` bundle 至少包含：

```text
contracts + freeze ledger
code revision + environment lock
generator/operator/split manifests
cell eligibility manifest
model and baseline manifests
input/target permission table
reference-role allowlist + stream/sample-ID manifest
metric registry + margins
power/precision report
seed schedules
exact commands
analysis scripts + synthetic dry-run expected schema
lockbox access policy
```

bundle 生成 versioned manifest 并登记 acceptance；之后才可执行 F2。

---

## 7. WP3：F2–F6 formal packages

### 7.1 F2 — Sufficient-view compatibility / C1

**Population**：`ELIGIBLE-COMPATIBLE-PAIR`。  
**Models**：promoted proposed、C1 strongest baseline、metadata-free、forced-invariance、
independent marginals；其他 eligible models 完整报告。  
**Primary**：`ΔG_suf`。  
**Required**：absolute \(\bar G_{\mathrm{suf}}\) 与 pair-side \(R_{\mathrm{excess}}\) ceilings、
full-view non-inferiority、marginals、collapse/support guards。  
**Decision**：CMR `C1-DEC` / Gate C。

执行必须：

- 同一 checkpoint family 同时预测 pair 两侧；
- 保留 realized-pair \(G_i\)，再 asset/pair-class 聚合；
- 不从 low \(G\) 推断低 ambiguity；
- 不因 explicit metadata ablation 无 effect 判 C1 失败；
- 不使用 F3/F4 结果重新选择 candidate。

### 7.2 F3 — Partial-identifiability response / C2

**Population**：eligible critical/random/redundant matched triplets。  
**Models**：promoted proposed、C2 strongest baseline、forced invariance、generic widening、
mask-rate-only/minimal controls。  
**Co-primary**：`C2-P1 ΔR_crit`、`C2-P2 ΔG_loss` 与 `C2-P3 I_R`。

**Fatal scientific guards**：absolute critical-risk/loss-geometry ceilings、failure-time CRPS
non-inferiority、model density/support integrity 与 full-view fidelity。

**Admissibility/estimability**：permission/schema contract 与 evaluator/reference numerical
health。

**Scope annotations**：oracle-active shape response、explanatory controls 与 joint dependence。

**Decision**：CMR `C2-DEC` / Gate D；Gate D 只由 C2-core 决定，scope annotation step 不是
独立 gate。

执行必须：

- 只在 oracle 已通过 \(\mathcal A^\star_{\mathrm{obs}}\) 与
  \(\Delta\mathcal A^\star_{\mathrm{crit}}\) 的 triplets 上确认；
- critical/control rows 复用 parent observation realization；
- `C2-P1` 按 query → asset → optimization seed → critical-cell macro 聚合；
- `C2-P2` 对 critical–parent、critical–matched-random、critical–redundant 三个 pair classes
  macro 等权，class 内 asset 等权；任一 class 不可估计时不得对剩余 classes 重归一化；
- `C2-P3` 默认使用 matched-random control；只有 `FRZ-3` 前冻结的 whole-channel fallback
  才可改用 matched-redundant，禁止逐 triplet 混用；
- 同时报告 location、scale、modality、tail、dependence 中实际发生的 reference change；
- modality under-response 与 direction reversal 分开；variogram/conditional curves 只生成
  scope annotations，不升为第四 endpoint；
- coverage/width 不能替换 proper score/geometry。

`C2-G6a` 失败记录为 `C2-INVALID / CONTRACT-VIOLATION`；reference/evaluator numerical
failure 记录为 `C2-NON-ESTIMABLE / EXECUTION-HOLD`；model 自身 invalid support/collapse 或
任一 core component失败才记录为 `C2-CORE-FAIL`。core failure 后仍计算 scope diagnostics，
但全部标记 exploratory。

### 7.3 F4 — Compositional holdout / C3

**Population**：predeclared unseen joint \(S\times R\times Q\) cells，各单因素 training seen。  
**Models**：promoted proposed 与 C3 strongest baseline，其他 baselines 为完整比较。  
**Primary**：`ΔC_raw`，cell-macro raw weights。  
**Required**：absolute held-out ceiling、sufficient/loss strata、worst-cell、influence、support
contracts 与 leakage audit。  
**Robustness only**：\(C_{m,\mathrm{matched}},\Delta C_{\mathrm{matched}}\)。  
**Decision**：CMR `C3-DEC` / Gate E。

只有 `C1` 与 `C2-core` 通过时 C3 才保持 confirmatory。`C2-CORE-PASS` 带 shape、dependence
或 attribution limitation 时不阻断 C3，但 annotations 向后传播；`C2-CORE-FAIL` 时 C3
降为 exploratory。

F4 只评价泛化，不重选 architecture/loss/stopping/operator encoding。matched analysis：

- descriptors/weights/overlap/ESS/truncation 在 lockbox 前冻结；
- common support 不足即 `NON-ESTIMABLE`；
- raw/matched 冲突保留 raw 主结论；
- matched 有利不能 rescue raw failure。

F4 的 primary training allocation 是 `balanced-support`：seen cells 等 exposure，且 proposed
与 baselines 共享相同 total asset/target/optimizer budget。`baseline-support` 按冻结的
deployment-like frequency 独立重跑并作为 allocation sensitivity；它不与 balanced result
pooled，也不能救回 primary。两套 support 使用相同 held-out evaluation rows，避免把
evaluation difficulty 改变误作 training-support effect。

### 7.4 F5 — Method ablations

F5 在 promoted model 已冻结后解释机制，不参与重新 promotion。最低 mapping：

| Ablation | 对应问题 |
|---|---|
| remove nonrecoverable \(P_{\mathrm{obs}}\) metadata | 合法 metadata 是否有增量；允许无 effect |
| joint → independent marginals | joint factorization 是否贡献 C1/C2 fidelity |
| oracle relation → all-view invariance | universal invariance 在 loss views 是否有害 |
| direct vs relation | 仅当 relation 获 promotion 时验证增量 |
| end-to-end → frozen/head-only | coupling 是否必要 |
| remove latent \(k\) | multimodal representation 是否需要 |
| factorized encoding → raw fields | representation choice 是否关键 |
| mixture → unimodal | posterior shape capacity 是否关键 |
| specialized ↔ TSFM backbone | backbone/pretraining contribution |

若某 ablation 与预期方向不同，更新机制解释，不改 primary Claim metric。

### 7.5 F6 — Alternate generator

使用 `GEN-B` 独立 assets/operator seeds，运行冻结的 promoted candidate、strongest baselines 和
同一 metrics。F6 评价方向稳定与适用边界，不允许在 GEN-B 上重新 HPO 到与 GEN-A 完全不同的
方法；只可使用预声明 family-specific normalization/observation interface adaptation。

若 GEN-A 成功、GEN-B 失败，不能写跨 generator 普遍结论；分析 failure 来自 dynamics、
measurement nonlinearity、posterior shape 或 support。

---

## 8. Baseline eligibility 与选择

### 8.1 Core baseline pool

| ID | Model family | 必须共享 | 区别变量 | 正文角色候选 |
|---|---|---|---|---|
| `B-DET` | point state/RUL GRU/Transformer | split/views/targets where applicable | deterministic output | engineering floor |
| `B-STDPROB` | standard probabilistic posterior | backbone/head capacity budget、joint target data | 无额外 process metadata/relations | ordinary probabilistic baseline |
| `B-INDEP` | observation-aware independent marginals | \(P_{\mathrm{obs}}\)、encoder、supervision | state/time heads independent | joint factorization test |
| `B-METAFREE` | metadata-free matched | event values/minimal structural fields | 删除不能由 event history恢复的 metadata | metadata increment |
| `B-INVAR` | forced all-view invariance | paired data/backbone/head | universal consistency target | key conceptual baseline |
| `B-WIDEN` | generic detached widening/calibration | source model/data | generic scale/quantile repair | generic uncertainty baseline |
| `B-CDE` | Neural CDE + same posterior head | data/target/tuning budget | continuous-time backbone | timing baseline |
| `B-SET` | eligible sensor-set/semantic encoder | data/target/head | flexible set representation | sensor-interface baseline |
| `B-TSFM-*` | max two TSFMs + same head | split/metrics/permissions | pretrained backbone, frozen/PEFT | comparator only |

### 8.2 Eligibility criteria

baseline 只有全部满足才可成为 strongest：

- 可复现 code/license 或清楚标为本研究适配；
- model input/target permissions 有明示 contract；
- 无 \(P_{\mathrm{gen}}\)、future load、lockbox leakage；
- tuning budget 与 proposed 同等级；
- posterior output 可计算对应 primary metric；
- training/convergence 无系统性失败；
- 参数量、compute、pretraining data advantage 已报告；
- 未因 test result 被事后加入或删除。

deterministic baseline不能成为 joint-posterior Claim 的 strongest，但必须用于工程可比性。
TSFM 若有额外预训练数据，作为 data-advantage comparator 单列。

### 8.3 Strongest baseline freeze

允许每个 Claim 有一个预先冻结、最能挑战该 Claim 的 baseline \(b_C^\star\)，但选择只用
development/validation：

- `C1`：先满足 per-view/full-view guard，再按 validation `M-GEO` 最低；
- `C2`：先满足 failure/full-view guard，再按 validation critical `M-RX`、loss `M-GEO`
  的预声明 lexicographic order；
- `C3`：在 validation-only balanced-support pseudo-composition rotations 上
`ΔC_raw` 最低；
- ties 使用 validation joint \(R_{\mathrm{excess}}\)，再依次以更低实测 compute 与 canonical
  model ID 作为 deterministic tie-breaker。

pseudo-composition rotations 的 cells/weights 必须在运行前冻结，不能使用 formal held-out
cells 的 outcome。每个 \(b_C^\star\) 可不同，但在 test/lockbox 前必须唯一；结果中仍展示所有
eligible baselines，不能藏起比 frozen strongest 偶然更好的模型。

strongest-baseline designation 发生在各 baseline 的 Pgen-blind checkpoint 已冻结之后，属于
analysis-side comparator selection。evaluator 可使用 oracle eligibility strata，但 model
训练与 epoch selection 不得读取这些 strata；selection table 必须保存所有 eligible models
的排序，而不是只保留获选者。

上述所有 oracle-relative designation metrics 只能消费
`reference_role=same_info_selection, split_role=validation`；不得消费
`same_info_eligibility` 或任一 test/lockbox `same_info_metric` artifact。

### 8.4 Supervision/permission matrix

| Model class | Events/values | minimal IDs/times/masks | extra legal \(P_{\mathrm{obs}}\) | joint \(Y\) draws | same-info relation samples | \(P_{\mathrm{gen}}\) |
|---|---:|---:|---:|---:|---:|---:|
| proposed direct | yes | yes | yes | yes | no | **never** |
| proposed relation | yes | yes | yes | yes | train-only | **never** |
| standard probabilistic | yes | required structure only | no | yes | no | **never** |
| observation-aware independent | yes | yes | yes | same marginals | no | **never** |
| metadata-free | yes | yes | no nonrecoverable metadata | yes | according to parent family only | **never** |
| forced invariance | yes | yes | yes | yes | no oracle distance; paired identity target | **never** |
| generic widening | yes/source representation | yes | matched to source | same target/source | no | **never** |
| CDE/set/TSFM | yes | interface-required | same allowlist | same target | only if explicitly same method branch | **never** |

`B-STDPROB` “不输入 \(P_{\mathrm{obs}}\)”不意味着删除 event sequence 必需的 timestamps/sensor IDs；
它只不使用额外 process features/relations。否则比较会把可解析输入接口与科学条件化混为一谈。

---

## 9. Training、HPO 与 checkpoint contract

### 9.1 Equal-budget rule

core proposed/baseline families必须预先分配：

- 相同数量级的 HPO trials；
- 相同 max epochs、early-stopping opportunity 与 validation information；
- 同样 optimization seed count；
- 合理的 family-specific hyperparameter ranges，范围在运行前发布；
- 相同 metric implementation 与 row weights。

完全相同 hyperparameters 不代表公平；公平是相同信息和调优机会。exact budgets 为
`PENDING-DESIGN`，在首个 F1 trial 前冻结。

### 9.2 Checkpoint selection

checkpoint 只按 validation joint proper score 与预声明 guardrail rule选择。禁止：

- 按某个 held-out cell、ambiguity level 或最有利 metric 选择；
- 为 C1/C2/C3 使用不同 proposed checkpoints；
- 在 formal result 后换 early-stopping epoch；
- 对 proposed 多次重启只保留最佳，对 baseline 保留单次；
- 用 generator labels 做 auxiliary validation。

### 9.3 Relation target use

若 relation branch 使用 same-information oracle samples：

- 只来自 development training assets；
- 与 eligibility/selection/metric:test/metric:lockbox sample streams 分离；
- distance estimator 与 normalization 固定；
- 不读取 validation/test/lockbox oracle samples；
- \(\lambda_{\mathrm{geom}}\) grid 和 selection rule在 first trial 前冻结。

### 9.4 Parameterization upgrade

默认 mixture → conditional spline flow 的唯一升级 trigger 必须量化为 absolute posterior
predictive failure，例如多个预声明 reference-shape diagnostics 超出阈值且非 optimization
failure。升级后不得保留两种 parameterization 到 test 再挑；必须在 validation 决定一个。

---

## 10. Statistical execution

### 10.1 Per-asset tables first

metric runner 先产出 immutable per-row/per-asset tables，再 aggregate。analysis 必须可以仅凭：

- per-asset losses；
- cell/pair/triplet manifest；
- fixed weights；
- bootstrap seed；

复算所有 Claim effects。聚合报告不能成为唯一数据源。

### 10.2 Paired bootstrap

默认 procedure：

1. 在 generator/cell eligibility strata 内重采样 independent asset IDs；
2. 同一 replicate 为所有 models/views 使用相同 asset selection；
3. 保留 asset 内全部 query/view repeated measures；
4. 先按 optimization seeds 平均 losses；
5. 计算 Claim-level macro estimand；
6. 若 oracle numerical component 不可忽略，嵌套抽取 independent oracle repeat 或合并保守
   error bound；
7. 输出 point estimate、CI、margin decision 与 bootstrap diagnostics。

bootstrap replicate count/CI construction 在 `CM-T16` 冻结。若 strata 中 assets 不足，先在
power 阶段增加 assets，不能在 formal 阶段改成 row bootstrap。

### 10.3 Multiple comparisons

- Gate C→D→E fixed sequence；
- Claim co-primary 使用 intersection；C2 明确为 P1∩P2∩P3；
- C2 sample-size simulation 以整个 core intersection 的 joint pass probability为目标，不能
  用各 component 分别达到 0.90 替代；作为 intersection-union decision，不对 P1/P2/P3
  再机械执行 Bonferroni；
- individual cells 与 secondary metrics 不作为“任选一个成功”；
- average、worst-cell、matched robustness 与 alternate generator 分表；
- public datasets 先选 dataset-specific primary，不能事后挑 CRPS/NLL/IBS。

### 10.4 Reporting seeds

报告：

- seed-averaged loss estimand；
- each-seed effects；
- between-seed SD；
- asset × seed variance component；
- optimization failure rate。

若最终另报 ensemble，必须在所有 eligible models 上用相同 ensemble size，并单列 compute；
ensemble 不替换 single-model primary。

---

## 11. WP4 / F7–F8：public PHM 与 TSFM

### 11.1 Dataset audit before use

最低 external families：

1. N-CMAPSS；
2. XJTU-SY 或 audit 后冻结的一套 bearing run-to-failure data。

每套 audit 包含：许可、asset/trajectory count、channels、sampling、operating conditions、
failure/censoring definition、合法 split、泄漏风险、可构造的 \(S/R/Q\) interventions、
\(\Pi_u\) 估计方式与 metrics。

bearing dataset 选择只能基于 audit quality 与任务适合度，不基于 model outcome。

### 11.2 F7 public latent-marginal bridge

public model 只优化/评价：

\[
q_\phi(\Delta T\mid O)=\sum_k\int q_\phi(k,\tilde h,\Delta T\mid O)d\tilde h.
\]

执行：

- asset-level split；
- training-only scaler、sensor mapping 与 \(\Pi_u\) estimation；
- observed event/failure/censoring supervision；
- simulator initialization yes/no ablation；
- specialized probabilistic baselines；
- controlled sensing transformations；
- failure-time proper score、calibration、point guardrail。

不计算 public \(h_t\) oracle，不把 \(\tilde h\) 作 physical interpretation，不用 public result
反证或证明 controlled-world C1/C2。

### 11.3 F8 TSFM comparator

最多两个满足许可、复现和输入接口的 TSFM。每个执行 frozen adapter 与 PEFT，在同 posterior
head、split、target 与 permission 下比较 specialized backbone。记录 pretraining corpus/data
advantage、parameters、training/inference cost。

若 TSFM 无稳定优势，放 Supplementary 或删除正文叙事；不得更换 TSFM 直到出现有利结果。

---

## 12. Controls 与泄漏审计

### 12.1 必做 pre-run audits

| Audit ID | 检查 |
|---|---|
| `AUD-01` | model dataloader allowlist 无 \(P_{\mathrm{gen}}\) |
| `AUD-02` | random batch dump 中无 intervention/mechanism/future fields |
| `AUD-03` | same-information reference conditioning trace |
| `AUD-04` | asset/split key collision |
| `AUD-05` | held-out cell factor coverage 与 tuple exclusion |
| `AUD-06` | normalization/scaler development-only |
| `AUD-07` | matched triplet count/coverage/SNR/mask balance |
| `AUD-08` | selection/test/lockbox reference samples 未进入 training cache，且 role/split consumer allowlist 无越权 |
| `AUD-09` | metric code 在 analytic distributions 上通过 identity checks |
| `AUD-10` | seeds/commands/manifests 可复现且 revision IDs 一致 |

任一 fatal audit 失败时停止 run；不得“先训练看看是否影响结果”。

### 12.2 Minimal negative controls

- coherent full-target permutation：pipeline sanity only；
- metadata-only / process-only without values：检查 shortcut；
- mask-rate-only：检查 generic missingness heuristic；
- generic widening：检查 coverage-through-overdispersion；
- omniscient oracle：simulator/inference sanity only。

这些 controls 进入 Supplementary，除非其结果推翻中心解释。它们不是各自独立贡献或正文
Results 章节。

---

## 13. Failures、retries 与 amendments

### 13.1 Training/runtime failure policy

在 `FRZ-3` 前冻结：

- 什么构成 infrastructure failure vs model failure；
- 每个 model/seed 的统一 retry cap；
- retry 是否复用 seed；
- NaN/invalid distribution 的 scoring rule；
- missing prediction 的 penalty；
- 超时/资源中断的处理；
- 何时整个 model family 判为 ineligible。

同一 policy 必须作用于 proposed 和 baselines。只对不利 seed 反复重启属于 protocol violation。

Claim evaluator 还必须输出 `execution_status` 与 `scientific_status` 两个字段：

- permission/leakage violation：`execution_status=INVALID`，不填科学 pass/fail；
- reference/evaluator numerical failure：`execution_status=NON-ESTIMABLE`，
  `scientific_status=NOT-EVALUATED`；
- execution valid 时，模型 invalid support/collapse 与 primary/scientific-guard failure 才进入
  `scientific_status=CORE-FAIL`。

### 13.2 Amendment classes

| Class | 示例 | 处理 |
|---|---|---|
| `A-NONSUBSTANTIVE` | typo、report rendering、未影响数值的路径修复 | 记录 diff/revision，不重开 science freeze |
| `B-PREOUTCOME` | 在 formal outcomes 不可见时发现 metric/code bug | 修复、提升 protocol version、重跑所有受影响 models/splits |
| `C-OUTCOME-AWARE` | 看到 test/lockbox 后改 margin/cell/model/metric | 原 confirmatory sequence失效；新版本只能标 exploratory 或建立新 lockbox |
| `D-FATAL-LEAKAGE` | asset/P_gen/future/test leakage | 丢弃所有受影响 runs，重建 split/lockbox |

所有 amendments 进入 append-only ledger，包含发现时间、当时已见数据、受影响 artifacts 与
裁决。

### 13.3 Stop rules

- Gate A 失败：重设 world 或缩小 claim，不调更多模型；
- Gate B 失败：一次 parameterization upgrade 后停止当前 method；
- Gate C 或 `C2-CORE-FAIL`：当前完整方法论文停止，按 V4.1a 转向矩阵处理；
- `C2-INVALID` 或 `C2-NON-ESTIMABLE`：停止受影响 execution，修复合同/实现问题并按冻结
  design 重算；不得写成方法科学失败；
- Gate E 失败：收缩 compositional claim，不修改 C1/C2 results；
- Gate F 失败：限制到 controlled-world 适用性，不伪造真实 latent conclusion。

---

## 14. Artifact 与 provenance contract

### 14.1 Formal run namespace

建议目录：

```text
formal_runs/
  contracts/
  world/<generator_version>/
  oracle/<oracle_version>/
  f0_oracle_validation/
  f1_development_qualification/
  f2_sufficient_compatibility/
  f3_information_loss/
  f4_composition/
  f5_ablations/
  f6_alternate_generator/
  f7_public_phm/
  f8_tsfm/
  lockbox/
  reports/
```

不得延续 `r48_*` 命名，也不得覆盖 R1–R47 artifacts。

### 14.2 每个 run 必存

- immutable code revision、dirty-worktree diff snapshot、environment lock；
- exact command、config、stdout/stderr 与 resource report；
- dataset/generator/operator/split manifest + revision ID；
- \(P_{\mathrm{obs}}/P_{\mathrm{gen}}\) schema、\(\Pi_u\)、input/target permissions；
- trainable/frozen modules；
- checkpoint selection log 与 candidates；
- per-asset raw predictions、posterior/reference sample identifiers；
- atomic/per-asset metrics；
- bootstrap seeds/results；
- aggregate tables、gate decision、failure report；
- provenance parent pointers。

### 14.3 Retention

不得删除：

- raw example/prediction tables used by Claims；
- key checkpoints；
- reference samples或可验证的 immutable sample shards；
- manifests/revisions；
- aggregate/audit/reports；
- amendment/failure logs。

只可删除有明确重建路径的缓存；每次删除写入 ledger，含 target、reason、recoverability 与
artifact revision。

---

## 15. Manuscript-facing output contract

内部 F/Gate 编号不作为正文结构。formal artifacts 最终映射为：

| Formal evidence | 正文发现 |
|---|---|
| F0 oracle map | observation processes change irreducible prognostic ambiguity |
| F1 compact qualification | conditional posterior fidelity is learnable |
| F2 | sufficient views remain posterior-compatible |
| F3 | information-losing views retain the right posterior change |
| F4/F6 | behavior extrapolates, with stated generator/composition boundary |
| F7/F8 | public failure-time marginals and backbone comparison |

input permissions、matching、negative controls、seed decomposition、full baseline table、oracle
budgets 与 amendments主要进入 Methods/Supplementary。若某 control 揭示中心 shortcut，才提升到
正文解释；严谨性不能被删除，只是不抢占论文正面故事。

---

## 16. Freeze ledger：当前仍需实例化的字段

| ID | 字段 | 决定程序 | Deadline |
|---|---|---|---|
| `FP-P01` | generator parameters/support 与 primary/alternate role | WP1 oracle/design audit | `FRZ-1` |
| `FP-P02` | \(\Pi_u\)、query law、normalization | task + development reference | `FRZ-1` |
| `FP-P03` | oracle budgets/repeats/ESS rules | budget ladder + MC/effect ratio | Gate A 前 |
| `FP-P04` | eligible cells/pairs/triplets/holdouts | oracle-only manifest | Gate A/`FRZ-1` |
| `FP-P05` | model architecture/head/components | development + one upgrade rule | `FRZ-2` |
| `FP-P06` | HPO budgets/ranges/early stopping | equal-budget design | first F1 前 |
| `FP-P07` | \(\lambda_{\mathrm{geom}}\) grid/promotion margins | validation design | first F1 前 |
| `FP-P08` | strongest baselines per Claim | frozen validation rules | `FRZ-2` |
| `FP-P09` | asset/query/seed sample sizes + joint-power target/covariance simulation | full-intersection power + CI precision | `FRZ-3` |
| `FP-P10` | test/lockbox combination、execution/cancel 与 heterogeneity rule | resource/precision only | `FRZ-3` |
| `FP-P11` | Claim margins/CI/bootstrap；CM-T01–T11、T14、T16–T19 一次性锁定 | CMR numerical registry | `FRZ-3` 且首次 F2 evaluation 前 |
| `FP-P12` | failure/retry policy | symmetric dry-run evidence | `FRZ-3` |
| `FP-P13` | bearing dataset | license/channel/trajectory/failure audit | public split lock |
| `FP-P14` | max two TSFM IDs | reproducibility/license/interface audit | F8 前 |

每项完成后记录 `value`, `status`, `evidence_path`, `data_seen`, `decision_time`, `owner`,
`code_revision`, `manifest_revision`。所有 `FP-P01`–`FP-P12` 完成前不得打开 formal
test/lockbox。

---

## 17. Protocol readiness checklist

### 17.1 进入 WP1/F0

- [ ] 四份 contracts 已审阅，符号/Claims 无冲突；
- [ ] machine schemas 已建立；
- [ ] R1–R47 明确标为 pilot，不复用其 test rows 作 confirmation；
- [ ] generator/oracle code 使用新 namespace；
- [ ] world-level decisions 不依赖 learned formal outcome。

### 17.2 进入 WP2/F1

- [ ] Gate A 通过；
- [ ] oracle/cell eligibility manifest 已冻结；
- [ ] train/eligibility/selection/metric:test/metric:lockbox reference streams 与 sample IDs 分离；
- [ ] \(P_{\mathrm{obs}}/P_{\mathrm{gen}}\) allowlist audit 通过；
- [ ] F1 candidate/baseline HPO budgets 已冻结。

### 17.3 进入 WP3/F2–F6

- [ ] Gate B 通过；
- [ ] promoted candidate 唯一且同用于 C1–C3；
- [ ] strongest baselines per Claim 唯一；
- [ ] power/precision、margins、weights、seeds、failure policy 全部锁定；
- [ ] CM-T01–T11、T14、T16–T19 已一次性写入 versioned `FRZ-3` registry；
- [ ] test/lockbox combination rule 锁定；
- [ ] code/env/analysis dry-run 通过；
- [ ] `FRZ-3` bundle acceptance 已登记且 lockbox 未访问。

### 17.4 进入论文强结论

- [ ] Gate C/D 按 co-primary + guardrails 通过；
- [ ] 若保留 compositional 题目，Gate E 通过；
- [ ] public claim 不超过 Gate F 证据；
- [ ] negative/dependence diagnostics 未揭示未解释的系统性冲突；
- [ ] claim–evidence table 能逐句指向 figure/table/artifact；
- [ ] 独立脚本从 per-asset tables 复算全部 primary estimates。

该 checklist 通过后，工作才从“方向与合同”进入真正的正式研究程序。
