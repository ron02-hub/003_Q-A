"""
EV走行音アンケート 統合分析スクリプト
データ分析計画書に基づく全分析を実行
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io
from datetime import datetime

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SD_AXES, SOUND_SAMPLES

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR = OUTPUT_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# データ読み込み
DATA_DIR = Path(__file__).parent.parent / "data" / "sample_data"
JSON_FILE = DATA_DIR / "sample_responses.json"
CSV_FILE = DATA_DIR / "sample_responses.csv"

print("=" * 60)
print("EV走行音アンケート データ分析")
print("=" * 60)
print(f"データファイル: {JSON_FILE}")
print(f"出力ディレクトリ: {OUTPUT_DIR}")
print()

# データ読み込み
print("[1/7] データ読み込み中...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    responses = json.load(f)

df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
print(f"  読み込み完了: {len(responses)}件の回答データ")
print()

# ============================================================================
# Layer 1: 記述統計分析
# ============================================================================
print("[2/7] Layer 1: 記述統計分析を実行中...")

# 1.1 回答者属性の集計
demographics_summary = {
    "age_group": df["age_group"].value_counts().to_dict(),
    "gender": df["gender"].value_counts().to_dict(),
    "driving_experience": df["driving_experience"].value_counts().to_dict(),
    "ev_experience": df["ev_experience"].value_counts().to_dict(),
    "sound_sensitivity": {
        "mean": float(df["sound_sensitivity"].mean()),
        "std": float(df["sound_sensitivity"].std()),
        "min": int(df["sound_sensitivity"].min()),
        "max": int(df["sound_sensitivity"].max()),
    }
}

# 1.2 SD法評価の集計
sd_summary = {}
for sample_id in SOUND_SAMPLES:
    sd_summary[sample_id] = {}
    for axis in SD_AXES:
        col_name = f"sd_{sample_id}_{axis['id']}"
        if col_name in df.columns:
            sd_summary[sample_id][axis["id"]] = {
                "mean": float(df[col_name].mean()),
                "std": float(df[col_name].std()),
                "min": int(df[col_name].min()),
                "max": int(df[col_name].max()),
            }

# 1.3 購買意欲・WTPの集計
purchase_summary = {}
wtp_summary = {}
for sample_id in SOUND_SAMPLES:
    intent_col = f"purchase_intent_{sample_id}"
    wtp_col = f"wtp_{sample_id}"
    
    if intent_col in df.columns:
        purchase_summary[sample_id] = {
            "mean": float(df[intent_col].mean()),
            "std": float(df[intent_col].std()),
            "distribution": df[intent_col].value_counts().to_dict(),
        }
    
    if wtp_col in df.columns:
        wtp_summary[sample_id] = df[wtp_col].value_counts().to_dict()

print("  記述統計分析完了")
print()

# ============================================================================
# Layer 2: 比較分析
# ============================================================================
print("[3/7] Layer 2: 比較分析を実行中...")

# 2.1 サンプル間比較（SD評価）
sd_comparison = {}
for axis in SD_AXES:
    axis_id = axis["id"]
    axis_data = {}
    for sample_id in SOUND_SAMPLES:
        col_name = f"sd_{sample_id}_{axis_id}"
        if col_name in df.columns:
            axis_data[sample_id] = {
                "mean": float(df[col_name].mean()),
                "std": float(df[col_name].std()),
            }
    sd_comparison[axis_id] = axis_data

# 2.2 購買意欲比較
purchase_comparison = {}
for sample_id in SOUND_SAMPLES:
    intent_col = f"purchase_intent_{sample_id}"
    if intent_col in df.columns:
        purchase_comparison[sample_id] = {
            "mean": float(df[intent_col].mean()),
            "std": float(df[intent_col].std()),
        }

# 2.3 最良・最悪音の分析
best_worst_analysis = {
    "best_sound": df["best_sound"].value_counts().to_dict(),
    "worst_sound": df["worst_sound"].value_counts().to_dict(),
}

print("  比較分析完了")
print()

# ============================================================================
# Layer 3: 相関・因果分析
# ============================================================================
print("[4/7] Layer 3: 相関・回帰分析を実行中...")

# 3.1 SD軸間相関（Priusを例に）
correlation_matrix = {}
for sample_id in SOUND_SAMPLES:
    axis_cols = [f"sd_{sample_id}_{axis['id']}" for axis in SD_AXES]
    available_cols = [col for col in axis_cols if col in df.columns]
    if available_cols:
        corr = df[available_cols].corr()
        correlation_matrix[sample_id] = corr.to_dict()

# 3.2 SD評価-購買意欲相関
sd_purchase_correlation = {}
for sample_id in SOUND_SAMPLES:
    intent_col = f"purchase_intent_{sample_id}"
    if intent_col in df.columns:
        axis_corrs = {}
        for axis in SD_AXES:
            sd_col = f"sd_{sample_id}_{axis['id']}"
            if sd_col in df.columns:
                corr = df[sd_col].corr(df[intent_col])
                axis_corrs[axis["id"]] = float(corr) if not pd.isna(corr) else 0.0
        sd_purchase_correlation[sample_id] = axis_corrs

# 3.3 購買意欲への重要度分析（相関係数の絶対値でランキング）
importance_ranking = {}
for sample_id in SOUND_SAMPLES:
    if sample_id in sd_purchase_correlation:
        corrs = sd_purchase_correlation[sample_id]
        # 絶対値でソート
        sorted_corrs = sorted(corrs.items(), key=lambda x: abs(x[1]), reverse=True)
        importance_ranking[sample_id] = [
            {"axis": axis_id, "correlation": corr, "importance": abs(corr)}
            for axis_id, corr in sorted_corrs
        ]

print("  相関・回帰分析完了")
print()

# ============================================================================
# Layer 4: セグメント分析
# ============================================================================
print("[5/7] Layer 4: セグメント分析を実行中...")

# 4.1 属性別セグメント分析
segment_analysis = {}

# 年齢層別
age_segments = {}
for age_group in df["age_group"].unique():
    age_df = df[df["age_group"] == age_group]
    age_segments[age_group] = {}
    for sample_id in SOUND_SAMPLES:
        intent_col = f"purchase_intent_{sample_id}"
        if intent_col in age_df.columns:
            age_segments[age_group][sample_id] = {
                "mean": float(age_df[intent_col].mean()),
                "count": len(age_df),
            }
segment_analysis["age_group"] = age_segments

# 性別
gender_segments = {}
for gender in df["gender"].unique():
    gender_df = df[df["gender"] == gender]
    gender_segments[gender] = {}
    for sample_id in SOUND_SAMPLES:
        intent_col = f"purchase_intent_{sample_id}"
        if intent_col in gender_df.columns:
            gender_segments[gender][sample_id] = {
                "mean": float(gender_df[intent_col].mean()),
                "count": len(gender_df),
            }
segment_analysis["gender"] = gender_segments

# EV経験別
ev_segments = {}
for ev_exp in df["ev_experience"].unique():
    ev_df = df[df["ev_experience"] == ev_exp]
    ev_segments[ev_exp] = {}
    for sample_id in SOUND_SAMPLES:
        intent_col = f"purchase_intent_{sample_id}"
        if intent_col in ev_df.columns:
            ev_segments[ev_exp][sample_id] = {
                "mean": float(ev_df[intent_col].mean()),
                "count": len(ev_df),
            }
segment_analysis["ev_experience"] = ev_segments

print("  セグメント分析完了")
print()

# ============================================================================
# Layer 5: 統合インサイト
# ============================================================================
print("[6/7] Layer 5: 統合インサイト分析を実行中...")

# 5.1 ラダリング分析
laddering_analysis = {
    "why_good": {},
    "feeling_good": {},
    "why_bad": {},
    "feeling_bad": {},
}

# ネットワーク分析用：共起関係を計算
laddering_cooccurrence = {
    "why_good_feeling_good": {},  # why_goodとfeeling_goodの共起
    "why_bad_feeling_bad": {},     # why_badとfeeling_badの共起
}

for resp in responses:
    if "grid_evaluation" in resp and "laddering_best" in resp["grid_evaluation"]:
        ladder = resp["grid_evaluation"]["laddering_best"]
        why_list = ladder.get("why_good", [])
        feeling_list = ladder.get("feeling_good", [])
        
        for reason in why_list:
            laddering_analysis["why_good"][reason] = laddering_analysis["why_good"].get(reason, 0) + 1
        for feeling in feeling_list:
            laddering_analysis["feeling_good"][feeling] = laddering_analysis["feeling_good"].get(feeling, 0) + 1
        
        # 共起関係を計算
        for why in why_list:
            for feeling in feeling_list:
                key = f"{why} → {feeling}"
                laddering_cooccurrence["why_good_feeling_good"][key] = \
                    laddering_cooccurrence["why_good_feeling_good"].get(key, 0) + 1
    
    if "grid_evaluation" in resp and "laddering_worst" in resp["grid_evaluation"]:
        ladder = resp["grid_evaluation"]["laddering_worst"]
        why_list = ladder.get("why_bad", [])
        feeling_list = ladder.get("feeling_bad", [])
        
        for reason in why_list:
            laddering_analysis["why_bad"][reason] = laddering_analysis["why_bad"].get(reason, 0) + 1
        for feeling in feeling_list:
            laddering_analysis["feeling_bad"][feeling] = laddering_analysis["feeling_bad"].get(feeling, 0) + 1
        
        # 共起関係を計算
        for why in why_list:
            for feeling in feeling_list:
                key = f"{why} → {feeling}"
                laddering_cooccurrence["why_bad_feeling_bad"][key] = \
                    laddering_cooccurrence["why_bad_feeling_bad"].get(key, 0) + 1

# ラダリング分析にネットワーク情報を追加
laddering_analysis["cooccurrence"] = laddering_cooccurrence

# 5.2 インタビュー分析
interview_analysis = {
    "sound_importance": {
        "mean": float(df["sound_importance"].mean()) if "sound_importance" in df.columns else 0.0,
        "distribution": df["sound_importance"].value_counts().to_dict() if "sound_importance" in df.columns else {},
    }
}

print("  統合インサイト分析完了")
print()

# ============================================================================
# 結果の保存
# ============================================================================
print("[7/7] 分析結果を保存中...")

analysis_results = {
    "analysis_date": datetime.now().isoformat(),
    "total_responses": len(responses),
    "layer1_descriptive": {
        "demographics": demographics_summary,
        "sd_ratings": sd_summary,
        "purchase_intent": purchase_summary,
        "wtp": wtp_summary,
    },
    "layer2_comparative": {
        "sd_comparison": sd_comparison,
        "purchase_comparison": purchase_comparison,
        "best_worst": best_worst_analysis,
    },
    "layer3_correlation": {
        "sd_axis_correlation": correlation_matrix,
        "sd_purchase_correlation": sd_purchase_correlation,
        "importance_ranking": importance_ranking,
    },
    "layer4_segmentation": segment_analysis,
    "layer5_insights": {
        "laddering": laddering_analysis,
        "interview": interview_analysis,
    },
}

# JSON保存
json_output = OUTPUT_DIR / "analysis_results.json"
with open(json_output, "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2)

print(f"  JSON保存完了: {json_output}")

# Excel保存（主要結果をテーブル形式で）
excel_output = OUTPUT_DIR / "analysis_results.xlsx"
with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
    # 回答者属性
    pd.DataFrame([demographics_summary]).to_excel(writer, sheet_name="回答者属性", index=False)
    
    # SD評価サマリー
    sd_data = []
    for sample_id in SOUND_SAMPLES:
        for axis in SD_AXES:
            if sample_id in sd_summary and axis["id"] in sd_summary[sample_id]:
                row = {
                    "サンプル": sample_id,
                    "評価軸": axis["name"],
                    "平均": sd_summary[sample_id][axis["id"]]["mean"],
                    "標準偏差": sd_summary[sample_id][axis["id"]]["std"],
                }
                sd_data.append(row)
    pd.DataFrame(sd_data).to_excel(writer, sheet_name="SD評価", index=False)
    
    # 購買意欲
    purchase_data = []
    for sample_id in SOUND_SAMPLES:
        if sample_id in purchase_summary:
            row = {
                "サンプル": sample_id,
                "平均": purchase_summary[sample_id]["mean"],
                "標準偏差": purchase_summary[sample_id]["std"],
            }
            purchase_data.append(row)
    pd.DataFrame(purchase_data).to_excel(writer, sheet_name="購買意欲", index=False)
    
    # 重要度ランキング
    importance_data = []
    for sample_id in SOUND_SAMPLES:
        if sample_id in importance_ranking:
            for rank, item in enumerate(importance_ranking[sample_id], 1):
                row = {
                    "サンプル": sample_id,
                    "ランク": rank,
                    "評価軸": item["axis"],
                    "相関係数": item["correlation"],
                    "重要度": item["importance"],
                }
                importance_data.append(row)
    pd.DataFrame(importance_data).to_excel(writer, sheet_name="重要度ランキング", index=False)

print(f"  Excel保存完了: {excel_output}")
print()

# ============================================================================
# サマリー表示
# ============================================================================
print("=" * 60)
print("分析完了サマリー")
print("=" * 60)
print(f"総回答数: {len(responses)}名")
print()
print("【主要発見事項】")
print()

# 最良音
if best_worst_analysis["best_sound"]:
    best = max(best_worst_analysis["best_sound"].items(), key=lambda x: x[1])
    print(f"最も好まれた走行音: {best[0]} ({best[1]}名, {best[1]/len(responses)*100:.1f}%)")

# 購買意欲が最も高いサンプル
if purchase_comparison:
    best_purchase = max(purchase_comparison.items(), key=lambda x: x[1]["mean"])
    print(f"購買意欲が最も高いサンプル: {best_purchase[0]} (平均: {best_purchase[1]['mean']:.2f})")

# 重要度TOP3（Priusを例に）
if "Prius" in importance_ranking and importance_ranking["Prius"]:
    print("\n【購買意欲への重要度 TOP3 (Prius)】")
    for i, item in enumerate(importance_ranking["Prius"][:3], 1):
        axis_name = next((ax["name"] for ax in SD_AXES if ax["id"] == item["axis"]), item["axis"])
        print(f"  {i}. {axis_name}: 相関係数 {item['correlation']:.3f}")

print()
print("=" * 60)
print(f"分析結果は以下に保存されました:")
print(f"  - {json_output}")
print(f"  - {excel_output}")
print("=" * 60)
