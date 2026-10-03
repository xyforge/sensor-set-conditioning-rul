# Formal Problem Specification

合同编号：`FPS-4.1a`  
版本：`0.1.3-wp0`（2026-08-22）

状态：**科学对象已冻结；实现字段待设计校准后锁定**  
规范性来源：[V4.1a 研究计划](../t3_phm_detailed_research_plan.md)  
配套合同：[Oracle 与 cell eligibility](./oracle_and_cell_eligibility_spec.md) · [Claim–metric registry](./claim_metric_registry.md) · [Formal experiment protocol](./formal_experiment_protocol.md)

> 本合同冻结“研究对象究竟是什么、模型和 reference 各自允许知道什么、哪些结论可以由哪些数据世界支持”。它不选择网络宽度，不规定 oracle 数值预算，也不定义统计通过门槛；这些分别由配套合同承担。

---

## 1. 合同语言、状态与优先级

### 1.1 规范性关键词

- **必须 / MUST**：违反即使对应 run 不具备确认性资格。
- **禁止 / MUST NOT**：违反即构成信息泄漏、estimand 改变或结论越界。
- **应该 / SHOULD**：除非留下书面偏离理由，否则必须执行。
- **可以 / MAY**：不改变中心 estimand 的实现自由度。

### 1.2 冻结状态

本文件使用三种状态：

| 状态 | 含义 |
|---|---|
| `LOCKED-SCIENCE` | 科学含义已冻结；不得因结果不利而修改 |
| `PENDING-DESIGN` | 数值或工程字段必须按预声明程序确定，不能凭直觉填写 |
| `LOCKED-EXECUTION` | 字段已写入 versioned final manifest 并进入 lockbox；之后只能按 amendment 规则变更 |

当前 Sections 2–11 为 `LOCKED-SCIENCE`。Section 12 列出的实现标识符为
`PENDING-DESIGN`；其数值不影响本合同的科学成立，但未锁定前不得开始确认性 F2–F6。

### 1.3 文档优先级

1. V4.1a 冻结论文的科学主线和叙事边界。
2. 四份 formal contracts 冻结可执行含义；同一对象只由其职责文件定义。
3. 机器可读 manifests 只能实例化合同，不得静默改变合同。
4. 若代码、配置或报告与合同冲突，以合同为准，该 run 标记为 `CONTRACT-VIOLATION`，不得通过重新解释代码挽救。

任何实质 amendment 必须说明：变更原因、接触过的数据、受影响 Claims、是否需要新
lockbox，以及旧结果为何仍可或不可比较。看到 test/lockbox 结果后修改 target、信息集、
primary endpoint 或方向性判据，自动使原确认性序列失效。

---

## 2. 唯一科学问题与 estimand family

### 2.1 科学问题

第一篇论文只回答：

> 当 observation process 的 sensor、timing 与 quality/missingness 因素发生组合式变化时，模型能否学习忠实于当前可观测证据的 joint prognostic posterior：让没有造成有意义信息损失的 views 保持 posterior-compatible，让机制关键信息丢失的 views 保留 reference 所要求的歧义和形状变化，并把这种行为外推到训练未见的因素组合？

### 2.2 中心目标

对查询时刻 \(t\)，定义：

\[
Y_t=(h_t,T_{\mathrm{fail}}),
\qquad
V_t=(\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u).
\]

受控数据世界中的中心 estimand 为：

\[
\pi_t^\star(Y_t\mid V_t),
\]

中心 learned object 为：

\[
q_\phi(Y_t\mid V_t)
=q_\phi\!\left(h_t,T_{\mathrm{fail}}\mid
\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u\right).
\]

RUL 只由

\[
\Delta T_t=T_{\mathrm{fail}}-t
\]

派生，不是第二个独立 scientific target。

### 2.3 论文不优化的对象

以下均不是第一篇论文的中心 learned object：

- 独立 uncertainty/widening score；
- learned sufficiency 或 abstention score；
- maintenance utility 或 action policy；
- generator-side failure mechanism classifier；
- 一般 domain label 或万能 sensor-ontology representation。

