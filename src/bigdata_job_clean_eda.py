# -*- coding: utf-8 -*-
"""
大数据招聘岗位数据分析 —— 数据清洗 + EDA 探索性分析（pandas）
=================================================================
适用数据：和鲸社区公开数据集 job_all.csv（全国"大数据开发"类岗位，2022-11 快照）
运行方式：
    python bigdata_job_clean_eda.py [数据路径] [输出目录]
    不传参时默认读取本脚本同目录下的 job_all.csv，并把产物也写到同目录。
依赖：pandas, numpy（jieba 为可选的技能词频增强，未安装时自动跳过）。
说明：本脚本只做清洗与分析，不删除任何原始数据；所有中间结果写新文件。
"""

import os
import sys
import re
import ast
import warnings
import numpy as np
import pandas as pd

# 屏蔽读取含反斜杠的公开数据文本时触发的一次性 SyntaxWarning（不影响计算）
warnings.filterwarnings("ignore", category=SyntaxWarning)

# ------------------------------------------------------------------
# 0. 路径与参数
# ------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "job_all.csv")
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else BASE
os.makedirs(OUT_DIR, exist_ok=True)


def section(title):
    """打印分段标题，方便运行后核对每一步输出。"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ==================================================================
# 1. 读取原始数据
# ==================================================================
section("1. 读取原始数据")
raw = pd.read_csv(DATA_PATH)
print(f"原始记录数：{len(raw)}，字段数：{raw.shape[1]}")
print("原始字段：", list(raw.columns))

df = raw.copy()


# ==================================================================
# 2. 去重
# ==================================================================
section("2. 去重")
# 2.1 整行完全重复
n_before = len(df)
df = df.drop_duplicates()
print(f"整行去重：移除 {n_before - len(df)} 条，剩余 {len(df)} 条")

# 2.2 业务主键去重：同一公司 + 同一职位 + 同一描述 + 同一发布时间，视为同一条重复发布
key = ["公司名称", "职位名称", "职位描述或任职要求", "发布时间"]
n_before = len(df)
df = df.drop_duplicates(subset=key, keep="first")
print(f"主键去重（{key}）：再移除 {n_before - len(df)} 条，剩余 {len(df)} 条")


# ==================================================================
# 3. 解析"地区经验学历"列 —— 回填缺失 + 派生城市/区县
#    该列是 JSON 风格列表字符串：["城市-区县", "工作经验", "学历"]
#    实测 100% 可解析，可完整回填缺失的经验与学历。
# ==================================================================
section("3. 解析地区经验学历（回填缺失、派生城市）")
# 经验取值白名单与有序数值映射（在清洗前先定义，供步骤 3 判定脏值）
EXP_MAP = {
    "无需经验": 0, "经验不限": 0, "在校生/应届生": 0, "1年以下": 0.5, "1年经验": 1,
    "2年经验": 2, "3-4年经验": 3.5, "3-5年经验": 4, "5-7年经验": 6,
    "8-9年经验": 8.5, "5-10年经验": 7.5, "10年以上经验": 10,
}
VALID_EXP = set(EXP_MAP.keys())

def parse_list(s):
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) and len(v) == 3 else None
    except Exception:
        return None

parsed = df["地区经验学历"].apply(parse_list)
print(f"解析失败行数：{parsed.isna().sum()}（应为 0）")

df["城市地区"] = df["城市地区"].fillna(parsed.apply(lambda x: x[0] if x else None))   # 回填城市地区缺失
df["工作经验_回填"] = parsed.apply(lambda x: x[1] if x else None)
df["学历_回填"] = parsed.apply(lambda x: x[2] if x else None)

# 工作经验：原值缺失 → 用回填值补足
# 工作经验：原值若为脏值（如混入的"大专""10-12发布"）先置空，再用回填值补足
df["工作经验要求"] = df["工作经验要求"].apply(lambda v: v if v in VALID_EXP else np.nan)
df["工作经验要求"] = df["工作经验要求"].fillna(df["工作经验_回填"])

# 学历：原值若为脏值（如"11-16发布"）先置空，再用回填值补足
VALID_EDU = {"初中及以下", "高中", "中技/中专", "大专", "本科", "硕士", "博士"}
df["学历要求"] = df["学历要求"].apply(lambda v: v if v in VALID_EDU else np.nan)
df["学历要求"] = df["学历要求"].fillna(df["学历_回填"])

# 派生城市（取"城市-区县"的第一段）与区县（第二段，可能为空）
df["城市"] = df["城市地区"].str.split("-").str[0]
df["区县"] = df["城市地区"].str.split("-").str[1]

# 工作地点缺失时，用"城市-区县"兜底，保证后续地域分析有值
df["工作地点"] = df["工作地点"].fillna(df["城市地区"])

print(f"回填后 工作经验要求 缺失：{df['工作经验要求'].isna().sum()}")
print(f"回填后 学历要求 缺失：{df['学历要求'].isna().sum()}")
print(f"回填后 城市 缺失：{df['城市'].isna().sum()}")


# ==================================================================
# 4. 缺失值处理（剩余字段）
# ==================================================================
section("4. 缺失值处理")
# 学历/经验回填后仍缺的记为"未注明"，便于分组统计时不丢行
df["学历要求"] = df["学历要求"].fillna("未注明")
df["工作经验要求"] = df["工作经验要求"].fillna("未注明")
# 公司规模/类型/福利/职位描述缺失统一记为"未注明"
for col in ["公司规模", "公司类型", "公司福利", "职位描述或任职要求"]:
    df[col] = df[col].fillna("未注明")

print("清洗后各列缺失数：")
print(df.isna().sum()[df.isna().sum() > 0] if df.isna().sum().sum() else "（无缺失）")


# ==================================================================
# 5. 字段类型转换
# ==================================================================
section("5. 字段类型转换")

# 5.1 发布时间：字符串 ->  datetime
df["发布时间"] = pd.to_datetime(df["发布时间"], format="%Y/%m/%d %H:%M", errors="coerce")

# 5.2 薪酬：混乱文本 ->  月薪下限 / 上限 / 中点（单位：元/月）
def parse_salary(text):
    """把 '8千-1.6万' / '12-20万/年' / '1.5-2.5万·13薪' 等统一换算成 元/月。"""
    if pd.isna(text):
        return (np.nan, np.nan)
    s = str(text).strip()
    annual = "年" in s                  # 含"年"视为年薪，最终 ÷12
    core = s.split("·")[0]              # 去掉 "·13薪" 这类附加说明
    parts = re.split(r"[-~—]", core)    # 按区间分隔符拆分上/下限

    def conv(p):
        p = p.strip()
        if not p:
            return np.nan
        m = re.search(r"\d+(?:\.\d+)?", p)
        if not m:
            return np.nan
        num = float(m.group())
        if "千" in p:
            return num * 1000
        if "万" in p:
            return num * 10000
        if annual:                      # 含"年"且无显式单位（如"12-20万/年"的前段"12"）
            return num * 10000
        return num                      # 兜底按"元"

    lo = conv(parts[0])
    hi = conv(parts[-1]) if len(parts) > 1 else lo
    if annual:
        lo, hi = lo / 12.0, hi / 12.0
    return (lo, hi)

sal = df["薪酬"].apply(parse_salary)
df["月薪下限"] = sal.apply(lambda x: x[0])
df["月薪上限"] = sal.apply(lambda x: x[1])
df["月薪中点"] = (df["月薪下限"] + df["月薪上限"]) / 2.0
print(f"薪酬解析失败（仍为 NaN）：{df['月薪中点'].isna().sum()} 条")

# 5.3 工作经验 ->  有序数值（便于按资历排序与分组）
df["经验年限"] = df["工作经验要求"].map(EXP_MAP)   # 未知/未注明 -> NaN

# 5.4 学历 ->  有序类别（大专是本项目关注层次，放在中间便于观察）
EDU_ORDER = ["初中及以下", "高中", "中技/中专", "大专", "本科", "硕士", "博士", "未注明"]
df["学历要求"] = pd.Categorical(df["学历要求"], categories=EDU_ORDER, ordered=True)


# ==================================================================
# 6. 异常值处理（薪酬）
# ==================================================================
section("6. 异常值处理")
salary = df["月薪中点"].dropna()
q1, q3 = salary.quantile(0.25), salary.quantile(0.75)
iqr = q3 - q1
lo_fence, hi_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
# 统计洞察：IQR 栅栏外的"异常"多为高薪长尾（右偏正常），只标记、不删除、不剔除统计
df["薪酬_IQR异常"] = (df["月薪中点"] < lo_fence) | (df["月薪中点"] > hi_fence)
# 领域可信性：月薪明显不合常理（<1000 或 >200000 元/月）才从薪资统计中排除
df["薪酬_异常"] = (df["月薪中点"] < 1000) | (df["月薪中点"] > 200000)
print(f"月薪中点 IQR 栅栏：[{lo_fence:,.0f}, {hi_fence:,.0f}] 元/月")
print(f"统计性离群（IQR 1.5 倍外，多为高薪长尾）：{int(df['薪酬_IQR异常'].sum())} 条（仅洞察，保留）")
print(f"领域不可信、剔除出薪资统计（<1000 或 >200000）：{int(df['薪酬_异常'].sum())} 条")


# ==================================================================
# 7. 保存清洗结果
# ==================================================================
section("7. 保存清洗结果")
keep_cols = [
    "职位名称", "公司名称", "城市", "区县", "工作地点", "城市地区",
    "学历要求", "工作经验要求", "经验年限", "公司规模", "公司类型", "公司福利",
    "薪酬", "月薪下限", "月薪上限", "月薪中点", "薪酬_异常",
    "发布时间", "职位描述或任职要求",
]
clean = df[keep_cols].copy()
clean_path = os.path.join(OUT_DIR, "cleaned_jobs.csv")
clean.to_csv(clean_path, index=False, encoding="utf-8-sig")
print(f"已保存清洗后数据：{clean_path}（{len(clean)} 行）")


# ==================================================================
# 8. 探索性分析（描述统计 + 分组统计 + 技能词频）
# ==================================================================
section("8.1 描述统计：整体概况")
print(f"清洗后样本量：{len(clean)}")
print("\n字段完整度（缺失率）：")
miss = (clean.isna().mean() * 100).round(2)
print(miss[miss > 0] if miss.sum() else "（核心字段无缺失）")

print("\n薪酬（元/月，已排除领域不可信值）描述统计：")
valid_sal = clean.loc[clean["月薪中点"].notna() & ~clean["薪酬_异常"], "月薪中点"]
print(valid_sal.describe(percentiles=[.1, .25, .5, .75, .9]).round(0))

print("\n学历分布：")
print(clean["学历要求"].value_counts(dropna=False))
print("\n工作经验分布：")
print(clean["工作经验要求"].value_counts(dropna=False))
print("\n招聘需求 Top15 城市：")
print(clean["城市"].value_counts().head(15))
print("\n公司规模分布：")
print(clean["公司规模"].value_counts())
print("\n公司类型分布：")
print(clean["公司类型"].value_counts())
print("\n岗位细分 Top15（职位名称）：")
print(clean["职位名称"].value_counts().head(15))


def salary_by(col, top=None, sort_by_count=False):
    """通用分组薪资统计：中位数 / 均值 / 样本量。"""
    valid = clean["月薪中点"].notna() & ~clean["薪酬_异常"]
    g = clean.loc[valid].groupby(col, observed=True)["月薪中点"]
    out = pd.DataFrame({"薪资中位数": g.median(), "薪资均值": g.mean(), "岗位数": g.count()})
    out = out.round(0)
    if top:
        out = out.sort_values("岗位数", ascending=False).head(top) if sort_by_count else out
    return out

section("8.2 分组统计：业务维度对比")
print("\n(1) 学历 × 薪资（中位数/均值/岗位数）：")
edu_tbl = salary_by("学历要求").sort_values("薪资中位数", ascending=False)
print(edu_tbl)

print("\n(2) 工作经验 × 薪资（按经验年限排序）：")
exp_tbl = salary_by("工作经验要求")
exp_tbl = exp_tbl.reindex(clean.dropna(subset=["经验年限"])["工作经验要求"].value_counts().index)
print(exp_tbl)

print("\n(3) 城市 × 薪资/岗位数（Top15 需求城市）：")
city_tbl = salary_by("城市", top=15, sort_by_count=True)
print(city_tbl)

print("\n(4) 公司规模 × 薪资/岗位数：")
scale_tbl = salary_by("公司规模")
print(scale_tbl)

print("\n(5) 学历 × 工作经验 交叉（岗位数，透视表）—— 重点关注「大专」行：")
pivot = pd.pivot_table(
    clean, index="学历要求", columns="工作经验要求",
    values="职位名称", aggfunc="count", observed=True, fill_value=0,
).reindex(columns=clean["工作经验要求"].value_counts().index)
print(pivot)

print("\n(6) 岗位细分 × 平均薪资（Top15，按平均薪资排序）：")
job_tbl = salary_by("职位名称")
job_tbl = job_tbl[job_tbl["岗位数"] >= 10].sort_values("薪资中位数", ascending=False).head(15)
print(job_tbl)


# 8.3 技能需求词频（基于职位描述的关键词命中，无需 jieba）
section("8.3 技能需求词频（职位描述关键词命中）")
SKILLS = ["hadoop", "hive", "spark", "flink", "kafka", "python", "java", "sql",
          "hbase", "storm", "elasticsearch", "kylin", "zookeeper", "linux",
          "shell", "scala", "docker", "kubernetes", "etl", "数据仓库", "数仓", "数据分析"]
desc = clean["职位描述或任职要求"].astype(str).str.lower()
skill_count = {s: int(desc.str.contains(s, regex=False).sum()) for s in SKILLS}
skill_tbl = pd.DataFrame(
    {"技能": list(skill_count.keys()), "命中职位描述数": list(skill_count.values())}
).sort_values("命中职位描述数", ascending=False)
print(skill_tbl.to_string(index=False))
skill_path = os.path.join(OUT_DIR, "skill_frequency.csv")
skill_tbl.to_csv(skill_path, index=False, encoding="utf-8-sig")
print(f"已保存技能词频：{skill_path}")

# 8.4 保存分组结果便于做图
for name, tbl in [("salary_by_edu", edu_tbl), ("salary_by_city", city_tbl),
                  ("salary_by_scale", scale_tbl), ("salary_by_job", job_tbl)]:
    tbl.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), encoding="utf-8-sig")

print("\n全部步骤完成。核对以上输出后，即可用分组 CSV 在 Excel / Power BI / ECharts 中出图。")
