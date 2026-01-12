"""
EV走行音アンケート 可視化スクリプト
データ分析計画書に基づくチャート生成
"""
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import io
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# seabornのオプショナルインポート
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("警告: seabornが見つかりません。一部のグラフはmatplotlibで代替します。")

# 日本語フォント設定
import platform
font_list = [f.name for f in font_manager.fontManager.ttflist]

if platform.system() == 'Windows':
    # Windowsで利用可能な日本語フォントを試行
    japanese_fonts = ['Yu Gothic', 'MS Gothic', 'MS PGothic', 'MS Mincho', 'MS PMincho', 'Meiryo', 'Meiryo UI']
    font_found = False
    
    for font_name in japanese_fonts:
        # フォント名の完全一致または部分一致を確認
        matching_fonts = [f for f in font_list if font_name.lower() in f.lower()]
        if matching_fonts:
            # 最初に見つかったフォントを使用
            selected_font = matching_fonts[0]
            plt.rcParams['font.family'] = selected_font
            print(f"日本語フォント設定: {selected_font}")
            font_found = True
            break
    
    if not font_found:
        # フォールバック: 日本語フォントが見つからない場合
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Yu Gothic', 'MS Gothic', 'MS PGothic', 'Meiryo', 'DejaVu Sans']
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
elif platform.system() == 'Darwin':  # macOS
    # macOSで利用可能な日本語フォントを試行
    japanese_fonts = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Hiragino Kaku Gothic Pro', 
                      'Arial Unicode MS', 'AppleGothic', 'Osaka', 'STHeiti', 'STSong']
    font_found = False
    
    for font_name in japanese_fonts:
        matching_fonts = [f for f in font_list if font_name.lower() in f.lower()]
        if matching_fonts:
            selected_font = matching_fonts[0]
            # フォントを明示的に設定（フォントパスを直接取得）
            try:
                font_path = None
                for font_info in font_manager.fontManager.ttflist:
                    if font_info.name == selected_font:
                        font_path = font_info.fname
                        break
                
                if font_path and Path(font_path).exists():
                    # フォントプロパティを作成
                    font_prop = font_manager.FontProperties(fname=str(font_path))
                    plt.rcParams['font.family'] = selected_font
                    plt.rcParams['font.sans-serif'] = [selected_font] + [f for f in plt.rcParams['font.sans-serif'] if f != selected_font]
                    print(f"日本語フォント設定: {selected_font} (パス: {font_path})")
                    font_found = True
                    break
            except Exception as e:
                print(f"フォント設定エラー ({selected_font}): {e}")
                continue
    
    if not font_found:
        # フォールバック: システムのデフォルト日本語フォントを使用
        plt.rcParams['font.family'] = 'Hiragino Sans'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans'] + [f for f in plt.rcParams['font.sans-serif'] if f != 'Hiragino Sans']
        print("日本語フォント設定: Hiragino Sans (デフォルト)")
else:
    # Linux等の場合
    japanese_fonts = ['Noto Sans CJK JP', 'Noto Sans JP', 'Takao', 'IPAexGothic', 'IPAPGothic']
    font_found = False
    
    for font_name in japanese_fonts:
        matching_fonts = [f for f in font_list if font_name.lower() in f.lower()]
        if matching_fonts:
            selected_font = matching_fonts[0]
            plt.rcParams['font.family'] = selected_font
            print(f"日本語フォント設定: {selected_font}")
            font_found = True
            break
    
    if not font_found:
        plt.rcParams['font.family'] = 'DejaVu Sans'
        print("警告: 日本語フォントが見つかりません。DejaVu Sansを使用します。")

# マイナス記号の文字化け防止
plt.rcParams['axes.unicode_minus'] = False

