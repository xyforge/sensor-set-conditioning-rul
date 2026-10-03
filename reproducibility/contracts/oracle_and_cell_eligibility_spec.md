# Oracle and Cell Eligibility Specification

合同编号：`OCES-4.1a`  
版本：`0.1.3-wp0`（2026-08-22）

状态：**定义与判定逻辑已冻结；数值 thresholds/budgets 待设计校准**  
上游合同：[Formal problem specification](./formal_problem_spec.md)  
下游合同：[Claim–metric registry](./claim_metric_registry.md) · [Formal experiment protocol](./formal_experiment_protocol.md)

> 本合同决定哪些 reference posterior 可以被称为可信、哪些 observation cells 有资格进入 Claim 1 或 Claim 2，以及 matched controls 如何构造。它先于任何 learned-model promotion；learned-model 结果禁止参与 cell eligibility。

---

## 1. 职责与非职责

本合同负责：

1. same-information reference inference 与 numerical validation；
2. \(B^\star\)、\(\mathcal A^\star_{\mathrm{obs}}\) 和 \(D^\star\) 的估计；
3. task-sufficient、posterior-compatible、information-losing 与 design-ambiguous 的资格判定；
4. critical/random/redundant matched triplets；
5. compositional cells 的 oracle-only strata 与 manifest；
6. oracle Monte Carlo uncertainty 对 eligibility 的保守传播。

本合同不负责：模型选择、Claim 的模型间 effect estimate、baseline superiority、public-PHM
external plausibility 或论文正文叙事。

---

## 2. Oracle 的信息集与角色分离

### 2.1 中心 same-information oracle

对 realized view

\[
v=(\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u),
\]

中心 oracle 输出：

\[
\pi^\star_t(Y_t\mid v),\qquad Y_t=(h_t,T_{\mathrm{fail}}).
\]

它必须边缘化：

- row-specific 隐藏 \(P_{\mathrm{gen}}\)；
- \(K_{\mathrm{fail}}\)；
- realized future workload \(u_{>t}\)；
- 未被 \(P_{\mathrm{obs}}\) 合法暴露的 true noise/missingness/operator attributes。

### 2.2 Oracle 输出角色

每份 posterior sample artifact 必须包含 `reference_role` 与 `split_role`：

| role | 必需的 `split_role` | 允许用途 | 禁止用途 |
|---|---|---|---|
| `same_info_train` | `development/model_train` | density/optional relation training target | eligibility、validation selection、formal scoring |
| `same_info_eligibility` | `development/world_design` | \(B^\star,\mathcal A^\star_{\mathrm{obs}},D^\star\)、cell qualification | model training、validation selection、formal scoring |
| `same_info_selection` | `validation` | Gate B validation guardrails；已冻结 branch checkpoint 之间的 candidate promotion 与 strongest-baseline designation | model gradients、per-branch epoch/checkpoint selection、cell eligibility、test/lockbox formal scoring |
| `same_info_metric` | `test` 或 `lockbox` | frozen model 的 formal \(R_{\mathrm{excess}},G\) | training、eligibility、candidate/baseline/checkpoint selection |
| `omniscient_sanity_only` | `audit_only` | analytic/simulator/inference debugging | 上述全部 scientific uses |

`reference_role` 不能只靠目录名推断。每个 artifact 还必须记录
`reference_stream_id` 与 `reference_sample_set_id`。以下五个用途使用互不重叠的 sample IDs 与
独立 random-stream namespaces：`train`、`eligibility`、`selection`、`metric:test` 和
`metric:lockbox`；test 与 lockbox 不得共享 realized reference draws。可以共享已冻结的 oracle
程序、proposal family 与全局参数，但不得跨这些用途复用 realized proposal particles、
resampling draws 或 evaluation draws。

### 2.3 Oracle 程序独立性

oracle inference code 必须独立于 learned model 的 encoder、posterior head 和 checkpoint。
允许共享 simulator definition 与 normalized target coordinates；禁止：

