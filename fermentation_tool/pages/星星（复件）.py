import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import random

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(page_title="💖 For 星星", layout="wide")

st.markdown("""
<h1 style='text-align: center; color: #ff3366; font-size: 50px; text-shadow: 0 0 10px #ffccd5;'>
    💌 致我最爱的星星
</h1>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------
# 爱心公式
# --------------------------
def heart(t, scale=1):
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    return x * scale, y * scale

# --------------------------
# 绘图
# --------------------------
fig, ax = plt.subplots(figsize=(9, 8), dpi=110)
ax.set_facecolor("#fff0f5")
fig.patch.set_facecolor("#fff0f5")
ax.axis("equal")
ax.axis("off")

# 渐变色
cmap = LinearSegmentedColormap.from_list("", ["#ff8fab", "#ff5e87", "#ff2e63", "#ff0040"])

t = np.linspace(0, 2 * np.pi, 1000)
x, y = heart(t)

# 爱心点
scatter = ax.scatter(x, y, c=x+y, cmap=cmap, s=15, alpha=0.9)

# 粒子系统
particles = []
for _ in range(120):
    px = random.uniform(-10, 10)
    py = random.uniform(-12, 12)
    particles.append([px, py, random.uniform(0.3, 1.2), random.random()])

particle_scatter = ax.scatter(
    [p[0] for p in particles], [p[1] for p in particles],
    color="#ff3366", s=8, alpha=0.7
)

# --------------------------
# 超强动态效果
# --------------------------
def update(frame):
    # 1. 爱心呼吸跳动
    scale = 1.0 + 0.09 * np.sin(frame / 5)
    nx, ny = heart(t, scale)
    scatter.set_offsets(np.column_stack((nx, ny)))

    # 2. 粒子飘动 + 上升 + 飘散
    for p in particles:
        p[1] += 0.22
        p[0] += random.uniform(-0.18, 0.18)
        if p[1] > 16:
            p[1] = random.uniform(-14, -10)
            p[0] = random.uniform(-9, 9)

    particle_scatter.set_offsets(np.array([[p[0], p[1]] for p in particles]))

    return scatter, particle_scatter

# 启动动画
ani = FuncAnimation(fig, update, frames=120, interval=40, blit=True)

# --------------------------
# 中央表白文字（发光效果）
# --------------------------
ax.text(0, -6.5, "⭐ 星星 · 我超级喜欢你 ⭐",
        fontsize=28, fontweight="bold", ha="center",
        color="white",
        bbox=dict(boxstyle="round,pad=0.7", facecolor="#ff3366", alpha=0.9))

# --------------------------
# 显示动画
# --------------------------
st.pyplot(fig)

# --------------------------
# 底部动态表白文字
# --------------------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; font-size:26px; color:#ff3366; font-weight:bold; text-shadow: 0 0 8px #ffccd5;">
    遇见你之前 世界是平静的<br>
    遇见你之后 每一秒都是心动<br>
    <br>
    🌟 星星，你是我的全世界 🌟<br>
    <br>
    <span style="font-size:32px; color:#ff0040;">❤️ 我会一直爱你 ❤️</span>
</div>
""", unsafe_allow_html=True)


