import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import random

# --------------------------
# 页面配置（浪漫全屏）
# --------------------------
st.set_page_config(page_title="💖 致星星", layout="wide")
st.markdown(
    """
    <h1 style='text-align: center; color: #ff4060; font-size: 48px;'>
        💌 致我最爱的星星
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------------
# 爱心数学公式（动态版）
# --------------------------
def heart_coords(t, scale=1.0):
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    return x * scale, y * scale

# --------------------------
# 动态爱心 + 粒子飘散
# --------------------------
fig, ax = plt.subplots(figsize=(8, 7), dpi=100)
ax.set_facecolor("#fff5f7")
fig.patch.set_facecolor("#fff5f7")
ax.axis("equal")
ax.axis("off")

# 渐变玫瑰色
cmap = LinearSegmentedColormap.from_list("", ["#ff9aab","#ff708a","#ff4060","#e60040"])

# 基础点
t = np.linspace(0, 2*np.pi, 800)
x, y = heart_coords(t)
scatter = ax.scatter(x, y, c=x+y, cmap=cmap, s=12, alpha=0.9)

# 粒子系统
particles = []
for _ in range(70):
    px = random.uniform(-10, 10)
    py = random.uniform(-10, 10)
    particles.append([px, py, random.uniform(2, 6), random.random()])
particle_scatter = ax.scatter([p[0] for p in particles], [p[1] for p in particles],
                             color="#ff4060", s=6, alpha=0.6)

# --------------------------
# 动画更新函数（会动！）
# --------------------------
def update(frame):
    # 爱心呼吸缩放
    scale = 1.0 + 0.06 * np.sin(frame / 8)
    x_new, y_new = heart_coords(t, scale)
    scatter.set_offsets(np.column_stack([x_new, y_new]))
    
    # 粒子上升飘散
    for p in particles:
        p[1] += 0.15
        p[0] += random.uniform(-0.1, 0.1)
        if p[1] > 15:
            p[1] = random.uniform(-12, -8)
            p[0] = random.uniform(-8, 8)
    particle_scatter.set_offsets(np.array([[p[0], p[1]] for p in particles]))
    
    return scatter, particle_scatter

# 启动动画
ani = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

# 中央表白文字
ax.text(0, -6, "星星 · 我喜欢你", fontsize=24, fontweight="bold",
        ha="center", color="white",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#ff4060", alpha=0.9))

# --------------------------
# 显示到 Streamlit
# --------------------------
st.pyplot(fig)

# --------------------------
# 底部浪漫文案
# --------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:22px; color:#ff4060;">
        遇见你之后<br>
        所有的温柔都有了方向<br>
        我的世界因你而闪闪发光<br>
        <b>我会永远偏爱你，守护你 ❤️</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h3 style='text-align:center; color:#e60040; margin-top:30px;'>
        ❤️ 只爱星星 · 永远永远 ❤️
    </h3>
    """,
    unsafe_allow_html=True
)

