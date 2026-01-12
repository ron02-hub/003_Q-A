"""
セッション管理モジュール
"""
import uuid
import random
from datetime import datetime
from typing import Any, Dict, Optional
import streamlit as st


class SessionManager:
    """セッション状態を管理するクラス"""
    
    def __init__(self):
        """セッションマネージャーの初期化"""
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """セッション状態を初期化"""
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if "current_phase" not in st.session_state:
            st.session_state.current_phase = 1
        
        if "current_step" not in st.session_state:
            st.session_state.current_step = 1
        
        if "responses" not in st.session_state:
            st.session_state.responses = {}
        
        if "start_time" not in st.session_state:
            st.session_state.start_time = datetime.now().isoformat()
        
        if "group" not in st.session_state:
            st.session_state.group = self._assign_group()
        
        if "sample_order" not in st.session_state:
            st.session_state.sample_order = None
        
        if "completed" not in st.session_state:
            st.session_state.completed = False
        
        if "audio_check_passed" not in st.session_state:
            st.session_state.audio_check_passed = False
    
    def _assign_group(self) -> str:
        """ランダムにグループを割り当て"""
        return random.choice(["A", "B"])
    
    @property
    def session_id(self) -> str:
        """セッションIDを取得"""
        return st.session_state.session_id
    
    @property
    def current_phase(self) -> int:
        """現在のフェーズを取得"""
        return st.session_state.current_phase
    
    @property
    def current_step(self) -> int:
        """現在のステップを取得"""
        return st.session_state.current_step
    
    @property
    def group(self) -> str:
        """割り当てグループを取得"""
        return st.session_state.group
    
    @property
    def responses(self) -> Dict[str, Any]:
        """回答データを取得"""
        return st.session_state.responses
    
    @property
    def sample_order(self) -> Optional[list]:
        """サンプル順序を取得"""
        return st.session_state.sample_order
    
    def set_sample_order(self, order: list) -> None:
        """サンプル順序を設定"""
        st.session_state.sample_order = order
    
    def next_step(self) -> None:
        """次のステップへ進む"""
        st.session_state.current_step += 1
    
    def next_phase(self) -> None:
        """次のフェーズへ進む"""
        st.session_state.current_phase += 1
        st.session_state.current_step = 1
    
    def set_phase(self, phase: int) -> None:
        """フェーズを設定"""
        st.session_state.current_phase = phase
        st.session_state.current_step = 1
    
    def set_step(self, step: int) -> None:
        """ステップを設定"""
        st.session_state.current_step = step
    
    def save_response(self, key: str, value: Any) -> None:
        """回答を保存"""
        st.session_state.responses[key] = value
    
    def get_response(self, key: str, default: Any = None) -> Any:
        """回答を取得"""
        return st.session_state.responses.get(key, default)
    
    def get_progress(self) -> float:
        """進捗率を取得（0-100）"""
        # フェーズごとのステップ数（概算）- Phase4（RCT）削除後
        phase_steps = {
            1: 5,  # 導入・属性収集
            2: 10,  # SD法評価 + 評価グリッド法
            3: 5,  # デプスインタビュー
            4: 3,  # まとめ（旧Phase5）
        }
        
        total_steps = sum(phase_steps.values())
        completed_steps = sum(phase_steps.get(i, 0) for i in range(1, self.current_phase))
        completed_steps += min(self.current_step, phase_steps.get(self.current_phase, 1))
        
        return min(100, (completed_steps / total_steps) * 100)
    
    def set_audio_check_passed(self, passed: bool) -> None:
        """音声チェック結果を設定"""
        st.session_state.audio_check_passed = passed
    
    @property
    def audio_check_passed(self) -> bool:
        """音声チェック結果を取得"""
        return st.session_state.audio_check_passed
    
    def complete_survey(self) -> None:
        """アンケートを完了"""
        st.session_state.completed = True
        st.session_state.responses["completed_at"] = datetime.now().isoformat()
    
    @property
    def is_completed(self) -> bool:
        """アンケートが完了したかを取得"""
        return st.session_state.completed
    
    def get_all_data(self) -> Dict[str, Any]:
        """全てのセッションデータを取得"""
        return {
            "session_id": self.session_id,
            "group": self.group,
            "start_time": st.session_state.start_time,
            "current_phase": self.current_phase,
            "current_step": self.current_step,
            "sample_order": self.sample_order,
            "completed": self.is_completed,
            "responses": self.responses,
        }
    
    def reset(self) -> None:
        """セッションをリセット"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self._initialize_session()
