# 大数据招聘岗位数据分析

**从 4,100 条带脏值的招聘原始数据，到 4 条可立刻执行的求职结论。**

一个完整的数据分析闭环：数据质量诊断 → 清洗 → 口径定义 → 分组聚合 → 四维可视化 → 业务落地。

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-11557C)
![Rows](https://img.shields.io/badge/清洗后样本-3%2C498%20%E6%9D%A1-2E5F8A)
![License](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF-%E4%BB%85%E7%94%A8%E4%BA%8E%E6%B1%82%E8%81%8C%E5%B1%95%E7%A4%BA-lightgrey)

> 作者：大数据技术专业（专科）大三在读 · 目标岗位：数据助理 / 初级数据分析 / 大数据开发助理

---

## 导航

| 内容 | 入口 |
|---|---|
| 📘 项目完整报告（六章 + 简历版描述） | [REPORT.md](REPORT.md) |
| 🌐 在线作品集（GitHub Pages） | <https://gentle-tj.github.io/job-analysis/> |
| 📥 PDF 版报告（14 页） | [assets/report_full.pdf](assets/report_full.pdf) |
| 📊 可视化专题（方案设计 · 口径检验） | [docs/visual-analysis.md](docs/visual-analysis.md) |
| 🗂 清洗后主表 | [data/clean_jobs_3498.csv](data/clean_jobs_3498.csv) |

---

## 这个项目解决什么问题

作为专科大三学生第一次面对招聘市场，有三个很具体的问题：

1. **我这个学历，实际能投的岗位有多少？**
2. **该按什么顺序补技能？** 「做数据先学 Python」是普遍说法，但市场优先要什么，没人给基于数据的答案。
3. **我锁定的目标地域（川渝），机会量够不够？**

与其凭感觉海投，不如先把市场数据化。

**数据**：和鲸社区公开招聘数据集（全国「大数据开发」方向岗位，2022-11 快照，4,100 行 × 15 字段，44 类职位、69 家公司）
**技术栈**：Python · Pandas · NumPy · Matplotlib

---

## 清洗做了什么

| 环节 | 处理方式 | 结果 |
|---|---|---|
| 去重 | 整行去重 602 条；再用业务主键二次校验（剩 3 条，JD 不同故保留）。**不按「公司+职位名」去重**，否则会错删到 77 条 | 4,100 → **3,498** |
| 缺失回填 | 用 100% 可解析的 `地区经验学历` 结构化列回填，而非 `dropna` | 学历缺失 476 → **0**，经验 475 → 1 |
| 脏值清洗 | 合法枚举白名单过滤混入的发布日期串（如「11-16发布」），统一转义符 | 枚举干净 |
| 类型转换 | 解析「8千-1.2万」「15-20万/年」「1.5-2万·13薪」等 6 类写法 → 月薪下限/上限/中点 | 薪酬可用率 **98.0%** |
| 异常值 | 领域兜底剔除单位错误（实测触发 0 条）+ IQR 诊断，363 条离群高薪**保留不删** | 保留真实薪资上限 |

---

## 四条核心结论

| 结论 | 数据支撑 |
|---|---|
| **学历卡「入场券」，不卡「工资条」** | 专科可投 899 条（25.7%），74.3% 岗位要求本科以上；但大专中位 11,501 元 vs 本科 12,001 元，仅差 500 元 |
| **川渝要主攻成都、保留异地** | 成都 184 条（全国第 6）、重庆 78 条（第 11），川渝合计仅 7.5%；「大专 + 无需经验」全川渝只有 **6 条** |
| **技能优先级 SQL > Java > Python** | SQL 覆盖率 40%、Java 39%（剔除 JavaScript 误命中后 34%）、数据分析 29%、**Python 仅 22%** |
| **用项目把经验栏从 0 填到 1** | 要求 3 年以上经验占 61.5%，应届友好岗仅 9.1%；「1 年经验」段 469 条（大专 158 条）是平衡点 |

---

## 图表

**图 1｜各学历要求岗位数量与薪资中位数**

![各学历岗位数量与薪资中位数](assets/vis_edu.png)

**图 2｜岗位数量 Top12 城市（川渝高亮）**

![Top12 城市岗位数量](assets/vis_city.png)

**图 3｜技能需求 Top15**

![技能需求 Top15](assets/vis_skill.png)

**图 4｜经验要求分布与学历构成**

![经验要求分布与学历构成](assets/vis_exp.png)

每张图的图表说明、读图结论与局限说明见 [完整报告](REPORT.md)。

---

## 几个关键判断

数据分析的价值不只在代码，更在这些判断：

- **缺失值回填优于删除。** 直接删掉 11.6% 的行，丢的恰好是信息维护差的小公司，样本会系统性偏向大企业。
- **去重必须锚定业务定义。** 按「公司 + 职位名」去重会把 3,498 条压成 77 条——同一家公司的「大数据开发工程师」重复上千次。锚点是「一条记录 = 一次岗位发布」。
- **IQR 是诊断工具，不是清洗指令。** 363 条超上界的记录全是两三万以上的真实高薪岗，删掉等于人为压掉薪资天花板。
- **技能词频做了口径稳健性检验。** 中文 JD 无词边界，正则 `\b` 实测命中 0 条，只能子串匹配，导致 `NoSQL` 命中 SQL、`JavaScript` 命中 Java（192 条）。严格口径下 SQL 1,338 / Java 1,184，**排序不变、优势更明显**。
- **图 1 刻意不做双轴。** 两组薪资只差 500 元，若用截断右轴画，视觉上会放大成数倍的假溢价。Y 轴只放岗位数，薪资用柱内数字标注。

---

## 仓库结构

```
.
├── README.md                        # 仓库首页（本文件）
├── REPORT.md                        # 完整项目报告（GitHub 直接阅读）
├── index.md                         # GitHub Pages 站点首页
├── _config.yml                      # Jekyll 站点配置
├── docs/
│   ├── project-report.md            # 报告（Pages 排版版）
│   └── visual-analysis.md           # 可视化专题（方案 + 口径检验）
├── src/
│   ├── bigdata_job_clean_eda.py     # 清洗 + EDA 脚本
│   └── job_visualization.py         # 四图绘制脚本
├── assets/
│   ├── vis_edu.png                  # 图1 学历 × 岗位数 × 薪资
│   ├── vis_city.png                 # 图2 城市 Top12
│   ├── vis_skill.png                # 图3 技能 Top15
│   ├── vis_exp.png                  # 图4 经验 × 学历构成
│   └── report_full.pdf              # 报告 PDF（14 页）
└── data/
    └── clean_jobs_3498.csv          # 清洗后主表（3,498 × 19）
```

---

## 快速开始

```bash
git clone https://github.com/gentle-tj/job-analysis.git
cd job-analysis

pip install pandas numpy matplotlib

# 复现四张图（仓库内已附清洗后数据）
python src/job_visualization.py data/clean_jobs_3498.csv charts

# 从头复现清洗（需自备原始 job_all.csv）
python src/bigdata_job_clean_eda.py job_all.csv clean_output
```

> 原始 `job_all.csv` 未纳入仓库（体积与授权原因）；`data/clean_jobs_3498.csv` 为清洗结果，可直接复现全部图表与统计数字。

---

## 局限性与边界

1. **样本是主题垂直切片**：44 类职位、69 家公司，`大数据开发工程师` 单一名称占 36.3%，技能词频会被模板化 JD 放大，不能外推为「全国大数据岗位需求」。
2. **单时间点快照**：数据集中在 2022-11，不支持趋势类结论。
3. **薪资离散化严重**：薪酬由区间报价换算，各分组中位数差异普遍小于一个报价档，只做「量级相当」的表述。
4. **技能词频为子串匹配**：存在误命中，已做严格口径检验，根本解法是分词 + 同义词归并。
5. **川渝子样本极小**：成都 184 条、重庆 78 条，「大专 + 无需经验」仅 6 条，三重交叉仅作方向参考。

所有结论限定在「2022 年 11 月、大数据开发方向、本数据集覆盖范围内」。这些局限写在报告里，而不是藏在脚注。

---

## 联系方式

- GitHub：[gentle-tj](https://github.com/gentle-tj)
- 在线作品集：<https://gentle-tj.github.io/job-analysis/>

> 数据均来自公开渠道，仅用于能力展示与技术交流。