这些量可以从 posterior 派生或用于诊断，但不得增加为第四项核心贡献。

---

## 3. 受控世界的联合生成合同

### 3.1 基础随机对象

在联合设计 law 下，独立实验单位是 base asset/trajectory \(A\)。每个 asset 至少包含：

\[
A=(\theta_A,h_0,K_{\mathrm{fail}},\omega_H),
\]

其中 \(\theta_A\) 是 asset-level parameters，\(K_{\mathrm{fail}}\) 是 generator-only
failure-mechanism label，\(\omega_H\) 是 latent-process randomness。给定 past operating
context \(u_{\le t}\)，latent degradation 满足：

\[
d h(\tau)
=f_\theta(h(\tau),u(\tau),\tau)d\tau
+G_\theta(h(\tau),u(\tau),\tau)dW_\tau.
\]

本合同不要求特定 SDE 数值形式；具体 competing stochastic 与 nonlinear/switching
families 由 generator manifest 冻结。但两个 families 都必须输出相同语义的
\(h_t,T_{\mathrm{fail}},P_{\mathrm{obs}},P_{\mathrm{gen}}\) 和 row keys。

### 3.2 未来工况政策

失效时间依赖未来工况：

\[
T_{\mathrm{fail}}
=\inf\{\tau>t:g(h(\tau),u(\tau))\ge 0\}.
\]

第一篇只采用“未来 realized workload 未知、任务政策已知”的合同：

\[
u_{>t}\sim\Pi_u(\cdot\mid u_{\le t}).
\]

primary controlled world 将查询时刻前实际测得的 operating context \(u_{\le t}\) 作为
observation history 中的合法 covariates 暴露给 model 与 reference。若某 public dataset
不观测其中一部分，则 model 与 reference-free objective 均不得使用该私有 past context；
相应 \(\Pi_u\) 只能条件于部署时可见 history。禁止 oracle 私下读取完整
\(u_{\le t}\) 而 model 只看 sensors。

因此：

1. reference 必须对 realized \(u_{>t}\) 积分；
2. model 禁止读取 realized \(u_{>t}\)；
3. 同一 matched comparison 必须共享 \(\Pi_u\)；
4. 若全实验只有一个 \(\Pi_u\)，模型接口将其视为隐式常量；
5. 只有部署时确实已知多个任务政策时，才允许输入 policy identifier；该 identifier
   不得编码 realized future sequence。

将来若研究已知 future mission plan \(u_{t:T}\)，必须另立 estimand，不能与本篇数值合并。

### 3.3 Observation process

对 sensor \(j\) 与 event \(n\)：

\[
x_{j,n}=H_{S,j}\!\left(h(\tau_{j,n}),u(\tau_{j,n})\right)
+\epsilon_{j,n}(Q),
\qquad
\tau_{j,n}\sim R_j.
\]

查询前事件历史表示为无固定网格假设的集合：

\[
\mathcal O_{\le t}
=\{(s_j,\tau_{j,n},x_{j,n},q_{j,n},m_{j,n}):\tau_{j,n}\le t\}.
\]

正式 observation-process design 只改变：

- \(S\)：sensor set / measurement operator；
- \(R\)：sampling rate、regularity 与 timestamp pattern；
- \(Q\)：noise、drift、outage 与 missingness。

delay、active sensing、maintenance action 与跨企业 ontology 不得混入主 factorial design。

### 3.4 Query-time law

query times 不是可随结果挑选的 rows。其抽样 law \(t_q\sim\Pi_t\) 必须：

- 在 asset split 之前定义语义、在生成 views 之前实例化；
- 在 cells 和 models 间共享；
- 避开不可比较的失效后窗口；
- 以预声明 relative-life/time strata 保证不同生命阶段可比；
- 在最终 metric 中先按 asset 和 query-time stratum 聚合，不能把 windows 当独立样本。

\(\Pi_t\) 的具体 strata 和每 asset 数量是 `PENDING-DESIGN`，由 formal protocol 锁定。

