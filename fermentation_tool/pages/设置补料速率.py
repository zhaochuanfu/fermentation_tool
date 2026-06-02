import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os

# 解决中文乱码
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def calculate_step_area(x, y, x_start, x_end, where='post'):
    if where != 'post':
        raise NotImplementedError("仅支持post类型阶梯")
    if x_start > x_end:
        x_start, x_end = x_end, x_start
    area = 0.0
    for i in range(len(x)-1):
        x_left = x[i]
        x_right = x[i+1]
        current_y = y[i]
        overlap_left = max(x_left, x_start)
        overlap_right = min(x_right, x_end)
        if overlap_right > overlap_left:
            width = overlap_right - overlap_left
            area += current_y * width
    return area

def get_step_y_at_x(x_nodes, y_nodes, x_target):
    pos = np.searchsorted(x_nodes, x_target, side="right") - 1
    if 0 <= pos < len(y_nodes):
        return y_nodes[pos]
    return 0.0

# 页面配置
st.set_page_config(page_title="发酵补料计算工具", layout="wide")
st.title("🧪 发酵补料计算工具")
st.divider()

# 初始化会话状态存储曲线参数
if "save_x" not in st.session_state:
    st.session_state.save_x = "0,14,18,20,23,25,30,32.5,35,40,45,50"
if "save_y" not in st.session_state:
    st.session_state.save_y = "0,250,325,400,500,600,850,1000,1250,1750,2350,3000"

# 1. 发酵计划曲线
st.subheader("1. 发酵计划曲线")
col_x, col_y = st.columns(2)
with col_x:
    x_input = st.text_input("发酵时间h", value=st.session_state.save_x)
with col_y:
    y_input = st.text_input("计划补料速率g/h", value=st.session_state.save_y)

# 发酵计划保存/加载
st.markdown("---")
save_col1, save_col2, load_col = st.columns(3)
with save_col1:
    plan_name = st.text_input("方案名称", placeholder="输入名称保存当前计划")
with save_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 保存发酵计划"):
        os.makedirs("plans", exist_ok=True)
        with open(f"plans/{plan_name}.json", "w", encoding="utf-8") as f:
            json.dump({"x": x_input, "y": y_input}, f, ensure_ascii=False)
        st.success(f"已保存：{plan_name}")

# 读取已有方案
plan_list = ["选择方案加载"]
if os.path.exists("plans"):
    plan_list += [f[:-5] for f in os.listdir("plans") if f.endswith(".json")]

with load_col:
    st.markdown("<br>", unsafe_allow_html=True)
    load_plan = st.selectbox("📂 选择历史方案", plan_list)
    # 新增载入按钮
    if st.button("🔄 载入选中方案") and load_plan != "选择方案加载":
        with open(f"plans/{load_plan}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # 更新会话状态，刷新曲线参数
        st.session_state.save_x = data["x"]
        st.session_state.save_y = data["y"]
        st.rerun()

st.markdown("---")

# 2. 计算区间
st.subheader("2. 计算区间")
c1, c2 = st.columns(2)
with c1:
    x_start = st.number_input("起始时间", step=0.1)
with c2:
    x_end = st.number_input("结束时间", step=0.1)

# 3. 实际重量
st.subheader("3. 实际重量")
c3, c4 = st.columns(2)
with c3:
    start_weight = st.number_input("起始时间重量",  step=0.1)
with c4:
    end_weight = st.number_input("结束时间重量", step=0.1)

# 4. 泵速调节
st.subheader("4. 泵速调节")
c5, c6 = st.columns(2)
with c5:
    work_cycle = st.number_input("工作周期", step=0.1)
with c6:
    work_time = st.number_input("工作时间", value=1.3, step=0.1)

# 数据解析
try:
    x_nodes = [float(v.strip()) for v in x_input.split(",") if v.strip()]
    y_nodes = [float(v.strip()) for v in y_input.split(",") if v.strip()]
    valid = len(x_nodes) >= 2 and len(x_nodes) == len(y_nodes)
except:
    valid = False

if not valid:
    st.error("节点数据格式错误，请保证XY节点数量一致且不少于2个")
else:
    plan_weight = calculate_step_area(x_nodes, y_nodes, x_start, x_end)
    actual_weight = start_weight - end_weight
    plan_rate = get_step_y_at_x(x_nodes, y_nodes, x_end)

    if plan_weight > 0:
        actual_rate = plan_rate * actual_weight / plan_weight
    else:
        actual_rate = 0.0

    if actual_rate > 0 and plan_rate > 0:
        new_cycle = work_cycle * actual_rate / plan_rate
    else:
        new_cycle = 0.0

    # 计算结果（1位小数）
    st.divider()
    st.subheader("📊 计算结果")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("计划补料量", f"{plan_weight:.1f}")
    with col2:
        st.metric("实际补料量", f"{actual_weight:.1f}")
    with col3:
        st.metric("当前计划速率", f"{plan_rate:.1f}")
    with col4:
        st.metric("实际补料速率", f"{actual_rate:.1f}")
    with col5:
        st.metric("修改周期", f"{new_cycle:.1f}")

    # 各阶段周期数
    st.divider()
    st.subheader("⏱ 各阶段周期数变化")

    cycle_list = []
    if actual_rate > 0:
        for i in range(len(y_nodes)):
            rate = y_nodes[i]
            if rate <= 0:
                cyc = 0.0
            else:
                cyc = work_cycle * actual_rate / rate
            cycle_list.append({
                "时间节点": x_nodes[i],
                "计划速率": rate,
                "周期数": round(cyc, 1)
            })

    df = pd.DataFrame(cycle_list)
    st.dataframe(df, use_container_width=True)

    # 绘图
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.step(x_nodes, y_nodes, where="post", color="red", linewidth=2, label="plan-rate")
    x_fill = np.linspace(x_start, x_end, 1000)
    y_fill = np.zeros_like(x_fill)
    for idx, xi in enumerate(x_fill):
        pos = np.searchsorted(x_nodes, xi, side="right") - 1
        if 0 <= pos < len(y_nodes):
            y_fill[idx] = y_nodes[pos]

    ax.fill_between(x_fill, 0, y_fill, color="lightcoral", alpha=0.5, label=f"plan-weight：{plan_weight:.1f}")
    ax.set_xlabel("time")
    ax.set_ylabel("plan-rate")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

