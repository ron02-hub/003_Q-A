# -*- coding: utf-8 -*-
"""
EV走行音アンケート レポート生成スクリプト
HTML形式の分析レポートを生成
"""
import json
from pathlib import Path
from datetime import datetime
import sys
import io
from urllib.parse import quote

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
ANALYSIS_FILE = OUTPUT_DIR / "analysis_results.json"
CHARTS_DIR = OUTPUT_DIR / "charts"

print("=" * 60)
print("EV走行音アンケート レポート生成")
print("=" * 60)

# 分析結果読み込み
print(f"[DEBUG] 分析結果ファイル読み込み開始: {ANALYSIS_FILE}")
try:
    with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)
    print(f"[DEBUG] 分析結果読み込み完了: {len(results)}件のキー")
except Exception as e:
    print(f"[ERROR] 分析結果読み込みエラー: {e}")
    raise

# 画像ファイル名をURLエンコード（日本語ファイル名対応）
print("[DEBUG] 画像ファイル名のURLエンコード開始")
try:
    chart_files = {
        'C01': quote('C01_回答者属性分布.png'),
        'C02': quote('C02_SD評価レーダーチャート.png'),
        'C03': quote('C03_購買意欲分布.png'),
        'C04': quote('C04_SD軸相関マトリクス.png'),
        'C05': quote('C05_購買意欲要因分析.png'),
        'C06': quote('C06_セグメント特性_年齢層別.png'),
        'C07': quote('C07_ラダリング分析.png'),
        'C07-2': quote('C07-2_ラダリングネットワーク分析.png'),
        'C08': quote('C08_最良最悪音選択.png'),
    }
    print(f"[DEBUG] 画像ファイル名のURLエンコード完了: {len(chart_files)}件")
except Exception as e:
    print(f"[ERROR] 画像ファイル名のURLエンコードエラー: {e}")
    raise

