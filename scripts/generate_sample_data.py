"""
サンプルデータ生成スクリプト
100名分の疑似アンケート回答データを生成
"""
import json
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import sys
import io

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SD_AXES, PURCHASE_INTENT_OPTIONS, WTP_OPTIONS,
    AGE_GROUPS, GENDER_OPTIONS, PREFECTURES,
    LADDERING_WHY_GOOD_OPTIONS, LADDERING_FEELING_GOOD_OPTIONS,
    LADDERING_WHY_BAD_OPTIONS, LADDERING_FEELING_BAD_OPTIONS,
)

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "sample_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# サンプル数
NUM_SAMPLES = 100

# 走行音サンプル
SOUND_SAMPLES = ["Prius", "Fit", "Model3"]

# 各サンプルの特性（SD評価のバイアス）
SAMPLE_CHARACTERISTICS = {
    "Prius": {
        "volume": 1.5,       # 静か寄り
        "texture": 1.0,      # 滑らか寄り
        "pleasantness": 1.0, # 心地よい寄り
        "arousal": -0.5,     # やや退屈寄り
        "luxury": 1.5,       # 高級感あり
        "innovation": 0.5,   # やや先進的
        "power": -0.5,       # やや弱め
        "safety": 1.5,       # 安心感あり
        "naturalness": 0.5,  # やや自然
    },
    "Model3": {
        "volume": 0.5,       # やや静か
        "texture": 0.5,      # やや滑らか
        "pleasantness": 0.5, # やや心地よい
        "arousal": 1.5,      # ワクワク
        "luxury": 1.0,       # 高級感あり
        "innovation": 2.0,   # 非常に先進的
        "power": 1.5,        # 力強い
        "safety": 0.5,       # やや安心
        "naturalness": -1.0, # やや人工的
    },
    "Fit": {
        "volume": 0.0,       # 普通
        "texture": 0.5,      # やや滑らか
        "pleasantness": 0.5, # やや心地よい
        "arousal": 0.0,      # 普通
        "luxury": -0.5,      # やや安っぽい
        "innovation": -0.5,  # やや古臭い
        "power": 0.0,        # 普通
        "safety": 0.5,       # やや安心
        "naturalness": 1.5,  # 自然
    },
}

# 運転経験オプション
DRIVING_EXPERIENCE_OPTIONS = ["1年未満", "1-5年", "5-10年", "10-20年", "20年以上"]

# EV経験オプション
EV_EXPERIENCE_OPTIONS = ["所有している", "試乗したことがある", "乗ったことはない"]

# 分布設定
AGE_DISTRIBUTION = [0.15, 0.25, 0.30, 0.20, 0.10]
GENDER_DISTRIBUTION = [0.55, 0.40, 0.025, 0.025]
DRIVING_EXPERIENCE_DISTRIBUTION = [0.05, 0.15, 0.25, 0.30, 0.25]
EV_EXPERIENCE_DISTRIBUTION = [0.20, 0.30, 0.50]


def weighted_choice(options, weights):
    """重み付きランダム選択"""
    return random.choices(options, weights=weights, k=1)[0]


def generate_demographics():
    """回答者属性を生成"""
    age_group = weighted_choice(AGE_GROUPS, AGE_DISTRIBUTION)
    gender = weighted_choice(GENDER_OPTIONS, GENDER_DISTRIBUTION)
    
    # 年齢に応じてEV経験を調整
    ev_weights = EV_EXPERIENCE_DISTRIBUTION.copy()
    if age_group in ["20-29歳", "30-39歳"]:
        ev_weights = [0.25, 0.35, 0.40]  # 若い世代はEV経験多め
    elif age_group in ["60-70歳"]:
        ev_weights = [0.10, 0.25, 0.65]  # 高齢世代はEV経験少なめ
    
    return {
        "age_group": age_group,
        "gender": gender,
        "prefecture": random.choice(PREFECTURES),
        "driving_experience": weighted_choice(DRIVING_EXPERIENCE_OPTIONS, DRIVING_EXPERIENCE_DISTRIBUTION),
        "ev_experience": weighted_choice(EV_EXPERIENCE_OPTIONS, ev_weights),
        "sound_sensitivity": random.randint(3, 8),  # 3-8の範囲で分布
    }


