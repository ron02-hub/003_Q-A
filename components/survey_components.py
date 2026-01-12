"""
アンケートUIコンポーネント
"""
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from typing import List, Optional, Tuple, Callable


def render_page_top_anchor() -> None:
    """
    ページトップのアンカーポイントを設置（A案）
    各ページの先頭で呼び出す
    """
    st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)


def render_scroll_to_top_script() -> None:
    """
    自動スクロールトップのJavaScriptを挿入（B案）
    ページ遷移時に自動的にトップにスクロール
    """
    # セッション状態でページ遷移を検出
    current_key = f"{st.session_state.get('current_phase', 1)}_{st.session_state.get('current_step', 1)}"
    last_key = st.session_state.get('_last_scroll_key', '')
    
    if current_key != last_key:
        st.session_state['_last_scroll_key'] = current_key
        # ページが変わった時のみスクロール実行
        components.html(
            """
            <script>
                (function() {
                    try {
                        // Streamlitのメインコンテナを取得してスクロール
                        var containers = [
                            window.parent.document.querySelector('[data-testid="stAppViewContainer"]'),
                            window.parent.document.querySelector('section.main'),
                            window.parent.document.querySelector('.main')
                        ];
                        for (var i = 0; i < containers.length; i++) {
                            if (containers[i]) {
                                containers[i].scrollTop = 0;
                            }
                        }
                        window.parent.scrollTo(0, 0);
                    } catch (e) {
                        console.log('Auto scroll error:', e);
                    }
                })();
            </script>
            """,
            height=0,
        )


def render_progress_bar(progress: float) -> None:
    """
    進捗バーを表示
    
    Args:
        progress: 進捗率（0-100）
    """
    st.progress(progress / 100)
    st.caption(f"進捗: {progress:.0f}%")


def render_sd_slider(
    axis_id: str,
    axis_name: str,
    left_label: str,
    right_label: str,
    key: str,
    default_value: int = 0,
) -> int:
    """
    SD法スライダーを表示
    
    Args:
        axis_id: 評価軸ID
        axis_name: 評価軸名
        left_label: 左極ラベル
        right_label: 右極ラベル
        key: Streamlitキー
        default_value: デフォルト値
        
    Returns:
        選択された値（-3〜+3）
    """
    st.markdown(f"**{axis_name}**")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown(f"<div style='text-align: right; color: #666;'>{left_label}</div>", unsafe_allow_html=True)
    
    with col2:
        value = st.slider(
            label=axis_name,
            min_value=-3,
            max_value=3,
            value=default_value,
            key=key,
            label_visibility="collapsed",
        )
    
    with col3:
        st.markdown(f"<div style='text-align: left; color: #666;'>{right_label}</div>", unsafe_allow_html=True)
    
    return value


def render_likert_scale(
    question: str,
    options: List[str],
    key: str,
    horizontal: bool = False,
) -> Optional[str]:
    """
    リッカート尺度を表示
    
    Args:
        question: 質問文
        options: 選択肢リスト
        key: Streamlitキー
        horizontal: 水平表示するか
        
    Returns:
        選択された値
    """
    st.markdown(f"**{question}**")
    
    if horizontal:
        return st.radio(
            label=question,
            options=options,
            key=key,
            horizontal=True,
            label_visibility="collapsed",
        )
    else:
        return st.radio(
            label=question,
            options=options,
            key=key,
            label_visibility="collapsed",
        )


def render_navigation_buttons(
    on_next: Optional[Callable] = None,
    on_back: Optional[Callable] = None,
    show_back: bool = True,
    next_label: str = "次へ",
    back_label: str = "戻る",
    next_disabled: bool = False,
    show_page_top: bool = True,
) -> Tuple[bool, bool]:
    """
    ナビゲーションボタンを表示
    
    Args:
        on_next: 次へボタンのコールバック
        on_back: 戻るボタンのコールバック
        show_back: 戻るボタンを表示するか
        next_label: 次へボタンのラベル
        back_label: 戻るボタンのラベル
        next_disabled: 次へボタンを無効化するか
        show_page_top: ページトップボタンを表示するか（A案）
        
    Returns:
        (次へが押されたか, 戻るが押されたか)
    """
    st.markdown("---")
    
    # 4列レイアウト: [戻る] [ページトップ] [空白] [次へ]
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    back_clicked = False
    next_clicked = False
    
    with col1:
        if show_back:
            if st.button(back_label, key="nav_back", use_container_width=True):
                back_clicked = True
                if on_back:
                    on_back()
    
    with col2:
        if show_page_top:
            # ページトップボタン（A案）- クリック時にJavaScriptでスクロール
            st.markdown(
                """
                <a href="#page-top" onclick="scrollToPageTop(); return false;" 
                   style="display: inline-block; width: 100%; text-align: center; 
                          padding: 0.5rem 1rem; background-color: #f0f2f6; 
                          border: 1px solid #d0d0d0; border-radius: 4px; 
                          text-decoration: none; color: #333; cursor: pointer;">
                    ⬆ ページトップ
                </a>
                <script>
                    function scrollToPageTop() {
                        try {
                            var containers = [
                                window.parent.document.querySelector('[data-testid="stAppViewContainer"]'),
                                window.parent.document.querySelector('section.main'),
                                window.parent.document.querySelector('.main')
                            ];
                            for (var i = 0; i < containers.length; i++) {
                                if (containers[i]) {
                                    containers[i].scrollTo({top: 0, behavior: 'smooth'});
                                }
                            }
                            window.parent.scrollTo({top: 0, behavior: 'smooth'});
                        } catch (e) {
                            console.log('Scroll error:', e);
                        }
                    }
                </script>
                """,
                unsafe_allow_html=True
            )
    
    with col4:
        if st.button(next_label, key="nav_next", use_container_width=True, disabled=next_disabled, type="primary"):
            next_clicked = True
            if on_next:
                on_next()
    
    return next_clicked, back_clicked


