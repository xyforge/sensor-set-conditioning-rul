# Claim–Metric Registry

合同编号：`CMR-4.1a`  
版本：`0.1.3-wp0`（2026-08-22）

状态：**C2 mathematical contract 已完成 pre-outcome 修订；effect margins/precision fields 待锁定**

上游合同：[Formal problem](./formal_problem_spec.md) · [Oracle/cell eligibility](./oracle_and_cell_eligibility_spec.md)  
执行合同：[Formal experiment protocol](./formal_experiment_protocol.md)

> 本文件是“什么结果允许支持什么句子”的唯一登记表。一个 metric 未在此登记为 primary 或 required guardrail，就不能在看到结果后升格以挽救 Claim；一个 robustness result 无论多有利，也不能替换失败的 primary estimand。

---

## 1. Claim hierarchy 与决策原则

### 1.1 冻结层级

| Claim ID | 科学主张 | 论文角色 | 失败后果 |
|---|---|---|---|
| `C1` | task-sufficient、posterior-compatible views 下，learned posterior 复现 compatibility，同时保持 per-view/full-information fidelity | 科学核心 | 当前完整论文主线不成立 |
| `C2` | matched information-losing views 下，learned joint posterior 同时改善 critical-view fidelity、loss-pair relation fidelity，并表现出相对于 noncritical control 的 critical-specific advantage | 科学核心、关键 gate | 当前 identifiability 方法论文不成立 |
| `C3` | C1/C2 behavior 外推到未见 \(S\times R\times Q\) compositions | 外推主张 | 删除题目/摘要中的 compositional claim，收缩论文 |
| `E1` | public PHM 上 failure-time marginal 具有 bounded external plausibility | 外部适用性 | 降低应用范围，不反向否定 controlled-world C1/C2 |
| `T1` | TSFM backbone 提供额外价值 | comparator question | 可从正文删除，不影响论文主线 |

确认性顺序为 `Gate A → Gate B → C1 → C2 → C3 → E1`。下一级不得救回上一级；
`T1` 不属于确认性 family。

### 1.2 交集式通过

每个 Claim 由：

1. 一个或多个直接承载主张的 **primary estimands**；
2. 防止伪成功的 **required guardrails**；
3. 只解释机制或边界的 **secondary/robustness diagnostics**；

组成。Claim 通过需要所有 primary 与 required guardrails 同时通过。secondary endpoint
不能 rescue；它只按本 registry 的 claim-linked rule 生成 scope limitation 或 interpretation
hold，不自动升级为 universal kill switch。

---

## 2. 评价样本、atomic losses 与聚合顺序

### 2.1 Row keys

受控世界每个评价 row 至少由以下键唯一确定：

```text
generator_family_id
asset_id
query_time_id
query_stratum_id
observation_realization_id
cell_id
view_pair_id / triplet_id (when applicable)
model_family_id
optimization_seed
checkpoint_id
reference_role
split_role
reference_stream_id
reference_sample_set_id
```

同一 base asset 的 rows 不独立。任何 CI、bootstrap 或 hierarchical model 必须以
`asset_id` 为最小独立重采样单位，并保留 generator/cell strata。

### 2.2 Atomic oracle-relative excess risk

对 realized view \(i\)、model \(m\)、optimization seed \(s\)：

\[
R_{m,s,i}
=\mathbb E_{Y\sim\pi_i^\star}S_{\mathrm{ES}}(q_{m,s,i},Y)
-\mathbb E_{Y\sim\pi_i^\star}S_{\mathrm{ES}}(\pi_i^\star,Y).
\]

理论上 \(R_{m,s,i}\ge0\)。有限 Monte Carlo estimator 可轻微为负；必须保留 raw value，
不得逐 row clipping。系统性负值触发 metric/oracle implementation audit。

在标准 energy distance 定义下：

\[
R_{m,s,i}=\tfrac12 d_{\mathrm E}(q_{m,s,i},\pi_i^\star),
\]

因此 score 与 reference-distance 应在独立 sample audit 中数值一致。

### 2.3 Atomic pairwise geometry error

\[
G_{m,s,i}(a,b)
=\left|
d_{\mathrm E}(q^a_{m,s,i},q^b_{m,s,i})
-D_i^\star(a,b)
\right|.
\]

它比较同一 realized pair 的 learned/reference relation。禁止先跨 assets 平均 learned
posteriors 再计算 distance；那会改变 estimand。

### 2.4 固定聚合顺序

对 metric \(M\in\{R,G,\mathrm{CRPS},\ldots\}\)，默认聚合为：

1. **query/observation level**：在每个预声明 query-time stratum 内平均 repeated rows；
2. **asset level**：各 query-time strata 等权，得到 \(M_{m,s,a,c}\)；
3. **optimization-seed level**：平均 losses，
   \[
   \bar M_{m,a,c}=\frac1{S_m}\sum_{s=1}^{S_m}M_{m,s,a,c};
   \]
