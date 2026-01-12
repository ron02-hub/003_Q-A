"""
Phase 1: 導入・属性収集
"""
import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.session_manager import SessionManager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    AGE_GROUPS, GENDER_OPTIONS, PREFECTURES,
    AUDIO_CHECK_OPTIONS, AUDIO_CHECK_CORRECT, TEST_AUDIO_FILE,
)
from components.survey_components import (
    render_audio_player, render_navigation_buttons,
)


def render_phase1(session: "SessionManager") -> None:
    """
    Phase 1をレンダリング
    
    Args:
        session: セッションマネージャー
    """
    step = session.current_step
    
    if step == 1:
        _render_consent(session)
    elif step == 2:
        _render_basic_info(session)
    elif step == 3:
        _render_driving_experience(session)
    elif step == 4:
        _render_sound_sensitivity(session)
    elif step == 5:
        _render_audio_check(session)
    else:
        # Phase 1完了、Phase 2へ
        session.next_phase()
        st.rerun()


def _render_consent(session: "SessionManager") -> None:
    """同意取得画面"""
    st.markdown("## Step1: 調査への参加同意 (ページ 1)")
    
    st.info("""
    本アンケートは、EV走行音に関する研究調査です。
    所要時間は約45分です。
    
    あなたの回答は匿名化され、研究目的のみに使用されます。
    音声の再生が必要なため、ヘッドホンまたはイヤホンのご使用を推奨します。
    """)
    
    st.markdown("### 以下の点についてご同意ください")
    
    consent1 = st.checkbox("調査への参加に同意します", key="consent1")
    consent2 = st.checkbox("データが匿名化された上で研究目的に使用されることに同意します", key="consent2")
    consent3 = st.checkbox("音声の再生が必要なことを理解しています", key="consent3")
    
    all_consented = consent1 and consent2 and consent3
    
    def on_next():
        if all_consented:
            session.save_response("consent", {
                "participation": consent1,
                "data_usage": consent2,
                "audio_requirement": consent3,
            })
            session.next_step()
    
    next_clicked, _ = render_navigation_buttons(
        on_next=on_next,
        show_back=False,
        next_disabled=not all_consented,
    )
    
    if next_clicked and all_consented:
        st.rerun()


def _render_basic_info(session: "SessionManager") -> None:
    """基本属性入力画面"""
    st.markdown("## Step1: 基本情報 (ページ 2)")
    
    st.markdown("### 年齢")
    age_group = st.radio(
        "年齢グループを選択してください",
        options=AGE_GROUPS,
        key="age_group",
        horizontal=True,
        label_visibility="collapsed",
    )
    
    st.markdown("### 性別")
    gender = st.radio(
        "性別を選択してください",
        options=GENDER_OPTIONS,
        key="gender",
        horizontal=True,
        label_visibility="collapsed",
    )
    
    st.markdown("### お住まいの地域")
    prefecture = st.selectbox(
        "都道府県を選択してください",
        options=PREFECTURES,
        key="prefecture",
        label_visibility="collapsed",
    )
    
    def on_next():
        session.save_response("basic_info", {
            "age_group": age_group,
            "gender": gender,
            "prefecture": prefecture,
        })
        session.next_step()
    
    def on_back():
        session.set_step(1)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_driving_experience(session: "SessionManager") -> None:
    """運転経験入力画面"""
    st.markdown("## Step1: 運転経験 (ページ 3)")
    
    st.markdown("### 運転歴")
    driving_years = st.slider(
        "運転歴は何年ですか？",
        min_value=0,
        max_value=50,
        value=10,
        key="driving_years",
        help="運転免許を取得してからの年数",
    )
    st.caption(f"運転歴: {driving_years}年")
    
    st.markdown("### EV所有経験")
    ev_experience = st.radio(
        "電気自動車（EV）を所有した経験はありますか？",
        options=["はい", "いいえ"],
        key="ev_experience",
        horizontal=True,
    )
    
    def on_next():
        session.save_response("driving_experience", {
            "driving_years": driving_years,
            "ev_experience": ev_experience == "はい",
        })
        session.next_step()
    
    def on_back():
        session.set_step(2)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_sound_sensitivity(session: "SessionManager") -> None:
    """音への感度入力画面"""
    st.markdown("## Step1: 音への感度 (ページ 4)")
    
    st.markdown("### 周囲の音をどのくらい気にしますか？")
    
    sound_sensitivity = st.slider(
        "1（全く気にしない）〜 5（とても気にする）",
        min_value=1,
        max_value=5,
        value=3,
        key="sound_sensitivity",
    )
    
    sensitivity_labels = {
        1: "全く気にしない",
        2: "あまり気にしない",
        3: "どちらでもない",
        4: "やや気にする",
        5: "とても気にする",
    }
    st.caption(f"選択: {sensitivity_labels[sound_sensitivity]}")
    
    def on_next():
        session.save_response("sound_sensitivity", sound_sensitivity)
        session.next_step()
    
    def on_back():
        session.set_step(3)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_audio_check(session: "SessionManager") -> None:
    """音声チェック画面"""
    st.markdown("## Step1: 音声環境の確認 (ページ 5)")
    
    st.info("""
    🎧 **ヘッドホンまたはイヤホンの使用を推奨します**
    
    これから音声を再生しますので、周囲の環境が静かであることを確認してください。
    """)
    
    st.warning("""
    🔊 **音量調整のお願い**
    
    テスト音声を再生する前に、デバイスの音量を適切なレベルに調整してください。
    音量が大きすぎたり小さすぎたりすると、正確な評価ができない場合があります。
    
    **推奨**: 通常の会話が聞こえる程度の音量に設定してください。
    """)
    
    st.markdown("### テスト音声を再生してください")
    
    # 音声プレイヤー
    audio_played = render_audio_player(TEST_AUDIO_FILE, label="▶️ テスト音声")
    
    if audio_played:
        st.markdown("---")
        st.markdown("### 今の音声は何の音でしたか？")
        
        selected_answer = st.radio(
            "選択してください",
            options=AUDIO_CHECK_OPTIONS,
            key="audio_check_answer",
            label_visibility="collapsed",
        )
        
        # 前回の回答結果を表示
        if "audio_check_attempted" in st.session_state and st.session_state.audio_check_attempted:
            if selected_answer != AUDIO_CHECK_CORRECT:
                st.error("不正解です。もう一度音声を聴いて選択してください。")
        
        def on_next():
            st.session_state.audio_check_attempted = True
            if selected_answer == AUDIO_CHECK_CORRECT:
                session.save_response("audio_check", {
                    "passed": True,
                    "answer": selected_answer,
                })
                session.set_audio_check_passed(True)
                session.next_step()
        
        def on_back():
            session.set_step(4)
        
        is_correct = selected_answer == AUDIO_CHECK_CORRECT
        
        next_clicked, back_clicked = render_navigation_buttons(
            on_next=on_next,
            on_back=on_back,
            next_label="確認して次へ" if not is_correct else "次へ",
        )
        
        if next_clicked:
            if is_correct:
                st.rerun()
            else:
                st.session_state.audio_check_attempted = True
                st.rerun()
        elif back_clicked:
            st.rerun()
    else:
        st.warning("音声ファイルを読み込めませんでした。管理者にお問い合わせください。")