- 用 learned representation 作为唯一 proposal 且不做 exact weighting/correction；
- 用 learned result 选择 oracle budget、cells 或 favorable posterior samples；
- 用 test-model failure 反向调 oracle until agreement；
- 以 omniscient reference 替换难算的 same-information reference。

若 amortized proposal 用于加速，最终 sample/weight 必须针对 same-information target 做
importance correction，并通过独立 analytic/SBC audit。

### 2.4 Eligibility、selection 与 formal scoring 的样本隔离

cell/pair/triplet 的资格只能由独立的 world-design assets（来自
`development/world_design` subpartition，且不进入 model gradients 或 validation
selection）和 `same_info_eligibility` stream 冻结。test 与 lockbox 继承 cell-class
eligibility，不得根据各自在正式样本上的 \(\widehat B^\star,\widehat{\mathcal A}^\star\)
或 \(\widehat D^\star\) 重新纳入、删除或重分层。

validation 的 `same_info_selection` samples 只能在每个 branch 的 Pgen-blind checkpoint 已经
冻结后，由独立 evaluator 用于 Gate B、direct/relation promotion、strongest-baseline
designation 和预声明 validation guardrails。它可以消费已冻结的 eligibility manifest，但
不能重新定义 cells，也不能回流到 optimizer、epoch selector 或 model input。

test/lockbox 的 `same_info_metric` samples 仍用于计算 \(R_{\mathrm{excess}}\) 与 \(G_i\)，并可
检查 reference numerical health。若它们显示预冻结 cell class 在新 assets 上发生重大
oracle regime reversal，必须报告为 design/generalization failure；禁止把该 cell
post hoc 改成 `DESIGN-AMBIGUOUS` 后从 primary set 移除。只有纯 numerical reference
failure 可按预声明 missing-reference policy 处理，且不能依模型结果决定。

---

## 3. 设计单位、配对与外层期望

### 3.1 联合设计单位

定义：

\[
\mathcal I=(A,H_{\le t},t_q,\Xi)
\sim\mathbb P^{\Pi_u}_{\mathrm{design}},
\]

其中：

- \((A,H_{\le t})\)：base asset 与查询前 latent trajectory；
- \(t_q\)：预声明 query-time law 的 realization；
- \(\Xi\)：full observation field、event schedule、measurement noise 和 intervention
  randomization 所需的 observation randomness；
- \(\Pi_u\)：固定的 future-context policy，不随 cell 改变。

cell \(c\) 作用于同一个 \(\mathcal I\)，产生 \(V_{\mathcal I,c}\)。所有 cell-level estimands
最终对 base assets 取期望；同一 asset 上的 query times 和 views 是相关重复测量。

### 3.2 Parent-first view generation

每个 matched family 必须先生成一个 parent/full observation field，再从该 parent 产生 views：

```text
base asset + latent path + query time
             |
             v
      parent observation field c+
        /          |           \
 critical ccrit  random crnd  redundant cred
```

retained events 必须复用 parent 中相同的 timestamp、value 与 measurement-noise realization，
不得为每个 deletion view 重新抽噪声。这样 paired contrast 才隔离 observation operator，且
最大化降方差。

### 3.3 信息序关系

Claim 2 的 information-loss eligibility 不只要求“看起来数据更少”，还要求 degraded view
不比 parent 获得额外 task information。正式条件是存在预声明 Markov/garbling kernel
\(K_c\)，使：

\[
Y_t\longrightarrow V_{c^+}\longrightarrow V_c,
\qquad
V_c\sim K_c(\cdot\mid V_{c^+}).
\]

deterministic deletion、event thinning 与独立附加噪声都可满足该 Blackwell-garbling 条件。
若只是非嵌套 sensor swap，或 degradation mask 额外携带 parent view 中不存在的 latent
information，则不满足。