4. **cell level**：跨 assets 取 mean/effect，CI 由 asset-clustered paired resampling；
5. **claim level**：eligible pair/cell classes 使用预声明 macro weights 聚合。

不得在第 3 步先构造
\(\bar q=S^{-1}\sum_s q_s\)，除非部署对象已预先声明为 ensemble 且所有 baselines 同样
ensemble；ensemble 是另一个 estimand，必须单列。

### 2.5 默认 weighting contract

除非 machine manifest 在 lockbox 前登记不同 task-relevance weights，primary 使用：

- assets 等权；
- query-time strata 等权；stratum 内 rows 等权；
- eligible cells/pair classes macro 等权；
- models 共享完全相同的 row set 和 weights；
- missing prediction 不重新归一为对该 model 有利的 support，视为 failure 并按预声明
  worst valid loss/失败规则处理。

该默认避免 row-rich assets、dense sampling cells 或 cell 数较多的 factor level 支配结果。
task-frequency-weighted micro average 只作 deployment robustness，不能替代 macro primary。

---

## 3. Metric registry

### 3.1 Controlled-world primary metrics

| Metric ID | 定义/对象 | 越好方向 | 统计单位 | 角色 |
|---|---|---:|---|---|
| `M-JES` | normalized \(Y=(h,T_{\mathrm{fail}})\) joint energy score | lower | asset | atomic proper score |
| `M-RX` | joint oracle-relative excess risk \(R_{\mathrm{excess}}\) | lower，0 ideal | asset | C1/C2/C3 primary building block |
| `M-GEO` | realized-pair geometry error \(G_i\)，聚合为 \(\bar G\) | lower，0 ideal | paired asset | C1/C2 primary |
| `M-FCRPS` | continuous failure-time CRPS | lower | asset | C2 required guardrail / E1 primary |
| `M-FNLL` | continuous failure-time NLL | lower | asset | C2 density guardrail |
| `M-SES` | state marginal energy score | lower | asset | C1 per-view guardrail |

joint energy score 是中心 proper score。state/failure marginals 不得取代 joint endpoint，
但必须报告以定位错误来自哪一部分。

### 3.2 Secondary dependence diagnostics

| Metric ID | 定义 | 角色/限制 |
|---|---|---|
| `M-VS` | variogram score \(\mathrm{VS}_p\) | dependence-sensitive secondary guardrail；不是第四 primary |
| `M-CFC` | learned/reference \(p(T_{\mathrm{fail}}\mid h\text{ stratum})\) curve discrepancy | 可解释 dependence guardrail |
| `M-CORR` | state–failure linear/rank correlation discrepancy | descriptive only；不得单独证明 joint coupling |

Variogram 参数必须在 lockbox 前冻结：

\[
\mathrm{VS}_p(q,y)=
\sum_{r<s}w_{rs}
\left(|y_r-y_s|^p-\mathbb E_q|Y_r-Y_s|^p\right)^2.
\]

\(p,w_{rs}\)、coordinate normalization 和 conditional-curve health strata 只可由
development/reference distribution决定。若 `M-VS` 与 `M-JES/M-RX` 系统性反向，C2 进入
`INTERPRETATION-HOLD`；它不能凭单个 noisy cell 推翻 primary，也不能单独 rescue。

### 3.3 Calibration 与 point diagnostics

| Metric ID | 内容 | 角色 |
|---|---|---|
| `M-CAL` | PIT/rank calibration、coverage across nominal levels | required uncertainty interpretation |
| `M-SHARP` | interval width/entropy conditional on coverage | secondary；更宽不自动更好 |
| `M-MAE` | failure-time/RUL MAE | point-performance guardrail/comparability |
| `M-RMSE` | failure-time/RUL RMSE | secondary |
| `M-NASA` | NASA score when dataset convention requires | public comparability only |

“uncertainty 改善”只有在 proper score 不劣、calibration 不劣、sharpness 方向与 reference
一致、full view 不过度保守且 leakage/heuristic controls 不推翻时才可表述。

### 3.4 Public PHM metrics

| Metric ID | Setting | 角色 |
|---|---|---|
| `M-PUB-CRPS` | uncensored/known run-to-failure | E1 primary |
| `M-PUB-IBS` | censoring setting | E1 primary alternative |
| `M-PUB-SNLL` | survival NLL | E1 density endpoint |
| `M-PUB-CAL` | PIT/reliability/coverage–sharpness | E1 required guardrail |
| `M-PUB-MAE` | point RUL | non-inferiority guardrail |

dataset audit 必须在 test 前为每个 public family 选择 `CRPS` 或 `IBS/SNLL` primary，不能
同时计算后挑最有利者。

---

## 4. Claim 1 registry：sufficient-view compatibility

### 4.1 Eligible population

只包含 oracle manifest 中状态为 `ELIGIBLE-COMPATIBLE-PAIR` 的 pair classes。pair 两侧必须：

