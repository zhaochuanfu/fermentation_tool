import streamlit as st
import cobra
import pandas as pd
import io
from cobra.io import load_model
 
# -------------------------- 页面设置 --------------------------
st.set_page_config(
    page_title="COBRApy 学习平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📘 COBRApy 学习与可视化平台")


# 初始化模型
if "model" not in st.session_state:
    st.session_state.model = None

# -------------------------- 侧边栏 --------------------------

# 侧边栏
with st.sidebar:
    st.header("1️⃣ 模型加载")
    st.info("使用 cobrapy 自带测试模型，无需上传！")

    # ✅ 一键加载官方教科书模型（你给的示例代码）
    if st.button("✅ 加载教科书模型 iAF1260b"):
        try:
            # 这就是你发的官方代码！！！
            model = load_model("iAF1260b")
            
            st.session_state.model = model
            st.success(f"""
            ✅ 加载成功！
            反应：{len(model.reactions)}
            代谢物：{len(model.metabolites)}
            基因：{len(model.genes)}
            """)
            
        except Exception as e:
            st.error(f"错误：{str(e)}")

    # 重置
    st.divider()
    if st.button("🔄 重置模型"):
        st.session_state.model = None
        st.rerun()

model = st.session_state.model
if model is None:
    st.warning("👈 请先上传 SBML 模型（.xml）")
    st.markdown("""
    **学习用模型下载：**
    - e_coli_core.xml  （推荐）
    - iJO1366.xml
    - textbook.xml
    """)
    st.stop()

# -------------------------- 模型基本信息 --------------------------
st.subheader("2️⃣ 模型基本信息")
col1, col2, col3, col4 = st.columns(4)
col1.metric("反应数量", len(model.reactions))
col2.metric("代谢物数量", len(model.metabolites))
col3.metric("基因数量", len(model.genes))
col4.metric("分区", len(model.compartments))

with st.expander("查看分区详情"):
    st.write(model.compartments)

st.divider()

# -------------------------- FBA 模拟 --------------------------
st.subheader("3️⃣ FBA 通量平衡分析")
if st.button("🚀 运行 FBA"):
    with st.spinner("计算中..."):
        sol = model.optimize()
        st.session_state.solution = sol
        st.success(f"✅ 计算完成！生长速率：{sol.objective_value:.6f}")

if "solution" in st.session_state:
    sol = st.session_state.solution
    fluxes = []
    for r in model.reactions:
        fluxes.append({
            "反应ID": r.id,
            "反应公式": r.build_reaction_string(),
            "通量值": sol.fluxes[r.id]
        })
    df = pd.DataFrame(fluxes)
    st.dataframe(df, use_container_width=True)

    # 导出Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="FBA通量")
    st.download_button("📥 导出通量结果", buffer, "fba_fluxes.xlsx")

st.divider()

# -------------------------- FVA 通量变异分析 --------------------------
st.subheader("4️⃣ FVA 通量变异分析")
fva_fraction = st.slider("最优百分比", 0.5, 1.0, 0.95)
if st.button("📊 运行 FVA"):
    with st.spinner("正在进行FVA..."):
        try:
            fva_res = cobra.flux_analysis.flux_variability_analysis(
                model, fraction_of_optimum=fva_fraction
            )
            st.dataframe(fva_res, use_container_width=True)
        except Exception as e:
            st.error(f"FVA失败：{e}")

st.divider()

# -------------------------- 基因敲除 --------------------------
st.subheader("5️⃣ 单基因敲除模拟")
if len(model.genes) > 0:
    gene_ids = [g.id for g in model.genes]
    selected_gene = st.selectbox("选择要敲除的基因", gene_ids)
    if st.button("🔬 执行敲除"):
        with model:
            gene = model.genes.get_by_id(selected_gene)
            gene.knock_out()
            sol_ko = model.optimize()
            st.warning(f"敲除后生长速率：{sol_ko.objective_value:.6f}")
else:
    st.info("该模型无基因信息")

st.divider()

# -------------------------- 反应浏览 --------------------------
st.subheader("6️⃣ 反应查看")
search = st.text_input("搜索反应ID")
rxn_list = [r for r in model.reactions if search in r.id]
show_rxns = st.slider("显示数量", 10, 200, 50)

rxn_data = []
for r in rxn_list[:show_rxns]:
    rxn_data.append({
        "ID": r.id,
        "名称": r.name,
        "公式": r.build_reaction_string(),
        "下界": r.lower_bound,
        "上界": r.upper_bound
    })

st.dataframe(pd.DataFrame(rxn_data), use_container_width=True)

st.divider()
st.success("✅ 功能全部基于 COBRApy 官方文档实现")


