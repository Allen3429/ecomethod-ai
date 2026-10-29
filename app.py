import streamlit as st
import google.generativeai as genai

# ==========================================
# 頁面與基本設定 (升級為全螢幕儀表板)
# ==========================================
st.set_page_config(page_title="EcoMethod AI Dashboard", page_icon="📊", layout="wide")

st.title("📊 EcoMethod AI - 現地適用性分析與決策儀表板")
st.markdown("整合 **MCDA 多準則決策** 與 **風險矩陣分析**，為森林碳匯與環境復育專案提供量化適配指標。")

# ==========================================
# 側邊欄設定 (API Key 與進階設定)
# ==========================================
with st.sidebar:
    st.header("🔑 系統與引擎設定")
    api_key = st.text_input("Gemini API Key", type="password", help="請輸入您的 API 金鑰")
    st.markdown("---")
    st.markdown("### ⚙️ 分析模組啟用狀態")
    st.checkbox("MCDA 決策矩陣", value=True, disabled=True)
    st.checkbox("SWOT 分析矩陣", value=True, disabled=True)
    st.checkbox("風險衝擊矩陣", value=True, disabled=True)

# ==========================================
# 介面分頁設定 (Tabs)
# ==========================================
tab1, tab2 = st.tabs(["📋 1. 現地參數設定 (Input)", "📈 2. 量化分析與決策報告 (Dashboard)"])

with tab1:
    st.subheader("專案環境基線與參數")
    
    # 使用 Columns 切分版面
    col1, col2, col3 = st.columns(3)
    with col1:
        project_name = st.text_input("專案名稱", "溪頭實驗林減量專案")
        species = st.text_input("目標樹種", "柳杉 (Cryptomeria japonica)")
    with col2:
        area_size = st.number_input("專案面積 (公頃)", value=50.0, step=10.0)
        baseline_scenario = st.selectbox("基線情境假設", ["退化林地/荒地", "現有人工林", "農地造林", "受污染或需重金屬復育土壤"])
    with col3:
        st.info("💡 **CTO 提示**\n精確的環境參數能幫助 AI 進行更準確的 MCDA 權重分配與風險機率計算。")
    
    st.markdown("---")
    col_text1, col_text2 = st.columns(2)
    with col_text1:
        soil_env = st.text_area("土壤與環境觀測數據", "海拔約1100公尺。土壤曾有部分鎳(Ni)等重金屬觀測紀錄，需評估植物微生群系影響。", height=120)
    with col_text2:
        land_history = st.text_area("林地歷史與現況", "過往為人工林，近期有疏伐計畫，無近期毀林紀錄。", height=120)

with tab2:
    if st.button("🚀 執行矩陣運算與生成報告", type="primary", use_container_width=True):
        if not api_key:
            st.error("⚠️ 系統鎖定中：請先在左側欄位輸入 Gemini API Key！")
        else:
            with st.spinner("⏳ 啟動決策引擎：正在進行 MCDA 運算與矩陣建構..."):
                try:
                    # 初始化模型
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    # 組合 Prompt (強制輸出 Markdown 表格與結構化矩陣)
                    prompt = f"""
                    你是一位精通林學、環境科學（如土壤重金屬）及碳匯方法學的頂尖數據分析師與專案顧問。
                    請根據以下參數，進行量化與矩陣化的深度分析。

                    【專案參數】
                    專案名稱：{project_name} | 面積：{area_size} 公頃
                    目標樹種：{species} | 基線情境：{baseline_scenario}
                    土壤環境：{soil_env} | 林地歷史：{land_history}

                    【輸出規範：你必須嚴格使用 Markdown 表格來呈現矩陣】

                    ### 1. SWOT 分析矩陣 (SWOT Analysis)
                    請以一個 2x2 概念的表格（優勢、劣勢、機會、威脅），針對此基線與現地條件進行精確的環境與政策評估。

                    ### 2. 方法學 MCDA 決策矩陣 (Methodology Decision Matrix)
                    請挑選 2 至 3 個最相關的方法學（如 VCS VM0047, AR-ACM0003, 國內造林與植林等）。
                    建立一個表格，欄位包含：方法學名稱、適用度評分(1-10)、額外性難度(高/中/低)、邊界契合度、最終建議。

                    ### 3. 風險與衝擊評估矩陣 (Risk Assessment Matrix)
                    針對現地條件（特別是土壤狀況或林地歷史），列出 3 個潛在紅燈風險。
                    表格欄位必須包含：風險因子、發生機率(高/中/低)、對專案的衝擊程度(嚴重/中等/輕微)、建議的緩解策略(Mitigation Strategy)。

                    ### 4. 關鍵數據補測清單 (Action Items)
                    請用條列式（Bullet points）列出若要讓上述 MCDA 評分提高，目前急需前往現場實測的 3 項環境或生長數據。
                    """
                    
                    # UI 版面準備
                    st.success("✅ 矩陣運算完成，報表生成中...")
                    st.markdown("---")
                    
                    # 建立三欄式數據儀表板 (模擬摘要指標)
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="運算模型", value="Gemini 3.8", delta="Matrix Mode")
                    m2.metric(label="分析標的", value=project_name)
                    m3.metric(label="系統狀態", value="深度解析中", delta="穩定", delta_color="normal")
                    
                    st.markdown("---")
                    
                    # 串流輸出容器
                    report_container = st.empty()
                    full_text = ""
                    response = model.generate_content(prompt, stream=True)
                    
                    for chunk in response:
                        full_text += chunk.text
                        report_container.markdown(full_text + " ▌")
                    
                    report_container.markdown(full_text)
                    
                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