- 有 tractable parent；
- 各自 `ELIGIBLE-SUFFICIENT`；
- asset/query/observation realization 匹配；
- 未用于 checkpoint selection；
- 按 test/lockbox split 独立评价。

### 4.2 Primary estimand

令 \(b^\star\) 为 lockbox 前冻结的 strongest eligible baseline。定义：

\[
\Delta G_{\mathrm{suf}}
=\mathbb E_{(a,b)\in\mathcal P_{\mathrm{suf}}}
\left[
\bar G_{\mathrm{proposed}}(a,b)
-\bar G_{b^\star}(a,b)
\right].
\]

方向：负值有利。`C1-P1` 通过当 superiority decision bound 排除
\(-\delta_{G,1}\) 以内的无实质差异区域，具体写为：

\[
U\{CI(\Delta G_{\mathrm{suf}})\}< -\delta_{G,1}.
\]

\(\delta_{G,1}\ge0\) 必须由 oracle MC floor、pilot/design variance 与最小可解释 geometry
improvement 冻结；不得用 observed percentage improvement 反推。

本文件各 Claim section 中的 \(b^\star\) 均指该 Claim 按 formal protocol 单独冻结的
\(b_C^\star\)，不是看到 test 后从所有 baselines 中取逐 cell 最优者。

### 4.3 Required guardrails

| ID | Estimand | 通过方向 |
|---|---|---|
| `C1-G0` | proposed 的 absolute \(\bar G_{\mathrm{suf}}\) | upper decision bound 不高于 \(\tau_{G,1}^{\mathrm{abs}}\)；相对胜出但仍远离 reference 不算成功 |
| `C1-G1` | pair 两侧 macro joint \(R_{\mathrm{excess}}\) | 不高于 \(\tau_{R,1}^{\mathrm{abs}}\)，且相对 strongest baseline 至少 non-inferior；不得靠两个坏 posterior 同时 collapse 降低 \(G\) |
| `C1-G2` | full-information joint \(R_{\mathrm{excess}}\) | non-inferior within \(\delta_{R,\mathrm{full}}\) |
| `C1-G3` | state/failure marginal proper scores | 均无预声明 catastrophic degradation |
| `C1-G4` | learned posterior dispersion/support check | 不发生 collapse、support truncation 或 invalid \(\Delta T\) |

显式 \(P_{\mathrm{obs}}\) ablation 与 forced-invariance ablation 不是 Gate C 必过方向。前者可与
event history 冗余；后者主要预期在 information-losing views 失效。它们只解释机制，不能
救回 `C1-P1`。

### 4.4 允许的结论

只有 `C1-P1` 与 `C1-G0`–`C1-G4` 全部通过，才能写“learned posteriors reproduce
compatibility across task-sufficient views without sacrificing full-information fidelity”。
仅报告 low cross-view distance 而无 per-view fidelity 时禁止使用该句。

---

## 5. Claim 2 registry：information-loss response

### 5.1 Eligible population

只包含 oracle manifest 中：

- `ELIGIBLE-INFORMATION-LOSS` critical cells；
- 对应 `ORDERED-NONCRITICAL-CONTROL` random/redundant cells；
- 通过 exact/eligible weighted matching 的 triplets；
- 合法 garbling relation；
- reference numerical error 达标。

`NONORDERED-SWAP` 与 `NONORDERED-INFORMATIVE-MISSINGNESS` 不进入 Claim 2 primary。

唯一 strongest baseline \(b_{C2}^\star\) 在 `F1-P5/FRZ-2` 冻结。选择严格遵循 FEP
Section 8.3：先通过 failure/full-view guards，再按 validation critical `M-RX`、loss
`M-GEO` 的预声明 lexicographic order 排序；仍并列时依次使用 validation joint
\(R_{\mathrm{excess}}\)、实测 compute 与 canonical model ID。designation 只能发生在所有
eligible baseline 的 Pgen-blind checkpoint 已冻结之后，并保存完整排序表。

### 5.2 Primary estimand 1：critical-view per-view fidelity

\[
\Delta R_{\mathrm{crit}}
=\mathbb E_{c\in\mathcal C_{\mathrm{crit}}}
\left[
R_{\mathrm{excess,proposed}}(c)
-R_{\mathrm{excess},b^\star}(c)
\right].
\]

方向：负值有利。`C2-P1` 通过条件：

\[
U\{CI(\Delta R_{\mathrm{crit}})\}< -\delta_{R,2}.
\]

它确保 proposed 在真正 information-losing views 上整体 posterior 更接近 reference，而不
只调整 width。

`C2-P1` 明确按 Section 2.4 聚合：query/observation rows 先在 query stratum 内平均，随后
query strata 在 asset 内等权，再平均 optimization-seed losses，最后对 eligible critical
cells 作 cell-macro 等权。CI 使用 asset-clustered paired resampling；不得让 rows 更多的
asset、dense cell 或某个 critical factor level获得额外权重。

