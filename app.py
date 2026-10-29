import streamlit as st
import google.generativeai as genai

# ==========================================
# 頁面與基本設定
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
# 📋 第一區塊：參數設定 (Input)
# ==========================================
st.header("📋 1. 現地參數設定")

col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.text_input("專案名稱", "溪頭實驗林減量專案")
    species = st.text_input("目標樹種", "柳杉 (Cryptomeria japonica)")
with col2:
    area_size = st.number_input("專案面積 (公頃)", value=50.0, step=10.0)
    baseline_scenario = st.selectbox("基線情境假設", ["退化林地/荒地", "現有人工林", "農地造林", "受污染或需重金屬復育土壤"])
with col3:
    st.info("💡 確保參數精確，能提升 MCDA 權重分配與風險機率計算的準確度。")

col_text1, col_text2 = st.columns(2)
with col_text1:
    soil_env = st.text_area("土壤與環境觀測數據", "海拔約1100公尺。土壤曾有部分鎳(Ni)等重金屬觀測紀錄，需評估植物微生群系影響。", height=100)
with col_text2:
    land_history = st.text_area("林地歷史與現況", "過往為人工林，近期有疏伐計畫，無近期毀林紀錄。", height=100)

st.markdown("<br>", unsafe_allow_html=True) # 增加一點留白

# ==========================================
# 🚀 執行按鈕與動態展開的第二區塊
# ==========================================
if st.button("🚀 執行矩陣運算與生成報告", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ 系統鎖定中：請先在左側欄位輸入 Gemini API Key！")
    else:
        # 動態展開第二區塊標題
        st.markdown("---")
        st.header("📈 2. 量化分析與決策報告")
        
        try:
            # 建立進度條元件
            my_bar = st.progress(5, text="初始化 AI 引擎 (5%)...")
            
            # 初始化模型
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            prompt = f"""
            你是一位精通林學、環境科學及碳匯方法學的頂尖數據分析師。
            請根據以下參數，進行量化與矩陣化的深度分析。

            【專案參數】
            專案名稱：{project_name} | 面積：{area_size} 公頃
            目標樹種：{species} | 基線情境：{baseline_scenario}
            土壤環境：{soil_env} | 林地歷史：{land_history}

            【輸出規範：嚴格使用 Markdown 表格】
            1. SWOT 分析矩陣：針對此基線與現地條件進行評估 (2x2表格)。
            2. 方法學 MCDA 決策矩陣：挑選2-3個相關方法學，包含適用度評分、額外性難度、邊界契合度、最終建議。
            3. 風險與衝擊評估矩陣：列出3個潛在紅燈風險，包含發生機率、衝擊程度、緩解策略。
            4. 關鍵數據補測清單：條列式列出急需前往現場實測的3項數據。
            """
            
            my_bar.progress(15, text="資料傳輸中，請求分析矩陣 (15%)...")
            
            # 渲染摘要數據卡片
            m1, m2, m3 = st.columns(3)
            m1.metric(label="運算模型", value="Gemini 3.8", delta="Matrix Mode")
            m2.metric(label="分析標的", value=project_name)
            m3.metric(label="系統狀態", value="深度解析中", delta="穩定", delta_color="normal")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 準備串流與進度運算
            report_container = st.empty()
            full_text = ""
            response = model.generate_content(prompt, stream=True)
            
            chunk_count = 0
            estimated_total_chunks = 40
            
            for chunk in response:
                chunk_count += 1
                percent_complete = min(int(15 + (chunk_count / estimated_total_chunks) * 80), 95)
                my_bar.progress(percent_complete, text=f"矩陣建構與邏輯推演中... ({percent_complete}%)")
                
                full_text += chunk.text
                report_container.markdown(full_text + " ▌")
            
            my_bar.progress(100, text="✅ 運算完成！分析報告 100% 產出。")
            report_container.markdown(full_text)
            
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            my_bar.empty()
