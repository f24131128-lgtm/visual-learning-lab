# Study B v1 — PDF vs VLL 小型探索比較（審核待核準）

目的：在同一人內描述兩個接近的概念題于 PDF／VLL 條件的原始表現。人數 3–5，人工閱卷，不是因果實驗或統計證實。與 Study A 評分完全分開。

概念為 source-supported SHM 的振幅 A 與週期 T：`x(t)=A cos(2πt/T+φ)`。采用人工 A-axis PASS 的 Day27 POST_FIX `phase_shift_lab`；實際控制為 A/T/φ，不是 k/m、阻尼或强迫振動。來源 Figure 23.4 未指定位移／時間單位，不自行寫 m/s；各值用教材未指定單位。source facts A=3、T=π、φ=π/4 固定不動；題目數值是明確的假設探索。

兩條件相同教材為 `.day27-local/subsets/harmonic.pdf` 八頁原內容。PDF 條件用普通 PDF reader，允許原生缩放／查找，只有该 PDF、題目與紙筆。VLL 條件允許現有 Source、Learn、Explore、Practice 和預先生成內容／本機 Lab；阻擋新 AI 請求，不給答案或新 explanations，正常作答無需 compiler。不加載錯述 k/m 控制的 planner。記錄是否使用 Practice 或已生成文字；這比較整個準備 VLL 內容與交互包，不能把差異只歸因于滑桿。

## 順序與 carryover

所有人先做 Study A，再做 Study B，以保持 Study A 的真實 first-use。Study A 與 B 共用 SHM 是明確限制：先前探索可能练習到 B 的概念；記錄是否已調過振幅／週期／相位及是否收到概念相關救援，不據此事後删人。不能宣稱 B 是獨立新手學習或消除先前接触。

Study B A 題永远先于 B 題。P01/P03/P05：A=PDF→B=VLL；P02/P04：A=VLL→B=PDF。這樣每題在兩條件下都有人做，兩個條件順序交替；task order 本身未完全平衡。n=3 為 2:1，n=4 為 2:2，n=5 為 3:2。取已同意參與者依到場次序配置代碼，不能看熟悉度／表現重新分組，不選擇只發表人數平衡的子集。

PDF 與 VLL 均先顯示同一份完整材料，第一次任務前僅允許兩分鐘中性設備準備：PDF reader 缩放／翻頁，VLL 已在 A 用過、不教操作或內容。每題開始前 VLL fresh session 從 Learn、無 focus、Lab 默認值（不會沿用 A／上題探索）；PDF 打開首頁，無查找結果。題目要求的假設參數由學員選擇是否输入，不由主持人調成答案。題目出現後才計時，無額外閱讀期。每題 300 秒，目標 180–300 秒，超時保留部分答案與 observed time=300，標 timed_out；不可當作已完成時間。兩題間兩分鐘休息，不反饋正解；換條件關闭另一份窗口並收回前題答案。

## 凍結與評估

FROZEN_TASKS.md 與 FROZEN_SCORING.md 的 exact bytes 和 TASK_ORDER_ASSIGNMENTS.json 將在審核包 hashes 封存。狀態 REVIEW_PENDING，尚未人工批准。審核人需確認問題難度／匹配、source support、正確答案和 rubric；修改只能在任何人參與前另封新版本。第一次作答後不能改 rubric。

記錄每題 task_id、position、condition、score_0_1_2（人類閱卷）、correct/partially_correct/incorrect、completed/timed_out/withdrew/app_failure、elapsed_s、confidence 1–5、understanding 1–5、source_evidence_used true/false/null、引用頁/式/圖、原始推理及人類評分說明。信心題：「你對這題答案有多大把握？」理解題：「你覺得自己對這題概念理解多少？」1=很低、5=很高，完成後立即問，不提示答案。

PDF 與 VLL 每人各一題（各 0–2），不加總成單一 learning gain。使用 source evidence 必須指出可識別頁、式、圖或對應語句，單說「看了教材」不算；不能强制它來決定概念分數。預期答案不得給學員；收答案後由 human reviewer評分，Codex 只能整理已評分數據。若有邊界作答需人工判斷並記錄，不能改凍結 rubric。

## 將來報告（本次不做）

顯示每個真實代碼兩行及 Study A 行；分別報告 PDF／VLL 0/1/2 分布、原始／中位完成時間、超時數、信心與理解中位／範圍、證據與推理 notes。無結果現在不作圖。小樣本、非隨機、任務難度差異、固定題序、carryover、英文教材、自評偏差、已知內容和研究入口 accommodation 都要保留。不得宣稱 VLL 統計提升、已證明更有效、普遍受偏好或學習效能成立。

