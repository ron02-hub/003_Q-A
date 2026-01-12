"""
Phase 3: デプスインタビュー型質問
"""
import streamlit as st
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from services.session_manager import SessionManager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import INTERVIEW_QUESTIONS
from components.survey_components import render_navigation_buttons


def render_phase3(session: "SessionManager") -> None:
    """
    Phase 3をレンダリング
    
    Args:
        session: セッションマネージャー
    """
    step = session.current_step
    
    if step == 1:
        _render_interview_intro(session)
    elif step == 2:
        _render_interview_topic2(session)  # 順番変更: 購買決定要因を先に
    elif step == 3:
        _render_interview_topic1(session)  # 順番変更: 印象に残った走行音を後に
    elif step == 4:
        _render_interview_topic3(session)
    else:
        # Phase 3完了、Phase 4へ
        session.next_phase()
        st.rerun()


def _render_interview_intro(session: "SessionManager") -> None:
    """インタビュー導入画面"""
    st.markdown("## Step3: 詳細調査 (ページ 1)")
    
    st.markdown("""
    これから、走行音についていくつか質問させていただきます。
    あなたの率直なお気持ちをお聞かせください。
    
    正解や不正解はありませんので、思ったことを自由にお答えください。
    """)
    
    st.markdown("""
    ### 質問の流れ
    
    1. **購買決定要因について** - 走行音の重要度
    2. **印象に残った走行音について** - 最も印象的だった音の詳細
    3. **理想の走行音について** - あなたにとっての理想
    """)
    
    def on_next():
        session.next_step()
    
    def on_back():
        session.set_phase(2)
        # Phase 2の最後のステップへ
        samples = session.sample_order or []
        session.set_step(len(samples) + 4)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
        next_label="インタビューを始める",
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _get_ordinal_name(num: int) -> str:
    """序数を日本語に変換"""
    ordinals = {1: "1つ目", 2: "2つ目", 3: "3つ目", 4: "4つ目", 5: "5つ目"}
    return ordinals.get(num, f"{num}つ目")


def _render_interview_topic1(session: "SessionManager") -> None:
    """トピック1: 印象に残った走行音について（順番変更で2番目に表示）"""
    st.markdown("## Step3: 印象に残った走行音について (ページ 3)")
    
    samples = session.sample_order or []
    
    # サンプルの表示名を作成
    sample_display_names = {s: f"走行音 {_get_ordinal_name(i+1)}" for i, s in enumerate(samples)}
    
    # チャット風の表示
    _render_assistant_message("先ほど視聴していただいた走行音の中で、最も印象に残った音はどれでしたか？")
    
    impressive_sound = st.selectbox(
        "走行音を選択",
        options=samples,
        key="interview_impressive_sound",
        format_func=lambda x: sample_display_names.get(x, x),
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    
    _render_assistant_message("その音のどこが印象に残りましたか？")
    
    impressive_reason = st.text_area(
        "印象に残った点",
        key="interview_impressive_reason",
        height=100,
        label_visibility="collapsed",
        placeholder="例: 静かで落ち着く感じがした、力強さを感じた など",
    )
    
    st.markdown("---")
    
    _render_assistant_message("その印象は、ポジティブでしたか、ネガティブでしたか？")
    
    impression_type = st.radio(
        "印象のタイプ",
        options=["ポジティブ", "ネガティブ", "どちらでもない"],
        key="interview_impression_type",
        horizontal=True,
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    
    _render_assistant_message("なぜそう感じたのですか？")
    
    impression_why = st.text_area(
        "理由",
        key="interview_impression_why",
        height=100,
        label_visibility="collapsed",
        placeholder="その印象を受けた理由を教えてください",
    )
    
    def on_next():
        session.save_response("interview_topic1", {
            "impressive_sound": impressive_sound,
            "impressive_reason": impressive_reason,
            "impression_type": impression_type,
            "impression_why": impression_why,
        })
        session.next_step()
    
    def on_back():
        session.set_step(2)  # 購買決定要因に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_interview_topic2(session: "SessionManager") -> None:
    """トピック2: 購買決定要因について（順番変更で1番目に表示）"""
    st.markdown("## Step3: 購買決定要因について (ページ 2)")
    
    _render_assistant_message("価格、航続距離、デザインなど、車を購入する際の各要素について重要度を教えてください。")
    
    st.markdown("**各要素の重要度を評価してください（1〜10）**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        price_importance = st.slider("価格", 1, 10, 7, key="importance_price")
        range_importance = st.slider("航続距離", 1, 10, 6, key="importance_range")
        design_importance = st.slider("デザイン", 1, 10, 5, key="importance_design")
    
    with col2:
        brand_importance = st.slider("ブランド", 1, 10, 4, key="importance_brand")
        safety_importance = st.slider("安全性能", 1, 10, 8, key="importance_safety")
        sound_compare = st.slider("走行音", 1, 10, 5, key="importance_sound_compare")
    
    st.markdown("---")
    
    comparison_comment = st.text_area(
        "他の要素との比較について、コメントがあればお書きください（任意）",
        key="interview_comparison_comment",
        height=100,
        label_visibility="visible",
        placeholder="例: 走行音は価格ほど重要ではないが、安全性と同じくらい気になる など",
    )
    
    def on_next():
        session.save_response("interview_topic2", {
            "importance_comparison": {
                "price": price_importance,
                "range": range_importance,
                "design": design_importance,
                "brand": brand_importance,
                "safety": safety_importance,
                "sound": sound_compare,
            },
            "comparison_comment": comparison_comment,
        })
        session.next_step()
    
    def on_back():
        session.set_step(1)  # 導入画面に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_interview_topic3(session: "SessionManager") -> None:
    """トピック3: 理想の走行音について"""
    st.markdown("## Step3: 理想の走行音について (ページ 4)")
    
    _render_assistant_message("あなたにとって理想的なEV走行音とは、どんな音だと思いますか？")
    
    ideal_sound_description = st.text_area(
        "理想の走行音を自由に描写してください",
        key="interview_ideal_sound",
        height=150,
        label_visibility="collapsed",
        placeholder="例: 静かだけど存在感がある音、自然で心地よい音、高級感のある重厚な音 など",
    )
    
    st.markdown("---")
    
    _render_assistant_message("既存の車やその他の音で、イメージに近いものはありますか？")
    
    similar_examples = st.text_area(
        "イメージに近い音の例",
        key="interview_similar_examples",
        height=100,
        label_visibility="collapsed",
        placeholder="例: Tesla Model Sの音、新幹線の発車音、高級オーディオのような音 など",
    )
    
    st.markdown("---")
    
    _render_assistant_message("最後に、EV走行音に関して他に伝えたいことはありますか？")
    
    additional_thoughts = st.text_area(
        "その他のコメント（任意）",
        key="interview_additional_thoughts",
        height=100,
        label_visibility="collapsed",
        placeholder="走行音に関する意見や要望があればお書きください",
    )
    
    def on_next():
        session.save_response("interview_topic3", {
            "ideal_sound_description": ideal_sound_description,
            "similar_examples": similar_examples,
            "additional_thoughts": additional_thoughts,
        })
        session.next_step()
    
    def on_back():
        session.set_step(3)  # 印象に残った走行音に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_assistant_message(content: str) -> None:
    """アシスタントメッセージを表示"""
    with st.chat_message("assistant"):
        st.markdown(content)