---

## 4. 信息边界：\(P_{\mathrm{obs}}\) 与 \(P_{\mathrm{gen}}\)

### 4.1 生成关系

\[
P_{\mathrm{gen}}
\longrightarrow
(\mathcal O_{\le t},P_{\mathrm{obs}}),
\qquad
q_\phi\text{ 只能读取 }V_t.
\]

\(P_{\mathrm{obs}}\) 与 \(P_{\mathrm{gen}}\) 必须存放在不同 schema namespaces，且
model dataloader 使用显式 allowlist，不使用 denylist。

### 4.2 可观测字段 allowlist

只有部署时真实可取得并具有清楚语义的字段可进入 \(P_{\mathrm{obs}}\)：

| 字段族 | 允许内容 | 限制 |
|---|---|---|
| sensor identity/set | sensor ID、当前存在的 sensors | ID 映射只从 development 建立 |
| event time | absolute/relative timestamp、time gap、observed interval | 不得包含未来 event schedule |
| realized availability | value-validity、mask、outage indicator | 只能是查询时刻前已实现状态 |
| quality | 设备真实提供的 quality flag | simulator 自知的真实 noise class 不等于 quality flag |
| past operating context | 查询时刻前已实现、部署时可测的 load/setting covariates | 不包含 future mission realization |
| semantics | unit、location、physical role | 必须有部署来源；不可由 latent relevance 反推 |
| policy | observable \(\Pi_u\) identifier | 不得包含 realized future load |

sensor set、timestamps 和 masks 可能已是 \(\mathcal O_{\le t}\) 的可测函数。因此
“process-conditioned”要求使用完整 observable information set，但不要求冗余 metadata
ablation 必须产生增益。

### 4.3 Generator-only fields

以下字段属于 \(P_{\mathrm{gen}}\)，禁止作为 input、training target、auxiliary loss、
checkpoint-selection signal 或 feature-engineering source：

- `intervention_class`：critical / random / redundant；
- 真实 missingness/noise-generating mechanism；
- latent failure-mechanism relevance；
- 真实 observation-operator class；
- \(K_{\mathrm{fail}}\)；
- realized future workload；
- omniscient posterior summaries。

它们只可用于 generator construction、oracle inference 的隐藏变量积分、matched-control
construction、eligibility stratification 和 test 后解释。

analysis-side evaluator 可以读取由 oracle 合同冻结的 `cell_id/pair_id/eligibility_status`
以完成分层、matching 与 Claim aggregation，但这些字段必须从 model batch、gradient graph
和 per-branch epoch/checkpoint selection 中物理隔离。每个 branch 的 checkpoint 只能由
不含 generator labels 的 pooled validation proper-score rule 选择；随后才可由独立 evaluator
按预声明 relation/Claim rule 做 candidate promotion 或 strongest-baseline designation。
这属于 analysis，不得把 eligibility status 回写为 model feature 或 auxiliary target。

### 4.4 最小物理 schema

正式数据 artifact 至少分为：

```text
asset/
  asset_id, generator_family_id, latent_seed, split_id
latent_private/
  h_path, K_fail, realized_future_u, failure_boundary_state
observation/
  events, query_time, P_obs
generator_private/
  P_gen, operator_parameters, intervention_class
target_controlled/
  h_t, T_fail, censoring_status
oracle/
  same_information_reference_samples_by_role, diagnostics
audit_only/
  omniscient_reference_samples (optional)
```

训练 schema view 必须排除 `latent_private/` 和 `generator_private/`，但在 simulator-supervised
regime 中可通过专门 target channel 暴露 `target_controlled/(h_t,T_fail)`。target channel
不得回流到 encoder input。`oracle/` 下每个 sample artifact 必须显式携带 OCES 定义的
`reference_role`、`split_role`、`reference_stream_id` 与 `reference_sample_set_id`；消费者必须
通过 purpose allowlist 读取，不能把 validation selection reference 当作 train reference，
也不能把 test/lockbox metric reference 当作 selection reference。

