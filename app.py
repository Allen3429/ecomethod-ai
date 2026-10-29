import streamlit as st
from groq import Groq

# 頁面設定
st.set_page_config(page_title="EcoMethod AI", page_icon="🌲", layout="wide")

st.title("🌲 EcoMethod AI - 減量專案現地適用性評估引擎")
st.markdown("基於開源 Meta Llama 3 打造，專為森林碳匯與 ESG 專案設計的方法學適配分析 SaaS 工具。")

# 側邊欄設定 (放 API Key 確保安全)
with st.sidebar:
    st.header("🔑 系統設定")
    st.markdown("請輸入你的 Groq API Key 以啟動引擎：")
    api_key = st.text_input("Groq API Key", type="password")
    st.markdown("[👉 點此免費申請 Groq API Key](https://console.groq.com/keys)")
    st.markdown("---")
    st.markdown("👨‍💻 核心技術架構：Streamlit + Groq (Meta Llama 3 70B)")

# 主畫面輸入區
st.header("📋 現地條件輸入")
col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input("專案名稱", "溪頭實驗林減量專案")
    species = st.text_input("目標樹種", "柳杉")
    
with col2:
    soil_env = st.text_area("土壤與環境狀況", "海拔約1100公尺，土壤曾有部分重金屬觀測紀錄", height=130)
    land_history = st.text_area("林地歷史與現況", "過往為人工林，近期有疏伐計畫", height=130)

# 執行按鈕與邏輯
if st.button("🚀 生成評估報告", type="primary"):
    if not api_key:
        st.error("⚠️ 系統鎖定中：請先在左側欄位輸入 Groq API Key！")
    else:
        with st.spinner("⏳ 雲端運算中：AI 正在比對各大方法學並生成報告，請稍候..."):
            try:
                # 啟動 Groq 客戶端
                client = Groq(api_key=api_key)
                
                # 組合 Prompt 邏輯
                prompt = f"""
                你是一位頂尖的「森林碳匯與 ESG 專案方法學適配專家」。請用繁體中文回答。
                我將提供一塊林地的現地條件。請根據國內外常見的減量方法學（如台灣環境部造林與植林、森林經營碳匯方法學、Verra VCS 等），評估這塊地的適配性。

                【現地條件】
                專案名稱：{project_name}
                目標樹種：{species}
                土壤與環境狀況：{soil_env}
                林地歷史與現況：{land_history}

                【請嚴格依照以下結構輸出報告】
                1. 總結判定 (The Verdict)：這塊林地申請碳匯專案的整體可行性（高/中/低），並用一句話說明核心挑戰。
                2. 潛在適用方法學 (Applicable Methodologies)：列出 1~2 個最有可能適用的方法學，並說明符合的條件。
                3. 現地紅燈警告 (Red Flags)：指出目前現地條件中，可能違反方法學邊界條件的致命傷。
                4. 需補充關鍵數據 (Missing Data)：若要啟動專案，顧問或業主還需要去現場補測哪些關鍵數據？
                """
                
                # 呼叫開源模型
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "你是一位專業的環境科學與碳匯顧問。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                # 顯示結果
                result = completion.choices[0].message.content
                st.success("✅ 報告生成完畢！")
                st.markdown("---")
                st.markdown(f"### 📄 【{project_name}】AI 評估報告")
                st.write(result)
                
            except Exception as e:
                st.error(f"❌ 發生錯誤，請檢查 API Key 是否正確。錯誤代碼：{e}")
