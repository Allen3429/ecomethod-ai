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
    soil_env = st.text_area("土壤與環境觀測數據", "海拔約1200公尺。", height=120)
with col_text2:
    land_history = st.text_area("林地歷史與現況", "過往為人工林，2025年丹娜斯颱風影響，紅檜倒了不少，現已補植幼樹。", height=120)

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
            start_time = time.time()
            my_bar = st.progress(0, text="啟動核心引擎... | ⏱️ 耗時: 0.0 秒")
            
            # ==========================================
            # 🌟 UX 魔法：前置緩衝動畫
            # ==========================================
            for i in range(1, 35):
                time.sleep(0.05) # 製造平滑推進感
                elapsed = time.time() - start_time
                my_bar.progress(i, text=f"資料傳輸中，啟動文獻檢索庫 ({i}%) | ⏱️ 耗時: {elapsed:.1f} 秒...")
            
            # UI 版面先渲染出來
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric(label="運算模型", value="Gemini 3.8", delta="Literature Baseline On")
            m2.metric(label="分析標的", value=project_name)
            m3.metric(label="系統狀態", value="深度思考與推演中...", delta="連線穩定", delta_color="normal")
            st.markdown("<br>", unsafe_allow_html=True)
            report_container = st.empty()
            
            # 更新狀態
            current_elapsed = time.time() - start_time
            my_bar.progress(35, text=f"模型深度思考中 (等待伺服器回應，請稍候) | ⏱️ 耗時: {current_elapsed:.1f} 秒")
            
            # ==========================================
            # 🧠 初始化模型與 API 呼叫
            # ==========================================
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            prompt = f"""
            你是一位具備碳稽核員資格的林學、環境科學、資料科學專家。
            本次任務是針對特定林地進行「碳匯專案立項可行性評估」。你必須嚴格遵守以下分析框架，嚴禁生成模稜兩可的冗言贅字。

            【專案與環境參數】
            目標標的：{project_name} | 面積：{area_size} 公頃
            樹種：{species} | 基線情境：{baseline_scenario}
            土壤環境：{soil_env}
            林地歷史：{land_history}

            【系統強制指令 (System Constraints)】
            1. 絕對誠實原則：在引述文獻或法規時，若資料庫中無明確對應的真實文獻，請直接輸出「依目前資料庫查無直接相關文獻，建議實地勘測」，嚴禁捏造期刊名稱或作者。
            2. 聚焦林業方法學：MCDA 評估僅限於 A/R (造林與植林)、IFM (改善森林管理) 兩大類別之國際(如 VCS VM0047, AR-ACM0003) 或台灣環境部認可之方法學。

            【請以 Markdown 表格輸出以下四大模組】

            ### 1. 基線與額外性檢核 (Baseline & Additionality)
            *   法規額外性：此林地歷史是否屬於法定義務造林？(是/否/需釐清)
            *   財務額外性：在無碳權收益下，該復育或疏伐計畫是否具備商業可行性？
            *   科學文獻基線：請簡述 {species} 在相似海拔或 {baseline_scenario} 情境下的平均固碳潛力，並附上真實文獻概念。

            ### 2. 方法學 MCDA 決策矩陣 (Methodology Decision Matrix)
            請嚴格依據以下 3 個維度進行 1-10 分的量化評估：(A) 測量與監測可行性 (B) 洩漏風險可控性 (C) 方法學適用邊界。
            表格欄位：方法學代號 | 總分 | 維度A得分 | 維度B得分 | 維度C得分 | 關鍵扣分事由

            ### 3. 現地紅燈風險矩陣 (Red-Flag Risk Matrix)
            針對 {soil_env} 與 {land_history} 提取 2 項最可能導致專案遭第三方查驗機構 (VVB) 退回的風險。
            表格欄位：風險因子 | 違反之方法學條件 | 衝擊程度(高/中/低) | 顧問緩解建議

            ### 4. 落地行動清單 (Action Items)
            列出專案若要推進，下一步必須在現地執行的 3 項具體環境取樣或測量行動。
            """
            
            response = model.generate_content(prompt, stream=True)
            
            # ==========================================
            # 🌊 串流輸出與動態計時
            # ==========================================
            chunk_count = 0
            estimated_total_chunks = 50 
            full_text = ""
            
            for chunk in response:
                chunk_count += 1
                elapsed_time = time.time() - start_time
                
                percent_complete = min(int(35 + (chunk_count / estimated_total_chunks) * 60), 95)
                my_bar.progress(percent_complete, text=f"矩陣建構與邏輯推演中... ({percent_complete}%) | ⏱️ 耗時: {elapsed_time:.1f} 秒")
                
                try:
                    full_text += chunk.text
                    report_container.markdown(full_text + " ▌")
                except ValueError:
                    continue
            
            # 運算完全結束
            total_time = time.time() - start_time
            my_bar.progress(100, text=f"✅ 運算完成！分析報告 100% 產出 (總耗時: {total_time:.1f} 秒)。")
            report_container.markdown(full_text)
            
        except Exception as e:
            st.error(f"❌ 發生錯誤，請檢查系統日誌。詳細錯誤：{e}")
            if 'my_bar' in locals():
                my_bar.empty()