---

## 5. Same-information reference posterior

### 5.1 中心 reference

令 \(\rho_{\mathrm{gen}}\) 为冻结设计/部署 law 对隐藏 generator attributes 诱导的条件分布。
中心 reference 必须与 model 共享信息集：

\[
\pi_t^\star(Y_t\mid V_t)
=\iint
p(Y_t\mid\mathcal O_{\le t},P_{\mathrm{obs}},p_{\mathrm{gen}},u_{>t})
\rho_{\mathrm{gen}}(dp_{\mathrm{gen}}\mid
\mathcal O_{\le t},P_{\mathrm{obs}})
\Pi_u(du_{>t}\mid u_{\le t}).
\]

“知道 simulator 的全局 law”不等于“知道当前 row 的隐藏 intervention label”。oracle
程序可以使用生成机制计算积分，但每个 row 的 center reference 禁止额外条件于 model
不可见的 realization-specific \(P_{\mathrm{gen}}\)。

### 5.2 Failure mechanism 与 learned mixture index

若生成世界有 \(K_{\mathrm{fail}}\)：

\[
\pi_t^\star(h_t,T_{\mathrm{fail}}\mid V_t)
=\sum_K\pi_t^\star(h_t,K,T_{\mathrm{fail}}\mid V_t).
\]

learned model 可使用未命名的 latent mixture index \(k\)：

\[
q_\phi(h_t,T_{\mathrm{fail}}\mid V_t)
=\sum_k q_\phi(h_t,k,T_{\mathrm{fail}}\mid V_t).
\]

\(k\) 不等于 \(K_{\mathrm{fail}}\)。训练后可报告二者 association 作为诊断，但禁止称为
failure-mode recovery，也禁止以 \(K_{\mathrm{fail}}\) 监督 \(k\)。

### 5.3 Omniscient reference

条件于真实 \(P_{\mathrm{gen}}\) 或 realized \(u_{>t}\) 的 posterior 可以计算，但必须：

- 标记为 `reference_role=omniscient_sanity_only`；
- 存在独立目录和字段前缀；
- 不进入 model training、cell eligibility、primary metrics 或 checkpoint selection；
- 只检查 simulator/oracle code 的极限行为。

---

## 6. Learned posterior contract

### 6.1 输入与输出

模型接口必须等价于：

\[
(\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u)
\xrightarrow{\ q_\phi\ }
\mathcal P(h_t,T_{\mathrm{fail}}).
\]

默认实现可采用：

\[
q_\phi(k,h_t,\Delta T_t\mid c_t)
=q_\phi(k\mid c_t)
q_\phi(h_t\mid k,c_t)
q_\phi(\Delta T_t\mid h_t,k,c_t),
\quad \Delta T_t>0.
\]

允许 Gaussian mixture 或开发阶段一次性升级的 conditional flow；参数化不是 scientific
claim。无论实现如何，必须可：

- 采样 joint \((h_t,T_{\mathrm{fail}})\)；
- 计算或稳定估计 joint log density；
- 得到 state 与 continuous failure-time marginals；
- 保留 location、scale、multimodality、dependence 与 tail change；
- 让 joint objective 更新 encoder/filter/head，而非只训练 detached widening head。

### 6.2 受控世界 supervision

Simulator-supervised primary regime 允许使用 development trajectories 的 joint draws
\((Y_t,V_t)\) 做 conditional density estimation：

\[
\mathcal L_{\mathrm{joint}}
=-\mathbb E_{Y\sim\pi^\star(\cdot\mid V)}\log q_\phi(Y\mid V).
\]

这里的训练 draw 可由联合 simulator posterior sampling 或验证后的 same-information
reference sampling提供。若 relation candidate 被开发规则允许，其 target 也必须来自同一
same-information reference。validation/test/lockbox reference 禁止进入训练。

### 6.3 关系原则与可选 regularizer

科学原则是 oracle-derived informativeness relations，而不是某个固定 loss。允许比较：

