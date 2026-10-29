try:
            import time # 確保有引入 time 模組
            start_time = time.time()
            my_bar = st.progress(0, text="啟動核心引擎... | ⏱️ 耗時: 0.0 秒")
            
            # ==========================================
            # 🌟 UX 魔法：前置緩衝動畫 (掩蓋 TTFB 等待時間)
            # ==========================================
            for i in range(1, 35):
                time.sleep(0.08) # 製造平滑推進感
                elapsed = time.time() - start_time
                my_bar.progress(i, text=f"資料傳輸中，啟動文獻檢索庫 ({i}%) | ⏱️ 耗時: {elapsed:.1f} 秒...")
            
            # UI 版面先渲染出來，減少畫面停滯感
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric(label="運算模型", value="Gemini 3.8", delta="Literature Baseline On")
            m2.metric(label="分析標的", value=project_name)
            m3.metric(label="系統狀態", value="深度思考與推演中...", delta="連線穩定", delta_color="normal")
            st.markdown("<br>", unsafe_allow_html=True)
            report_container = st.empty()
            
            # 更新狀態，準備進入真正的 API 阻塞期
            current_elapsed = time.time() - start_time
            my_bar.progress(35, text=f"模型深度思考中 (等待伺服器回應，請稍候) | ⏱️ 耗時: {current_elapsed:.1f} 秒")
            
            # ==========================================
            # 🧠 初始化模型與 API 呼叫 (此處會短暫阻塞等待首字)
            # ==========================================
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            prompt = f"""
            你是一位精通林學、景觀生態學及碳匯方法學（如 VCS, 台灣環境部造林與植林）的頂尖數據分析師。
            請根據以下參數進行深度分析，並且【每一項決策與風險都必須提供真實文獻或法規作為判斷依據】。

            【專案參數】
            專案名稱：{project_name} | 面積：{area_size} 公頃
            目標樹種：{species} | 基線情境：{baseline_scenario}
            土壤環境：{soil_env} | 林地歷史：{land_history}

            【輸出規範：嚴格使用 Markdown 表格，並於表格後方補充文獻支持】
            1. 歷史基線與文獻回顧 (Baseline & Literature)：引述 1-2 篇與該樹種或該土壤修復技術（如 PMFC 對重金屬鎳的移除或碳排影響）相關的真實學術概念或歷史資料。
            2. 方法學 MCDA 決策矩陣：挑選2-3個相關方法學。欄位包含：方法學名稱、適用度評分(1-10)、邊界契合度、【判斷依據(Justification)】。
            3. 風險與衝擊評估矩陣：列出3個潛在紅燈風險。欄位包含：風險因子、衝擊程度、【法規或科學支持依據】、緩解策略。
            4. 關鍵數據補測清單：列出急需前往現場實測的3項數據。
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
                
                # 進度條從 35% 開始往上疊加，最高到 95%
                percent_complete = min(int(35 + (chunk_count / estimated_total_chunks) * 60), 95)
                my_bar.progress(percent_complete, text=f"矩陣建構與邏輯推演中... ({percent_complete}%) | ⏱️ 耗時: {elapsed_time:.1f} 秒")
                
                try:
                    full_text += chunk.text
                    report_container.markdown(full_text + " ▌")
                except ValueError:
                    # 避免 Google 安全審查機制擋住某些字詞導致程式崩潰
                    continue
            
            # 運算完全結束，結算總耗時
            total_time = time.time() - start_time
            my_bar.progress(100, text=f"✅ 運算完成！分析報告 100% 產出 (總耗時: {total_time:.1f} 秒)。")
            report_container.markdown(full_text)
            
        except Exception as e:
            st.error(f"❌ 發生錯誤，請檢查系統日誌。詳細錯誤：{e}")
            if 'my_bar' in locals():
                my_bar.empty()
