@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo  EV走行音アンケート データ分析実行
echo ============================================
echo.

REM 仮想環境の存在確認
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
    echo 仮想環境を有効化しました
) else (
    echo 仮想環境が見つかりません。システムのPythonを使用します。
    echo.
    echo 必要なライブラリをインストール中...
    python -m pip install --upgrade pip >nul 2>&1
    REM 分析に必要なライブラリのみインストール（エラーを無視）
    python -m pip install pandas numpy matplotlib seaborn scipy scikit-learn openpyxl >nul 2>&1
    echo ライブラリのインストール処理を完了しました。
    echo （一部のライブラリが既にインストール済みの場合はエラーが表示されることがありますが、問題ありません）
)
echo.

echo [Step 1/3] データ分析を実行中...
python scripts\run_analysis.py
if errorlevel 1 (
    echo エラー: データ分析に失敗しました
    pause
    exit /b 1
)
echo.

echo [Step 2/3] 可視化を生成中...
python scripts\visualization.py
if errorlevel 1 (
    echo エラー: 可視化生成に失敗しました
    pause
    exit /b 1
)
echo.

echo [Step 3/3] レポートを生成中...
python scripts\report_generator.py
if errorlevel 1 (
    echo エラー: レポート生成に失敗しました
    pause
    exit /b 1
)
echo.

echo ============================================
echo  分析完了！
echo ============================================
echo.
echo 出力ファイル:
echo   - data\analysis\analysis_results.json
echo   - data\analysis\analysis_results.xlsx
echo   - data\analysis\analysis_report.html
echo   - data\analysis\charts\*.png
echo.
pause
