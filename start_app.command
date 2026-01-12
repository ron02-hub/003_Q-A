#!/bin/bash
# 文字エンコーディングをUTF-8に設定
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8

cd "$(dirname "$0")"

# 仮想環境の有効化（存在する場合）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python -m streamlit run app.py
