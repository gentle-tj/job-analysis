# -*- coding: utf-8 -*-
"""
大数据招聘岗位数据集 —— 可视化出图脚本
================================================
输入：bigdata_job_clean_eda.py 产出的 cleaned_jobs.csv（清洗后 3,498 行 × 19 列）
输出：charts/ 目录下 4 张 PNG + 控制台打印的关键数字（用于核对图表与结论）

用法：
    python job_visualization.py
    python job_visualization.py cleaned_jobs.csv 我的图表目录

四张图：
    图1  学历要求：岗位数量 + 薪资中位数（双轴组合图）
    图2  城市 Top12：岗位数量 + 薪资中位数（横向条形图，川渝高亮）
    图3  技能需求 Top15（横向条形图）
    图4  经验要求分布 × 学历构成（堆叠柱状图）
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 非交互后端，保证无界面环境也能存图
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------- 0. 中文与字体
# Windows 下 matplotlib 默认字体不含中文，不做这三行设置图形里的中文会全是"豆腐块"
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False   # 负号正常显示（否则会显示成方框）
plt.rcParams["figure.dpi"] = 120             # 屏幕预览清晰度
plt.rcParams["savefig.dpi"] = 200            # 存图清晰度（作品集网页用 200 足够）
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.linewidth"] = 0.8

# ---------------------------------------------------------------- 1. 配色
C_MAIN = "#2E5F8A"      # 主色：深蓝
C_ACCENT = "#E07A5F"    # 强调色：暖橙
C_HL = "#C0392B"        # 高亮色：川渝
C_GRAY = "#95A5A6"      # 次要：灰
C_LIGHT = "#A8C4DC"
BG = "#FFFFFF"


def fmt_money(x, _pos=None):
    """坐标轴金额格式：12000 -> 1.2万"""
    return f"{x/10000:.1f}万"


# ---------------------------------------------------------------- 2. 读数据
def load(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["月薪中点"] = pd.to_numeric(df["月薪中点"], errors="coerce")
    # 清洗阶段只"标记"异常值，这里沿用同一口径：剔除被标记的、以及领域上明显错误的值
    if "薪酬_异常" in df.columns:
        bad = df["薪酬_异常"].fillna(False).astype(bool)
        df.loc[bad, "月薪中点"] = np.nan
    df.loc[(df["月薪中点"] < 1000) | (df["月薪中点"] > 200000), "月薪中点"] = np.nan
    # 脏值合并："在校生\\/应届生" 与 "在校生/应届生" 是同一种值，被转义符拆成了两类
    df["工作经验要求"] = (df["工作经验要求"].astype(str)
                                      .str.replace("\\/", "/", regex=False))
    # 学历分档：专科 / 本科 / 其他（硕士、博士、中技、高中、初中）
    df["学历分档"] = np.where(df["学历要求"] == "大专", "大专",
                     np.where(df["学历要求"] == "本科", "本科", "其他"))
    return df


def section(t):
    print("\n" + "=" * 62)
    print(t)
    print("=" * 62)


# ---------------------------------------------------------------- 图1 学历
def fig_edu(df, out):
    """图1：各学历要求的岗位数量（柱）+ 薪资中位数（右轴折线）"""
    order = ["本科", "大专", "硕士", "博士", "中技/中专", "高中", "初中及以下"]
    g = (df.groupby("学历要求")
           .agg(岗位数=("学历要求", "size"), 薪资中位数=("月薪中点", "median"))
           .reindex(order))
    total = len(df)
    share = g["岗位数"] / total * 100

    # 设计说明：这里刻意不做"柱+右轴折线"的双轴图。
    # 本数据薪酬是区间报价（如「15-20万/年」）换算的，离散化严重，各学历中位数
    # 只差 500–1000 元。若用截断的右轴去画，视觉上会放大成巨大的"学历溢价"，
    # 属于典型的图表误导；因此 Y 轴只承载岗位数，薪资中位数作为柱内数字标注呈现。
    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = np.arange(len(g))
    colors = [C_MAIN if v == "本科" else (C_ACCENT if v == "大专" else C_LIGHT)
              for v in g.index]
    ax.bar(x, g["岗位数"], width=0.58, color=colors, zorder=3)

    ymax = g["岗位数"].max()
    for xi, (cnt, sh, med) in enumerate(zip(g["岗位数"], share, g["薪资中位数"])):
        # 柱顶：岗位数与占比
        ax.text(xi, cnt + ymax * 0.02, f"{cnt:,} 条\n{sh:.1f}%", ha="center",
                va="bottom", fontsize=9, color="#333333", linespacing=1.45)
        # 柱内：薪资中位数（柱太矮时标注放到柱子上方，避免文字溢出）
        # 仅对样本量 ≥100 的学历标注薪资：博士 35、中技 27、高中 23、初中 3 条，
        # 样本太小，中位数没有统计意义，标出来只会干扰阅读。
        if cnt < 100:
            continue
        label = f"中位 {med:,.0f}"
        if cnt >= ymax * 0.16:
            ax.text(xi, cnt * 0.5, label, ha="center", va="center", fontsize=8.5,
                    color="white", fontweight="bold", rotation=90)
        else:
            ax.text(xi, cnt + ymax * 0.14, label, ha="center", va="bottom",
                    fontsize=8, color=C_HL)

    ax.set_ylabel("岗位数量（条）", fontsize=11)
    ax.set_xlabel("学历要求", fontsize=11)
    ax.set_ylim(0, ymax * 1.30)
    ax.set_xticks(x)
    ax.set_xticklabels(g.index, fontsize=10)
    ax.grid(axis="y", linestyle=":", color="#DDDDDD", zorder=0)
    ax.set_axisbelow(True)

    ax.set_title("图1  各学历要求岗位数量与薪资中位数（n=3,498）",
                 fontsize=13, fontweight="bold", pad=14)
    # 图例：用色块说明颜色含义
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=C_MAIN, label="本科（主力需求）"),
                       Patch(color=C_ACCENT, label="大专（可投池）"),
                       Patch(color=C_LIGHT, label="其他学历")],
              loc="upper right", fontsize=9, frameon=False)

    fig.text(0.012, 0.015,
             "注：柱内数字为薪资中位数。原始薪酬为区间报价，换算后离散化明显，"
             "各学历中位数差仅 0.5–1.0 千元（相当于一个报价档），不宜解读为学历溢价。",
             fontsize=7.5, color="#777777")
    fig.tight_layout(rect=[0, 0.035, 1, 1])
    p = os.path.join(out, "vis_edu.png")
    fig.savefig(p, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    section("图1 学历维度")
    print(g.assign(占比=share.round(1)).to_string())
    return g


# ---------------------------------------------------------------- 图2 城市
def fig_city(df, out, topn=12):
    """图2：城市 Top12 岗位数量（横向条形），川渝高亮并标注薪资中位数"""
    g = (df.groupby("城市")
           .agg(岗位数=("城市", "size"), 薪资中位数=("月薪中点", "median"))
           .sort_values("岗位数", ascending=False).head(topn)
           .sort_values("岗位数"))          # 横向图从下往上画，升序排列后最大值在顶部

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [C_HL if c in ("成都", "重庆") else
              (C_LIGHT if c not in ("上海", "广州", "深圳", "北京") else C_MAIN)
              for c in g.index]
    bars = ax.barh(np.arange(len(g)), g["岗位数"], height=0.66, color=colors, zorder=3)

    for i, (city, cnt, med) in enumerate(zip(g.index, g["岗位数"], g["薪资中位数"])):
        label = f"{cnt} 条"
        if pd.notna(med):
            label += f"    中位 {med:,.0f}"
        ax.text(cnt + 8, i, label, va="center", fontsize=9,
                color=C_HL if city in ("成都", "重庆") else "#333333",
                fontweight="bold" if city in ("成都", "重庆") else "normal")

    ax.set_yticks(np.arange(len(g)))
    ax.set_yticklabels(g.index, fontsize=10)
    for tick, city in zip(ax.get_yticklabels(), g.index):
        if city in ("成都", "重庆"):
            tick.set_color(C_HL)
            tick.set_fontweight("bold")

    ax.set_xlabel("岗位数量（条）", fontsize=11)
    # 不设 ylabel：城市名本身就是刻度标签，再加"城市"二字会与标签挤在一起
    ax.set_xlim(0, g["岗位数"].max() * 1.30)
    ax.grid(axis="x", linestyle=":", color="#DDDDDD", zorder=0)
    ax.set_axisbelow(True)

    cq_cy = int(df[df["城市"].isin(["成都", "重庆"])].shape[0])
    ax.set_title(f"图2  岗位数量 Top{topn} 城市（n=3,498）", fontsize=13,
                 fontweight="bold", pad=14)
    ax.text(0.99, 0.03,
            f"川渝合计 {cq_cy} 条，占全国样本 {cq_cy/len(df)*100:.1f}%\n"
            f"（成都第 {list(g.sort_values('岗位数', ascending=False).index).index('成都')+1}、"
            f"重庆第 {list(g.sort_values('岗位数', ascending=False).index).index('重庆')+1}）",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color=C_HL,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#FDF2EE",
                      edgecolor=C_HL, linewidth=0.8))

    fig.tight_layout()
    p = os.path.join(out, "vis_city.png")
    fig.savefig(p, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    section("图2 城市维度")
    print(g.sort_values("岗位数", ascending=False).to_string())
    print(f"川渝合计：{cq_cy} 条")
    return g


# ---------------------------------------------------------------- 图3 技能
def fig_skill(df, out, topn=15):
    """图3：技能关键词需求 Top15（横向条形，按命中职位描述数排序）"""
    # 技能词典与 bigdata_job_clean_eda.py 保持一致
    SKILLS = ["sql", "java", "数据分析", "python", "hadoop", "linux", "spark", "hive",
              "kafka", "hbase", "数据仓库", "flink", "etl", "shell", "scala", "docker",
              "elasticsearch", "storm", "zookeeper", "数仓", "kubernetes", "kylin"]
    text = df["职位描述或任职要求"].fillna("").str.lower()
    hits = {k: int(text.str.contains(k.lower(), regex=False).sum()) for k in SKILLS}
    s = pd.Series(hits).sort_values(ascending=False).head(topn).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6.4))
    # 按需求强度做深浅渐变，视觉上区分"必学"和"加分项"
    cmap = plt.cm.Blues
    norm = (s - s.min()) / (s.max() - s.min() + 1e-9)
    colors = [cmap(0.32 + 0.55 * v) for v in norm]

    ax.barh(np.arange(len(s)), s.values, height=0.68, color=colors, zorder=3)
    for i, (k, v) in enumerate(zip(s.index, s.values)):
        ax.text(v + 14, i, f"{v}  ({v/len(df)*100:.0f}%)", va="center",
                fontsize=9, color="#333333")

    ax.set_yticks(np.arange(len(s)))
    ax.set_yticklabels([k.upper() if k.isascii() else k for k in s.index], fontsize=10)
    ax.set_xlabel("提及该技能的职位描述数（条）", fontsize=11)
    ax.set_ylabel("技能关键词", fontsize=11)
    ax.set_xlim(0, s.max() * 1.22)
    ax.grid(axis="x", linestyle=":", color="#DDDDDD", zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(f"图3  技能需求 Top{topn}（n=3,498，括号内为岗位覆盖率）",
                 fontsize=13, fontweight="bold", pad=14)
    fig.tight_layout()
    p = os.path.join(out, "vis_skill.png")
    fig.savefig(p, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    section("图3 技能维度")
    print(pd.Series(hits).sort_values(ascending=False).to_string())
    return s


# ---------------------------------------------------------------- 图4 经验
def fig_exp(df, out):
    """图4：经验要求分布（堆叠柱，按学历构成拆分）"""
    # 经验段归并：把冗长的原始枚举压成 6 段，便于阅读
    EXP_ORDER = ["无需经验", "1年经验", "2年经验", "3-4年经验", "5-7年经验", "8年以上"]
    exp_map = {
        "无需经验": "无需经验", "在校生/应届生": "无需经验", "1年以下": "无需经验",
        "1年经验": "1年经验", "2年经验": "2年经验", "3-4年经验": "3-4年经验",
        "3-5年经验": "3-4年经验", "5-7年经验": "5-7年经验", "5-10年经验": "5-7年经验",
        "8-9年经验": "8年以上", "10年以上经验": "8年以上",
    }
    d = df.copy()
    d["经验段"] = d["工作经验要求"].map(exp_map)
    d = d[d["经验段"].notna()]
    ct = (pd.crosstab(d["经验段"], d["学历分档"])
            .reindex(EXP_ORDER)
            .reindex(columns=["大专", "本科", "其他"]).fillna(0).astype(int))

    fig, ax = plt.subplots(figsize=(9, 5.4))
    x = np.arange(len(ct))
    b1 = ax.bar(x, ct["大专"], width=0.6, color=C_ACCENT, label="大专", zorder=3)
    b2 = ax.bar(x, ct["本科"], width=0.6, bottom=ct["大专"], color=C_MAIN,
                label="本科", zorder=3)
    b3 = ax.bar(x, ct["其他"], width=0.6, bottom=ct["大专"] + ct["本科"],
                color=C_GRAY, label="其他学历", zorder=3)

    totals = ct.sum(axis=1)
    for xi, (tot, go, ben) in enumerate(zip(totals, ct["大专"], ct["本科"])):
        ax.text(xi, tot + 22, f"{tot} 条", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#333333")
        if go >= totals.max() * 0.03:   # 色块太薄时不写字，否则数字会溢出到柱子外面
            ax.text(xi, go / 2, f"{go}", ha="center", va="center",
                    fontsize=8.5, color="white", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(ct.index, fontsize=10)
    ax.set_ylabel("岗位数量（条）", fontsize=11)
    ax.set_xlabel("工作经验要求", fontsize=11)
    ax.set_ylim(0, totals.max() * 1.18)
    ax.grid(axis="y", linestyle=":", color="#DDDDDD", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9.5, frameon=False)

    fresh = int(totals.get("无需经验", 0))
    dazhuan_tot = int(ct["大专"].sum())
    ax.set_title("图4  经验要求分布与学历构成（n=3,498）", fontsize=13,
                 fontweight="bold", pad=14)
    ax.text(0.015, 0.94,
            f"应届友好（无需经验）仅 {fresh} 条，占 {fresh/len(d):.1%}\n"
            f"大专岗位 {dazhuan_tot} 条，其中 {ct.loc['无需经验','大专']} 条不限经验",
            transform=ax.transAxes, va="top", fontsize=9, color=C_HL,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#FDF2EE",
                      edgecolor=C_HL, linewidth=0.8))

    fig.tight_layout()
    p = os.path.join(out, "vis_exp.png")
    fig.savefig(p, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    section("图4 经验维度")
    print(ct.assign(合计=ct.sum(axis=1)).to_string())
    print(f"应届友好占比：{fresh}/{len(d)} = {fresh/len(d):.1%}")
    return ct


# ---------------------------------------------------------------- 主流程
def main():
    csv = sys.argv[1] if len(sys.argv) > 1 else "cleaned_jobs.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "charts"
    os.makedirs(out, exist_ok=True)

    df = load(csv)
    print(f"读入：{csv}")
    print(f"样本量：{len(df):,} 行；有效薪资样本：{df['月薪中点'].notna().sum():,} 行")
    print(f"薪酬覆盖率：{df['月薪中点'].notna().mean():.1%}")

    fig_edu(df, out)
    fig_city(df, out)
    fig_skill(df, out)
    fig_exp(df, out)

    print("\n" + "=" * 62)
    print(f"出图完成，4 张 PNG 已保存至：{os.path.abspath(out)}")
    print("=" * 62)


if __name__ == "__main__":
    main()
