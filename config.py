"""
EV走行音アンケートアプリケーション 設定ファイル
"""
import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent

# 素材ディレクトリ
MATERIAL_DIR = BASE_DIR / "99_Material"
TEST_AUDIO_DIR = MATERIAL_DIR / "00_Test"
SAMPLE_VIDEO_DIR = MATERIAL_DIR / "01_sample_Movie"
SAMPLE_AUDIO_DIR = MATERIAL_DIR / "01_sample_WAV"  # 音声ファイル用（バックアップ）

# データ保存ディレクトリ
DATA_DIR = BASE_DIR / "data"
RESPONSES_DIR = DATA_DIR / "responses"
EXPORTS_DIR = DATA_DIR / "exports"

# ディレクトリ作成
DATA_DIR.mkdir(exist_ok=True)
RESPONSES_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# テスト音声ファイル
TEST_AUDIO_FILE = TEST_AUDIO_DIR / "猫の鳴き声1.mp3"

# 走行音サンプル動画ファイル（メイン）
VIDEO_SAMPLES = {
    "Prius": SAMPLE_VIDEO_DIR / "01_NBox_Prius.mp4",
    "Fit": SAMPLE_VIDEO_DIR / "02_NBox_Fit.mp4",
    "Model3": SAMPLE_VIDEO_DIR / "03_NBox_Model3.mp4",
}

# 走行音サンプル音声ファイル（バックアップ/レガシー）
AUDIO_SAMPLES = {
    "Prius": SAMPLE_VIDEO_DIR / "01_NBox_Prius.mp4",
    "Fit": SAMPLE_VIDEO_DIR / "02_NBox_Fit.mp4",
    "Model3": SAMPLE_VIDEO_DIR / "03_NBox_Model3.mp4",
}

# 走行音サンプル名リスト（分析用）
SOUND_SAMPLES = list(VIDEO_SAMPLES.keys())

# アンケート設定
SURVEY_CONFIG = {
    "total_phases": 5,
    "target_duration_minutes": 45,
    "samples_per_evaluation": 3,  # 評価するサンプル数
}

# SD法評価軸
SD_AXES = [
    {"id": "volume", "name": "音量感", "left": "うるさい", "right": "静か"},
    {"id": "texture", "name": "質感", "left": "ざらざら", "right": "滑らか"},
    {"id": "pleasantness", "name": "快感情", "left": "不快", "right": "心地よい"},
    {"id": "arousal", "name": "覚醒", "left": "退屈", "right": "ワクワク"},
    {"id": "luxury", "name": "高級感", "left": "安っぽい", "right": "高級感がある"},
    {"id": "innovation", "name": "先進性", "left": "古臭い", "right": "先進的"},
    {"id": "power", "name": "パワー感", "left": "弱々しい", "right": "力強い"},
    {"id": "safety", "name": "安心感", "left": "不安", "right": "安心"},
    {"id": "naturalness", "name": "自然さ", "left": "人工的", "right": "自然"},
]

# 購買意欲選択肢
PURCHASE_INTENT_OPTIONS = [
    "1: 全く購入したくない",
    "2: あまり購入したくない",
    "3: どちらかといえば購入したくない",
    "4: どちらでもない",
    "5: どちらかといえば購入したい",
    "6: 購入したい",
    "7: 非常に購入したい",
]

# WTP選択肢
WTP_OPTIONS = [
    "0円（追加では支払いたくない）",
    "1万円まで",
    "3万円まで",
    "5万円まで",
    "10万円まで",
    "20万円まで",
    "30万円以上",
]

# 年齢グループ
AGE_GROUPS = ["20-29歳", "30-39歳", "40-49歳", "50-59歳", "60-70歳"]

# 性別選択肢
GENDER_OPTIONS = ["男性", "女性", "その他", "回答しない"]

# 都道府県
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]

# 音声チェック選択肢
AUDIO_CHECK_OPTIONS = [
    "猫の鳴き声",
    "犬の鳴き声",
    "鳥のさえずり",
    "車のエンジン音",
    "雨の音",
]
AUDIO_CHECK_CORRECT = "猫の鳴き声"