def generate_sd_rating(sample_id, axis_id, base_bias=0):
    """SD法評価を生成"""
    # サンプル特性によるバイアス
    sample_bias = SAMPLE_CHARACTERISTICS[sample_id].get(axis_id, 0)
    
    # 基本値（正規分布的）
    base_value = random.gauss(0, 1.2)
    
    # バイアスを適用
    value = base_value + sample_bias + base_bias
    
    # 範囲を制限（-3〜+3）
    value = max(-3, min(3, round(value)))
    
    return int(value)


def generate_evaluations(demographics):
    """評価データを生成"""
    # サンプル順序をランダム化
    sample_order = SOUND_SAMPLES.copy()
    random.shuffle(sample_order)
    
    # 音感度によるバイアス
    sensitivity_bias = (demographics["sound_sensitivity"] - 5) * 0.1
    
    # SD評価
    sd_ratings = {}
    for sample_id in SOUND_SAMPLES:
        sd_ratings[sample_id] = {}
        for axis in SD_AXES:
            sd_ratings[sample_id][axis["id"]] = generate_sd_rating(
                sample_id, axis["id"], sensitivity_bias
            )
    
    # 購買意欲（SD評価の平均に相関）
    purchase_intent = {}
    for sample_id in SOUND_SAMPLES:
        avg_rating = sum(sd_ratings[sample_id].values()) / len(sd_ratings[sample_id])
        # 平均評価を購買意欲に変換（1-7スケール）
        intent = int(4 + avg_rating * 0.8 + random.gauss(0, 0.8))
        purchase_intent[sample_id] = max(1, min(7, intent))
    
    # WTP（購買意欲に相関）
    wtp = {}
    for sample_id in SOUND_SAMPLES:
        intent = purchase_intent[sample_id]
        wtp_index = int((intent - 1) / 6 * 6 + random.gauss(0, 1))
        wtp_index = max(0, min(6, wtp_index))
        wtp[sample_id] = WTP_OPTIONS[wtp_index]
    
    # 自由コメント（テンプレートベース）
    free_comments = {}
    comment_templates = [
        "全体的に{感想}と感じました。",
        "{特徴}が印象的でした。",
        "この走行音は{評価}だと思います。",
        "{特徴}で、{感想}。",
        "もう少し{要望}があると良いと思います。",
    ]
    positive_impressions = ["良い", "心地よい", "落ち着く", "高級感がある", "先進的"]
    negative_impressions = ["うるさい", "安っぽい", "違和感がある", "不自然"]
    
    for sample_id in SOUND_SAMPLES:
        avg_rating = sum(sd_ratings[sample_id].values()) / len(sd_ratings[sample_id])
        if avg_rating > 0.5:
            impression = random.choice(positive_impressions)
        elif avg_rating < -0.5:
            impression = random.choice(negative_impressions)
        else:
            impression = "普通"
        
        template = random.choice(comment_templates)
        comment = template.format(
            感想=impression,
            特徴=random.choice(["静粛性", "質感", "力強さ", "高級感"]),
            評価=impression,
            要望=random.choice(["静かさ", "力強さ", "自然さ"]),
        )
        free_comments[sample_id] = comment
    
    return {
        "sample_order": sample_order,
        "sd_ratings": sd_ratings,
        "purchase_intent": purchase_intent,
        "wtp": wtp,
        "free_comments": free_comments,
    }