### 5.3 Primary estimand 2：loss-pair relation fidelity

令 \(\mathcal P_{\mathrm{loss}}\) 包含 critical–parent、critical–random 与
critical–redundant 的预声明 matched pairs：

\[
\Delta G_{\mathrm{loss}}
=\mathbb E_{(a,b)\in\mathcal P_{\mathrm{loss}}}
\left[
\bar G_{\mathrm{proposed}}(a,b)
-\bar G_{b^\star}(a,b)
\right].
\]

方向：负值有利。`C2-P2` 通过条件：

\[
U\{CI(\Delta G_{\mathrm{loss}})\}< -\delta_{G,2}.
\]

`C2-P1` 与 `C2-P2` 分别承载 per-view fidelity 与 relation fidelity；两者最终与 Section
5.4 的 critical-specific interaction `C2-P3` 共同构成 C2 co-primary intersection。

\(\mathcal P_{\mathrm{loss}}\) 的聚合遵循 Section 2.5 的 macro weighting contract：
critical–parent、critical–matched-random、critical–redundant 三个 pair classes 等权，class
内按 query → asset → optimization-seed 的顺序聚合并对 assets 等权。不得按 realized pair
数量或 \(D^\star\) 大小加权。任一预声明 pair class 因 reference/evaluator 原因不可估计时，
`C2-P2` 进入 `C2-NON-ESTIMABLE / EXECUTION-HOLD`；不得自动删除该 class 后重归一化其余
两类。

### 5.4 Primary estimand 3：critical-specific interaction

定义 model error 的 critical-control interaction：

\[
I_R=
\left[R_{\mathrm{prop}}(c_{\mathrm{crit}})
-R_{\mathrm{prop}}(c_{\mathrm{ctrl}})\right]
-
\left[R_{b^\star}(c_{\mathrm{crit}})
-R_{b^\star}(c_{\mathrm{ctrl}})\right].
\]

若 proposed 的优势对 critical information loss 更强，则 \(I_R<0\)。`C2-P3` 通过条件为：

\[
U\{CI(I_R)\}< -\delta_{I,2}.
\]

该 estimand 只在 oracle 已证实
\(\Delta\mathcal A^\star_{\mathrm{crit}}>0\) 的 matched triplets 上计算。primary
\(c_{\mathrm{ctrl}}\) 固定为 matched-random；matched-redundant 的 \(I_R\) 单独作为
robustness diagnostic。若 world-design eligibility manifest 在 `FRZ-3` 前判定整个
matched-random channel 未达到预声明 matching adequacy，primary control 可整体切换为
matched-redundant并记录；禁止在 formal analysis 中逐 triplet 混用两种 control。两类
interaction 均可报告，但不得用 robustness control rescue `C2-P3`。

`C2-P3` 使用与 P1 相同的 query → asset → optimization-seed 聚合，再对 eligible triplets
macro 等权；primary-control routing 与最终 triplet weights 必须在首次 F2 formal evaluation
前冻结。

因此 C2 的科学核心明确是：

\[
C2_{\mathrm{primary}}=C2\text{-}P1\cap C2\text{-}P2\cap C2\text{-}P3.
\]

### 5.5 Fatal scientific guardrails

| ID | Estimand/check | 通过方向 |
|---|---|---|
| `C2-G0` | proposed 的 absolute critical \(R_{\mathrm{excess}}\) 与 loss-pair \(\bar G\) | upper decision bounds 分别不高于 \(\tau_{R,2}^{\mathrm{abs}},\tau_{G,2}^{\mathrm{abs}}\) |
| `C2-G2` | continuous \(T_{\mathrm{fail}}\) CRPS | proposed 至少 non-inferior；\(\delta_{\mathrm{CRPS,NI}}\) 对应 `CM-T08` 登记的 failure-time CRPS non-inferiority margin |
| `C2-G3-MODEL` | model-generated continuous \(T_{\mathrm{fail}}\) density/support | 无由模型自身导致的 invalid support、collapse 或 catastrophic density failure |
| `C2-G4` | full-information \(R_{\mathrm{excess}}\) | proposed 至少 non-inferior；与 `C2-G2` 共同保证 full-information 与 failure-time proper-score fidelity |

`C2-G4` 不单独证明“模型没有全局变宽”。核心论文句子不得把 full-view
\(R_{\mathrm{excess}}\) non-inferiority 改写为对 global dispersion mechanism 的直接排除。

### 5.6 Admissibility、estimability 与 scope diagnostics

`C2-G6a` 是合同有效性的前提：model input、training target、selection 与 evaluator 均必须
满足 permission/schema contract，且不存在 \(P_{\mathrm{gen}}\)、future 或 formal-outcome
leakage。它不作为模型科学性能 endpoint。

`C2-X1-NUMERICAL` 是可估计性条件：reference samples、oracle MC、metric evaluator 与
bootstrap 必须通过预声明 numerical-health checks。该条件与 `C2-G3-MODEL` 分开，避免把
evaluator/reference 故障写成 density-model failure。