def render_audio_player(
    audio_path: Path,
    label: Optional[str] = None,
    autoplay: bool = False,
) -> bool:
    """
    音声プレイヤーを表示
    
    Args:
        audio_path: 音声ファイルのパス
        label: ラベル
        autoplay: 自動再生するか
        
    Returns:
        再生可能かどうか
    """
    if label:
        st.markdown(f"**{label}**")
    
    if not audio_path.exists():
        st.error(f"音声ファイルが見つかりません: {audio_path}")
        return False
    
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        
        st.audio(audio_bytes, format=f"audio/{audio_path.suffix[1:]}")
        return True
    except Exception as e:
        st.error(f"音声ファイルの読み込みに失敗しました: {e}")
        return False


def render_video_player(
    video_path: Path,
    label: Optional[str] = None,
    autoplay: bool = False,
) -> bool:
    """
    動画プレイヤーを表示
    
    Args:
        video_path: 動画ファイルのパス
        label: ラベル
        autoplay: 自動再生するか
        
    Returns:
        再生可能かどうか
    """
    if label:
        st.markdown(f"**{label}**")
    
    if not video_path.exists():
        st.error(f"動画ファイルが見つかりません: {video_path}")
        return False
    
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        # 動画ファイルの拡張子に応じてフォーマットを決定
        suffix = video_path.suffix.lower()
        if suffix in [".mp4", ".m4v"]:
            video_format = "video/mp4"
        elif suffix == ".webm":
            video_format = "video/webm"
        elif suffix == ".ogg":
            video_format = "video/ogg"
        elif suffix in [".wav", ".mp3"]:
            # 音声ファイルの場合は音声プレイヤーを使用
            st.audio(video_bytes, format=f"audio/{suffix[1:]}")
            return True
        else:
            video_format = "video/mp4"
        
        st.video(video_bytes, format=video_format)
        return True
    except Exception as e:
        st.error(f"動画ファイルの読み込みに失敗しました: {e}")
        return False


def render_multiselect_with_other(
    question: str,
    options: List[str],
    key: str,
    max_selections: int = 3,
    include_other: bool = True,
    other_label: str = "その他",
) -> Tuple[List[str], str]:
    """
    その他入力付き複数選択を表示
    
    Args:
        question: 質問文
        options: 選択肢リスト
        key: Streamlitキー
        max_selections: 最大選択数
        include_other: その他を含めるか
        other_label: その他のラベル
        
    Returns:
        (選択されたオプションのリスト, その他の入力内容)
    """
    st.markdown(f"**{question}**（{max_selections}つまで選択可能）")
    
    # チェックボックスで複数選択
    selected = []
    cols = st.columns(2)
    for i, option in enumerate(options):
        with cols[i % 2]:
            if st.checkbox(option, key=f"{key}_{i}"):
                if len(selected) < max_selections:
                    selected.append(option)
    
    other_text = ""
    if include_other:
        st.markdown("**その他（自由記述）**")
        other_text = st.text_input(
            label=other_label,
            key=f"{key}_other",
            label_visibility="collapsed",
            placeholder="その他の理由があれば入力してください",
        )
    
    return selected, other_text


def render_chat_message(role: str, content: str) -> None:
    """
    チャットメッセージを表示
    
    Args:
        role: 役割（"assistant" or "user"）
        content: メッセージ内容
    """
    with st.chat_message(role):
        st.markdown(content)


def render_sample_card(
    sample_id: str,
    sample_name: str,
    selected: bool = False,
    key: str = "",
) -> bool:
    """
    サンプル選択カードを表示
    
    Args:
        sample_id: サンプルID
        sample_name: サンプル名
        selected: 選択されているか
        key: Streamlitキー
        
    Returns:
        選択されたかどうか
    """
    container = st.container(border=True)
    with container:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{sample_name}**")
        with col2:
            is_selected = st.checkbox("選択", value=selected, key=key, label_visibility="collapsed")
    
    return is_selected
