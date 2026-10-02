"""The user's exact live acceptance material; test/probe input only."""

THREE_PHASE_TEXT = """三相平衡交流系統中，三相電流彼此相差 120°：

Ia(t) = A cos(ωt)
Ib(t) = A cos(ωt - 2π/3)
Ic(t) = A cos(ωt - 4π/3)

三個相電流分別沿著空間中相差 120° 的三個方向產生磁場分量。
三個磁場向量相加後形成合成旋轉磁場。
當時間改變時，各相電流的瞬時值會改變，磁場分量也會跟著改變，
但在理想平衡三相系統中，合成磁場會以穩定大小旋轉。

提高頻率會使旋轉磁場旋轉得更快；
提高振幅 A 則會增加各相電流與合成磁場的大小。"""


def acceptance_analysis():
    return dict(analysis_language="zh-TW", quick_summary=THREE_PHASE_TEXT,
                learning_scene_candidate=dict(suitable=True, domain="spatial_dynamics", reason="三相波形與旋轉向量共用時間。"))