以下仅为 claim-linked scope annotations：

| ID | Diagnostic | 作用 |
|---|---|---|
| `C2-G5` | predeclared oracle-active location/scale/modality/tail descriptors | 系统性方向冲突或严重 under-response 生成 `SHAPE-LIMITED` |
| `C2-G6b` | mask-rate-only、metadata-only 与其他 explanatory controls | 仅对不具完整 strongest-baseline eligibility 的 controls 生成 `ATTRIBUTION-LIMITED` |
| `C2-G7` | `M-VS`/`M-CFC` | 跨多数 critical cells 的系统性 joint-dependence 冲突生成 `DEPENDENCE-LIMITED` |

`C2-G5/G7` 的 descriptor、activity threshold、aggregation 与 conflict threshold 必须在
`CM-T19` 冻结。对 modality，oracle-active mode-count change 未在 learned posterior 中出现
属于 under-response，不等同于 direction reversal；只有二者变化方向相反才记 reversal。
under-response 仅在超过 `CM-T19` 冻结的 response-magnitude threshold 时生成
`SHAPE-LIMITED`。

完整 eligible controls（包括 `B-WIDEN`）通过 Section 8.3 strongest-baseline channel 进入
P1/P2/P3，而不再由 `C2-G6b` 进行第二次 fatal 裁决。若 `B-WIDEN` 成为
\(b_{C2}^\star\) 并使任一 primary 失败，结果直接是 `C2-CORE-FAIL`。不具完整 C2 eligibility
的 heuristic controls 只限制 attribution 表述。

### 5.7 C2 decision states 与 Gate D

\[
C2_{\mathrm{core}}=
P1\cap P2\cap P3\cap G0\cap G2\cap G3\text{-MODEL}\cap G4.
\]

状态按以下顺序裁决：

1. `C2-G6a` permission/leakage violation → `C2-INVALID / CONTRACT-VIOLATION`；受影响 run
   不产生科学结论；
2. `C2-X1-NUMERICAL` 失败 → `C2-NON-ESTIMABLE / EXECUTION-HOLD`；修复 evaluator/reference
   后按冻结分析重算，不记为模型失败；
3. 任一 P1/P2/P3 或 fatal scientific guard 失败 → `C2-CORE-FAIL`；
4. core 通过且 G5/G6b/G7 均无 limitation → `C2-FULL-PASS`；
5. core 通过但存在 scope conflict → `C2-CORE-PASS / SHAPE-LIMITED`、
   `DEPENDENCE-LIMITED`、`ATTRIBUTION-LIMITED` 或其组合。

Gate D 只由 `C2-core` 决定；scope diagnostics 生成 annotations，不构成独立 gate。发生
`C2-CORE-FAIL` 时，G5/G6b/G7 仍完整计算并报告，但标记为 exploratory，不能改变最终状态。

`C2-CORE-PASS`（包括带 limitation）允许 C3 按 fixed sequence 继续 confirmatory；
`C2-CORE-FAIL` 使 C3 降为 exploratory。C3 结果不能 rescue C2，也不能移除已生成的 scope
limitations。

### 5.8 允许的科学表述与禁止的 rescue

`C2-FULL-PASS` 支持的核心句子是：proposed 在 information-losing views 上同时改善
critical-view fidelity、loss-pair relation fidelity 与 critical-specific interaction，并保持
full-information 与 failure-time proper-score fidelity，且不存在 permission leakage 或模型
自身的灾难性 density/support failure。带 limitation 的 core pass 必须在相应 shape、
dependence 或 attribution 句子中收缩表述。

以下均不能通过 C2：

- coverage 更高但 `C2-P1/P2/P3` 失败；
- interval 更宽但 failure-time CRPS/NLL 变差；
- learned critical/random ordering 看似正确，但用了 hidden intervention label；
- permutation control 更差，但 absolute learnability ceiling 未通过；
- omniscient reference 下成功、same-information reference 下失败。

---

## 6. Claim 3 registry：compositional extrapolation

### 6.1 Raw composition loss

对 model \(m\)，定义每个 support set 的 cell-macro oracle-relative risk：

\[
\mu_m(\mathcal C)
=\frac1{|\mathcal C|}
\sum_{c\in\mathcal C}
\mathbb E_A\bar R_{m,A,c},
\]

其中 \(\bar R_{m,A,c}\) 已按 Section 2 的 query-stratum 与 seed-loss 顺序聚合。然后：

\[
C_m
=\mu_m(\mathcal C_{\mathrm{heldout}})
-\mu_m(\mathcal C_{\mathrm{seen}}).
\]

Claim 3 primary model-relative estimand：

\[
\Delta C_{\mathrm{raw}}
=C_{\mathrm{proposed}}-C_{b^\star}.
\]

方向：负值有利，即 proposed 从 seen 到 held-out 的额外退化小于 strongest baseline。
`C3-P1` 通过条件：

