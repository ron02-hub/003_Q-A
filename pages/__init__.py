"""
ページモジュール
"""
from .phase1_introduction import render_phase1
from .phase2_evaluation import render_phase2
from .phase3_interview import render_phase3
from .phase4_rct import render_phase4
from .phase5_summary import render_phase5

__all__ = [
    "render_phase1",
    "render_phase2",
    "render_phase3",
    "render_phase4",
    "render_phase5",
]
