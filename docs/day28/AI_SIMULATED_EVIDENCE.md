# DAY 28 — AI-SIMULATED RED TEAM

2026-10-12（Asia/Taipei）。這是同一個 AI agent 採五種操作策略的隔離瀏覽器 red team；不是五位真人、不是五個獨立受試者，也不是學習成效研究。未填真人 CSV、未套真人 rubric、未推算人類時間、成功率或分數。Day28 human PREP 狀態仍是 `PREP_ONLY_REVIEW_PENDING`。

## 恢復與證據邊界

沿用上一 Session 的 [原始 operations.json](../day28-ai-red-team/evidence/operations.json) 及九張原始截圖。AI01–AI03 沒有重做；AI04/AI05 實際已保存紀錄，故沒有重新建立測試封包或付費生成。原始檔、freeze manifest 的 SHA-256 保存於 [baseline-integrity.json](../day28-ai-red-team/baseline-integrity.json)，新測試逐檔核對。真人 frozen files、題目、rubric、分派、prepared inputs 和入口未改；production UI 的修復另列於 Day28 報告，不能把歷史 production seal 當成修復後版本。

前一 Session 的 AI05 紀錄包含一次正式「開始理解」提交；沒有保存最終回應或請求帳務，不能追認為本次 offline request count=0。本次恢復工作沒有呼叫付費 Responses/files API；新離線 lane 另有 request guard 與零 attempts 證據。

## 五種情境：實際狀態

| 情境／操作策略 | 執行狀態 | 實際操作與結果 | 卡點與批評 |
|---|---|---|---|
| AI01 完全不懂程式的大學生 | 執行；控制任務成功 | prepared→Source→選 sinusoidal formula→全域 Explore→展開參數→A 3→2.90→Source。 | 來源公式沒有 linked semantic ID，不能從公式抵達控制；控制藏在長流程圖後。成功操作不代表理解。 |
| AI02 懂公式、不熟 AI 工具 | 執行；控制任務成功 | Source 選 angular frequency formula→Explore→展開參數→T 3.20→ω 約 1.9635→Source 原公式。 | 必須自行從來源公式辨認實驗中的 T；公式區域本身沒有可驗證 owner。不能聲稱產品自動建立了精確對應。 |
| AI03 沒耐心、容易放棄 | 執行；生成入口失敗 | 空首頁按開始理解→載入示例→Explore→建立 Spatial Learning Scene→prepared request guard 拒絕。 | 是 offline accommodation 的註定失敗 CTA，不是 production 模型生成失敗；沒有聲稱模擬了真人放棄率。 |
| AI04 懷疑產品價值 | 執行；來源查證部分成功 | 看摘要→Source→打開 page 選單，只有 1–3→來源準備工具→延伸學習→探索方式，嘗試核對摘要中的 7–8 頁。 | 畫面宣稱分析 8 頁，但主 Atlas viewer 僅 3 頁，範圍及其他頁的查證路徑不直觀。紀錄未證明所有 Source Lens 入口都不可用。 |
| AI05 想上傳自己的 PDF | 執行；上傳成功，端到端 PARTIAL | 新隔離分頁的正式首頁→檔案選擇器上傳公開 MIT harmonic.pdf（8 頁，作為自備教材代理）→開始理解→顯示正在分析。 | 最後保存畫面仍在分析中。生成完成、輸出品質及使用者自有私密 PDF：**NOT TESTED**。不得把等待狀態判作 timeout 或 API failure。 |

所有日期／操作事件可在原始 JSON 核對；未將事件間距當成人類任務時間。AI04/AI05 已有保存紀錄，所以沒有為補足五人數字而重測或杜撰。

## 原始截圖

- AI01：[首頁](../day28-ai-red-team/evidence/AI01-home.jpg)、[Source 卡點](../day28-ai-red-team/evidence/AI01-source-dead-end.jpg)、[改值](../day28-ai-red-team/evidence/AI01-change.jpg)。
- AI02：[公式卡點](../day28-ai-red-team/evidence/AI02-formula-dead-end.jpg)；T/ω 的成功數值在 operations.json，不另稱有截圖。
- AI03：[空首頁](../day28-ai-red-team/evidence/AI03-empty-start.jpg)、[offline 拒絕](../day28-ai-red-team/evidence/AI03-build-failure.jpg)。
- AI04：[頁數限制](../day28-ai-red-team/evidence/AI04-page-limit.jpg)。
- AI05：[正式首頁](../day28-ai-red-team/evidence/AI05-home.jpg)、[載入中](../day28-ai-red-team/evidence/AI05-loading.jpg)。

## 五個主要 UX 問題

| 優先序 | 分類 | 可核對的問題 | 證據／推論邊界 |
|---|---|---|---|
| 1 | VERIFIED | Source 概念／formal representation 與真正的參數操作距離太遠，控制折疊且位於流程圖之後。 | AI01/02 操作＋截圖。來源公式缺少 owner 是資料限制，不能用假連結遮掩。 |
| 2 | VERIFIED | prepared lane 保留需要新 AI 的生成 CTA，按下才告知不允許。 | AI03 guard 拒絕；offline 設計錯誤，不能歸咎模型。 |
| 3 | VERIFIED | 主 Source viewer 的可選頁面與已分析頁面範圍不一致，查證 7–8 頁需另找路徑。 | AI04 選單只有 1–3。無法推論原 PDF 遺失或所有 8 頁不可查看。 |
| 4 | VERIFIED（限 prepared lane） | 中文 UI 搭配英文生成摘要、節點、控制 label，首次操作需切換語言理解。 | AI01/04 可見英文；prepared analysis_language=en 是已保存內容，切 UI 不應偷偷翻譯。對真人理解的影響未測。 |
| 5 | HYPOTHESIS | 自備 PDF 分析中的等待與不確定性可能讓使用者無法判斷何時取得可操作模型。 | AI05 只有 loading 證據；尚未測完成、延遲、取消、真人耐心，不能宣稱已驗證放棄。 |