def generate_grid_evaluation(evaluations):
    """評価グリッド法の回答を生成"""
    # 各サンプルの平均評価を計算
    sample_scores = {}
    for sample_id, ratings in evaluations["sd_ratings"].items():
        sample_scores[sample_id] = sum(ratings.values()) / len(ratings)
    
    # 最良音と最悪音を選択
    sorted_samples = sorted(sample_scores.items(), key=lambda x: x[1], reverse=True)
    best_sound = sorted_samples[0][0]
    worst_sound = sorted_samples[-1][0]
    
    # ラダリング（良い理由）
    laddering_best = {
        "why_good": random.sample(LADDERING_WHY_GOOD_OPTIONS, k=random.randint(1, 3)),
        "feeling_good": random.sample(LADDERING_FEELING_GOOD_OPTIONS, k=random.randint(1, 3)),
    }
    
    # ラダリング（悪い理由）
    laddering_worst = {
        "why_bad": random.sample(LADDERING_WHY_BAD_OPTIONS, k=random.randint(1, 3)),
        "feeling_bad": random.sample(LADDERING_FEELING_BAD_OPTIONS, k=random.randint(1, 3)),
    }
    
    return {
        "best_sound": best_sound,
        "worst_sound": worst_sound,
        "laddering_best": laddering_best,
        "laddering_worst": laddering_worst,
    }


def generate_interview(demographics, grid_evaluation):
    """インタビュー回答を生成"""
    best_sound = grid_evaluation["best_sound"]
    
    # トピック1: 印象に残った走行音
    topic1_templates = [
        f"{best_sound}の走行音が最も印象的でした。静かで落ち着いた感じが良かったです。",
        f"{best_sound}は高級感があり、EVらしい先進性を感じました。",
        f"全体的にどの音も良かったですが、特に{best_sound}が心地よかったです。",
    ]
    
    # トピック2: 購買決定要因
    importance = random.randint(5, 9)
    topic2_templates = [
        f"走行音の重要度は{importance}/10くらいです。価格や航続距離の方が重要ですが、音も気になります。",
        f"重要度は{importance}/10です。試乗時に走行音を確認したいと思います。",
        f"正直あまり考えたことがなかったですが、{importance}/10くらいでしょうか。",
    ]
    
    # トピック3: 理想の走行音
    ideal_templates = [
        "静かすぎず、適度に存在感のある音が理想です。高級車のような質感があると良いですね。",
        "とにかく静かで、外の音も聞こえるくらいが良いです。安全面も考慮したいです。",
        "EVらしい先進的な音がいいですが、うるさくならない程度に。",
        "自然な感じで、長時間運転しても疲れない音が理想です。",
    ]
    
    return {
        "topic1": {
            "most_impressive": best_sound,
            "impression_detail": random.choice(topic1_templates),
            "positive_or_negative": "ポジティブ" if random.random() > 0.3 else "ネガティブ",
        },
        "topic2": {
            "sound_importance": importance,
            "comparison_with_others": random.choice(topic2_templates),
        },
        "topic3": {
            "ideal_sound": random.choice(ideal_templates),
        },
    }


def generate_summary():
    """まとめ回答を生成"""
    overall_templates = [
        "全体的に良い体験でした。EVの走行音について深く考える機会になりました。",
        "走行音の違いがこれほど印象に影響するとは思いませんでした。興味深い調査でした。",
        "EVの購入を検討しているので、参考になりました。",
        "もっと多くのサンプルを聴いてみたいと思いました。",
    ]
    
    additional_templates = [
        "特にありません。",
        "他のメーカーの走行音も聴いてみたいです。",
        "走行音だけでなく、車内の静粛性も重要だと思います。",
        "",
    ]
    
    return {
        "overall_impression": random.choice(overall_templates),
        "additional_comments": random.choice(additional_templates),
    }


def generate_single_response(index):
    """1名分の回答データを生成"""
    # タイムスタンプ（過去1週間のランダムな時刻）
    base_time = datetime.now() - timedelta(days=random.randint(0, 7))
    timestamp = base_time - timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    
    demographics = generate_demographics()
    evaluations = generate_evaluations(demographics)
    grid_evaluation = generate_grid_evaluation(evaluations)
    interview = generate_interview(demographics, grid_evaluation)
    summary = generate_summary()
    
    return {
        "response_id": index + 1,
        "session_id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "completed": True,
        "demographics": demographics,
        "evaluations": evaluations,
        "grid_evaluation": grid_evaluation,
        "interview": interview,
        "summary": summary,
    }