# HTMLレポート生成
print("[DEBUG] HTMLレポート生成開始")
html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV走行音アンケート 分析レポート</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .section h3 {
            color: #764ba2;
            margin-top: 25px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .chart {
            text-align: center;
            margin: 20px 0;
        }
        .chart img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .highlight {
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
        .insight-box {
            background-color: #e7f3ff;
            padding: 15px;
            border-left: 4px solid #2196F3;
            margin: 20px 0;
        }
        .stat-box {
            display: inline-block;
            background-color: #f8f9fa;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .stat-box strong {
            display: block;
            font-size: 1.5em;
            color: #667eea;
        }
        .insight-box ul {
            margin-left: 20px;
            line-height: 1.8;
        }
        .insight-box ul ul {
            margin-left: 20px;
            margin-top: 5px;
        }
        .insight-box h4 {
            color: #764ba2;
            margin-top: 20px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 EV走行音アンケート 分析レポート</h1>
        <p>分析日時: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M') + """</p>
        <p>総回答数: """ + str(results['total_responses']) + """名</p>
    </div>

    <!-- エグゼクティブサマリー -->
    <div class="section">
        <h2>📊 エグゼクティブサマリー</h2>
        <div class="highlight">
            <h3>主要発見事項</h3>
"""

# 最良音
best_worst = results["layer2_comparative"]["best_worst"]
if best_worst["best_sound"]:
    best = max(best_worst["best_sound"].items(), key=lambda x: x[1])
    html_content += f"""
            <p><strong>最も好まれた走行音:</strong> {best[0]} ({best[1]}名, {best[1]/results['total_responses']*100:.1f}%)</p>
"""

# 購買意欲
purchase_comp = results["layer2_comparative"]["purchase_comparison"]
if purchase_comp:
    best_purchase = max(purchase_comp.items(), key=lambda x: x[1]["mean"])
    html_content += f"""
            <p><strong>購買意欲が最も高いサンプル:</strong> {best_purchase[0]} (平均: {best_purchase[1]['mean']:.2f}/7.0)</p>
"""

# 重要度TOP3
importance = results["layer3_correlation"]["importance_ranking"]
if "Prius" in importance and importance["Prius"]:
    html_content += """
            <h4>購買意欲への重要度 TOP3 (Prius)</h4>
            <ol>
"""
    for i, item in enumerate(importance["Prius"][:3], 1):
        axis_name = next((ax["name"] for ax in SD_AXES if ax["id"] == item["axis"]), item["axis"])
        html_content += f"""
                <li>{axis_name}: 相関係数 {item['correlation']:.3f}</li>
"""
    html_content += """
            </ol>
"""

html_content += """
        </div>
    </div>

    <!-- 調査概要 -->
    <div class="section">
        <h2>📋 調査概要</h2>
        <h3>回答者属性</h3>
"""

# 回答者属性
demo = results["layer1_descriptive"]["demographics"]
html_content += f"""
        <div class="stat-box">
            <strong>{len(demo['age_group'])}</strong>
            <span>年齢層</span>
        </div>
        <div class="stat-box">
            <strong>{len(demo['gender'])}</strong>
            <span>性別区分</span>
        </div>
        <div class="stat-box">
            <strong>{len(demo['ev_experience'])}</strong>
            <span>EV経験区分</span>
        </div>
        <div class="stat-box">
            <strong>{demo['sound_sensitivity']['mean']:.1f}</strong>
            <span>平均音感度</span>
        </div>
"""

html_content += """
        <h3>年齢分布</h3>
        <table>
            <tr><th>年齢層</th><th>人数</th><th>割合</th></tr>
"""

for age, count in demo["age_group"].items():
    pct = count / results['total_responses'] * 100
    html_content += f"""
            <tr><td>{age}</td><td>{count}名</td><td>{pct:.1f}%</td></tr>
"""

html_content += """
        </table>
    </div>

    <!-- サンプル評価結果 -->
    <div class="section">
        <h2>🎵 サンプル評価結果</h2>
"""

# SD評価サマリー
sd_ratings = results["layer1_descriptive"]["sd_ratings"]
for sample_id in SOUND_SAMPLES:
    if sample_id in sd_ratings:
        html_content += f"""
        <h3>{sample_id} の評価</h3>
        <table>
            <tr><th>評価軸</th><th>平均</th><th>標準偏差</th></tr>
"""
        for axis in SD_AXES:
            if axis["id"] in sd_ratings[sample_id]:
                stats = sd_ratings[sample_id][axis["id"]]
                html_content += f"""
            <tr><td>{axis['name']}</td><td>{stats['mean']:.2f}</td><td>{stats['std']:.2f}</td></tr>
"""
        html_content += """
        </table>
        <div class="chart">
            <img src="charts/""" + chart_files['C02'] + """" alt="SD評価レーダーチャート">
        </div>
"""

# 購買意欲
purchase = results["layer1_descriptive"]["purchase_intent"]
html_content += """
        <h3>購買意欲</h3>
        <table>
            <tr><th>サンプル</th><th>平均</th><th>標準偏差</th></tr>
"""
for sample_id in SOUND_SAMPLES:
    if sample_id in purchase:
        stats = purchase[sample_id]
        html_content += f"""
            <tr><td>{sample_id}</td><td>{stats['mean']:.2f}</td><td>{stats['std']:.2f}</td></tr>
"""
html_content += """
        </table>
        <div class="chart">
            <img src="charts/""" + chart_files['C03'] + """" alt="購買意欲分布">
        </div>
    </div>
"""

html_content += """
    <!-- 要因分析 -->
    <div class="section">
        <h2>🔍 要因分析</h2>
        
        <div class="insight-box">
            <h3>📊 グラフの見方（小学生向け説明）</h3>
            <p><strong>このセクションでは、どんなグラフが使われているか、どうやって見るかを説明します。</strong></p>
            <h4>1. SD軸相関マトリクス（四角いマス目のグラフ）</h4>
            <ul>
                <li><strong>このグラフは何？</strong> 評価の項目同士がどのくらい似ているかを色で表したものです。</li>
                <li><strong>どう見るの？</strong> グラフの横と縦に項目名（「音量感」「快感情」など）が並んでいます。</li>
                <li><strong>色の意味は？</strong> 
                    <ul>
                        <li>🔴 <strong>赤い色</strong> = 数字が「+1」に近い = 似ている（一方が高いと、もう一方も高い）</li>
                        <li>⚪ <strong>白い色</strong> = 数字が「0」に近い = 関係がない</li>
                        <li>🔵 <strong>青い色</strong> = 数字が「-1」に近い = 逆の関係（一方が高いと、もう一方は低い）</li>
                    </ul>
                </li>
                <li><strong>マス目の数字は？</strong> マスの真ん中に書いてある数字（例：0.85、-0.32など）が、似ている度合いを表します。1.0に近いほど、とても似ています。</li>
                <li><strong>たとえば：</strong> 「快感情」と「高級感」が赤い色だったら、「心地よさ」と「高級感」は一緒に高くなりやすいということです。</li>
            </ul>
            
            <h4>2. 購買意欲への重要度（横棒グラフ）</h4>
            <ul>
                <li><strong>このグラフは何？</strong> 「車を買いたい！」と思う気持ちに、どの評価項目が大切かを表したグラフです。</li>
                <li><strong>どう見るの？</strong> 
                    <ul>
                        <li>左側に評価項目の名前が書いてあります（「高級感」「快感情」など）</li>
                        <li>右側に棒が伸びています</li>
                        <li>棒が右に長く伸びているほど、「車を買いたい」気持ちに大きく影響します</li>
                    </ul>
                </li>
                <li><strong>色の意味は？</strong>
                    <ul>
                        <li>🔵 <strong>青い棒</strong> = プラス（この項目が高くなると、買いたい気持ちが強くなる）</li>
                        <li>🔴 <strong>赤い棒</strong> = マイナス（この項目が高くなると、買いたい気持ちが弱くなる）</li>
                    </ul>
                </li>
                <li><strong>たとえば：</strong> 「高級感」の棒が一番長かったら、「高級感がある走行音だと、多くの人が車を買いたくなる」という意味です。</li>
                <li><strong>横軸の数字（相関係数）は？</strong> 
                    <ul>
                        <li>0.3以上 = 結構重要</li>
                        <li>0.5以上 = とても重要</li>
                        <li>-0.3以下 = 逆に影響する（高くなると買いたくなくなる）</li>
                    </ul>
                </li>
            </ul>
        </div>
        
        <h3>SD軸相関マトリクス</h3>
        <div class="chart">
            <img src="charts/""" + chart_files['C04'] + """" alt="SD軸相関マトリクス">
        </div>
        <p><em>※ 上記の「グラフの見方」を参考に、このグラフを見てください。色が濃い（赤や青）マスほど、関係が強いことを表します。</em></p>
        
        <h3>購買意欲への重要度</h3>
        <div class="chart">
            <img src="charts/""" + chart_files['C05'] + """" alt="購買意欲要因分析">
        </div>
        <p><em>※ 上記の「グラフの見方」を参考に、このグラフを見てください。棒が右に長い項目ほど、「車を買いたい」気持ちに大きく影響します。</em></p>
"""

# 重要度ランキング
for sample_id in SOUND_SAMPLES:
    if sample_id in importance and importance[sample_id]:
        html_content += f"""
        <h4>{sample_id} の購買意欲への重要度 TOP5</h4>
        <table>
            <tr><th>ランク</th><th>評価軸</th><th>相関係数</th></tr>
"""
        for rank, item in enumerate(importance[sample_id][:5], 1):
            axis_name = next((ax["name"] for ax in SD_AXES if ax["id"] == item["axis"]), item["axis"])
            html_content += f"""
            <tr><td>{rank}</td><td>{axis_name}</td><td>{item['correlation']:.3f}</td></tr>
"""
        html_content += """
        </table>
"""

html_content += """
    </div>
"""

html_content += """
    <!-- セグメント分析 -->
    <div class="section">
        <h2>👥 セグメント分析</h2>
        <div class="chart">
            <img src="charts/""" + chart_files['C06'] + """" alt="セグメント特性">
        </div>
"""

# 年齢層別分析
age_seg = results["layer4_segmentation"].get("age_group", {})
html_content += """
        <h3>年齢層別購買意欲</h3>
        <table>
            <tr><th>年齢層</th>"""
for sample_id in SOUND_SAMPLES:
    html_content += f"<th>{sample_id}</th>"
html_content += "</tr>"

for age_group in age_seg.keys():
    html_content += f"<tr><td>{age_group}</td>"
    for sample_id in SOUND_SAMPLES:
        mean = age_seg[age_group].get(sample_id, {}).get("mean", 0)
        html_content += f"<td>{mean:.2f}</td>"
    html_content += "</tr>"

html_content += """
        </table>
    </div>

    <!-- インサイト -->
    <div class="section">
        <h2>💡 インサイト</h2>
        <h3>ラダリング分析</h3>
        <div class="chart">
            <img src="charts/""" + chart_files['C07'] + """" alt="ラダリング分析">
        </div>
        
        <h4>ラダリングネットワーク分析</h4>
        <div class="insight-box">
            <p><strong>ネットワーク図の見方：</strong></p>
            <ul>
                <li><strong>ノード（丸）</strong> = ラダリングの選択肢（「高級感を感じる」「満足感が得られる」など）</li>
                <li><strong>矢印（→）</strong> = 同じ人に選ばれた関係（「高級感を感じる」→「満足感が得られる」）</li>
                <li><strong>太い矢印</strong> = 多くの人が一緒に選んだ関係（関係が強い）</li>
                <li><strong>たとえば：</strong> 「高級感を感じる」から「満足感が得られる」への矢印が太ければ、「高級感があると、満足感を感じる人が多い」という意味です</li>
            </ul>
        </div>
        <div class="chart">
            <img src="charts/""" + chart_files['C07-2'] + """" alt="ラダリングネットワーク分析">
        </div>
"""

# ラダリングTOP5
laddering = results["layer5_insights"]["laddering"]
html_content += """
        <h4>良い理由 TOP5</h4>
        <ol>
"""
why_good = sorted(laddering["why_good"].items(), key=lambda x: x[1], reverse=True)[:5]
for reason, count in why_good:
    html_content += f"<li>{reason} ({count}回)</li>"
html_content += """
        </ol>
        <h4>良い気持ち TOP5</h4>
        <ol>
"""
feeling_good = sorted(laddering["feeling_good"].items(), key=lambda x: x[1], reverse=True)[:5]
for feeling, count in feeling_good:
    html_content += f"<li>{feeling} ({count}回)</li>"
html_content += """
        </ol>
        <h3>最良・最悪音選択</h3>
        <div class="chart">
            <img src="charts/""" + chart_files['C08'] + """" alt="最良最悪音選択">
        </div>
    </div>
"""

html_content += """
    <!-- 提言 -->
    <div class="section">
        <h2>💼 提言</h2>
        <div class="insight-box">
            <h3>理想の走行音要件</h3>
"""

# 重要度から要件を導出
if "Prius" in importance and importance["Prius"]:
    html_content += """
            <h4>購買意欲を高める重要な要素（優先順位順）</h4>
            <ol>
"""
    for i, item in enumerate(importance["Prius"][:5], 1):
        axis_name = next((ax["name"] for ax in SD_AXES if ax["id"] == item["axis"]), item["axis"])
        html_content += f"<li>{axis_name}を重視した走行音設計</li>"
    html_content += """
            </ol>
"""

html_content += """
        </div>
    </div>

    <!-- 付録 -->
    <div class="section">
        <h2>📎 付録</h2>
        <h3>回答者属性詳細</h3>
        <div class="chart">
            <img src="charts/""" + chart_files['C01'] + """" alt="回答者属性分布">
        </div>
        <p><em>本レポートは自動生成されました。分析日時: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M') + """</em></p>
    </div>
</body>
</html>
"""

# HTMLファイル保存（UTF-8、BOMなし）
print("[DEBUG] HTMLファイル保存開始")
html_output = OUTPUT_DIR / "analysis_report.html"
try:
    with open(html_output, "w", encoding="utf-8", newline="") as f:
        f.write(html_content)
    print(f"[DEBUG] HTMLファイル保存完了: {html_output}")
    print(f"レポート生成完了: {html_output}")
except Exception as e:
    print(f"[ERROR] HTMLファイル保存エラー: {e}")
    print(f"[ERROR] エラー詳細: {type(e).__name__}: {str(e)}")
    import traceback
    print(f"[ERROR] トレースバック:")
    traceback.print_exc()
    raise

print("=" * 60)