\[
\mathcal L_{\mathrm{direct}}
=\mathcal L_{\mathrm{joint}}+\lambda_{\mathrm{reg}}\mathcal L_{\mathrm{reg}},
\]

和

\[
\mathcal L_{\mathrm{relation}}
=\mathcal L_{\mathrm{direct}}
+\lambda_{\mathrm{geom}}
\mathbb E_{(a,b)}
\left[d(q_\phi^a,q_\phi^b)-d(\pi^{\star,a},\pi^{\star,b})\right]^2.
\]

scalar geometry loss 只匹配一个关系量，不能替代 per-view density fidelity。若它未按
formal protocol 的开发规则获得 promotion，则 formal candidate 为 direct model 且
\(\lambda_{\mathrm{geom}}=0\)；禁止继续搜索第三种 relation loss。

---

## 7. 归一化与 target support

### 7.1 Joint metric space

\(h_t\) 与 \(\Delta T_t\) 必须用 development split 冻结的物理尺度或 robust scale 转换为
无量纲 joint metric space：

\[
\tilde Y_t=
\left(D_h^{-1}(h_t-\mu_h),
s_T^{-1}\,\psi(\Delta T_t)\right).
\]

\(\psi\) 默认为 identity 或 log-time，由 development reference 的 support 与 numerical
stability 一次性决定。所有 models、cells、splits、oracle distances 和 energy scores
必须共享 \((\mu_h,D_h,s_T,\psi)\)。

禁止：

- 按 cell 或 model 单独缩放；
- 使用 test/lockbox statistics；
- 为使某一 marginal 占优而在确认结果后修改 state/time 权重。

### 7.2 Positivity 与 censoring

\(\Delta T_t>0\) 必须由 distribution support 保证，不得靠评估时 clipping 隐藏 invalid
samples。受控 primary world 应保存 exact \(T_{\mathrm{fail}}\)；若设计含 administrative
censoring，censoring law 必须独立记录，且 joint oracle metric 与公开 survival metric
不得混成同一 estimand。

---

## 8. Public PHM 的唯一 bridge

公开 PHM 没有可信的 \(h_t\) oracle label。模型内部 coordinate 记为不作物理解读的
\(\tilde h_t\)，只训练和评价：

\[
q_\phi(\Delta T_t\mid\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u)
=\sum_k\int q_\phi(k,\tilde h_t,\Delta T_t\mid
\mathcal O_{\le t},P_{\mathrm{obs}},\Pi_u)d\tilde h_t.
\]

Public regime 合同：

1. 只使用 observed event/failure-time 或 censoring likelihood；
2. 只有工程上可论证为不删 task information 的 transformation 才可加 predictive-marginal
   consistency；
3. \(\Pi_u\) 若从数据估计，只能用 training assets，并在 test 前冻结；
4. simulator pretraining 只是 ablation，不形成平行 scientific route；
5. 不冻结并宣称跨设备保持真实 physical state module；
6. public results 只支持 failure-time predictive plausibility、calibration 和 controlled-shift
   robustness，不能证明真实 latent identifiability。

---

## 9. 允许与禁止的论文解释

### 9.1 若相应 gates 通过，可以主张

- observation process 在已建模生成 family 中改变 operational prognostic
  partial identifiability；
- task-sufficient views 的 posterior compatibility 可以被 learned model 复现；
- information-losing views 的 joint posterior change 可以被更忠实地表达；
- 上述行为可在预声明 unseen \(S\times R\times Q\) compositions 上检验；
- public PHM 上的 failure-time marginal 具有有边界的外部 plausibility。

### 9.2 无论结果如何，禁止主张

- 一般非线性系统的 structural/global identifiability theorem；
- 从真实工业数据恢复唯一 physical health state；
- \(k\) 恢复了真实 \(K_{\mathrm{fail}}\)；
- observation process 与 degradation mechanism 的普遍因果识别；
- 对未建模 sensor ontology、future policy 或 generator family 的无条件泛化；
- TSFM 是中心创新，或仅凭 interval widening/coverage 证明 uncertainty 正确。