# ラダリング選択肢（上位概念 - なぜ良いか）20個
LADDERING_WHY_GOOD_OPTIONS = [
    "落ち着く感じがする",
    "高級感を感じる",
    "安心できる",
    "心地よい",
    "自然な感じがする",
    "力強さを感じる",
    "先進的な印象",
    "洗練されている",
    "品質が高い",
    "スムーズな印象",
    "清潔感がある",
    "信頼感がある",
    "上品な印象",
    "モダンな印象",
    "エレガントな印象",
    "プレミアム感がある",
    "静寂感がある",
    "調和がとれている",
    "心が和む",
    "期待感が高まる",
]

# ラダリング選択肢（上位概念 - どんな気持ち）20個
LADDERING_FEELING_GOOD_OPTIONS = [
    "満足感が得られる",
    "安心感が得られる",
    "自信が持てる",
    "リラックスできる",
    "ワクワクする",
    "誇らしい気持ちになる",
    "信頼感が生まれる",
    "幸福感を感じる",
    "穏やかな気持ちになる",
    "前向きな気持ちになる",
    "特別感を感じる",
    "優越感を感じる",
    "充実感がある",
    "心が豊かになる",
    "癒される",
    "所有欲が満たされる",
    "ステータスを感じる",
    "自己肯定感が高まる",
    "愛着が湧く",
    "長く使いたいと思う",
]

# ラダリング選択肢（下位概念 - なぜ悪いか）20個
LADDERING_WHY_BAD_OPTIONS = [
    "うるさく感じる",
    "安っぽく感じる",
    "不安になる",
    "不快に感じる",
    "人工的な感じがする",
    "弱々しく感じる",
    "古臭い印象",
    "雑な印象",
    "品質が低い",
    "不自然な印象",
    "違和感がある",
    "信頼感がない",
    "チープな印象",
    "時代遅れな印象",
    "野暮ったい印象",
    "安物感がある",
    "騒がしい印象",
    "調和が取れていない",
    "落ち着かない",
    "期待外れな印象",
]

# ラダリング選択肢（下位概念 - どんな気持ち）20個
LADDERING_FEELING_BAD_OPTIONS = [
    "不満を感じる",
    "不安になる",
    "自信がなくなる",
    "落ち着かない",
    "がっかりする",
    "恥ずかしい気持ちになる",
    "信頼できなくなる",
    "不快感を感じる",
    "イライラする",
    "後悔しそう",
    "損した気分になる",
    "愛着が湧かない",
    "すぐ手放したくなる",
    "人に見せたくない",
    "品質に疑問を感じる",
    "期待を裏切られた気持ち",
    "選択を間違えた気持ち",
    "残念な気持ち",
    "ストレスを感じる",
    "長く使いたくない",
]

# インタビュー質問
INTERVIEW_QUESTIONS = {
    "topic1": [
        "先ほど聴いていただいた走行音の中で、最も印象に残った音はどれでしたか？",
        "その音のどこが印象に残りましたか？",
        "その印象は、ポジティブでしたか、ネガティブでしたか？",
        "なぜそう感じたのですか？",
        "その気持ちは、EVを選ぶときに重要だと思いますか？",
    ],
    "topic2": [
        "もし新しいEVを購入するとしたら、走行音はどのくらい重要ですか？",
        "1から10で表すと、どのくらいの重要度ですか？",
        "価格、航続距離、デザインなど、他の要素と比べるとどうですか？",
    ],
    "topic3": [
        "あなたにとって理想的なEV走行音とは、どんな音だと思いますか？",
        "既存の車やその他の音で、イメージに近いものはありますか？",
    ],
}

# UIテーマ設定
THEME = {
    "primary_color": "#1E88E5",
    "background_color": "#FFFFFF",
    "secondary_background": "#F5F5F5",
    "text_color": "#212121",
    "accent_color": "#00897B",
}
