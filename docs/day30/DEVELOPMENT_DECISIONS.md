# Human × ChatGPT × Codex：30 天的決策與修正

這份回顧依 Git 歷史、各 Day checkpoint 和原始工程證據整理。不是所有對話都有
可公開逐句紀錄，因此不替任何人或工具捏造台詞，也不把一次生成說成一次成功。

原始方向是把 PDF、文字與之後的圖像轉成可探索的理解空間。
[PRODUCT_VISION](../../PRODUCT_VISION.md) 與早期 `6e76e13`、`e8a4cb8`、
`09567a3` 等提交可見：從 PDF 與 Structured Outputs，逐步分離流程、概念圖和
比較資料，而非把所有關係硬套在同一張圖。Day9 的 Explain This 再把說明綁回
當前來源；Day12 之後的課程、測驗與錯誤複習，保留本機導覽及明確 AI 動作邊界。

[Day17–20](../DAY20_EVIDENCE.md) 把表現力推進到 Numeric Lab、安全算式、
動態模擬、有限集合機率與平面空間場景。AI 產生宣告，固定引擎驗證並運算。
Source Lens 顯示原頁，Source Atlas 把來源區域連回既有語意 ID；定位框仍是
估計，數學不變量與原生文字座標都不能自動證明教材對應正確。

[Day24](../DAY24_EVIDENCE.md) 的 direct manipulation 使用既有投影與可辨識
反解；放開才經 reducer 提交，過期、越界、錯誤 ownership 事件必須拒絕。
[Day25](../DAY25_EVIDENCE.md) 的 Grounded Semantic Twin 再把來源、表示與控制
透過共同 ID 接起來。原頁固定，探索改變的是模型狀態；這個區別是產品的核心。

[Day26](../DAY26_EVIDENCE.md) 用真實 MIT Chapter 5，完成來源 → 初速度向量
拖曳 → 已提交數值／軌跡 → 原來源的 Golden Path。但第一次中文編譯被安全
拒絕；之後明確重做英文分析才成功。語言與模型輸出同時變了，不能把成功歸因
於單一提示修正。測試也曾因移除舊 UI 失效；後續改用正式事件邊界，並保留
當時完整回歸不是全綠的記錄。不是所有程式碼或模型輸出第一次就正確。

`height=0` 暴露了另一個錯誤假設：長度不一定要嚴格大於零，地面發射的零高度
有明確物理意義。`scene/world/policy.py` 後來區分 quantity kind 與
positive／non_negative／signed domain；速度、頻率等的正值規則和整體安全
界線仍保留。這不是只對「height」這個名字增加特例。
[參數語意測試](../../tests/test_day26_parameter_semantics.py) 保留這個教訓。

[Day27](../DAY27_EVIDENCE.md) 把陌生教材放進凍結評估：原始人工語意結果是
4 PASS／4 PARTIAL／2 FAIL。來源範例數字被當成可任意拖曳的控制，會產生
「數學可以動、教材意思卻錯了」的結果。後續加入 source_fixed、source_variable、
hypothetical_exploration、derived 的契約，分開來源事實和假設控制。
[人工核准 follow-up](../day27/post_fix/human-approved-completion.md) 為
5 PASS／5 PARTIAL／0 FAIL；其中五個沿用先前分配，不能說成未碰過的獨立 holdout。

[Day28](../DAY28_EVIDENCE.md) 是五種 Codex 瀏覽器模擬策略，真人研究參與者
為零。owner 另回報兩位學生有正向非正式印象；這是 owner 回報的質性訊息，
不是 Study A/B，也沒有測量學習增益。模擬發現：formal 圖會把真正可操作的
Lab 壓到下面；來源連結也不夠密。Day30 雲端實查證明這個版面問題仍值得處理。

[Day29](../DAY29_EVIDENCE.md) 做預設拒絕、輸入／算式／payload 範圍與授權
整理，正式 PDF raster 換用 PDFium；歷史 PyMuPDF 分發義務沒有被抹掉。
[Post-Day29](../public-release/EVIDENCE.md) 加入 Google OIDC、持久帳本及限額
工程。工程已存在，並不表示外部付費驗收完成；Day30 保持 `VLL_LIVE_AI=""`，
不初始化 Neon、不動 Cloud secrets、不做真付費請求。

最後的競賽版本把已有能力包成免登入示例。Harmonic 沿用 Day27 人工核准素材；
第二份是 owner 明確核准的 **Day26 封存衍生版**，原始已接受 v2.2 快照缺少
現行 provenance 欄位，不能直接當 v2.4 重播。[衍生紀錄](../../prepared/projectile/PROVENANCE.md)
逐一記錄新增分類，保留公式／ID／範圍／Atlas 與 PDF，沒有新造成功 AI 回應。

[Day1 原文](https://ithelp.ithome.com.tw/articles/10411153)與
[Day17 的實際修正回顧](https://ithelp.ithome.com.tw/articles/10419435)也支持這個方向。
角色分工可這樣理解：Human 決定產品方向、辨認限制、否定錯誤假設、評估操作
是否有價值，並核准此次衍生版本。ChatGPT 提供設計規劃、概念批判、分析與
文件協作；不能把規劃當實作證據。Codex 執行程式整合、測試、瀏覽器操作與
證據整理；agent 自己的操作不能冒充真人學習研究。三者的價值來自可核對的
判斷與修正循環，而不是宣稱 AI 能一次理解所有 PDF。