\[
U\{CI(\Delta C_{\mathrm{raw}})\}< -\delta_C.
\]

seen/held-out cell weights、query strata 与 asset set 必须跨 models 完全相同。raw primary
禁止按 oracle posterior shape 重加权。`C3-P1` 的 primary training allocation 冻结为
`balanced-support`；`baseline-support` 使用同一 estimand 独立报告，不与 primary pooled，
也不能 rescue balanced-support failure。

### 6.2 Required generalization guardrails

| ID | Check | 判定 |
|---|---|---|
| `C3-G1` | held-out cell macro-average absolute \(R_{\mathrm{excess}}\) | 低于 learnability/utility ceiling |
| `C3-G2` | sufficient-heldout 与 loss-heldout 分层 effects | 两类均不出现预声明 unacceptable reversal |
| `C3-G3` | worst-cell/low-tail performance | 不能由单一容易 cell 掩盖系统性失败 |
| `C3-G4` | leave-one-cell-out influence | primary 方向不能完全由一个 cell 决定 |
| `C3-G5` | baseline-support sensitivity vs balanced-support primary | baseline-support 不要求单独 superiority，但不得被误写为 primary；若方向反转，必须收缩对自然 training allocation 的外推 |
| `C3-G6` | asset/split/operator/scaler collision audit | 无 held-out leakage |

worst-cell 是 guardrail，不要求 proposed 在每个 cell 都显著 superiority。具体 unacceptable
reversal 与 influence threshold 必须在 lockbox 前冻结，不能看 cell plot 后定义。

### 6.3 Oracle-matched robustness

允许用 oracle-only descriptors 对 seen cells 重加权：

\[
C_{m,\mathrm{matched}}
=\mu_m(\mathcal C_{\mathrm{heldout}})
-\mathbb E_{w_{\mathrm{oracle}}}
[R_{\mathrm{excess},m}\mid\mathrm{seen}],
\]

\[
\Delta C_{\mathrm{matched}}
=C_{\mathrm{proposed,matched}}
-C_{b^\star,\mathrm{matched}}.
\]

允许的 matching descriptors 仅限预冻结的
\(\bar B^\star,\mathcal A^\star_{\mathrm{obs}}\) 与 posterior-shape strata。必须报告：

- common-support fraction；
- effective sample size；
- maximum normalized weight；
- truncation fraction 与 rule；
- pre/post balance。

若任一 overlap/ESS threshold 失败，结果标为 `NON-ESTIMABLE`；禁止继续尝试新 propensity
model、bandwidth 或 truncation 直到显著。无论 \(\Delta C_{\mathrm{matched}}\) 多有利，都不能
救回失败的 `C3-P1`。raw/matched 冲突时保留 raw 主结论，并解释为 difficulty/shape
composition boundary。

### 6.4 分开报告的非主 estimands

- one-factor OOD；
- unseen intensity；
- unseen factor level；
- micro/deployment-frequency weighted penalty；
- alternate-generator composition penalty。

这些不能与 \(\Delta C_{\mathrm{raw}}\) pooled 成一个 effect。

---

## 7. Development qualification 与 candidate promotion

F1 不产生 paper claim，只决定是否有资格打开 confirmatory sequence。

本节所有 oracle-relative validation quantities 必须消费
`reference_role=same_info_selection, split_role=validation`。它只比较已由 pooled validation
proper-score rule 冻结的 branch checkpoints，用于 Gate B、candidate promotion 与
strongest-baseline designation；不得参与 model gradients、per-branch epoch/checkpoint
selection 或 cell eligibility。后续 C1–C3 formal scoring 只能消费各自 test/lockbox 的
`same_info_metric` streams。

### 7.1 Gate B absolute learnability

至少一个预声明 candidate 必须：

\[
\mu(R_{\mathrm{excess}}\mid\mathrm{seen\ validation})
\le\tau_{\mathrm{learn}},
\]

并相对 same-permission standard probabilistic baseline 至少 non-inferior。还必须满足：

- state/failure marginals 无 collapse；
- point accuracy 无 catastrophic cost；
- candidate promotion 唯一且冻结；
- coherent full-target permutation 明显更差仅作 pipeline sanity，不是 learnability 证明。

posterior predictive marginal/tail/conditional-shape checks 是 parameterization trigger 与后续
C2 scope evidence，不属于 Gate B core intersection。它们失败可触发唯一一次预声明 matched-head
upgrade trial；若 Gate B core 仍通过，绝对 shape threshold 未全部达到只记录
`SHAPE-LIMITATION`，不能单独停止当前方法或阻断 F2。

### 7.2 Direct vs relation promotion

direct candidate 是默认。relation candidate 只有同时满足以下条件才 promotion：

1. 在冻结 validation eligible pair macro-set 上，
   \[
   U\{CI(\bar G_{\mathrm{relation}}-\bar G_{\mathrm{direct}})\}
   <-\delta_{\mathrm{promote}};
   \]
