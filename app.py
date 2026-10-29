import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="EcoMethod AI Dashboard", page_icon="📊", layout="wide")

st.title("📊 EcoMethod AI - 現地適用性分析與決策儀表板")
st.markdown("整合 **MCDA 多準則決策**、**風險矩陣** 與 **真實文獻基線**，為森林碳匯與環境復育專案提供量化指標與學術依據。")

# ==========================================
# 側邊欄設定
# ==========================================
with st.sidebar:
    st.header("🔑 系統與引擎設定")
    api_key = st.text_input("Gemini API Key", type="password", help="請輸入您的 API 金鑰")
    st.markdown("---")
    st.markdown("### ⚙️ 分析模組啟用狀態")
    st.checkbox("動態耗時追蹤 (Dynamic Timer)", value=True, disabled=True)
    st.checkbox("引述法規與文獻 (Literature Baseline)", value=True, disabled=True)
    st.checkbox("決策判斷依據 (Justification)", value=True, disabled=True)

# ==========================================
# 📋 第一區塊：參數設定 (Input)
# ==========================================
st.header("📋 1. 現地參數與文獻設定")

col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.text_input("專案名稱", "溪頭實驗林碳匯與土壤復育專案")
    species = st.text_input("目標樹種", "柳杉 (Cryptomeria japonica)")
with col2:
    area_size = st.number_input("專案面積 (公頃)", value=50.0, step=10.0)
    baseline_scenario = st.selectbox("基線情境假設", ["受污染土壤與退化林地復育", "現有人工林", "農地造林"])
with col3:
    st.info("💡 系統將依據此處設定的樹種與情境，自動檢索對應的真實林學文獻與國內外方法學法規。")

col_text1, col_text2 = st.columns(2)
with col_text1:
    soil_env = st.text_area("土壤與環境觀測數據", "海拔約1100公尺。土壤具鎳(Ni)重金屬污染觀測紀錄，現正規劃導入植物微生物燃料電池(PMFC)進行修復，需評估此擾動對土壤碳層之影響。", height=120)
with col_text2:
    land_history = st.text_area("林地歷史與現況", "過往為人工林，無近期毀林紀錄，具備景觀生態學之斑塊與廊道連結價值。", height=120)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🚀 執行按鈕與動態展開的第二區塊
# ==========================================
if st.button("🚀 執行矩陣運算與生成報告", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ 系統鎖定中：請先在左側欄位輸入 Gemini API Key！")
    else:
        st.markdown("---")
        st.header("📈 2. 量化分析、決策報告與文獻支持")
        
        try:
            # 建立進度條元件
            my_bar = st.progress(5, text="初始化 AI 引擎 (5%) | ⏱️ 耗時: 0.0 秒...")
            
            # 記錄開始時間
            start_time = time.time()
            
            # 初始化模型
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            # 升級版 Prompt：要求依據與真實文獻
            prompt = f"""
            你是一位精通林學、景觀生態學及碳匯方法學（如 VCS, 台灣環境部造林與植林）的頂尖數據分析師。
            請根據以下參數進行深度分析，並且【每一項決策與風險都必須提供真實文獻或法規作為判斷依據】。

            【專案參數】
            專案名稱：{project_name} | 面積：{area_size} 公頃
            目標樹種：{species} | 基線情境：{baseline_scenario}
            土壤環境：{soil_env} | 林地歷史：{land_history}

            【輸出規範：嚴格使用 Markdown 表格，並於表格後方補充文獻支持】
            1. 歷史基線與文獻回顧 (Baseline & Literature)：引述 1-2 篇與該樹種或該土壤修復技術（如 PMFC 對重金屬鎳的移除或碳排影響）相關的真實學術概念或歷史資料。
            2. 方法學 MCDA 決策矩陣：挑選2-3個相關方法學 (需寫出真實代號，如 AR-ACM0003)。欄位包含：方法學名稱、適用度評分(1-10)、邊界契合度、【判斷依據(Justification)】。
            3. 風險與衝擊評估矩陣：列出3個潛在紅燈風險。欄位包含：風險因子、衝擊程度、【法規或科學支持依據】、緩解策略。
            4. 關鍵數據補測清單：列出急需前往現場實測的3項數據。
            """
            
            my_bar.progress(15, text="資料傳輸中，檢索文獻與歷史基線 (15%) | ⏱️ 耗時: 0.5 秒...")
            
            # 渲染摘要數據卡片
            m1, m2, m3 = st.columns(3)
            m1.metric(label="運算模型", value="Gemini 3.8", delta="Literature Baseline On")
            m2.metric(label="分析標的", value=project_name)
            m3.metric(label="系統狀態", value="文獻檢索與矩陣運算中", delta="穩定", delta_color="normal")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 準備串流與進度運算
            report_container = st.empty()
            full_text = ""
            response = model.generate_content(prompt, stream=True)
            
            chunk_count = 0
            estimated_total_chunks = 45 # 加上文獻會稍微長一點
            
            for chunk in response:
                chunk_count += 1
                
                # 計算耗時與進度
                elapsed_time = time.time() - start_time
                percent_complete = min(int(15 + (chunk_count / estimated_total_chunks) * 80), 95)
                
                # 動態更新進度條與計時器
                my_bar.progress(percent_complete, text=f"矩陣建構與邏輯推演中... ({percent_complete}%) | ⏱️ 耗時: {elapsed_time:.1f} 秒")
                
                full_text += chunk.text
                report_container.markdown(full_text + " ▌")
            
            # 運算完全結束，結算總耗時
            total_time = time.time() - start_time
            my_bar.progress(100, text=f"✅ 運算完成！分析報告 100% 產出 (總耗時: {total_time:.1f} 秒)。")
            report_container.markdown(full_text)
            
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            my_bar.empty()