---

## 10. 不变量与自动审计要求

每个 formal run 必须满足以下 invariants；建议将 ID 直接写入 schema tests：

| ID | 不变量 | 失败状态 |
|---|---|---|
| `FPS-I01` | model batch 中不存在任何 \(P_{\mathrm{gen}}\) 字段 | `LEAKAGE-FATAL` |
| `FPS-I02` | center reference 与 model 使用相同 \(V_t\) | `REFERENCE-MISMATCH` |
| `FPS-I03` | realized future \(u_{>t}\) 未进入 model/reference conditioning | `FUTURE-LEAKAGE` |
| `FPS-I04` | matched views 共享 asset、latent history、query time 与 \(\Pi_u\) | `PAIRING-INVALID` |
| `FPS-I05` | asset split 先于 view/cell generation | `SPLIT-LEAKAGE` |
| `FPS-I06` | \(K_{\mathrm{fail}}\) 未作为 input/target/selection signal | `MECHANISM-LEAKAGE` |
| `FPS-I07` | normalization 只由 development 产生并跨模型共享 | `METRIC-SPACE-CHANGED` |
| `FPS-I08` | public \(\tilde h_t\) 未被报告为真实 state | `CLAIM-BOUNDARY-VIOLATION` |
| `FPS-I09` | RUL 只从 \(T_{\mathrm{fail}}\) 派生 | `TARGET-DRIFT` |
| `FPS-I10` | 同一 checkpoint family 同时进入 Claims 1–3 | `MODEL-SELECTION-DRIFT` |
| `FPS-I11` | reference role、split role 与 consumer purpose 符合 OCES allowlist | `REFERENCE-ROLE-VIOLATION` |

审计至少包括 schema allowlist test、随机 batch dump、reference-conditioning trace、split-key
collision check、reference-role consumer trace 和 normalization manifest revision。

---

## 11. 合同验收标准

本合同可以从 `0.1.3-wp0` 升为 `1.0.0-locked`，当且仅当：

- [ ] 两个 generator families 都能实例化 Sections 3–5 的同一接口；
- [ ] `P_obs` 与 `P_gen` schema 已物理分离，并有 passing batch audit；
- [ ] \(\Pi_u\)、query-time law 和 target normalization 已写入 versioned manifest；
- [ ] same-information 的 train/eligibility/selection/metric streams 与 omniscient reference 在代码和存储上分离；
- [ ] controlled/public supervision permissions 已逐模型列出；
- [ ] 四份合同使用相同符号、Claim IDs 和 gate 方向；
- [ ] 所有 `PENDING-DESIGN` 字段已有证据来源和 lock deadline；
- [ ] 最终文件与机器 manifests 已登记 version/revision，lockbox access policy 已启用。

验收不要求任何 Claim 已经成功；它只要求问题被无歧义地实例化。

---

## 12. 待实例化字段（不得凭空赋值）

| 字段 ID | 内容 | 决定依据 | 最迟冻结点 |
|---|---|---|---|
| `FPS-P01` | generator family 版本与参数 support | WP1 physics/design audit；不得看 learned test result | F0 前 |
| `FPS-P02` | \(\Pi_u\) 的参数与 policy ID | task definition + development-only stress audit | F0 前 |
| `FPS-P03` | query-time strata 与每 asset queries | task relevance + precision simulation | power analysis 前 |
| `FPS-P04` | \(h/\Delta T\) normalization 与 \(\psi\) | development reference scale + numerical stability | F1 前 |
| `FPS-P05` | default mixture family/components | development posterior predictive checks | Gate B 前 |
| `FPS-P06` | conditional-flow upgrade trigger | absolute reference-shape failure rule | 首次 F1 前 |
| `FPS-P07` | public \(\Pi_u\) estimation rule | dataset audit，training assets only | F7 split lock 前 |

所有字段的最终值、证据 artifact、决策日期和审批者必须进入 formal protocol 的 freeze
ledger。`PENDING-DESIGN` 不能在结果表中被当成研究者自由度。