最嚴格的產品價值批評：核心承諾是「把教材變成可探索的理解」，但這份示例中 source 公式、概念節點與控制項的對應仍稀疏，使用者必須自己找、自己對照。即使滑桿能動，也只證明局部數值探索可用，還不足以證明來源理解可信、能泛化到自己的 PDF、或比閱讀 PDF 更能促成學習。AI red team 只能指出可見摩擦，不能證明上述價值成立或不成立。

## 選定兩項修復與 before / after

1. **Source→實際控制**：以前只有全域 Explore，需越過流程圖再開 expander。現在 Source 提供由 exact representation registrations 導出的概念選單；選概念→開啟連結實驗的參數控制→Explore 頂部已展開 A/T/φ，並有返回 Source 按鈕。重用 canonical focus、既有 Lab state／callback。未建立 inverse、假 draggable handle、頁框 owner 或另一個 semantic focus。
2. **offline prepared / Own PDF**：以前準備示例標示在頁尾，生成入口按下才拒絕。新的 `tests/manual_day28_red_team.py` 在頁首明示預先生成、自己的 PDF 在此只能 local upload preview；需要 AI 的按鈕 disabled＋原因，Responses/file-upload guard 保留。這是獨立 offline entrypoint；正式 `app.py` 的付費分析能力與 validator、原 frozen human entrypoint皆保留。正式 own-PDF live 品質未重測。

SHM 的來源振幅、週期區域沒有 semantic ID；實驗參數／曲線／metrics 的 owner 是 `amplitude_phase`。新入口只對該 validated 概念呈現控制，**沒有**把 p1_sine_formula 或 ω 公式直接連到參數。多 owner、錯 material/spec/pages、無可調參數、focus 改變都不使用捷徑。

## 真瀏覽器驗證（修復後工程驗證）

使用 Codex In-app Browser 的隔離分頁，僅畫面／accessibility 操作；不是 AppTest 冒充瀏覽器，也不是重測五種 persona。新 [post-fix-operations.json](../day28-ai-red-team/evidence/post-fix-operations.json) 記錄：

prepared homepage→試用→查看原始教材→concept selector 的唯一可見選項 `Express the motion as A cos(ω₀t + φ)`→開啟實驗控制→振幅滑桿鍵盤左一次 **3→2.90**→返回 Source→原 PDF 頁仍可見→再開控制，**2.90 保留**；source fact 仍為 **3**，末尾 counter **new AI/upload attempts: 0**。

空間場景、Explain、planner、動態模擬等新生成按鈕 disabled；slider、view navigation、重設、lesson navigation 繼續本機操作。API delta=0 由 guarded browser counter 及 AppTest mock 雙重確認；不是只根據網頁沒有錯誤推測。PDF bytes、source_context、analysis 完全不變由 AppTest equality 驗證，截圖只能提供可見頁面證據。

截圖：[清楚 offline 首頁](../day28-ai-red-team/evidence/after-offline-home.jpg)、[Source 控制捷徑](../day28-ai-red-team/evidence/after-source-control-link.jpg)、[A=2.90](../day28-ai-red-team/evidence/after-controls-change.jpg)、[返回 Source](../day28-ai-red-team/evidence/after-return-source.jpg)、[原頁內容](../day28-ai-red-team/evidence/after-return-source-page.jpg)。僅真實截圖，未修圖或重畫；自然側欄 viewport，沒有假稱固定桌面尺寸驗收。

## 測試與限制

新 focused 最終 **7/7 PASS，13.106 s**：[focused.log](../day28-ai-red-team/focused.log)。首次 2 failures 揭露 `st.button` 未被 container method patch 攔截，已修；第二次 2 errors 是測試 accessor，路徑已完成但最後 counter assertion 錯誤，已修。兩份初始 log 均保留，不隱藏失敗。沒有重跑 Day27 benchmark／PREP 套件來取代新驗證。完整 suite 最後只啟動一輪，**500/500 PASS，303.017 s，0 failures/errors/skips**：[full-regression.log](../day28-ai-red-team/full-regression.log)。狀態 **AI-SIMULATED RED TEAM DONE**，真人研究未完成。

瀏覽器 auto-review 曾因 focused failures 拒絕開頁；先完成修復並取得 7/7，再獲允許開同一 URL。8532 原來已有 frozen-preview server，首次新程序未綁定；核對 exact PID/command 後停止舊 preview，改用相同 port，沒有兩個成功綁定的 Day28 server。未更改 frozen entrypoint。

仍未進行真人學習成效驗證、production own-PDF 完成驗證、cross-domain 瀏覽器泛化或任意公式到控制的 grounding 驗證。未呼叫新的付費 OpenAI API，未 commit/push/checkout/reset，未開始 Day29。

教材截圖：MIT OpenCourseWare / Peter Dourmashkin，Chapter 23: Simple Harmonic Motion，原 PDF 第 3–10 頁 subset，原內容未改，CC BY-NC-SA 4.0；UI／估計框為產品加註，不是 MIT 背書。沿用 PREP 保存的來源及授權，不重新建立 corpus。