def generate_all_responses():
    """全回答データを生成"""
    print(f"Generating {NUM_SAMPLES} sample responses...")
    responses = []
    
    for i in range(NUM_SAMPLES):
        response = generate_single_response(i)
        responses.append(response)
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{NUM_SAMPLES} responses")
    
    return responses


def save_to_json(responses, filepath):
    """JSONファイルに保存"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    print(f"Saved to {filepath}")


def save_to_csv(responses, filepath):
    """CSVファイルに保存（フラット化）"""
    # フラット化したデータを作成
    flat_data = []
    
    for resp in responses:
        row = {
            "response_id": resp["response_id"],
            "session_id": resp["session_id"],
            "timestamp": resp["timestamp"],
            "age_group": resp["demographics"]["age_group"],
            "gender": resp["demographics"]["gender"],
            "prefecture": resp["demographics"]["prefecture"],
            "driving_experience": resp["demographics"]["driving_experience"],
            "ev_experience": resp["demographics"]["ev_experience"],
            "sound_sensitivity": resp["demographics"]["sound_sensitivity"],
            "best_sound": resp["grid_evaluation"]["best_sound"],
            "worst_sound": resp["grid_evaluation"]["worst_sound"],
        }
        
        # SD評価を展開
        for sample_id in SOUND_SAMPLES:
            for axis in SD_AXES:
                key = f"sd_{sample_id}_{axis['id']}"
                row[key] = resp["evaluations"]["sd_ratings"][sample_id][axis["id"]]
            
            # 購買意欲とWTP
            row[f"purchase_intent_{sample_id}"] = resp["evaluations"]["purchase_intent"][sample_id]
            row[f"wtp_{sample_id}"] = resp["evaluations"]["wtp"][sample_id]
        
        # インタビュー
        row["sound_importance"] = resp["interview"]["topic2"]["sound_importance"]
        
        flat_data.append(row)
    
    # CSVに書き出し
    if flat_data:
        fieldnames = flat_data[0].keys()
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_data)
    
    print(f"Saved to {filepath}")


def main():
    """メイン処理"""
    print("=" * 50)
    print("Sample Data Generator")
    print("=" * 50)
    
    # データ生成
    responses = generate_all_responses()
    
    # 保存
    json_path = OUTPUT_DIR / "sample_responses.json"
    csv_path = OUTPUT_DIR / "sample_responses.csv"
    
    save_to_json(responses, json_path)
    save_to_csv(responses, csv_path)
    
    # 統計情報を表示
    print("\n" + "=" * 50)
    print("Generation Complete!")
    print("=" * 50)
    print(f"Total responses: {len(responses)}")
    
    # 属性分布を確認
    age_dist = {}
    gender_dist = {}
    ev_dist = {}
    best_dist = {}
    
    for resp in responses:
        age = resp["demographics"]["age_group"]
        gender = resp["demographics"]["gender"]
        ev = resp["demographics"]["ev_experience"]
        best = resp["grid_evaluation"]["best_sound"]
        
        age_dist[age] = age_dist.get(age, 0) + 1
        gender_dist[gender] = gender_dist.get(gender, 0) + 1
        ev_dist[ev] = ev_dist.get(ev, 0) + 1
        best_dist[best] = best_dist.get(best, 0) + 1
    
    print("\n--- Age Distribution ---")
    for age, count in sorted(age_dist.items()):
        print(f"  {age}: {count} ({count/len(responses)*100:.1f}%)")
    
    print("\n--- Gender Distribution ---")
    for gender, count in sorted(gender_dist.items()):
        print(f"  {gender}: {count} ({count/len(responses)*100:.1f}%)")
    
    print("\n--- EV Experience Distribution ---")
    for ev, count in sorted(ev_dist.items()):
        print(f"  {ev}: {count} ({count/len(responses)*100:.1f}%)")
    
    print("\n--- Best Sound Selection ---")
    for sound, count in sorted(best_dist.items()):
        print(f"  {sound}: {count} ({count/len(responses)*100:.1f}%)")
    
    print("\n" + "=" * 50)
    print(f"Output files:")
    print(f"  - {json_path}")
    print(f"  - {csv_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
