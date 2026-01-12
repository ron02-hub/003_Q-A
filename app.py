"""
EV走行音アンケートアプリケーション

メインエントリーポイント
"""
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# パスの設定
import sys
sys.path.insert(0, str(Path(__file__).parent))

from config import DATA_DIR, THEME, SURVEY_CONFIG
from services.session_manager import SessionManager
from services.data_manager import DataManager
from pages.phase1_introduction import render_phase1
from pages.phase2_evaluation import render_phase2
from pages.phase3_interview import render_phase3
from pages.phase5_summary import render_phase5


def main():
    """メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title="EV走行音アンケート",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # セッション管理とデータ管理の初期化
    session = SessionManager()
    data_manager = DataManager(DATA_DIR)
    
    # カスタムCSS
    st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        .stProgress > div > div > div > div {
            background-color: #1E88E5;
        }
        .stRadio > div {
            gap: 0.5rem;
        }
        .stCheckbox > div {
            gap: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    _render_header(session)
    
    # メインコンテンツ
    _render_main_content(session, data_manager)
    
    # フッター
    _render_footer()


def _render_header(session: SessionManager) -> None:
    """ヘッダーをレンダリング"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 🚗 EV走行音アンケート")
    
    with col2:
        # 進捗バー
        progress = session.get_progress()
        st.progress(progress / 100)
        st.caption(f"進捗: {progress:.0f}%")
    
    st.markdown("---")


def _render_main_content(session: SessionManager, data_manager: DataManager) -> None:
    """メインコンテンツをレンダリング"""
    phase = session.current_phase
    step = session.current_step
    
    # A案: ページトップのアンカーポイントを設置
    st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)
    
    # B案: ページ遷移時に自動スクロールトップ
    _auto_scroll_to_top(phase, step)
    
    # フェーズインジケーター
    _render_phase_indicator(phase)
    
    # 各フェーズのレンダリング（Phase4削除、4がまとめに）
    if phase == 1:
        render_phase1(session)
    elif phase == 2:
        render_phase2(session)
    elif phase == 3:
        render_phase3(session)
    elif phase == 4:
        render_phase5(session, data_manager)
    else:
        st.error("不明なフェーズです")


def _render_phase_indicator(current_phase: int) -> None:
    """フェーズインジケーターをレンダリング"""
    phases = [
        ("Step1", "導入"),
        ("Step2", "評価"),
        ("Step3", "詳細調査"),
        ("Step4", "まとめ"),
    ]
    
    cols = st.columns(len(phases))
    
    for i, (step_name, phase_name) in enumerate(phases):
        phase_index = i + 1
        with cols[i]:
            if phase_index < current_phase:
                # 完了したフェーズ
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #E8F5E9; border-radius: 5px;">
                    <span style="color: #4CAF50;">✓</span> {step_name}
                </div>
                """, unsafe_allow_html=True)
            elif phase_index == current_phase:
                # 現在のフェーズ
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #E3F2FD; border-radius: 5px; border: 2px solid #1E88E5;">
                    <strong style="color: #1E88E5;">{step_name}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 未完了のフェーズ
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #F5F5F5; border-radius: 5px;">
                    <span style="color: #9E9E9E;">{step_name}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("")


def _auto_scroll_to_top(phase: int, step: int) -> None:
    """
    B案: ページ遷移時に自動でページトップにスクロール
    
    Args:
        phase: 現在のフェーズ
        step: 現在のステップ
    """
    # 現在のページを識別するキー
    current_key = f"{phase}_{step}"
    last_key = st.session_state.get('_last_scroll_key', '')
    
    # ページが変わった時のみスクロール実行
    if current_key != last_key:
        st.session_state['_last_scroll_key'] = current_key
        components.html(
            """
            <script>
                (function() {
                    try {
                        // 複数のコンテナをスクロールトップ
                        var selectors = [
                            '[data-testid="stAppViewContainer"]',
                            'section.main',
                            '.main',
                            '.stApp'
                        ];
                        for (var i = 0; i < selectors.length; i++) {
                            var el = window.parent.document.querySelector(selectors[i]);
                            if (el) {
                                el.scrollTop = 0;
                            }
                        }
                        // ウィンドウ自体もスクロール
                        window.parent.scrollTo(0, 0);
                        if (window.parent.document.body) {
                            window.parent.document.body.scrollTop = 0;
                        }
                        if (window.parent.document.documentElement) {
                            window.parent.document.documentElement.scrollTop = 0;
                        }
                    } catch (e) {
                        // エラーは無視
                    }
                })();
            </script>
            """,
            height=0,
        )


def _render_footer() -> None:
    """フッターをレンダリング"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #9E9E9E; font-size: 0.8em;">
        EV走行音アンケート調査 | © 2026
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
