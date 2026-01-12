"""
Phase 4: ランダム化比較試験
"""
import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.session_manager import SessionManager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.survey_components import render_navigation_buttons


def render_phase4(session: "SessionManager") -> None:
    """
    Phase 4をレンダリング
    
    Args:
        session: セッションマネージャー
    """
    step = session.current_step
    
    if step == 1:
        _render_rct_evaluation(session)
    else:
        # Phase 4完了、Phase 5へ
        session.next_phase()
        st.rerun()


def _render_rct_evaluation(session: "SessionManager") -> None:
    """ランダム化比較試験の評価画面"""
    st.markdown("## 総合比較評価")
    
    samples = session.sample_order or []
    group = session.group
    
    st.info(f"""
    🔬 **比較評価**
    
    あなたは **グループ {group}** に割り当てられています。
    
    先ほどの順序で聴いた走行音について、全体的な印象を教えてください。
    """)
    
    st.markdown("### 提示された走行音の順序")
    
    for i, sample in enumerate(samples, 1):
        st.markdown(f"{i}. **{sample}**")
    
    st.markdown("---")
    st.markdown("### 順序についての印象")
    
    order_impression = st.radio(
        "この順序で走行音を聴いたとき、全体的な印象はどうでしたか？",
        options=[
            "徐々に良くなった（後の方が良い印象）",
            "徐々に悪くなった（前の方が良い印象）",
            "中間が最も良かった",
            "中間が最も悪かった",
            "特に順序による影響は感じなかった",
        ],
        key="rct_order_impression",
    )
    
    st.markdown("---")
    st.markdown("### 順序の影響")
    
    order_influence = st.slider(
        "提示順序が評価に影響したと思いますか？（1: 全く影響なし 〜 10: 非常に影響あり）",
        min_value=1,
        max_value=10,
        value=5,
        key="rct_order_influence",
    )
    
    st.markdown("---")
    st.markdown("### 最終的な好み")
    
    final_preference = st.selectbox(
        "最終的に最も好みの走行音はどれですか？",
        options=samples,
        key="rct_final_preference",
        format_func=lambda x: f"走行音: {x}",
    )
    
    st.markdown("---")
    st.markdown("### 順序による評価変化（任意）")
    
    order_comment = st.text_area(
        "順序が評価に与えた影響について、何か気づいたことがあればお書きください",
        key="rct_order_comment",
        height=100,
        label_visibility="collapsed",
        placeholder="例: 最初に聴いた音が基準になった、最後の音が最も印象に残った など",
    )
    
    def on_next():
        session.save_response("rct_evaluation", {
            "group": group,
            "sample_order": samples,
            "order_impression": order_impression,
            "order_influence": order_influence,
            "final_preference": final_preference,
            "order_comment": order_comment,
        })
        session.next_step()
    
    def on_back():
        session.set_phase(3)
        session.set_step(4)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()
