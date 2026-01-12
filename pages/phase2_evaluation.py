"""
Phase 2: 音声評価・定量評価 & 評価グリッド法
"""
import streamlit as st
import random
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from services.session_manager import SessionManager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    AUDIO_SAMPLES, SD_AXES, PURCHASE_INTENT_OPTIONS, WTP_OPTIONS,
    SURVEY_CONFIG, LADDERING_WHY_GOOD_OPTIONS, LADDERING_FEELING_GOOD_OPTIONS,
    LADDERING_WHY_BAD_OPTIONS, LADDERING_FEELING_BAD_OPTIONS,
)
from components.survey_components import (
    render_audio_player, render_video_player, render_sd_slider, render_navigation_buttons,
    render_multiselect_with_other,
)


def render_phase2(session: "SessionManager") -> None:
    """
    Phase 2をレンダリング
    
    Args:
        session: セッションマネージャー
    """
    # サンプル順序の初期化
    if session.sample_order is None:
        samples = list(AUDIO_SAMPLES.keys())
        if session.group == "A":
            random.shuffle(samples)
        else:
            random.shuffle(samples)
            samples.reverse()
        # 評価するサンプル数に制限
        samples = samples[:SURVEY_CONFIG["samples_per_evaluation"]]
        session.set_sample_order(samples)
    
    step = session.current_step
    samples = session.sample_order
    num_samples = len(samples)
    
    # ステップの構成:
    # 1: 前提条件説明
    # 2〜num_samples+1: 各サンプルのSD法評価
    # num_samples+2: 最良・最悪音の選択
    # num_samples+3: 最良音のラダリング
    # num_samples+4: 最悪音のラダリング
    
    if step == 1:
        _render_precondition(session, num_samples)
    elif step <= num_samples + 1:
        _render_sd_evaluation(session, samples[step - 2], step - 1, num_samples)
    elif step == num_samples + 2:
        _render_best_worst_selection(session, samples)
    elif step == num_samples + 3:
        _render_laddering_good(session)
    elif step == num_samples + 4:
        _render_laddering_bad(session)
    else:
        # Phase 2完了、Phase 3へ
        session.next_phase()
        st.rerun()


def _render_precondition(session: "SessionManager", num_samples: int) -> None:
    """前提条件説明画面"""
    st.markdown("## Step2: 走行音評価 (ページ 1)")
    
    st.info("""
    🚗 **これから走行音の評価を行います**
    
    以下の条件で、電気自動車の走行シーンを動画で視聴していただきます。
    """)
    
    st.markdown("---")
    st.markdown("### 評価対象車両")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        **車両プロファイル:**
        - **外観**: Honda N-Box
        - **価格**: 200万円
        - **燃費**: 20.0km/L（WLTCモード）
        - **その他の考慮事項**:
          - 維持費（税金・保険料）の安さ
          - 先進安全装備（Honda SENSING）の充実
          - 室内空間の広さと使い勝手
          - リセールバリュー（下取り価格）の高さ
        """)
    
    with col2:
        # N-Boxの外観イメージ（テキストで代替）
        st.markdown("""
        <div style="background-color: #f0f0f0; padding: 40px; text-align: center; border-radius: 10px;">
            <p style="font-size: 60px; margin: 0;">🚗</p>
            <p style="color: #666; margin-top: 10px;">Honda N-Box</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 評価の流れ")
    
    st.success(f"""
    📹 **動画視聴について**
    
    - 走行シーンの動画を **{num_samples}種類** 視聴していただきます
    - 各動画を視聴後、**印象評価** を行います
    - すべての動画視聴後、**追加の質問**があります
    
    ⏱️ 所要時間: 約15〜20分
    """)
    
    def on_next():
        session.next_step()
    
    def on_back():
        session.set_phase(1)
        session.set_step(5)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
        next_label="動画視聴を開始",
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _get_ordinal_name(num: int) -> str:
    """序数を日本語に変換"""
    ordinals = {1: "1つ目", 2: "2つ目", 3: "3つ目", 4: "4つ目", 5: "5つ目"}
    return ordinals.get(num, f"{num}つ目")


