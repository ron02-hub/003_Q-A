"""
アプリケーション起動スクリプト
"""
import os
import subprocess
import sys

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# カレントディレクトリを変更
os.chdir(script_dir)

# Streamlitアプリを起動
app_path = os.path.join(script_dir, "app.py")
print(f"Starting Streamlit app from: {app_path}")

subprocess.run([
    sys.executable, 
    "-m", 
    "streamlit", 
    "run", 
    app_path,
    "--server.headless", "true",
    "--server.port", "8501"
])