2. per-view validation joint \(R_{\mathrm{excess}}\) 相对 direct 通过 non-inferiority margin
   \(\delta_{\mathrm{promote,NI}}\)；
3. full-information、state 与 failure marginals 无 guardrail failure；
4. improvement 在 sufficient/loss validation strata 中不呈相反的 catastrophic behavior。

否则冻结 direct candidate 与 \(\lambda_{\mathrm{geom}}=0\)。不允许用 F2–F6 results 重开
promotion，也不允许搜索第三个 relation loss。

---

## 8. External plausibility 与 TSFM registry

### 8.1 E1

每个 public family 先按 dataset audit 选择一个 primary proper score。E1 通过需要：

- 两个设备 families 均完成 asset-level evaluation；
- proposed 对 strongest eligible public baseline 的 primary proper score 至少 non-inferior，
  且至少在预声明 controlled sensing shift 或 calibration contrast 上有净收益；
- point MAE 在 \(\delta_{\mathrm{pub,MAE}}\) 内 non-inferior；
- calibration–sharpness 不显示 generic overdispersion；
- 结论不依赖 dataset-specific 大规模额外 tuning。

E1 只能支持 failure-time marginal 的 bounded plausibility。

### 8.2 T1

TSFM 比较报告：

- specialized vs frozen-adapter vs PEFT；
- same posterior head/input permission；
- low-data 与 held-out composition effects；
- parameter count、pretraining data advantage、train/inference compute。

无优势是允许结果。TSFM 结果不得改变 strongest scientific baseline 的选择规则，也不得
作为 C1/C2 失败后的替代 novelty。

---

## 9. Statistical decision contract

### 9.1 Paired inference

对所有 lower-is-better metrics，统一定义 model contrast：

\[
\Delta M=M_{\mathrm{proposed}}-M_{b_C^\star}.
\]

superiority 使用 \(U\{CI(\Delta M)\}<-\delta_{\mathrm{sup}}\)；non-inferiority 使用
\(U\{CI(\Delta M)\}<\delta_{\mathrm{NI}}\)；absolute adequacy 使用
\(U\{CI(M_{\mathrm{proposed}})\}\le\tau_{\mathrm{abs}}\)。所有
\(\delta_{\mathrm{sup}},\delta_{\mathrm{NI}},\tau_{\mathrm{abs}}\) 均为非负且在 formal
outcomes 不可见时冻结。若某 metric 是 higher-is-better，必须在 machine registry 中先乘
\(-1\) 转成统一 loss direction，禁止每张表临时改变符号。

所有 proposed-vs-baseline effects 使用相同 assets、cells、queries 和 oracle samples 的
paired contrasts。primary CI 使用：

- 按 `asset_id` cluster resampling；
- generator/cell class 分层；
- 同一 bootstrap replicate 对所有 models/views 使用相同 asset indices；
- optimization seeds 在 loss level 聚合，另报告 seed variance；
- oracle MC uncertainty由独立 repeat 或 nested component 传播。

若使用 hierarchical model 替代 bootstrap，必须在 lockbox 前冻结 formula、priors、contrast
和 convergence criteria，并证明与 asset-level paired estimand一致。

### 9.2 Multiplicity

- C1 → C2 → C3 使用 fixed-sequence hierarchy；C1 core 失败后 C2/C3 只作 exploratory，
  `C2-CORE-FAIL` 后 C3 只作 exploratory；`C2-CORE-PASS` 即使带 scope limitation，C3 仍可
  confirmatory，但 limitation 必须向后传播。
- 每个 Claim 的 co-primary/fatal scientific guardrails 使用 intersection rule，不因全部需要
  通过而放宽阈值。C2 的 P1/P2/P3 是 intersection-union decision components，不再对三者
  机械追加 Bonferroni；其 joint power 由 FEP Section 6 的 covariance-aware simulation设计。
- individual cells、marginals、calibration levels 和 TSFM variants 为 secondary family，完整
  报告 effect/CI，并按 registry 冻结的 FDR 或 descriptive policy处理。
- 不以“至少一个 metric 显著”定义任何 Claim。

### 9.3 Missing/failed runs

训练失败、NaN、invalid posterior support 或 inference timeout 不能静默丢弃。处理规则必须在
formal protocol 冻结为：预声明有限重试、失败计数、是否使用 worst valid score 或将 model
判为不合格。不得只重跑 proposed 或只保留成功 seeds。

---

## 10. Claim decision table