def _render_sd_evaluation(session: "SessionManager", sample_id: str, current_num: int, total_num: int) -> None:
    """SD法評価画面"""
    ordinal = _get_ordinal_name(current_num)
    page_num = current_num + 1  # 前提条件ページが1なので+1
    st.markdown(f"## Step2: 走行音評価 ({current_num}/{total_num}) (ページ {page_num})")
    
    st.info(f"""
    🎵 **走行音 {ordinal}**
    
    以下の動画を視聴して、印象を評価してください。
    動画は何度でも再生できます。
    """)
    
    # 動画プレイヤー
    video_path = AUDIO_SAMPLES.get(sample_id)
    if video_path:
        render_video_player(video_path, label=f"▶️ 走行音 {ordinal}")
    else:
        st.error(f"音声ファイルが見つかりません: {sample_id}")
        return
    
    st.markdown("---")
    st.markdown("### 印象評価")
    st.caption("各項目について、-3（左）〜+3（右）の範囲で評価してください。")
    
    # SD法スライダー
    sd_scores = {}
    for axis in SD_AXES:
        score = render_sd_slider(
            axis_id=axis["id"],
            axis_name=axis["name"],
            left_label=axis["left"],
            right_label=axis["right"],
            key=f"sd_{sample_id}_{axis['id']}",
            default_value=session.get_response(f"sd_{sample_id}_{axis['id']}", 0),
        )
        sd_scores[axis["id"]] = score
    
    st.markdown("---")
    st.markdown("### 購買意欲")
    
    st.markdown("""
    **前提条件（車両プロファイル）:**
    - 外観: Honda N-Box
    - 価格: 200万円
    - 燃費: 20.0km/L（WLTCモード）
    """)
    
    purchase_intent = st.radio(
        "この走行音を持つ車を購入したいと思いますか？",
        options=PURCHASE_INTENT_OPTIONS,
        key=f"purchase_intent_{sample_id}",
    )
    
    st.markdown("---")
    st.markdown("### 価格受容性（WTP）")
    
    wtp = st.radio(
        "この走行音が理想的だとしたら、車両価格（200万円）に対して、さらにいくらまでなら追加で支払えますか？",
        options=WTP_OPTIONS,
        key=f"wtp_{sample_id}",
    )
    
    st.markdown("---")
    st.markdown("### 自由記述（任意）")
    
    free_comment = st.text_area(
        "この走行音について、何か感じたことがあればお書きください。",
        key=f"free_comment_{sample_id}",
        height=100,
        label_visibility="collapsed",
        placeholder="自由にご記入ください（任意）",
    )
    
    def on_next():
        # 回答を保存
        session.save_response(f"evaluation_{sample_id}", {
            "sample_id": sample_id,
            "sd_scores": sd_scores,
            "purchase_intent": purchase_intent,
            "wtp": wtp,
            "free_comment": free_comment,
        })
        session.next_step()
    
    def on_back():
        if session.current_step > 2:
            session.set_step(session.current_step - 1)
        else:
            session.set_step(1)  # 前提条件説明に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_best_worst_selection(session: "SessionManager", samples: List[str]) -> None:
    """最良・最悪音の選択画面"""
    num_samples = len(samples)
    st.markdown(f"## Step2: トータル評価 (ページ {num_samples + 2})")
    
    st.markdown("""
    先ほど視聴していただいた走行音について、最も印象が良かったものと悪かったものを選んでください。
    """)
    
    # サンプルのインデックスに基づく表示名を作成
    sample_display_names = {s: f"走行音 {_get_ordinal_name(i+1)}" for i, s in enumerate(samples)}
    
    st.markdown("### 最も印象が良かった走行音")
    best_sound = st.radio(
        "最も印象が良かった走行音を選択してください",
        options=samples,
        key="best_sound",
        format_func=lambda x: sample_display_names.get(x, x),
        label_visibility="collapsed",
    )
    
    st.markdown("### 最も印象が悪かった走行音")
    # 全ての選択肢を表示（最良と同じものも選択可能に）
    worst_sound = st.radio(
        "最も印象が悪かった走行音を選択してください",
        options=samples,
        key="worst_sound",
        format_func=lambda x: sample_display_names.get(x, x),
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    st.markdown("### 評価軸の選択")
    
    axis_options = [f"{axis['name']}（{axis['left']} ↔ {axis['right']}）" for axis in SD_AXES]
    
    st.markdown("**最も印象が良かった理由として、どの評価軸が最も当てはまりますか？**")
    best_axis = st.selectbox(
        "評価軸を選択",
        options=axis_options,
        key="best_axis",
        label_visibility="collapsed",
    )
    
    st.markdown("**最も印象が悪かった理由として、どの評価軸が最も当てはまりますか？**")
    worst_axis = st.selectbox(
        "評価軸を選択",
        options=axis_options,
        key="worst_axis",
        label_visibility="collapsed",
    )
    
    def on_next():
        session.save_response("grid_selection", {
            "best_sound": best_sound,
            "worst_sound": worst_sound,
            "best_axis": best_axis,
            "worst_axis": worst_axis,
        })
        session.next_step()
    
    def on_back():
        session.set_step(len(samples) + 1)  # 最後のSD評価に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_laddering_good(session: "SessionManager") -> None:
    """ラダリング（良い方）画面"""
    num_samples = len(session.sample_order or [])
    page_num = num_samples + 3
    st.markdown(f"## Step2: ラダリング（上位概念探索） (ページ {page_num})")
    
    grid_selection = session.get_response("grid_selection", {})
    best_sound = grid_selection.get("best_sound", "")
    best_axis = grid_selection.get("best_axis", "")
    
    st.info(f"""
    **{best_sound}** の走行音について、**{best_axis}** が良いと感じた理由を深掘りします。
    """)
    
    st.markdown("### なぜそれが良いと感じましたか？")
    why_good, why_good_other = render_multiselect_with_other(
        question="当てはまるものを選択してください",
        options=LADDERING_WHY_GOOD_OPTIONS,
        key="laddering_why_good",
        max_selections=3,
    )
    
    st.markdown("---")
    st.markdown("### それが得られるとどんな気持ちになりますか？")
    feeling_good, feeling_good_other = render_multiselect_with_other(
        question="当てはまるものを選択してください",
        options=LADDERING_FEELING_GOOD_OPTIONS,
        key="laddering_feeling_good",
        max_selections=3,
    )
    
    st.markdown("---")
    st.markdown("### 他に似た音の例はありますか？")
    similar_sound_good = st.text_area(
        "自由にご記入ください",
        key="similar_sound_good",
        height=100,
        label_visibility="collapsed",
        placeholder="例: 高級車のエンジン音、電車の発車音など",
    )
    
    def on_next():
        session.save_response("laddering_good", {
            "why_good": why_good,
            "why_good_other": why_good_other,
            "feeling_good": feeling_good,
            "feeling_good_other": feeling_good_other,
            "similar_sound": similar_sound_good,
        })
        session.next_step()
    
    def on_back():
        session.set_step(len(session.sample_order) + 2)  # 最良・最悪音の選択に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_laddering_bad(session: "SessionManager") -> None:
    """ラダリング（悪い方）画面"""
    num_samples = len(session.sample_order or [])
    page_num = num_samples + 4
    st.markdown(f"## Step2: ラダリング（下位概念探索） (ページ {page_num})")
    
    grid_selection = session.get_response("grid_selection", {})
    worst_sound = grid_selection.get("worst_sound", "")
    worst_axis = grid_selection.get("worst_axis", "")
    
    st.info(f"""
    **{worst_sound}** の走行音について、**{worst_axis}** が悪いと感じた理由を深掘りします。
    """)
    
    st.markdown("### なぜそれが悪いと感じましたか？")
    why_bad, why_bad_other = render_multiselect_with_other(
        question="当てはまるものを選択してください",
        options=LADDERING_WHY_BAD_OPTIONS,
        key="laddering_why_bad",
        max_selections=3,
    )
    
    st.markdown("---")
    st.markdown("### それによってどんな気持ちになりますか？")
    feeling_bad, feeling_bad_other = render_multiselect_with_other(
        question="当てはまるものを選択してください",
        options=LADDERING_FEELING_BAD_OPTIONS,
        key="laddering_feeling_bad",
        max_selections=3,
    )
    
    st.markdown("---")
    st.markdown("### 他に似た音の例はありますか？")
    similar_sound_bad = st.text_area(
        "自由にご記入ください",
        key="similar_sound_bad",
        height=100,
        label_visibility="collapsed",
        placeholder="例: 安い電化製品の音、古い冷蔵庫の音など",
    )
    
    def on_next():
        session.save_response("laddering_bad", {
            "why_bad": why_bad,
            "why_bad_other": why_bad_other,
            "feeling_bad": feeling_bad,
            "feeling_bad_other": feeling_bad_other,
            "similar_sound": similar_sound_bad,
        })
        session.next_step()
    
    def on_back():
        session.set_step(len(session.sample_order) + 3)  # 上位概念探索に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()