# 日本語フォントプロパティを取得（グラフ生成時に使用）
def get_japanese_font_prop():
    """日本語フォントプロパティを取得"""
    if platform.system() == 'Darwin':  # macOS
        try:
            # Hiragino Sansのフォントパスを取得
            for font_info in font_manager.fontManager.ttflist:
                if 'Hiragino Sans' in font_info.name:
                    return font_manager.FontProperties(fname=font_info.fname)
            # フォールバック
            return font_manager.FontProperties(family='Hiragino Sans')
        except:
            return font_manager.FontProperties(family='Hiragino Sans')
    elif platform.system() == 'Windows':
        try:
            for font_info in font_manager.fontManager.ttflist:
                if 'Yu Gothic' in font_info.name or 'MS Gothic' in font_info.name:
                    return font_manager.FontProperties(fname=font_info.fname)
            return font_manager.FontProperties(family='Yu Gothic')
        except:
            return font_manager.FontProperties(family='Yu Gothic')
    else:
        return font_manager.FontProperties(family='DejaVu Sans')

# グローバルにフォントプロパティを設定
JAPANESE_FONT_PROP = get_japanese_font_prop()

def apply_japanese_font(ax):
    """軸のすべてのテキスト要素に日本語フォントを適用"""
    if ax.get_title():
        ax.set_title(ax.get_title(), fontproperties=JAPANESE_FONT_PROP)
    if ax.get_xlabel():
        ax.set_xlabel(ax.get_xlabel(), fontproperties=JAPANESE_FONT_PROP)
    if ax.get_ylabel():
        ax.set_ylabel(ax.get_ylabel(), fontproperties=JAPANESE_FONT_PROP)
    for label in ax.get_xticklabels():
        label.set_fontproperties(JAPANESE_FONT_PROP)
    for label in ax.get_yticklabels():
        label.set_fontproperties(JAPANESE_FONT_PROP)
    # 凡例がある場合
    if ax.get_legend():
        for text in ax.get_legend().get_texts():
            text.set_fontproperties(JAPANESE_FONT_PROP)

if HAS_SEABORN:
    sns.set_style("whitegrid")
    sns.set_palette("husl")

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SD_AXES, SOUND_SAMPLES

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "analysis"
CHARTS_DIR = OUTPUT_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# データ読み込み
DATA_DIR = Path(__file__).parent.parent / "data" / "sample_data"
CSV_FILE = DATA_DIR / "sample_responses.csv"
ANALYSIS_FILE = OUTPUT_DIR / "analysis_results.json"

print("=" * 60)
print("EV走行音アンケート 可視化生成")
print("=" * 60)

# データ読み込み
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
    analysis_results = json.load(f)

print(f"データ読み込み完了: {len(df)}件")
print()