| Decision ID | Primary | Fatal scientific guards | Admissibility/estimability | Scope diagnostics | Gate |
|---|---|---|---|---|---|
| `C1-DEC` | `C1-P1: ΔG_suf` | `C1-G0`–`G4` | formal reference/permission contract | N/A | C |
| `C2-DEC` | `C2-P1: ΔR_crit` + `C2-P2: ΔG_loss` + `C2-P3: I_R` | `C2-G0/G2/G3-MODEL/G4` | `C2-G6a` + `C2-X1-NUMERICAL` | `C2-G5/G6b/G7` | D（core only） |
| `C3-DEC` | `C3-P1: ΔC_raw` | `C3-G1`–`G6` | formal reference/permission contract | matched robustness | E |
| `E1-DEC` | dataset-specific public proper score | calibration + point NI + two-family completion | dataset/protocol validity | dataset-specific diagnostics | F |
| `T1-DEC` | low-data/held-out proper-score contrast | compute/data advantage | comparator eligibility | N/A | none |

`C1/C2` 是论文科学核心；`C3` 失败触发预声明收缩，不等于 C1/C2 自动失败。
`C2-SCOPE-DEC` 只是 annotation generation step，不是独立 pass/fail gate。

---

## 11. Numerical decision registry

以下数值必须由 scale、oracle error、pilot/design variance、power 与实际 PHM relevance
共同确定。`CM-T01`–`CM-T11`、`CM-T14`、`CM-T16`–`CM-T19` 必须全部转为
`LOCKED-EXECUTION` 并写入 versioned `FRZ-3 CONFIRMATORY` registry，且发生在首次 F2 test/lockbox
evaluation 之前。F2/F3/F4 只规定分析顺序，不提供逐阶段设置门槛的窗口；看到 F2 后才锁 C2
或 C3 门槛属于 outcome-aware design。`CM-T01` 因参与样本量计算，还必须更早在 power
analysis 前冻结。

| ID | 数值 | 用途 | 最迟冻结点 |
|---|---|---|---|
| `CM-T01` | confirmatory CI level / decision alpha | all Claims | power analysis 前；纳入 `FRZ-3` |
| `CM-T02` | \(\delta_{G,1}\) | C1 geometry superiority | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T03` | \(\delta_{R,\mathrm{full}}\) | C1/C2 full-view NI | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T04` | state/failure catastrophic limits | C1 guardrails | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T05` | \(\delta_{R,2}\) | C2 critical risk superiority | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T06` | \(\delta_{G,2}\) | C2 loss geometry superiority | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T07` | \(\delta_{I,2}\) | C2-P3 critical-specific interaction superiority | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T08` | failure-time CRPS non-inferiority margin、model density/support limits | C2-G2/G3-MODEL | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T09` | \(\delta_C\) | raw composition superiority | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T10` | C3 stratum reversal、worst-cell、leave-one-cell 与 support-sensitivity limits | C3 guardrails | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T11` | matched overlap/ESS/max-weight/truncation rules | C3 robustness | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T12` | \(\tau_{\mathrm{learn}}\) | Gate B absolute learnability | first F1 前 |
| `CM-T13` | \(\delta_{\mathrm{promote}},\delta_{\mathrm{promote,NI}}\) | relation promotion | first F1 前 |
| `CM-T14` | variogram \(p,w_{rs}\) 与 conditional strata | dependence guard | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T15` | public proper-score/MAE NI margins + controlled-shift/calibration minimum benefit | E1 | public test lock 前 |
| `CM-T16` | bootstrap replicates/secondary multiplicity policy | inference | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T17` | \(\tau_{G,1}^{\mathrm{abs}},\tau_{R,1}^{\mathrm{abs}}\) | C1 absolute adequacy | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T18` | \(\tau_{R,2}^{\mathrm{abs}},\tau_{G,2}^{\mathrm{abs}}\) | C2 absolute adequacy | `FRZ-3`；首次 F2 formal evaluation 前 |
| `CM-T19` | oracle-active response descriptors、activity、direction-conflict 与 under-response magnitude thresholds | C2 scope annotations | `FRZ-3`；首次 F2 formal evaluation 前 |

每项需附 `value`, `unit`, `direction`, `derivation_artifact`, `data_accessed`, `decision_date`,
`owner`, `registry_revision`, `status`。未填完不影响研究主线冻结，但阻止相应 formal package
执行。

---

## 12. Registry 验收清单

- [ ] 每个 Claim 只有本文件登记的 primary estimand；
- [ ] `C2` 同时要求 per-view fidelity、relation fidelity 与 critical-specific interaction；
- [ ] C2 scientific failure、contract invalidity 与 numerical non-estimability 可分别输出；
- [ ] shape、attribution 与 dependence diagnostics 明确只生成 scope annotations；
- [ ] `ΔC_raw` 是 C3 唯一 primary，matched analysis 无 rescue 权；
- [ ] assets、queries、seeds、cells 的聚合顺序已在代码单元测试中复现；
- [ ] strongest baseline 在 lockbox 前冻结；
- [ ] margins 有独立 derivation artifact，而非从 formal effect 反推；
- [ ] controlled-world confirmatory thresholds 已在首次 F2 evaluation 前一次性写入 versioned `FRZ-3` registry；
- [ ] Claim decision table 可由 per-asset metric table自动生成；
- [ ] 所有未登记 analyses 默认标为 exploratory。
