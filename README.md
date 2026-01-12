# EV走行音アンケートアプリケーション

EV走行音のユーザー印象を評価し、購買意欲向上につながるサウンドデザインの構築を目指すWebアンケートアプリケーションです。

## 🎯 概要

- **対象**: 日本国内の成人（20〜70歳）
- **所要時間**: 約45分
- **評価手法**: SD法、評価グリッド法、デプスインタビュー、ランダム化比較試験

## 📁 ディレクトリ構成

```
003_アンケート設計/
├── app.py                      # メインアプリケーション
├── config.py                   # 設定ファイル
├── requirements.txt            # 依存パッケージ
├── README.md                   # 本ファイル
├── .streamlit/
│   └── config.toml             # Streamlit設定
├── components/                 # UIコンポーネント
│   ├── __init__.py
│   └── survey_components.py
├── pages/                      # 各フェーズのページ
│   ├── __init__.py
│   ├── phase1_introduction.py
│   ├── phase2_evaluation.py
│   ├── phase3_interview.py
│   ├── phase4_rct.py
│   └── phase5_summary.py
├── services/                   # ビジネスロジック
│   ├── __init__.py
│   ├── session_manager.py
│   └── data_manager.py
├── data/                       # データ保存（自動生成）
│   ├── responses/              # 回答データ
│   └── exports/                # エクスポートデータ
└── 99_Material/                # 素材ファイル
    ├── 00_Test/                # テスト用音声
    └── 01_sample_Movie/        # 走行音サンプル
```

## 🚀 セットアップ

### 1. Python環境の準備

Python 3.8以上が必要です。

```bash
# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501` でアプリケーションにアクセスできます。

## 📋 アンケートの流れ

### Phase 1: 導入・属性収集（約5分）
- 調査への同意取得
- 基本属性（年齢、性別、地域）
- 運転経験
- 音への感度
- 音声環境チェック

### Phase 2: 音声評価（約25分）

#### Phase 2-1: SD法評価
- 走行音サンプルの聴取
- 9軸×7段階の印象評価
- 購買意欲評価
- 価格受容性（WTP）評価

#### Phase 2-2: 評価グリッド法
- 最良・最悪音の選択
- ラダリング（上位・下位概念探索）

### Phase 3: デプスインタビュー（約8分）
- チャット形式の対話
- 印象的だった走行音について
- 購買決定要因
- 理想の走行音

### Phase 4: ランダム化比較試験（約4分）
- 提示順序の影響評価
- 最終的な好み

### Phase 5: まとめ（約3分）
- 総合評価
- 追加コメント
- アンケートへのフィードバック

## 📊 データ出力

回答データは以下の形式で保存されます：

- **JSON**: `data/responses/{session_id}.json`
- **CSV/Excel**: `data/exports/` にエクスポート可能

## 🔧 設定

### config.py

主な設定項目：
- 音声ファイルのパス
- SD法の評価軸
- 選択肢の定義
- UIテーマ

### .streamlit/config.toml

Streamlitのテーマ設定：
- プライマリカラー
- 背景色
- フォント

## 📝 ドキュメント

- `要件定義書.md` - 機能要件・非機能要件
- `技術設計書.md` - システムアーキテクチャ
- `アンケート設計.md` - アンケート詳細設計
- `タスク実装ステップ計画書.md` - 開発タスク
- `mdファイル管理.md` - ドキュメント管理

## ⚠️ 注意事項

1. **音声再生環境**: ヘッドホン/イヤホンの使用を推奨
2. **ブラウザ**: Chrome, Firefox, Safari, Edge（最新版）を推奨
3. **所要時間**: 約45分の集中した時間を確保してください

## 📈 更新履歴

| バージョン | 日付 | 内容 |
|------------|------|------|
| 1.0.0 | 2026-01-09 | 初版リリース |

## 📞 お問い合わせ

アンケートに関するお問い合わせは、管理者までご連絡ください。