特别地，所谓 `MNAR-like` cell 只有在 realized mask 可由 parent observable field 与独立
randomization 生成、且给定 \(V_{c^+}\) 后不再依赖 \(Y_t\) 时，才能进入 Claim 2 的
information-loss set。若 mask 本身通过隐藏 state/mechanism 传递额外信息，该 cell 仍可由
same-information oracle 正确评分，但只能标为 `NONORDERED-INFORMATIVE-MISSINGNESS`，进入
robustness/boundary analysis，不能用“更多信息不增加 Bayes risk”解释。

此条件必须由 generator DAG/schema 审计确认，不能只根据经验 Bayes-risk ordering 推断。

---

## 4. Oracle 对象与估计量

所有距离和 scores 均在 [formal problem spec](./formal_problem_spec.md) 冻结的无量纲
joint target space中计算。令 energy score：

\[
S_{\mathrm{ES}}(Q,y)
=\mathbb E_{X\sim Q}\lVert X-y\rVert_2
-\frac12\mathbb E_{X,X'\sim Q}\lVert X-X'\rVert_2.
\]

### 4.1 Per-view Bayes ambiguity

\[
B^\star(v)
=\mathbb E_{Y\sim\pi^\star(\cdot\mid v)}
S_{\mathrm{ES}}(\pi^\star(\cdot\mid v),Y)
=\frac12\mathbb E_{Y,Y'\overset{iid}{\sim}\pi^\star(\cdot\mid v)}
\lVert Y-Y'\rVert_2.
\]

因此可用 posterior samples 的 U-statistic 估计；实现禁止包含 self-distances 或把有限样本
plug-in bias 当作 cell difference。每个 realized view 保存：

- point estimate \(\widehat B_i^\star(c)\)；
- independent-repeat Monte Carlo SE；
- posterior ESS/weight diagnostics；
- sample budget 与 sampler revision。

### 4.2 Cell-level ambiguity

\[
\bar B^\star(c)
=\mathbb E_{\mathcal I\sim\mathbb P^{\Pi_u}_{\mathrm{design}}}
B^\star(V_{\mathcal I,c}).
\]

估计顺序必须是：

1. 在每个 realized view 内估计 \(B^\star\)；
2. 在每个 asset 内聚合 query times/observation replicates；
3. 跨 assets 计算 cell mean 与 asset-clustered uncertainty。

不得把所有 posterior draws 或 query rows pooled 后假装为独立样本。

### 4.3 Observation-induced excess ambiguity

对有合法 parent \(c^+\) 的 cell：

\[
\mathcal A^\star_{\mathrm{obs}}(c;c^+)
=\bar B^\star(c)-\bar B^\star(c^+).
\]

其 row/asset estimator 必须保持 \((c,c^+)\) 配对。对合法 garbling，
\(\mathcal A^\star_{\mathrm{obs}}\ge 0\) 是联合设计分布下的理论方向，不是逐 asset、逐
trajectory 或逐 observation realization 的点态要求。个别差值为负不自动表示 oracle 错误。

对 critical cell 与 matched control：

\[
\Delta\mathcal A^\star_{\mathrm{crit}}
=\mathcal A^\star_{\mathrm{obs}}(c_{\mathrm{critical}};c^+)
-\mathcal A^\star_{\mathrm{obs}}(c_{\mathrm{control}};c^+).
\]

若一个 cell 没有合法 information parent，同形式 signed risk contrast可以报告，但字段名
必须为 `task_difficulty_contrast`，禁止写成 observation-induced information loss。

### 4.4 Pairwise posterior geometry

energy distance 定义为：

\[
d_{\mathrm E}(P,Q)
=2\mathbb E\lVert X-Y\rVert_2
-\mathbb E\lVert X-X'\rVert_2
-\mathbb E\lVert Y-Y'\rVert_2.
\]

对 realized pair：

\[
D_i^\star(a,b)
=d_{\mathrm E}\!\left(
\pi^\star(\cdot\mid V_i^a),
\pi^\star(\cdot\mid V_i^b)
\right),
\]

pair-class estimand：

\[
\bar D^\star(a,b)=
\mathbb E_{i\sim\mathbb P^{\Pi_u}_{\mathrm{design}}}D_i^\star(a,b).
\]

主 estimator 使用 unbiased/U-statistic-compatible sample energy distance；若有限样本版本可能
为负，只在 numerical tolerance 内截为 0，并同时保存 raw estimate。sliced Wasserstein 只作
预声明 robustness，不参与 eligibility rescue。

### 4.5 量的分工

| 对象 | 回答 | 不能回答 |
|---|---|---|
| \(B^\star(v)\) | 此 realized view 自身还剩多少 Bayes ambiguity | ambiguity 是否由 sensing 单独造成 |
| \(\mathcal A^\star_{\mathrm{obs}}(c;c^+)\) | 相对合法 parent，observation garbling 增加多少 risk | 两个 posterior 的具体 shape/direction |
| \(D_i^\star,\bar D^\star\) | 两个 views 的 posterior 应相差多少 | 每个 view 是否 informative |

任何报告不得用 posterior distance 代替 ambiguity，也不得用低 pairwise distance 单独定义
task sufficiency。

---

## 5. Oracle numerical validation

### 5.1 必须通过的 audit family

| ID | Audit | 最低输出 |
|---|---|---|
| `OR-A01` | analytic special case | reference moments/quantiles/distance 与解析值误差 |
| `OR-A02` | simulation-based calibration | rank histogram、coverage、global/local deviation |
| `OR-A03` | repeated MC stability | \(B,A,D\) 的 repeat SE 与 CI |
| `OR-A04` | budget ladder | 至少三个预冻结 sample budgets 的 convergence curve |
| `OR-A05` | importance/SMC health | ESS、max normalized weight、degeneracy/failure rate |
| `OR-A06` | same-information trace | 每个 conditioned/marginalized field 的 machine audit |
| `OR-A07` | parent/garbling audit | \(V_c\sim K_c(V_{c+})\) 的 code/DAG/schema proof |
| `OR-A08` | independent implementation spot-check | 至少一组 cells 由第二数值路径复算 |
| `OR-A09` | target-space invariance | normalization/revision contract 跨 cells 与 models 一致 |
| `OR-A10` | seed invariance | oracle conclusion 不依赖单个 MC seed |

### 5.2 Oracle error floor

对任一 eligibility estimand \(\theta\)，定义由独立 oracle repetitions 得到的 numerical
uncertainty bound \(\eta_{\mathrm{MC}}(\theta)\)。最终资格判定使用保守区间：

\[
CI_{\mathrm{tot}}(\theta)
=\left[L_{\mathrm{asset}}-\eta_{\mathrm{MC}},
U_{\mathrm{asset}}+\eta_{\mathrm{MC}}\right],
\]

或在 formal protocol 中冻结的等价 nested bootstrap/hierarchical estimator。不得只报告
asset variation 而忽略 oracle MC error，也不得把 posterior draws 数量当成 asset 样本量。

进入 Claims 1–2 的 cell 必须满足：

\[
\eta_{\mathrm{MC}}(\theta)
\le \kappa_{\mathrm{MC}}\,\delta_{\mathrm{sci}}(\theta),
\]

其中 \(\kappa_{\mathrm{MC}}\) 和相应 scientific effect 在看到 formal learned-model 结果前由
precision calibration 冻结。若预算上无法达到，cell 标为 `REFERENCE-UNCERTAIN`，不能通过
扩大 CI 或忽略 error floor 挽救。

### 5.3 Oracle validity gate

一个 generator family 只有在：

- same-information audit 无泄漏；
- analytic/SBC 与 MC stability 达标；
- 主 cells 的 ESS/degeneracy 达标；
- parent/garbling 关系可验证；
- thresholds 相对 MC floor 可分辨；

之后才可进入 Gate A。oracle validity 与 cell scientific usefulness 是两个条件：数值
oracle 正确但 interventions 不产生所需 contrast，仍视为问题世界无效。

---

## 6. Cell eligibility 状态机

### 6.1 Tractability guard

对每个 proposed parent \(c^+\)，先检验：

\[
\bar B^\star(c^+)\le\tau_{\mathrm{tract}}.
\]

\(\tau_{\mathrm{tract}}\) 必须在冻结 target space 中由 task relevance、no-history/reference
contrast 与 pilot/design variance共同设定。它排除“full information 下本来就几乎不可预测”
导致的伪 compatibility，不表示任务没有 process/future-load uncertainty。

若 parent 不通过，所有以其为 reference 的 child cells 标为 `INTRACTABLE-PARENT`，不进入
Claims 1–2。

### 6.2 Task-sufficient view class

在合法 parent 与 tractability guard 下，cell \(c\) 为 task-sufficient 当且仅当：

\[
CI_{\mathrm{tot}}
\left(\mathcal A^\star_{\mathrm{obs}}(c;c^+)\right)
\subseteq[-\epsilon_A,\epsilon_A].
\]

这是等价性判定，不得把“未显著大于 0”误作 sufficient。若 CI 太宽跨出等价区间，状态为
`INSUFFICIENT-PRECISION`，不是 sufficient。

### 6.3 Posterior-compatible sufficient pair

pair \((a,b)\) 为 compatible 当且仅当：

1. \(a,b\) 都已是 task-sufficient；
2. pair matching audit 通过；
3. 
   \[
   U\left[CI_{\mathrm{tot}}(\bar D^\star(a,b))\right]
   \le\epsilon_D.
   \]

低 \(D^\star\) 但任一 view 非 task-sufficient 的 pair 禁止进入 Claim 1；两个同样模糊的
posterior 不能被称为 sufficient pair。

### 6.4 Information-losing view class

cell \(c_{\mathrm{critical}}\) 为 Claim-2-eligible information-losing view 当且仅当：

1. parent tractable；
2. 有通过 Section 3.3 的 garbling relation；
3. critical/control matching 完成；
4. 
   \[
   L\left[CI_{\mathrm{tot}}
   (\mathcal A^\star_{\mathrm{obs}}(c_{\mathrm{critical}};c^+))\right]
   \ge\delta_A>0;
   \]
5. 
   \[
   L\left[CI_{\mathrm{tot}}
   (\Delta\mathcal A^\star_{\mathrm{crit}})\right]
   \ge\delta_{\mathrm{crit}}>0;
   \]
6. reference posterior 不是因 numerical degeneracy 或 near-empty view 才变宽；
7. cell 位于预声明 data-availability support，不是“几乎无观测”的极端。

这里 \(\delta_A,\delta_{\mathrm{crit}}\) 是最小科学效应，不是单纯 \(p<0.05\)。critical 只比
full 风险高但不比 matched random/redundant control 高的 cell，不足以支持 mechanism-specific
information-loss claim。

### 6.5 其他状态

每个 cell/pair 只能拥有一个 primary eligibility status：

| 状态 | 含义 | Claims 用途 |
|---|---|---|
| `ELIGIBLE-SUFFICIENT` | excess ambiguity 等价于 0 | Claim 1 view |
| `ELIGIBLE-COMPATIBLE-PAIR` | 两侧 sufficient 且 \(D^\star\) 小 | Claim 1 pair |
| `ELIGIBLE-INFORMATION-LOSS` | critical loss 与 matched contrast 均达科学效应 | Claim 2 |
| `ORDERED-NONCRITICAL-CONTROL` | 合法 garbling control，但未达到 critical effect | Claim 2 control |
| `NONORDERED-SWAP` | 非嵌套 sensor/operator swap | geometry/robustness only |
| `NONORDERED-INFORMATIVE-MISSINGNESS` | mask 可能额外携带 latent information | boundary only |
| `INTRACTABLE-PARENT` | full task 本身不可用 | exclude |
| `REFERENCE-UNCERTAIN` | oracle error/ESS 不达标 | exclude |
| `INSUFFICIENT-PRECISION` | 设计 CI 无法完成资格判定 | exclude or redesign before lock |
| `DEGENERATE-VIEW` | 几乎无数据或 target support 病态 | exclude |
| `DESIGN-AMBIGUOUS` | 不满足任一主资格且不属于明确边界类 | supplementary map |

资格必须在 model results 不可见时写入 immutable manifest。失败 cells 仍保留并报告，禁止
只删除不利 cell 而不显示 eligibility map。

---

## 7. Matched critical/random/redundant triplets

### 7.1 必须匹配的量

同一 triplet 至少匹配：

- base asset、latent path、query time 与 past operating context；
- future policy \(\Pi_u\)；
- parent cell \(c^+\)；
- active sensor count；
- observed event count、mask density 与 total time coverage；
- sampling scale/timestamp support；
- retained-event noise realization、SNR 与 quality distribution；
- factor-level support status；
- deletion severity。

critical/random/redundant 是 \(P_{\mathrm{gen}}\) 分层标签，绝不进入 model batch。
这里的 past operating context 只指部署可观测的 \(u_{\le t}\)；隐藏或 future context
不得因 matching 需要而进入模型，只能在 parent coupling 与 oracle integration 中保持同 law。

### 7.2 Control 选择

- **Redundant deletion** 删除对 target 在 parent 条件下增量信息低、但 event/count profile
  可匹配的 sensors。
- **Random deletion** 从预声明 eligible sensor pool 随机删除，条件于同等 count/coverage；
  randomization seed 在 model training 前冻结。
- **Critical deletion** 删除在 generator physics 中对 failure-relevant latent coordinate 具有
  独特增量信息的 sensors；“critical”由 generator design 定义，再由 oracle risk contrast
  验证，不由 learned-model effect 定义。

若 exact matching 物理上不可行：

1. 在 cell manifest 中预先列出无法匹配的 covariate；
2. 使用预声明 strata/weights；
3. 报告 overlap、ESS、maximum weight；
4. common support 不足时 triplet 为 `NON-ELIGIBLE`；
5. 禁止在看到 outcome 后更换 control pool。

### 7.3 Mask-rate heuristic audit

为了排除“mask 多就变宽”，critical 与 controls 的 count/mask distributions 应在设计层尽量
相同。mask-rate-only model 可作 downstream control，但它不参与 oracle eligibility。
若设计层仍存在明显 residual imbalance，必须在 Claim 2 的限制中报告，不能靠模型 control
完全补救。

---

## 8. Factorial grid 与 composition eligibility

### 8.1 因子空间

\[
\mathcal P_{\mathrm{design}}=S\times R\times Q.
\]

最低候选 levels：

| 因子 | 候选 levels |
|---|---|
| \(S\) | full、redundant deletion、matched random deletion、mechanism-critical deletion、direct/proxy swap |
| \(R\) | dense regular、sparse regular、irregular/jittered |
| \(Q\) | clean、heteroscedastic noise、bursty outage、合格的 MNAR-like/boundary missingness |

不是所有 Cartesian cells 都自动进入正式实验。F0 先生成完整 oracle eligibility map，再选择一个
最小但覆盖论文 claims 的 cell set。

### 8.2 Compositional holdout 资格

held-out joint cell 必须满足：

1. 该 \((S,R,Q)\) 联合 tuple 在训练中从未出现；
2. 每个单因素 level 在其他 training cells 中出现；
3. base assets 与 training/validation/test 先分离，再生成 view；
4. 至少包含 sufficient 与 information-losing 两类 eligible cells；
5. cell 只依据 oracle strata、factor coverage 与 design balance选择；
6. 不使用任何 learned-model held-out result；
7. baseline-support 与 balanced-support 分别生成独立 manifests。

one-factor OOD、unseen intensity 和 truly unseen factor level 必须另标，不得混入
compositional estimand。

### 8.3 两个 training-support contracts

两种 support allocation 使用相同 eligible seen/held-out tuples、asset splits、evaluation
rows 与总训练预算，但训练曝光不同：

- `balanced-support`：seen joint cells 等量贡献 assets/queries/minibatch exposure，作为
  Claim 3 的 primary scientific contract，用于隔离“组合未见”而非频率不平衡；
- `baseline-support`：按预冻结 design/deployment-like cell frequency 分配曝光，作为
  allocation-sensitivity contract。

总 optimizer updates、可见 base assets 和 target draws 必须 compute/data-budget matched；
不足部分不得通过重复少量 assets 伪装为新独立样本。两种 support 的
\(\Delta C_{\mathrm{raw}}\) 分别估计、分别报告，不 pooled。baseline-support 可解释
deployment sensitivity，但不能救回 balanced-support primary failure。

### 8.4 Ambiguity/shape strata

为结果解释和 matched robustness，oracle-only descriptors 可将 cells 分为预声明 strata：

- low / medium / high \(\mathcal A^\star_{\mathrm{obs}}\)；
- low / medium / high \(\bar D^\star\)；
- unimodal / multimodal；
- light / heavy tail；
- weak / strong state–failure dependence。

cut points 只由 development/design oracle distribution 确定并冻结。它们不能用于调整 raw
Claim 3 primary weights；oracle-shape matching 只用于 robustness，详见 registry。

---

## 9. Cell eligibility manifest

每个 generator family 输出一个行级 `cell_eligibility_manifest`。最低 schema：

| 字段 | 内容 |
|---|---|
| identity | `generator_family_id`, `cell_id`, `parent_cell_id`, `pair_id`, `triplet_id` |
| factors | `S_level`, `R_level`, `Q_level`, `support_contract` |
| ordering | `garbling_kernel_id`, `information_order_valid`, `ordering_failure_reason` |
| design | asset/query/observation counts，\(\Pi_u\) ID，query law ID |
| matching | count/coverage/SNR/mask balance，exact/weighted，overlap diagnostics |
| oracle | sampler/version/budget/ESS/failure rate，`reference_role`、`split_role`、`reference_stream_id`、`reference_sample_set_id` |
| ambiguity | \(\bar B^\star(c),\bar B^\star(c^+),\mathcal A^\star_{\mathrm{obs}}\)，total CI |
| geometry | relevant \(\bar D^\star\)，total CI |
| critical contrast | \(\Delta\mathcal A^\star_{\mathrm{crit}}\)，total CI |
| qualification | tractability/sufficiency/compatibility/loss booleans |
| status | 唯一 eligibility status 与 machine-readable exclusion reason |
| split use | development/validation/test/lockbox；seen/held-out/robustness |
| provenance | code revision、manifest revisions、creation time、amendment ID |

所有 estimates 同时保存 per-asset intermediate table；aggregate manifest 不能是唯一证据。

---

## 10. Threshold registry 与确定规则

当前只冻结 threshold 的语义和确定程序，不填未经 precision/pilot 支持的数值。

| ID | 量 | 角色 | 数值证据 | 状态/冻结点 |
|---|---|---|---|---|
| `OC-T01` | \(\tau_{\mathrm{tract}}\) | full-task tractability ceiling | target scale、no-history contrast、task relevance | `PENDING-DESIGN`，F0 前 |
| `OC-T02` | \(\epsilon_A\) | sufficiency equivalence half-width | smallest meaningful excess ambiguity + MC floor | `PENDING-DESIGN`，eligibility run 前 |
| `OC-T03` | \(\epsilon_D\) | posterior compatibility ceiling | reference repeat distance + meaningful shape change | `PENDING-DESIGN`，eligibility run 前 |
| `OC-T04` | \(\delta_A\) | minimum information-loss effect | pilot/design variance + task relevance | `PENDING-DESIGN`，eligibility run 前 |
| `OC-T05` | \(\delta_{\mathrm{crit}}\) | minimum critical-v-control excess | matched pilot variance + mechanism relevance | `PENDING-DESIGN`，eligibility run 前 |
| `OC-T06` | \(\kappa_{\mathrm{MC}}\) | max oracle-error/effect ratio | precision/resource analysis | `PENDING-DESIGN`，oracle budget lock 前 |
| `OC-T07` | oracle ESS floor | reference numerical health | sampler stress test | `PENDING-DESIGN`，F0 前 |
| `OC-T08` | max weight / degeneracy limit | reference numerical health | sampler stress test | `PENDING-DESIGN`，F0 前 |
| `OC-T09` | match overlap floor | weighted triplet eligibility | development design overlap | `PENDING-DESIGN`，cell selection 前 |
| `OC-T10` | matched ESS floor/max weight | weighted triplet eligibility | precision simulation | `PENDING-DESIGN`，cell selection 前 |

每个数值必须记录：单位、方向、估计版本、使用的 pilot/design rows、是否接触 learned-model
outcomes、决定日期和 registry revision。若现有 R1–R47 仅能提供 variance scale 而 estimand 不同，只可用于
保守资源界，不可直接复用旧 success threshold。

world-design calibration 可以提供 target scale、variance 与 oracle numerical floor，但不得
用当前 candidate cells 已观察到的 \(\widehat{\mathcal A}^\star\) 或
\(\widehat D^\star\) point effects 反向选择刚好通过的 \(\epsilon/\delta\)。最小科学效应先由
task relevance 与可分辨 precision 冻结；若 operator 未达到它，应修改/放弃 operator，而
不是移动 threshold。FRZ-0 允许 WP1 的仅限 world-design calibration，所有 thresholds 在
任何 formal model training 前转为 `LOCKED-EXECUTION`。

---

## 11. Gate A 判定

Gate A 采用 intersection rule；以下全部满足才通过：

1. oracle audits `OR-A01`–`OR-A10` 中的适用项通过；
2. 至少一个 primary generator family 有 tractable full parent；
3. 有足量 `ELIGIBLE-SUFFICIENT` views 与 `ELIGIBLE-COMPATIBLE-PAIR` 支撑 Claim 1；
4. 有足量严格 matched、ordered 的 `ELIGIBLE-INFORMATION-LOSS` triplets 支撑 Claim 2；
5. composition manifest 同时覆盖 sufficient 与 loss cells；
6. oracle MC floor 小于资格所需 scientific effects；
7. same-information/input-permission audits 无 fatal violation；
8. alternate generator 能形成独立 robustness set，或在开始 model confirmation 前书面收缩该边界。

Gate A 失败时只允许：修复 oracle implementation、重设 generator/operator design 或缩小
claim。禁止通过训练更多模型、调整 model loss 或删除不利 cells 使问题世界“看起来成立”。

---

## 12. 冻结与验收清单

进入 WP2 前：

- [ ] train/eligibility/selection/metric:test/metric:lockbox roles、sample IDs 和 random streams 已分离；
- [ ] parent-first generator 与 garbling kernels 有 schema/code tests；
- [ ] informative missingness/nonordered cells 已从 Claim 2 主集合分离；
- [ ] thresholds `OC-T01`–`OC-T10` 已从 `PENDING-DESIGN` 转为 `LOCKED-EXECUTION`；
- [ ] per-asset oracle intermediate tables 可复算 aggregate；
- [ ] cell/pair/triplet eligibility manifest 已登记 version/revision；
- [ ] seen/held-out cells 在 learned-model results 不可见时冻结；
- [ ] Gate A 决策与失败理由已生成 immutable report。

完成这些条件表示问题世界具有可执行资格，不表示任何 learned method 已成功。
