---
name: growth-activity-designer
description: 按方法论分步推演一个超市用增活动，从一句业务诉求直至产出可评审的完整产品方案（活动规则/逆向/曝光动线/成本与实验/决策点汇报表/可视化报告）。当业务提出新活动诉求、要出活动方案、要评估某个玩法怎么设计时使用。产出到产品方案为止，不含系统流程图与系统需求；预算管理归业务方，不在产出范围。
---

# growth-activity-designer 主控

每个生产任务在 skill 目录外开工作目录 `../runs/{活动名}/`——runs 与 skill 本体、mock 数据包平级：skill 是可复用的知识与流程，run 是一次场景的产物实录，两者不混装，同一套 skill 平行支撑多个活动场景。任务状态权威源是该目录下的 `ledger.json`，一切状态读写经 `scripts/ledger.py`；下一步只允许读上一步产物文件，门禁不过硬停。

## S1-S8 路由表

| 步 | 动作 | 打开什么 | 产物 | 门禁 |
|----|------|---------|------|------|
| S1 诉求澄清 | 只问业务四问 | `references/intake-questions.md` | `01-活动画像.md` | `scripts/check_brief.py` |
| S2 信息装载 | 按信息量地图定位信息件：静态直接装载，动态按取数口径生成索取清单，用户只补数确认；使用者无法直查系统时，由使用者提供数据包路径装载，信息底座逐条标注来源与时点 | `references/info-sources/`（先读 README） | `02-信息底座.md` | `scripts/check_context.py` |
| S3 玩法选型与规则设计 | 四步法：指标倒查玩法库→触发规则结构化→基本规则逐项→互斥扫描 | `references/rule-design-guide.md` + `references/playbooks/` + `references/assets-toolbox.md` | `03-活动规则.md` | `scripts/check_rules.py` |
| S4 逆向与风控 | 场景清单逐项过+结构性判据 | `references/reverse-checklist.md` | `04-逆向方案.md` | `scripts/check_reverse.py` |
| S5 曝光动线 | 触点×用户状态矩阵逐点设计 | `references/exposure-touchpoints.md` | `05-曝光动线.md` | 触点覆盖率校验（并入 check_experiment） |
| S6 成本与实验 | 成本公式化+实验点盘点+分轮计划 | `references/experiment-guide.md` | `06-成本与实验.md` | `scripts/check_experiment.py` |
| S7 方案汇编与审查 | 按模板汇编+审查清单过审（生成与审查分离） | `references/templates/方案模板.md` + `references/methodology.md` | `07-产品方案.md`、`08-决策点汇报表.md`、`09-审查报告.md` | `scripts/check_final.py` |
| S8 方案可视化 | 代码渲染，不改内容 | `scripts/render_report.py` + `references/templates/report-template.html` | `10-方案可视化.html` | 渲染成功+区块齐全 |

## 纪律

- 判断权留人：S2 信息确认、S7 决策点汇报表的请示项由使用者/mentor 拍板，skill 不替答；
- 每条信息有出处，每个数字有公式或来源；杠杆参数一律留实验位；
- examples 参照 few-shot，但禁止照抄案例参数——参数从当前诉求的信息底座推。