# ============================================================================
# C01: 回答者属性分布
# ============================================================================
print("[1/8] C01: 回答者属性分布を生成中...")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("回答者属性分布", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

# 年齢分布
df["age_group"].value_counts().plot(kind="bar", ax=axes[0, 0], color="skyblue")
axes[0, 0].set_title("年齢分布", fontproperties=JAPANESE_FONT_PROP)
axes[0, 0].set_xlabel("年齢層", fontproperties=JAPANESE_FONT_PROP)
axes[0, 0].set_ylabel("人数", fontproperties=JAPANESE_FONT_PROP)
axes[0, 0].tick_params(axis='x', rotation=45)
apply_japanese_font(axes[0, 0])

# 性別分布
df["gender"].value_counts().plot(kind="pie", ax=axes[0, 1], autopct="%1.1f%%")
axes[0, 1].set_title("性別分布", fontproperties=JAPANESE_FONT_PROP)
axes[0, 1].set_ylabel("")
apply_japanese_font(axes[0, 1])

# 運転経験分布
df["driving_experience"].value_counts().plot(kind="bar", ax=axes[0, 2], color="lightgreen")
axes[0, 2].set_title("運転経験分布", fontproperties=JAPANESE_FONT_PROP)
axes[0, 2].set_xlabel("運転経験", fontproperties=JAPANESE_FONT_PROP)
axes[0, 2].set_ylabel("人数", fontproperties=JAPANESE_FONT_PROP)
axes[0, 2].tick_params(axis='x', rotation=45)
apply_japanese_font(axes[0, 2])

# EV経験分布
df["ev_experience"].value_counts().plot(kind="bar", ax=axes[1, 0], color="coral")
axes[1, 0].set_title("EV経験分布", fontproperties=JAPANESE_FONT_PROP)
axes[1, 0].set_xlabel("EV経験", fontproperties=JAPANESE_FONT_PROP)
axes[1, 0].set_ylabel("人数", fontproperties=JAPANESE_FONT_PROP)
axes[1, 0].tick_params(axis='x', rotation=45)
apply_japanese_font(axes[1, 0])

# 音感度分布
df["sound_sensitivity"].hist(bins=10, ax=axes[1, 1], color="plum", edgecolor="black")
axes[1, 1].set_title("音感度分布", fontproperties=JAPANESE_FONT_PROP)
axes[1, 1].set_xlabel("音感度", fontproperties=JAPANESE_FONT_PROP)
axes[1, 1].set_ylabel("人数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[1, 1])

# 都道府県分布（TOP10）
df["prefecture"].value_counts().head(10).plot(kind="barh", ax=axes[1, 2], color="gold")
axes[1, 2].set_title("都道府県分布 (TOP10)", fontproperties=JAPANESE_FONT_PROP)
axes[1, 2].set_xlabel("人数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[1, 2])

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C01_回答者属性分布.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C01保存完了")

# ============================================================================
# C02: SD評価レーダーチャート
# ============================================================================
print("[2/8] C02: SD評価レーダーチャートを生成中...")
from math import pi

fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw=dict(projection='polar'))
fig.suptitle("SD評価レーダーチャート（サンプル別比較）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

axis_names = [axis["name"] for axis in SD_AXES]
axis_ids = [axis["id"] for axis in SD_AXES]
angles = [n / float(len(SD_AXES)) * 2 * pi for n in range(len(SD_AXES))]
angles += angles[:1]  # 閉じる

for idx, sample_id in enumerate(SOUND_SAMPLES):
    values = []
    for axis_id in axis_ids:
        col_name = f"sd_{sample_id}_{axis_id}"
        if col_name in df.columns:
            values.append(df[col_name].mean())
        else:
            values.append(0)
    values += values[:1]  # 閉じる
    
    axes[idx].plot(angles, values, 'o-', linewidth=2, label=sample_id)
    axes[idx].fill(angles, values, alpha=0.25)
    axes[idx].set_xticks(angles[:-1])
    axes[idx].set_xticklabels(axis_names, fontsize=9, fontproperties=JAPANESE_FONT_PROP)
    axes[idx].set_ylim(-3, 3)
    axes[idx].set_title(sample_id, fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
    axes[idx].grid(True)
    apply_japanese_font(axes[idx])

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C02_SD評価レーダーチャート.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C02保存完了")

# ============================================================================
# C03: 購買意欲分布
# ============================================================================
print("[3/8] C03: 購買意欲分布を生成中...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("購買意欲分布（サンプル別）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

for idx, sample_id in enumerate(SOUND_SAMPLES):
    intent_col = f"purchase_intent_{sample_id}"
    if intent_col in df.columns:
        df[intent_col].value_counts().sort_index().plot(kind="bar", ax=axes[idx], color="steelblue")
        axes[idx].set_title(sample_id, fontproperties=JAPANESE_FONT_PROP)
        axes[idx].set_xlabel("購買意欲 (1-7)", fontproperties=JAPANESE_FONT_PROP)
        axes[idx].set_ylabel("人数", fontproperties=JAPANESE_FONT_PROP)
        axes[idx].set_ylim(0, df[intent_col].value_counts().max() * 1.1)
        apply_japanese_font(axes[idx])

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C03_購買意欲分布.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C03保存完了")

# ============================================================================
# C04: SD軸相関マトリクス
# ============================================================================
print("[4/8] C04: SD軸相関マトリクスを生成中...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("SD軸相関マトリクス（サンプル別）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

for idx, sample_id in enumerate(SOUND_SAMPLES):
    axis_cols = [f"sd_{sample_id}_{axis['id']}" for axis in SD_AXES]
    available_cols = [col for col in axis_cols if col in df.columns]
    if available_cols:
        corr = df[available_cols].corr()
        axis_labels = [axis["name"] for axis in SD_AXES if f"sd_{sample_id}_{axis['id']}" in df.columns]
        
        if HAS_SEABORN:
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                       square=True, ax=axes[idx], cbar_kws={"shrink": 0.8},
                       xticklabels=axis_labels, yticklabels=axis_labels,
                       annot_kws={"size": 10})
            axes[idx].tick_params(axis='x', rotation=45, labelsize=9)
            axes[idx].tick_params(axis='y', rotation=0, labelsize=9)
            # カラーバーのラベルサイズを設定
            if len(axes[idx].collections) > 0:
                cbar = axes[idx].collections[0].colorbar
                if cbar is not None:
                    cbar.ax.tick_params(labelsize=9)
        else:
            # matplotlibで代替
            im = axes[idx].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1, aspect='auto')
            axes[idx].set_xticks(range(len(axis_labels)))
            axes[idx].set_yticks(range(len(axis_labels)))
            axes[idx].set_xticklabels(axis_labels, rotation=45, ha='right', fontsize=9, fontproperties=JAPANESE_FONT_PROP)
            axes[idx].set_yticklabels(axis_labels, fontsize=9, fontproperties=JAPANESE_FONT_PROP)
            # 相関係数をテキストで表示
            for i in range(len(axis_labels)):
                for j in range(len(axis_labels)):
                    text = axes[idx].text(j, i, f'{corr.iloc[i, j]:.2f}',
                                         ha="center", va="center", color="black", fontsize=10)
            plt.colorbar(im, ax=axes[idx], shrink=0.8)
        axes[idx].set_title(sample_id, fontsize=13, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        apply_japanese_font(axes[idx])

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C04_SD軸相関マトリクス.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C04保存完了")

# ============================================================================
# C05: 購買意欲要因分析
# ============================================================================
print("[5/8] C05: 購買意欲要因分析を生成中...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("購買意欲への重要度（相関係数）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

importance_ranking = analysis_results["layer3_correlation"]["importance_ranking"]

for idx, sample_id in enumerate(SOUND_SAMPLES):
    if sample_id in importance_ranking:
        ranking = importance_ranking[sample_id][:9]  # TOP9
        axis_names = [next((ax["name"] for ax in SD_AXES if ax["id"] == item["axis"]), item["axis"]) 
                     for item in ranking]
        correlations = [item["correlation"] for item in ranking]
        
        y_pos = np.arange(len(axis_names))
        colors = ['red' if x < 0 else 'blue' for x in correlations]
        
        axes[idx].barh(y_pos, correlations, color=colors, alpha=0.7)
        axes[idx].set_yticks(y_pos)
        axes[idx].set_yticklabels(axis_names, fontsize=10, fontproperties=JAPANESE_FONT_PROP)
        axes[idx].set_xlabel("相関係数", fontsize=11, fontproperties=JAPANESE_FONT_PROP)
        axes[idx].set_title(sample_id, fontsize=13, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        apply_japanese_font(axes[idx])
        axes[idx].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        axes[idx].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C05_購買意欲要因分析.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C05保存完了")

# ============================================================================
# C06: セグメント特性
# ============================================================================
print("[6/8] C06: セグメント特性を生成中...")
segment_analysis = analysis_results["layer4_segmentation"]

# 年齢層別の購買意欲
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("セグメント特性（年齢層別）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
age_segments = segment_analysis.get("age_group", {})
age_groups = list(age_segments.keys())
x = np.arange(len(SOUND_SAMPLES))
width = 0.8 / len(age_groups)

for i, age_group in enumerate(age_groups):
    means = [age_segments[age_group].get(sample_id, {}).get("mean", 0) 
             for sample_id in SOUND_SAMPLES]
    ax.bar(x + i * width, means, width, label=age_group, alpha=0.8)

ax.set_xlabel("サンプル", fontproperties=JAPANESE_FONT_PROP)
ax.set_ylabel("平均購買意欲", fontproperties=JAPANESE_FONT_PROP)
ax.set_title("年齢層別購買意欲比較", fontsize=14, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
ax.set_xticks(x + width * (len(age_groups) - 1) / 2)
ax.set_xticklabels(SOUND_SAMPLES, fontproperties=JAPANESE_FONT_PROP)
ax.legend(prop=JAPANESE_FONT_PROP)
ax.grid(axis='y', alpha=0.3)
apply_japanese_font(ax)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C06_セグメント特性_年齢層別.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C06保存完了")

# ============================================================================
# C07: ラダリング階層図（簡易版）
# ============================================================================
print("[7/8] C07: ラダリング分析を生成中...")
laddering = analysis_results["layer5_insights"]["laddering"]

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("ラダリング分析（上位概念・下位概念）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

# 良い理由TOP10
why_good = sorted(laddering["why_good"].items(), key=lambda x: x[1], reverse=True)[:10]
axes[0, 0].barh(range(len(why_good)), [x[1] for x in why_good], color="lightblue")
axes[0, 0].set_yticks(range(len(why_good)))
axes[0, 0].set_yticklabels([x[0] for x in why_good], fontsize=9, fontproperties=JAPANESE_FONT_PROP)
axes[0, 0].set_title("良い理由 TOP10", fontproperties=JAPANESE_FONT_PROP)
axes[0, 0].set_xlabel("選択回数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[0, 0])

# 良い気持ちTOP10
feeling_good = sorted(laddering["feeling_good"].items(), key=lambda x: x[1], reverse=True)[:10]
axes[0, 1].barh(range(len(feeling_good)), [x[1] for x in feeling_good], color="lightgreen")
axes[0, 1].set_yticks(range(len(feeling_good)))
axes[0, 1].set_yticklabels([x[0] for x in feeling_good], fontsize=9, fontproperties=JAPANESE_FONT_PROP)
axes[0, 1].set_title("良い気持ち TOP10", fontproperties=JAPANESE_FONT_PROP)
axes[0, 1].set_xlabel("選択回数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[0, 1])

# 悪い理由TOP10
why_bad = sorted(laddering["why_bad"].items(), key=lambda x: x[1], reverse=True)[:10]
axes[1, 0].barh(range(len(why_bad)), [x[1] for x in why_bad], color="lightcoral")
axes[1, 0].set_yticks(range(len(why_bad)))
axes[1, 0].set_yticklabels([x[0] for x in why_bad], fontsize=9, fontproperties=JAPANESE_FONT_PROP)
axes[1, 0].set_title("悪い理由 TOP10", fontproperties=JAPANESE_FONT_PROP)
axes[1, 0].set_xlabel("選択回数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[1, 0])

# 悪い気持ちTOP10
feeling_bad = sorted(laddering["feeling_bad"].items(), key=lambda x: x[1], reverse=True)[:10]
axes[1, 1].barh(range(len(feeling_bad)), [x[1] for x in feeling_bad], color="lightsalmon")
axes[1, 1].set_yticks(range(len(feeling_bad)))
axes[1, 1].set_yticklabels([x[0] for x in feeling_bad], fontsize=9, fontproperties=JAPANESE_FONT_PROP)
axes[1, 1].set_title("悪い気持ち TOP10", fontproperties=JAPANESE_FONT_PROP)
axes[1, 1].set_xlabel("選択回数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[1, 1])

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C07_ラダリング分析.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C07保存完了")

# ============================================================================
# C07-2: ラダリングネットワーク分析
# ============================================================================
print("[7.5/9] C07-2: ラダリングネットワーク分析を生成中...")

# networkxが利用可能か確認
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("  警告: networkxが見つかりません。簡易的なネットワーク図を生成します。")

if HAS_NETWORKX:
    # 日本語フォントを取得（JAPANESE_FONT_PROPから）
    try:
        font_family_str = JAPANESE_FONT_PROP.get_name() if hasattr(JAPANESE_FONT_PROP, 'get_name') else JAPANESE_FONT_PROP.get_family()[0] if hasattr(JAPANESE_FONT_PROP, 'get_family') else 'Hiragino Sans'
    except:
        font_family_str = 'Hiragino Sans'
    
    # ネットワークグラフを作成
    fig, axes = plt.subplots(1, 2, figsize=(18, 9))
    fig.suptitle("ラダリングネットワーク分析（共起関係）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
    
    cooccurrence = laddering.get("cooccurrence", {})
    
    # 良い理由→良い気持ちのネットワーク
    if "why_good_feeling_good" in cooccurrence:
        G_good = nx.DiGraph()
        edge_data = cooccurrence["why_good_feeling_good"]
        
        # TOP20の共起関係を抽出
        sorted_edges = sorted(edge_data.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # ノードの出現回数をカウント
        node_counts = {}
        edge_weights_dict = {}
        
        for edge_key, weight in sorted_edges:
            if " → " in edge_key:
                why, feeling = edge_key.split(" → ", 1)
                G_good.add_edge(why, feeling, weight=weight)
                edge_weights_dict[(why, feeling)] = weight
                node_counts[why] = node_counts.get(why, 0) + weight
                node_counts[feeling] = node_counts.get(feeling, 0) + weight
        
        # レイアウト計算
        pos = nx.spring_layout(G_good, k=2, iterations=50)
        
        # ノードサイズを出現回数に基づいて計算（最小500、最大3000）
        if node_counts:
            max_count = max(node_counts.values())
            min_count = min(node_counts.values())
            if max_count > min_count:
                node_sizes = [500 + (node_counts.get(node, 0) - min_count) / (max_count - min_count) * 2500 
                             for node in G_good.nodes()]
            else:
                node_sizes = [1500] * len(G_good.nodes())
        else:
            node_sizes = [1500] * len(G_good.nodes())
        
        # エッジの太さをweightに基づいて計算（最小1、最大8）
        edge_weights = [edge_weights_dict.get((u, v), 1) for u, v in G_good.edges()]
        if edge_weights:
            max_weight = max(edge_weights)
            min_weight = min(edge_weights)
            if max_weight > min_weight:
                edge_widths = [1 + (w - min_weight) / (max_weight - min_weight) * 7 
                              for w in edge_weights]
            else:
                edge_widths = [4] * len(edge_weights)
        else:
            edge_widths = [4] * len(G_good.edges())
        
        # ノードとエッジを描画
        nx.draw_networkx_nodes(G_good, pos, ax=axes[0], node_color="lightblue", 
                              node_size=node_sizes, alpha=0.7)
        nx.draw_networkx_edges(G_good, pos, ax=axes[0], edge_color="gray", 
                              arrows=True, arrowsize=20, alpha=0.6, width=edge_widths)
        # 日本語フォントを明示的に指定（フォントサイズを8→12に変更）
        nx.draw_networkx_labels(G_good, pos, ax=axes[0], font_size=12, font_family=font_family_str)
        
        axes[0].set_title("良い理由 → 良い気持ちのネットワーク", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        axes[0].axis("off")
    
    # 悪い理由→悪い気持ちのネットワーク
    if "why_bad_feeling_bad" in cooccurrence:
        G_bad = nx.DiGraph()
        edge_data = cooccurrence["why_bad_feeling_bad"]
        
        sorted_edges = sorted(edge_data.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # ノードの出現回数をカウント
        node_counts = {}
        edge_weights_dict = {}
        
        for edge_key, weight in sorted_edges:
            if " → " in edge_key:
                why, feeling = edge_key.split(" → ", 1)
                G_bad.add_edge(why, feeling, weight=weight)
                edge_weights_dict[(why, feeling)] = weight
                node_counts[why] = node_counts.get(why, 0) + weight
                node_counts[feeling] = node_counts.get(feeling, 0) + weight
        
        pos = nx.spring_layout(G_bad, k=2, iterations=50)
        
        # ノードサイズを出現回数に基づいて計算（最小500、最大3000）
        if node_counts:
            max_count = max(node_counts.values())
            min_count = min(node_counts.values())
            if max_count > min_count:
                node_sizes = [500 + (node_counts.get(node, 0) - min_count) / (max_count - min_count) * 2500 
                             for node in G_bad.nodes()]
            else:
                node_sizes = [1500] * len(G_bad.nodes())
        else:
            node_sizes = [1500] * len(G_bad.nodes())
        
        # エッジの太さをweightに基づいて計算（最小1、最大8）
        edge_weights = [edge_weights_dict.get((u, v), 1) for u, v in G_bad.edges()]
        if edge_weights:
            max_weight = max(edge_weights)
            min_weight = min(edge_weights)
            if max_weight > min_weight:
                edge_widths = [1 + (w - min_weight) / (max_weight - min_weight) * 7 
                              for w in edge_weights]
            else:
                edge_widths = [4] * len(edge_weights)
        else:
            edge_widths = [4] * len(G_bad.edges())
        
        nx.draw_networkx_nodes(G_bad, pos, ax=axes[1], node_color="lightcoral", 
                              node_size=node_sizes, alpha=0.7)
        nx.draw_networkx_edges(G_bad, pos, ax=axes[1], edge_color="gray", 
                              arrows=True, arrowsize=20, alpha=0.6, width=edge_widths)
        # 日本語フォントを明示的に指定（フォントサイズを8→12に変更）
        nx.draw_networkx_labels(G_bad, pos, ax=axes[1], font_size=12, font_family=font_family_str)
        
        axes[1].set_title("悪い理由 → 悪い気持ちのネットワーク", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        axes[1].axis("off")
    
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "C07-2_ラダリングネットワーク分析.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  C07-2保存完了")
else:
    # networkxがない場合：共起関係をテーブル形式で可視化
    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    fig.suptitle("ラダリングネットワーク分析（共起関係 TOP15）", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
    
    cooccurrence = laddering.get("cooccurrence", {})
    
    # 良い理由→良い気持ち
    if "why_good_feeling_good" in cooccurrence:
        edge_data = cooccurrence["why_good_feeling_good"]
        sorted_edges = sorted(edge_data.items(), key=lambda x: x[1], reverse=True)[:15]
        
        edges = [x[0] for x in sorted_edges]
        weights = [x[1] for x in sorted_edges]
        
        y_pos = np.arange(len(edges))
        axes[0].barh(y_pos, weights, color="lightblue", alpha=0.7)
        axes[0].set_yticks(y_pos)
        axes[0].set_yticklabels(edges, fontsize=8, fontproperties=JAPANESE_FONT_PROP)
        axes[0].set_title("良い理由 → 良い気持ち（共起回数 TOP15）", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        axes[0].set_xlabel("共起回数", fontproperties=JAPANESE_FONT_PROP)
        apply_japanese_font(axes[0])
        axes[0].invert_yaxis()
    
    # 悪い理由→悪い気持ち
    if "why_bad_feeling_bad" in cooccurrence:
        edge_data = cooccurrence["why_bad_feeling_bad"]
        sorted_edges = sorted(edge_data.items(), key=lambda x: x[1], reverse=True)[:15]
        
        edges = [x[0] for x in sorted_edges]
        weights = [x[1] for x in sorted_edges]
        
        y_pos = np.arange(len(edges))
        axes[1].barh(y_pos, weights, color="lightcoral", alpha=0.7)
        axes[1].set_yticks(y_pos)
        axes[1].set_yticklabels(edges, fontsize=8, fontproperties=JAPANESE_FONT_PROP)
        axes[1].set_title("悪い理由 → 悪い気持ち（共起回数 TOP15）", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
        axes[1].set_xlabel("共起回数", fontproperties=JAPANESE_FONT_PROP)
        apply_japanese_font(axes[1])
        axes[1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "C07-2_ラダリングネットワーク分析.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  C07-2保存完了（簡易版）")

# ============================================================================
# C08: 最良・最悪音選択
# ============================================================================
print("[8/9] C08: 最良・最悪音選択を生成中...")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("最良・最悪音選択", fontsize=16, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)

best_worst = analysis_results["layer2_comparative"]["best_worst"]

# 最良音
best_counts = best_worst["best_sound"]
axes[0].bar(best_counts.keys(), best_counts.values(), color="steelblue", alpha=0.7)
axes[0].set_title("最も好まれた走行音", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
axes[0].set_xlabel("サンプル", fontproperties=JAPANESE_FONT_PROP)
axes[0].set_ylabel("選択人数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[0])
axes[0].grid(axis='y', alpha=0.3)

# 最悪音
worst_counts = best_worst["worst_sound"]
axes[1].bar(worst_counts.keys(), worst_counts.values(), color="coral", alpha=0.7)
axes[1].set_title("最も好まれなかった走行音", fontsize=12, fontweight="bold", fontproperties=JAPANESE_FONT_PROP)
axes[1].set_xlabel("サンプル", fontproperties=JAPANESE_FONT_PROP)
axes[1].set_ylabel("選択人数", fontproperties=JAPANESE_FONT_PROP)
apply_japanese_font(axes[1])
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "C08_最良最悪音選択.png", dpi=300, bbox_inches="tight")
plt.close()
print("  C08保存完了")

print()
print("[9/9] 可視化生成完了")
print()
print("=" * 60)
print("可視化生成完了")
print(f"チャート保存先: {CHARTS_DIR}")
print("=" * 60)
