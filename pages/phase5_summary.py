"""
Phase 5: まとめ・自由記述
"""
import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.session_manager import SessionManager
    from services.data_manager import DataManager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.survey_components import render_navigation_buttons


def render_phase5(session: "SessionManager", data_manager: "DataManager" = None) -> None:
    """
    Phase 5をレンダリング
    
    Args:
        session: セッションマネージャー
        data_manager: データマネージャー
    """
    step = session.current_step
    
    if step == 1:
        _render_overall_impression(session)
    elif step == 2:
        _render_additional_comments(session)
    elif step == 3:
        _render_completion(session, data_manager)
    else:
        # 完了状態を維持
        _render_completion(session, data_manager)


def _render_overall_impression(session: "SessionManager") -> None:
    """総合評価画面"""
    st.markdown("## Step4: 総合評価 (ページ 1)")
    
    st.info("""
    📝 **まとめ**
    
    アンケートもあと少しで終了です。
    全体を通しての感想をお聞かせください。
    """)
    
    st.markdown("### EV走行音について")
    
    overall_impression = st.text_area(
        "全体を通して、EV走行音についてどのように感じましたか？",
        key="overall_impression",
        height=200,
        label_visibility="visible",
        placeholder="今回のアンケートを通じて感じたこと、気づいたことなどを自由にお書きください",
    )
    
    def on_next():
        session.save_response("overall_impression", {
            "impression": overall_impression,
        })
        session.next_step()
    
    def on_back():
        session.set_phase(3)
        session.set_step(4)  # Phase 3の最後のステップ（理想の走行音）に戻る
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_additional_comments(session: "SessionManager") -> None:
    """追加コメント画面"""
    st.markdown("## Step4: 追加コメント (ページ 2)")
    
    st.markdown("### 他に伝えたいことはありますか？")
    
    additional_comments = st.text_area(
        "ご自由にお書きください（任意）",
        key="additional_comments",
        height=200,
        label_visibility="collapsed",
        placeholder="アンケートについてのご意見、走行音に関する追加のコメントなど",
    )
    
    st.markdown("---")
    st.markdown("### アンケートについてのフィードバック")
    
    survey_feedback = st.radio(
        "このアンケートは回答しやすかったですか？",
        options=[
            "とても回答しやすかった",
            "回答しやすかった",
            "普通",
            "やや回答しにくかった",
            "とても回答しにくかった",
        ],
        key="survey_feedback",
    )
    
    feedback_comment = st.text_area(
        "アンケートの改善点があればお書きください（任意）",
        key="feedback_comment",
        height=100,
        label_visibility="visible",
        placeholder="質問の分かりにくさ、時間の長さなど",
    )
    
    def on_next():
        session.save_response("additional_comments", {
            "comments": additional_comments,
            "survey_feedback": survey_feedback,
            "feedback_comment": feedback_comment,
        })
        session.next_step()
    
    def on_back():
        session.set_step(1)
    
    next_clicked, back_clicked = render_navigation_buttons(
        on_next=on_next,
        on_back=on_back,
        next_label="回答を送信",
    )
    
    if next_clicked or back_clicked:
        st.rerun()


def _render_completion(session: "SessionManager", data_manager: "DataManager" = None) -> None:
    """完了画面"""
    # アンケート完了処理
    if not session.is_completed:
        session.complete_survey()
        
        # データを保存
        if data_manager:
            try:
                data_manager.save_responses_json(
                    session.session_id,
                    session.get_all_data()
                )
            except Exception as e:
                st.error(f"データの保存中にエラーが発生しました: {e}")
    
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>✅ アンケートが完了しました</h1>
        <p style="font-size: 1.2em; color: #666;">
            ご協力いただき、誠にありがとうございました。
        </p>
        <p style="font-size: 1.1em;">
            あなたの回答は、EV走行音の研究開発に<br>
            役立てさせていただきます。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown("---")
    
    # セッション情報の表示
    with st.expander("回答情報"):
        st.markdown(f"""
        - **セッションID**: `{session.session_id}`
        - **グループ**: {session.group}
        - **完了時刻**: {session.get_response("completed_at", "不明")}
        """)
