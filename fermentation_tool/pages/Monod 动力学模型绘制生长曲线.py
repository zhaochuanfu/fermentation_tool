import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import streamlit as st

# -------------------------- 全局设置 --------------------------
plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# -------------------------- 1. 定义模型函数 --------------------------
def monod_model(S, mu_max, Ks):
    """Monod 模型"""
    return mu_max * S / (Ks + S)

def calc_specific_growth_rate(t, X):
    """
    由时间t、菌体浓度X(OD) 计算逐点比生长速率 μ
    :param t: 时间数组
    :param X: OD/菌体浓度数组
    :return: mu 数组（长度比原数组少1）
    """
    mu_list = []
    for i in range(len(t)-1):
        dt = t[i+1] - t[i]
        if dt <= 0 or X[i] <= 0 or X[i+1] <= 0:
            mu_list.append(np.nan)
            continue
        mu = (np.log(X[i+1]) - np.log(X[i])) / dt
        mu_list.append(mu)
    return np.array(mu_list)

# -------------------------- 2. Streamlit 页面主体 --------------------------
st.set_page_config(page_title="Monod模型拟合工具", layout="wide")
st.title("🧫 发酵 OD时序数据 → 比生长速率 → Monod模型拟合")
st.markdown("""
**使用说明**
1. 输入/粘贴数据：时间 t(h)、OD600、底物浓度 S(g/L)
2. 程序自动计算比生长速率 μ
3. 拟合 Monod 模型，输出 μmax、Ks、拟合优度 R²
4. 查看生长曲线 & 拟合曲线图
""")

# 左右分栏
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📥 数据输入")
    input_mode = st.radio("数据录入方式", ["手动逐行输入", "粘贴文本数据"])

    # 方式1：手动输入
    if input_mode == "手动逐行输入":
        row_num = st.number_input("数据行数", min_value=3, max_value=50, value=8)
        data_rows = []
        for r in range(row_num):
            cols = st.columns(3)
            t_val = cols[0].number_input(f"t{r+1} (h)", value=float(r), step=0.1, key=f"t{r}")
            od_val = cols[1].number_input(f"OD{r+1}", value=1.0, step=0.1, key=f"od{r}")
            s_val = cols[2].number_input(f"S{r+1} (g/L)", value=5.0, step=0.1, key=f"s{r}")
            data_rows.append([t_val, od_val, s_val])
        df_raw = pd.DataFrame(data_rows, columns=["t(h)", "OD600", "S(g/L)"])

    # 方式2：粘贴文本
    else:
        st.info("格式：每行 时间 OD 底物浓度，空格/制表分隔")
        txt_data = st.text_area("粘贴数据", value="""0   0.2   20
1   0.35  18
2   0.62  15
3   1.10  11
4   1.85  7
5   2.60  4
6   3.20  2
7   3.40  0.5""", height=200)
        lines = txt_data.strip().split("\n")
        data_list = []
        for line in lines:
            parts = list(map(float, line.strip().split()))
            if len(parts) == 3:
                data_list.append(parts)
        df_raw = pd.DataFrame(data_list, columns=["t(h)", "OD600", "S(g/L)"])

    st.dataframe(df_raw, use_container_width=True)
    run_btn = st.button("🚀 开始计算 & 拟合", type="primary")

# -------------------------- 3. 计算与拟合逻辑 --------------------------
if run_btn:
    t_arr = df_raw["t(h)"].values
    od_arr = df_raw["OD600"].values
    s_arr = df_raw["S(g/L)"].values

    # 计算比生长速率
    mu_arr = calc_specific_growth_rate(t_arr, od_arr)
    # 对应底物浓度（取区间前点底物浓度）
    s_mu = s_arr[:-1]

    # 过滤无效值
    valid_idx = ~np.isnan(mu_arr) & (mu_arr > 0)
    s_valid = s_mu[valid_idx]
    mu_valid = mu_arr[valid_idx]

    if len(s_valid) < 3:
        st.error("有效数据点不足3个，无法拟合！请检查数据")
    else:
        # 拟合 Monod
        try:
            popt, pcov = curve_fit(monod_model, s_valid, mu_valid,
                                   bounds=((0, 0), (5.0, 50.0)))
            mu_max_fit, Ks_fit = popt

            # 计算 R²
            mu_fit = monod_model(s_valid, mu_max_fit, Ks_fit)
            ss_res = np.sum((mu_valid - mu_fit) ** 2)
            ss_tot = np.sum((mu_valid - np.mean(mu_valid)) ** 2)
            r2 = 1 - (ss_res / ss_tot)

            # 结果汇总表
            res_df = pd.DataFrame({
                "t_start(h)": t_arr[:-1][valid_idx],
                "S(g/L)": s_valid,
                "μ(1/h)": mu_valid
            })

            with col2:
                st.subheader("📊 计算 & 拟合结果")
                st.success("拟合完成！")
                st.markdown(f"""
                **Monod 模型参数**
                - 最大比生长速率 **μmax** = `{mu_max_fit:.4f}` 1/h
                - 半饱和常数 **Ks**     = `{Ks_fit:.4f}` g/L
                - 拟合优度 **R²**       = `{r2:.4f}`
                """)
                st.dataframe(res_df, use_container_width=True)

                # -------- 图1：菌体生长曲线 (OD-t) --------
                fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
                ax1.plot(t_arr, od_arr, "o-", color="#1f77b4", linewidth=2, markersize=6)
                ax1.set_xlabel("时间 t (h)")
                ax1.set_ylabel("OD600")
                ax1.set_title("菌体生长曲线 (OD-时间)")
                ax1.grid(alpha=0.3)
                st.pyplot(fig1)

                # -------- 图2：μ-S 散点 + Monod拟合曲线 --------
                fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)
                # 实验点
                ax2.scatter(s_valid, mu_valid, color="#d62728", s=60, label="实验 μ 数据", zorder=5)
                # 拟合平滑曲线
                s_smooth = np.linspace(min(s_valid), max(s_valid), 100)
                mu_smooth = monod_model(s_smooth, mu_max_fit, Ks_fit)
                ax2.plot(s_smooth, mu_smooth, color="#2ca02c", linewidth=2, label="Monod 拟合曲线")

                ax2.set_xlabel("底物浓度 S (g/L)")
                ax2.set_ylabel("比生长速率 μ (1/h)")
                ax2.set_title(f"Monod 模型拟合 | μmax={mu_max_fit:.3f}, Ks={Ks_fit:.3f}, R²={r2:.4f}")
                ax2.legend()
                ax2.grid(alpha=0.3)
                st.pyplot(fig2)

        except Exception as e:
            st.error(f"拟合失败：{str(e)}，请检查数据合理性（浓度/速率不能为负）")

