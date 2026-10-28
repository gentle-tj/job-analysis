---
layout: default
title: 大数据招聘岗位数据分析
---

# 大数据招聘岗位数据分析

**求职者画像聚类与求职竞争力分析** · 基于 12,000 条 Kaggle 招聘候选人数据

技术栈：Python (Pandas) · MySQL · Scikit-learn (K-Means) · ECharts

---

## 项目一句话

从「数据清洗 → MySQL 入库 → EDA → K-Means 聚类 → ECharts 可视化」完整跑通数据分析闭环，核心结论：**期望薪资与工作年限几乎不相关（r = 0.003）**，四类聚类画像给出求职者分层视角。

## 核心发现

- 期望薪资与工作年限 Pearson 相关系数 **r = 0.003**；0–2 年组与 10 年以上组期望月薪中位分别为 **43,430 元 / 43,060 元**，基本持平；同一经验段内薪资跨度可达 **6 倍**。
- K-Means（K=4）识别四类人群：高薪预期组（3,030 人）、低薪预期组（2,986 人）、低经验高分组（2,968 人）、资深高分组（3,016 人）。
- 六类学历占比 16.0%–17.9%、Top10 城市 9.5%–10.5%，分布接近均匀（数据为均衡采样，结论已限定样本范围）。

## 聚类散点图（K=4）

![聚类散点图](assets/chart_cluster_scatter.png)

## 查看完整内容

- 📊 **[大数据岗位招聘信息可视化分析（3,498 条清洗数据 · 4 张图表 + 4 条求职结论）](docs/visual-analysis.md)** ← 新增
- 📄 [完整项目报告（含 6 张图表与全部解读）](docs/report.md)
- 🧮 [清洗与 EDA 脚本](src/bigdata_job_clean_eda.py) · [可视化绘图脚本](src/job_visualization.py)
- 📊 [分析主数据集 data_cleaned.csv](data/data_cleaned.csv)
- 📌 [聚类结果 candidate_kmeans_result.csv](data/candidate_kmeans_result.csv)

> 本项目为求职作品集内容，数据与结论均可复现，欢迎交流。
