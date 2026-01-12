#!/bin/bash
# 文字エンコーディングをUTF-8に設定
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8

cd "$(dirname "$0")"

echo "============================================"
echo " Sample Data Generator"
echo " Generating 100 sample responses..."
echo "============================================"
echo ""

# 仮想環境の有効化
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "仮想環境が見つかりません。システムのPythonを使用します。"
fi

python scripts/generate_sample_data.py

echo ""
echo "============================================"
echo " Generation Complete!"
echo "============================================"
read -p "Press Enter to continue..."
