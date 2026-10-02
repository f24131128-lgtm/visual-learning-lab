"""Product UI translations; source text and generated material are never translated here."""

import streamlit as st

DEFAULT_LANGUAGE = "zh-TW"
LANGUAGE_NAMES = {"zh-TW": "繁體中文", "en": "English"}
RESPONSE_LANGUAGES = {"zh-TW": "Traditional Chinese", "en": "English"}
FONT_STACK = '"Noto Sans TC", "PingFang TC", "Microsoft JhengHei", system-ui, sans-serif'

UI_TEXT = {"zh-TW": {
    "See the idea. Find the connection.": "看見概念，找到連結。",
    "Turn complex ideas into something you can actually see.": "讓複雜的概念，成為看得見的理解。",
    "Start with what you’re learning": "從正在學習的內容開始",
    "Bring a page, a chapter, or an idea you want to understand.": "帶入一頁教材、一個章節，或你想理解的概念。",
    "Upload a PDF": "上傳 PDF",
    "PDFs are analyzed through both extracted text and visual pages.": "結合擷取文字與原始頁面的視覺內容分析 PDF。",
    "Or paste your content": "或貼上學習內容",
    "Paste your notes, a tricky explanation, or a concept you want to explore…": "貼上筆記、難懂的說明，或想深入探索的概念…",
    "Use one source at a time · PDF text and visual page content are analyzed together.": "一次使用一種來源 · PDF 文字與頁面視覺內容會一起分析。",
    "Visualize": "開始理解",
    "Please upload a PDF or paste some learning content first.": "請先上傳 PDF 或貼上學習內容。",
    "Please use only one source at a time: upload a PDF or paste text.": "請一次使用一種來源：上傳 PDF 或貼上文字。",
    "We couldn’t read this PDF. Please check that it is a valid PDF and try again.": "無法讀取這份 PDF，請確認檔案有效後再試。",
    "No extractable text was found in this PDF. It may be scanned or image-based. Visual analysis still requires a readable PDF file.": "這份 PDF 沒有可擷取的文字，可能是掃描檔或圖片。目前請使用含文字的 PDF。",
    "We couldn’t send this PDF for visual analysis. Please try again with a valid PDF file.": "無法傳送 PDF 進行視覺分析，請使用有效的 PDF 檔案再試一次。",
    "Analyzing your content…": "正在分析學習內容…",
    "OpenAI API key is not configured yet. Add OPENAI_API_KEY to .streamlit/secrets.toml and try again.": "尚未設定 OpenAI API 存取，請在 Secrets 設定 OPENAI_API_KEY 後再試。",
    "The analysis came back in an unexpected format. Please try again.": "分析回傳格式不完整，請再試一次。",
    "We couldn’t analyze that content right now. Check your API key and internet connection, then try again.": "目前無法分析內容，請確認 API 存取與網路連線後再試。",
    "Your learning snapshot": "學習概覽",
    "Quick Summary": "重點摘要",
    "Key Concepts": "關鍵概念",
    "Relationships": "概念關係",
    "Visual Evidence": "視覺證據",
    "Learning value:": "學習價值：",
    "Suggested Visualization": "建議視覺化",
    "Visual Flow": "視覺流程",
    "Concept Map": "概念圖",
    "Comparison": "並列比較",
    "Primary Visualization": "主要視覺化",
    "No key concepts were returned for this content.": "這份內容沒有可用的關鍵概念。",
    "No meaningful visual evidence was found in this content.": "這份內容沒有找到有意義的視覺證據。",
    "No explicit relationships were found in this content.": "這份內容沒有找到明確的概念關係。",
    "No visualization type was suggested for this content.": "這份內容沒有建議的視覺化類型。",
    "The selected Visual Flow could not be rendered because its structured data was incomplete.": "視覺流程的資料不完整，暫時無法顯示。",
    "The selected Concept Map could not be rendered because its structured data was incomplete.": "概念圖的資料不完整，暫時無法顯示。",
    "The selected Comparison could not be rendered because its structured data was incomplete.": "並列比較的資料不完整，暫時無法顯示。",
    "No strong primary visualization was detected for this material.": "這份教材目前沒有適合的主要視覺化。",
    "Takeaway": "學習重點",
    "Criterion": "比較面向",
    "Explain This": "深入說明",
    "Explain this": "深入說明",
    "Explain this step": "說明這個步驟",
    "In simple terms": "簡單來說",
    "Why it matters": "為什麼重要",
    "Intuition or example": "直覺或例子",
    "Source context: {note}": "來源脈絡：{note}",
    "Explaining this part…": "正在說明這個部分…",
    "OpenAI API access is not configured for explanations yet.": "尚未設定深入說明所需的 OpenAI API 存取。",
    "This explanation came back in an unexpected format. Please try again.": "說明回傳格式不完整，請再試一次。",
    "We couldn’t explain this item right now. Please try again.": "目前無法說明這個項目，請稍後再試。",
    "Explore this visualization": "探索這個視覺化",
    "No visualization elements are available to explore.": "目前沒有可探索的視覺化項目。",
    "Choose an item": "選擇項目",
    "Choose a step": "選擇步驟",
    "Choose a concept": "選擇概念",
    "That visualization element is no longer available.": "這個視覺化項目已無法使用。",
    "We couldn’t prepare that visualization element for explanation.": "目前無法準備這個項目的說明。",
    "Knowledge Check": "知識檢核",
    "No checkpoint questions are available for this lesson.": "這個課程目前沒有檢核題目。",
    "Choose an answer": "選擇答案",
    "Check answer": "檢查答案",
    "Choose an answer before checking.": "請先選擇答案。",
    "Correct": "答對了",
    "Not quite": "再想一下",
    "Knowledge Check: {correct} / {total} correct": "知識檢核：答對 {correct} / {total} 題",
    "Guided Learning": "引導學習",
    "A guided learning path is not available for this material.": "這份教材目前沒有可用的引導課程。",
    "Learn this material in {count} steps.": "透過 {count} 個步驟理解這份教材。",
    "Start guided learning": "開始引導學習",
    "Step {number} of {count}": "第 {number} / {count} 步",
    "Goal": "學習目標",
    "Explanation": "說明",
    "Why this comes next": "為什麼接著學這個",
    "Related visualization: {label}": "相關視覺化：{label}",
    "Previous": "上一步",
    "Next": "下一步",
    "Source: {pages}": "來源：{pages}",
    "Source": "來源",
    "p. {pages}": "第 {pages} 頁",
    "PDF source: text found on {found} of {total} page(s); analyzed {analyzed} page(s).": "PDF 來源：共 {total} 頁，其中 {found} 頁可擷取文字；已分析 {analyzed} 頁。",
    "Found extractable text on {found} of {total} PDF page(s); analyzing the first {analyzed} extractable page(s).": "PDF 共 {total} 頁，其中 {found} 頁可擷取文字；正在分析前 {analyzed} 個含文字的頁面。",
    "{kind} — Page {page}": "{kind} — 第 {page} 頁",
    "formula": "公式",
    "diagram": "圖解",
    "graph": "圖表",
    "waveform": "波形",
    "table": "表格",
    "image": "圖片",
    "other": "其他",
    "central": "核心",
    "primary": "主要",
    "supporting": "輔助",
    "previous step": "前一步",
    "next step": "下一步",
    "Flow": "流程",
    "Timeline": "時間軸",
    "Analogy": "類比",
    "Image / Diagram": "圖片／圖解",
    "Click a node to explore · Pan and zoom to navigate": "點選節點探索 · 拖移與縮放檢視",
    "The interactive canvas is unavailable. Showing the Graphviz view.": "互動畫布暫時無法使用，已切換為 Graphviz 圖表。",
    "Needs review": "需要複習",
    "Current lesson": "目前課程",
    "Explore this visualization · Choose from list instead": "探索這個視覺化 · 從清單選擇",
    "Choose a learning item": "選擇學習項目",
    "Use Graphviz view": "切換 Graphviz 圖表",
    "Try interactive view": "嘗試互動畫布",
    "Clear selection": "清除選取",
    "Learning Inspector": "學習探索面板",
    "Select a concept, step, or comparison item to explore its context and source.": "選擇概念、流程步驟或比較項目，探索脈絡與來源。",
    "This learning item is no longer available.": "這個學習項目已無法使用。",
    "Role: {role}": "角色：{role}",
    "Context": "脈絡",
    "Takeaway: {text}": "學習重點：{text}",
    "Connected steps": "相連步驟",
    "Connected to": "相關連結",
    "Source: pasted text": "來源：貼上文字",
    "Source: no validated page reference": "來源：沒有已驗證的頁碼",
    "Related lesson: Step {number} — {title}": "相關課程：第 {number} 步 — {title}",
    "Go to lesson step": "前往課程步驟",
    "No lesson step is linked to this item.": "這個項目沒有連結的課程步驟。",
    "Choose an item from the list below to explore this view.": "從下方清單選擇項目，探索這個圖表。",
    "Solid purple: selected · Dashed amber: needs review · Light purple: current lesson": "深紫色：已選取 · 琥珀色虛線：需複習 · 淺紫色：目前課程",
    "Source context is no longer available for this material.": "這份教材的來源脈絡已無法使用。",
    "Hide source": "收起來源",
    "View source": "查看來源",
    "Source Lens": "來源檢視",
    "Supplied pasted-text context": "原始貼上文字",
    "No supplied text context is available.": "沒有可用的原始文字。",
    "No validated source page is linked to this item.": "這個項目沒有已驗證的來源頁碼。",
    "Original PDF · Page {page}": "原始 PDF · 第 {page} 頁",
    "Text match highlighted for navigation; verify its meaning in context.": "已標示符合的原文位置，請結合前後文核對意義。",
    "Showing source page context; an exact text location was not found.": "顯示來源頁面脈絡；未找到精確的文字位置。",
    "We couldn’t preview this PDF page. The available extracted text is shown below.": "無法預覽這個 PDF 頁面，下方提供可用的擷取文字。",
    "Matching extracted excerpt": "符合的原文片段",
    "Visual evidence observed on original PDF page · from the existing analysis": "原始 PDF 頁面的視覺證據 · 來自既有分析",
    "Extracted text context": "擷取文字脈絡",
    "Extracted text from the same page; this is not an exact transcription of diagrams or formulas.": "以下為同頁的擷取文字，不代表圖解或公式的完整轉錄。",
    "No extracted text is available for this analyzed page.": "這個已分析頁面沒有可用的擷取文字。",
    "Text context is shortened for display.": "文字脈絡已縮短以便閱讀。",
    "One idea. More ways to understand it.": "一個概念，多種理解方式。",
    "Planned capabilities · coming in future versions": "規劃中的功能 · 將於後續版本推出",
    "Analogies": "類比說明",
    "Image Breakdown": "圖像拆解",
    "3D / Motion": "3D／動態",
    "Source Check": "來源核對",
    "Make unfamiliar ideas click with familiar examples.": "透過熟悉的例子理解陌生概念。",
    "Explore the parts of a diagram and what they mean.": "探索圖解的各個部分與意義。",
    "Explore spatial ideas and how systems change.": "探索空間概念與系統變化。",
    "Trace explanations back to the original PDF or source material.": "將說明追溯到原始 PDF 或來源資料。",
    "Understanding should come with evidence.": "理解，也要有證據。",
    "Planned Source Check will link generated explanations to their supporting source passages, so you can inspect the original context and spot oversimplifications.": "規劃中的來源核對會將生成說明連結到支持它的原文，讓你核對脈絡，辨識過度簡化的內容。",
    "Visual Learning Lab · Built in public, one day at a time.": "Visual Learning Lab · 每天一步，公開打造。",
    "Generated content will use the selected language after your next analysis. Current explanations and reviews keep the active analysis language.": "下次分析會使用新選擇的語言。目前的生成內容、深入說明與重點複習維持本次分析語言。",
    "Interactive Lab": "互動實驗室",
    "Choose an experiment": "選擇實驗",
    "Move a slider to explore. Changes are computed locally; no AI request is made.": "調整滑桿探索變化。所有變化都在本機計算，不會發送 AI 請求。",
    "Compare with default": "與預設值比較",
    "Reset parameters": "重設參數",
    "Default": "預設",
    "Current": "目前",
    "Value": "數值",
    "Try this": "試試看",
    "Open Interactive Lab": "開啟互動實驗室",
    "Interactive experiment": "互動實驗",
    "Recommended experiment": "推薦實驗",
    "Open lab: {title}": "開啟實驗：{title}",
    "Experiment selected below: {title}": "已選取下方實驗：{title}",
    "Go to Interactive Lab": "前往互動實驗室",
    "This experiment is undefined for these values. Adjust the parameters or reset to defaults.": "這組參數無法產生有效的實驗結果，請調整參數或重設預設值。",
    "This experiment could not be displayed. Your lesson and review are still available.": "目前無法顯示這個實驗。課程與複習仍可繼續使用。",
    "Some experiment data was invalid and was skipped. Other learning content is still available.": "部分實驗資料無效，已略過。其他學習內容仍可使用。",
    "Metric unavailable for these parameters: {label}": "這組參數無法計算：{label}",
    "Original source excerpts stay in their original language.": "來源原文保留原始語言。",
    "Create dynamic simulation": "建立動態模擬",
    "Create dynamic simulation: {title}": "建立動態模擬：{title}",
    "Creating a dynamic simulation…": "正在建立動態模擬…",
    "Dynamic Simulation Studio": "動態模擬工作室",
    "Dynamic simulation": "動態模擬",
    "Open simulation": "開啟模擬",
    "Open simulation: {title}": "開啟模擬：{title}",
    "Recommended simulation": "推薦動態模擬",
    "Go to Dynamic Simulation Studio": "前往動態模擬工作室",
    "Opens the saved simulation locally.": "在本機開啟已儲存的模擬。",
    "Optional: makes one AI request, then animation and controls are local.": "選用功能：建立時發送一次 AI 請求，之後的動畫與操作均在本機執行。",
    "Build once when motion would help. Playback and parameter changes make no AI requests.": "當動態有助理解時建立一次。播放與參數調整都不會發送 AI 請求。",
    "Uses the experiment parameters above. Changes restart playback and are computed locally.": "共用上方實驗的參數。調整後會從頭播放，所有變化均在本機計算。",
    "Play": "播放", "Pause": "暫停", "Reset": "重播",
    "Playback speed": "播放速度", "Current time": "目前時間",
    "Show trail": "顯示已走過軌跡", "Full path": "完整路徑", "Static view": "靜態檢視",
    "Observe this": "觀察看看",
    "Motion is not a useful fit for this experiment.": "這個實驗不適合透過動態模擬理解。",
    "Motion stops at the declared model boundary.": "動態會在模型設定的有效邊界停止。",
    "Play, pause, speed, reset and the timeline run in your browser. Metrics follow the same clock.": "播放、暫停、速度、重播與時間軸都在瀏覽器執行，數值使用同一個時間進度。",
    "Static view shows the x/y projection of this 3D trajectory.": "靜態檢視呈現這條 3D 軌跡在 x/y 平面的投影。",
    "Animation is unavailable. Showing a static trajectory at its initial time; 3D uses an x/y projection.": "動畫暫時無法使用，改顯示完整軌跡與起點；3D 軌跡使用 x/y 平面投影。",
    "Some simulation objects were invalid and were skipped.": "部分模擬物件無效，已略過。",
    "Some simulation values are undefined for these parameters and were skipped.": "部分模擬數值在這組參數下無法定義，已略過。",
    "Simulation API access is not configured yet.": "尚未設定建立動態模擬所需的 API 存取。",
    "The simulation data was incomplete or unsafe. Please try again.": "模擬資料不完整或不符合安全規則，請再試一次。",
    "We couldn’t create this simulation right now. Please try again.": "目前無法建立動態模擬，請稍後再試。",
    "This simulation is undefined for these values. Adjust the experiment parameters or reset them.": "這組參數無法產生有效的模擬，請調整上方實驗參數或重設預設值。",
    "This simulation could not be displayed. Your experiment, lesson and review remain available.": "目前無法顯示這個模擬。實驗、課程與複習仍可繼續使用。",
    "Dynamic simulations are unavailable for this context. Your experiment and lesson remain available.": "目前無法為這個脈絡提供動態模擬。實驗與課程仍可繼續使用。",
    "Richer 3D experiences": "更豐富的 3D 體驗",
    "Explore spatial models beyond point trajectories.": "探索軌跡之外的空間模型。",
    "Learning Scene": "互動學習場景",
    "This material can be explored as a coordinated probability workspace.": "這份教材適合用多視圖方式探索機率與集合。",
    "Build Learning Scene": "建立互動學習場景",
    "Compiling the Learning Scene…": "正在編譯互動學習場景…",
    "Learning Scene API access is not configured yet.": "尚未設定建立互動學習場景所需的 API 存取。",
    "The Learning Scene was incomplete or unsafe. Your analysis is still available.": "互動學習場景資料不完整或不符合安全規則；原有分析仍可使用。",
    "This Learning Scene could not be displayed. The rest of your learning material is still available.": "目前無法顯示互動學習場景；其餘學習內容仍可使用。",
    "Event / operation": "事件／運算",
    "Learning lens": "學習視角",
    "Explore": "探索",
    "De Morgan": "德摩根",
    "Inclusion–Exclusion": "容斥原理",
    "Sample Space": "樣本空間",
    "Click an outcome to focus it across every representation.": "點選結果，即可在所有表示中同步聚焦。",
    "Set View": "集合視圖",
    "This scene needs two events for the set view.": "此場景需要兩個事件才能顯示集合視圖。",
    "Highlighted outcomes are computed from the active expression: {expression}": "醒目結果由目前運算即時計算：{expression}",
    "Probability Tree": "機率樹",
    "Start": "開始",
    "Formula / Reasoning Lens": "公式／推理視角",
    "outside the declared events": "不屬於已宣告事件",
    "This lens needs two events.": "此學習視角需要兩個事件。",
    "De Morgan Lens": "德摩根視角",
    "Computed sets are identical.": "兩邊獨立計算出的集合完全相同。",
    "Computed sets differ.": "兩邊計算出的集合不同。",
    "Inclusion–Exclusion Lens": "容斥原理視角",
    "The overlap is subtracted once because it was counted in both events.": "重疊部分在兩個事件中各計算一次，因此必須扣除一次。",
    "Monte Carlo Simulation": "蒙地卡羅模擬",
    "Trials": "試驗次數",
    "Run again": "重新模擬",
    "Theoretical": "理論值",
    "Empirical": "實驗值",
    "Difference": "差距",
    "This workspace uses one validated semantic scene. All controls run locally after compilation.": "此工作區共用同一份已驗證語意場景；編譯完成後，所有操作都在本機執行。",
}}
UI_TEXT["en"] = {key: key for key in UI_TEXT["zh-TW"]}
UI_TEXT["en"]["review.complete"] = "Knowledge Check complete. No review areas were identified."
UI_TEXT["zh-TW"]["review.complete"] = "知識檢核已完成，目前沒有需要複習的項目。"
UI_TEXT["en"]["review.review_areas"] = "Review Queue"
UI_TEXT["zh-TW"]["review.review_areas"] = "複習清單"
UI_TEXT["en"]["review.related_questions"] = "Related to Question"
UI_TEXT["zh-TW"]["review.related_questions"] = "對應題目"
UI_TEXT["en"]["review.review_step"] = "Review step"
UI_TEXT["zh-TW"]["review.review_step"] = "複習此步驟"
UI_TEXT["en"]["review.unmapped"] = "Some missed questions do not have a usable lesson-step mapping."
UI_TEXT["zh-TW"]["review.unmapped"] = "部分答錯題目沒有可用的課程步驟對應。"
UI_TEXT["en"]["review.build"] = "Build focused review"
UI_TEXT["zh-TW"]["review.build"] = "建立重點複習"
UI_TEXT["en"]["review.building"] = "Building focused review…"
UI_TEXT["zh-TW"]["review.building"] = "正在建立重點複習…"
UI_TEXT["en"]["review.focused_review"] = "Focused Review"
UI_TEXT["zh-TW"]["review.focused_review"] = "重點複習"
UI_TEXT["en"]["review.review"] = "Review"
UI_TEXT["zh-TW"]["review.review"] = "複習"
UI_TEXT["en"]["review.what_to_fix"] = "What to fix"
UI_TEXT["zh-TW"]["review.what_to_fix"] = "需要釐清"
UI_TEXT["en"]["review.focused_explanation"] = "Focused explanation"
UI_TEXT["zh-TW"]["review.focused_explanation"] = "重點說明"
UI_TEXT["en"]["review.intuition"] = "Intuition or example"
UI_TEXT["zh-TW"]["review.intuition"] = "直覺或例子"
UI_TEXT["en"]["review.retry"] = "Retry Check"
UI_TEXT["zh-TW"]["review.retry"] = "再次檢核"
UI_TEXT["en"]["review.choose"] = "Choose an answer"
UI_TEXT["zh-TW"]["review.choose"] = "選擇答案"
UI_TEXT["en"]["review.check"] = "Check answer"
UI_TEXT["zh-TW"]["review.check"] = "檢查答案"
UI_TEXT["en"]["review.choose_first"] = "Choose an answer before checking."
UI_TEXT["zh-TW"]["review.choose_first"] = "請先選擇答案。"
UI_TEXT["en"]["review.correct"] = "Correct"
UI_TEXT["zh-TW"]["review.correct"] = "答對了"
UI_TEXT["en"]["review.not_quite"] = "Not quite"
UI_TEXT["zh-TW"]["review.not_quite"] = "再想一下"
UI_TEXT["en"]["review.no_retry"] = "No usable retry questions are available."
UI_TEXT["zh-TW"]["review.no_retry"] = "目前沒有可用的再次檢核題目。"
UI_TEXT["en"]["review.original"] = "Original Knowledge Check"
UI_TEXT["zh-TW"]["review.original"] = "原始知識檢核"
UI_TEXT["en"]["review.retry_result"] = "Retry Check"
UI_TEXT["zh-TW"]["review.retry_result"] = "再次檢核"
UI_TEXT["en"]["review.retry_complete"] = "All retry questions are complete."
UI_TEXT["zh-TW"]["review.retry_complete"] = "所有再次檢核題目皆已完成。"
UI_TEXT["en"]["review.correct_suffix"] = "correct"
UI_TEXT["zh-TW"]["review.correct_suffix"] = "答對"
UI_TEXT["en"]["review.source"] = "Source"
UI_TEXT["zh-TW"]["review.source"] = "來源"
UI_TEXT["en"]["review.error"] = "We couldn’t build the focused review right now. Please try again."
UI_TEXT["zh-TW"]["review.error"] = "目前無法建立重點複習，請稍後再試。"
UI_TEXT["en"]["review.key_error"] = "OpenAI API access is not configured for focused review yet."
UI_TEXT["zh-TW"]["review.key_error"] = "尚未設定重點複習所需的 OpenAI API 存取。"
UI_TEXT["en"]["review.format_error"] = "The focused review came back incomplete. Please try again."
UI_TEXT["zh-TW"]["review.format_error"] = "重點複習的回傳格式不完整，請再試一次。"


WORLD_TEXT = {
    "Spatial Learning World": "空間學習場景",
    "Build Spatial Learning World": "建立空間學習場景",
    "Explore one physical system through coordinated spatial, signal and vector views.": "以協調的空間、波形與向量視圖探索同一個物理系統。",
    "Spatial Scene": "空間視圖",
    "Signal / Waveform": "訊號／波形",
    "Vector / Phasor": "向量／相量",
    "Equation / State Lens": "方程式／狀態視角",
    "Time": "時間", "Play": "播放", "Pause": "暫停", "Replay": "重播",
    "Reset time": "重設時間", "Playback speed": "播放速度",
    "Current": "目前", "Baseline": "基準", "Delta": "差值",
    "What changed?": "哪些數值改變了？",
    "Set baseline": "設為比較基準", "Reset to baseline": "回到基準狀態", "Clear comparison": "清除比較",
    "Semantic focus": "觀察對象", "Model assumptions": "模型簡化假設",
    "Keyboard time control": "鍵盤時間控制／備援",
    "Keyboard parameter and focus controls": "鍵盤參數與觀察對象／備援",
    "Keyboard comparison controls": "鍵盤比較控制／備援",
    "Exploration Recording & Replay": "探索紀錄與回放",
    "Replay speed": "回放速度",
    "Replay step {step} / {count}": "回放步驟 {step}／{count}",
    "Initial state": "起始狀態",
    "Focus": "關注項目",
    "3D camera": "3D 相機",
    "2D interaction": "2D 互動",
    "3D camera unavailable; synchronized 2D remains active.": "3D 相機無法使用；同步 2D 視圖仍可操作。",
    "Synchronized planar camera (z = 0)": "同步平面相機視圖（z = 0）",
    "Drag to rotate; scroll to zoom.": "拖曳旋轉，滾輪縮放。",
    "These controls use committed state. Pause playback before using keyboard fallbacks.": "這些備援控制項使用已確認的狀態，請先暫停播放再操作。",
    "Updating shared state…": "正在同步系統狀態…",
    "Try this": "試試這個實驗", "Run experiment": "執行實驗",
    "Record / replay exploration": "記錄／重播探索",
    "Start recording": "開始記錄", "Stop recording": "停止記錄", "Clear recording": "清除記錄",
    "Replay exploration": "重播探索", "Recording": "記錄中", "Recording stopped": "已停止記錄",
    "Recorded steps: {count}": "已記錄步驟：{count}",
    "Replay complete": "探索重播完成", "Comparison": "基準與目前狀態比較", "Local exploration": "本機互動探索",
    "Drag a highlighted handle; click a waveform or trajectory to explore the same system.": "拖曳向量端點，或點選波形與軌跡，從不同視角操控同一個系統。",
    "Click a waveform or select an object to explore the same system.": "點選波形或選取物件，從不同視角探索同一個系統。",
    "3D camera / static fallback": "3D 相機／靜態備援視圖",
    "Planar model (z = 0)": "平面模型（z = 0）",
    "This camera view is a committed-state snapshot; continuous playback stays in the coordinated workspace.": "此相機視圖呈現已確認的狀態快照；連續播放在上方協調工作區內進行。",
    "That change is outside this validated model. The world was preserved.": "這項變更超出已驗證模型範圍，場景保留原狀。",
    "This recording could not be replayed safely.": "這段記錄無法安全重播。",
    "The coordinated browser view is unavailable. Local controls and the spatial fallback remain available.": "協調互動視圖目前無法使用，本機控制項與空間備援視圖仍可使用。",
}
UI_TEXT["zh-TW"].update(WORLD_TEXT)
UI_TEXT["en"].update({key: key for key in WORLD_TEXT})


ATLAS_TEXT = {
    "Inspect document structure locally": "本機解析文件結構",
    "Reading native PDF structure…": "正在讀取原生 PDF 結構…",
    "Optional local parser is not installed; Source Atlas still works.": "尚未安裝選配本機解析器；來源互動圖譜仍可使用。",
    "Local structure is unavailable for this PDF; original sources and AI grounding remain available.": "此 PDF 暫無法使用本機結構解析；原始來源與 AI 定位仍可使用。",
    "Native PDF structure: {count} text regions. No OCR or AI request.": "原生 PDF 結構：{count} 個文字區域。不含 OCR，不呼叫 AI。",
    "Native text locations only; figures and semantic links still require grounding.": "目前僅顯示原生文字位置；圖解與語意連結仍需另行定位。",
    "Native PDF text geometry; not OCR or semantic classification.": "位置來自原生 PDF 文字幾何；不含 OCR 或語意分類。",
    "Native PDF text geometry; semantic support remains estimated.": "位置來自原生 PDF 文字幾何；語意支持仍為估計。",
    "Native PDF text": "原生 PDF 文字",
    "Source Atlas": "來源互動圖譜",
    "Build Source Atlas": "建立來源互動圖譜",
    "Connect original formulas and diagrams to the same learning-world focus.": "將原始公式與圖示連到同一個學習場景焦點。",
    "Pages to ground (up to 3)": "選擇定位頁面（最多 3 頁）",
    "Page {page}": "第 {page} 頁",
    "Grounding selected source pages…": "正在定位所選來源頁面…",
    "Grounded pages: {pages}": "已處理頁面：{pages}",
    "Source grounding is unavailable. Existing analysis, sources and learning worlds are unchanged.": "來源定位目前無法使用；原有分析、來源與學習場景均保留。",
    "Original Source": "原始來源",
    "Interactive Meaning": "互動理解",
    "Estimated visual grounding; the original PDF remains the source of truth.": "視覺定位為模型估計，請以原始 PDF 核對。",
    "Pause world playback before selecting a source object; source navigation uses committed state.": "請先暫停場景播放，再選取來源物件；來源導覽使用已確認的共享狀態。",
    "Source page": "來源頁面",
    "Choose a source object": "選取來源物件",
    "The interactive source image is unavailable. Use the source list or existing Source Lens.": "互動來源影像目前無法使用，請使用來源清單或既有來源檢視。",
    "Grounding quality: {quality}": "定位品質：{quality}",
    "Grounding high": "高信心（仍需核對）",
    "Grounding medium": "中等信心（概略區域）",
    "Grounding low": "低信心（僅頁級）",
    "Page-level anchor only; no reliable visual box is available.": "僅保留頁級定位，沒有可靠的視覺框選區域。",
    "Linked meaning": "連結語意",
    "Explore linked meaning": "探索連結概念",
    "Open as interactive scene": "轉成互動場景",
    "Formula Trace": "公式追溯",
    "Verified extracted excerpt": "已核對的擷取原文",
    "Estimated visual transcription — verify on the original page.": "模型估計的視覺轉錄，請回原頁核對。",
    "Quantities": "語意量",
    "Parameters": "參數",
    "Driven representations": "連動表示",
    "Concept source trace": "概念來源軌跡",
    "No visual anchor for this focus. Existing page-level source links remain available.": "此焦點尚無視覺定位，可使用既有頁級來源連結。",
    "No reliable regions were grounded; page context is retained.": "未找到可靠區域，保留原始頁面脈絡。",
    "Zoom": "縮放",
    "Reset view": "重設檢視",
    "Diagram Breakdown": "拆解圖示",
    "All layers": "全部圖層",
    "Structure": "結構",
    "Labels": "標籤",
    "Vectors": "向量／箭頭",
    "Formulas": "公式",
    "Active focus only": "僅顯示目前焦點",
    "Hide labels": "隱藏標籤",
    "Reveal label": "揭示標籤",
    "Estimated region — verify on the original page.": "區域為估計定位，請核對原頁；隱藏標籤時點擊遮罩可揭示。",
    "Source Viewer": "互動來源檢視器",
}
UI_TEXT["zh-TW"].update(ATLAS_TEXT)
UI_TEXT["en"].update({key: key for key in ATLAS_TEXT})


def current_language():
    language = st.session_state.get("product_language", DEFAULT_LANGUAGE)
    return language if language in LANGUAGE_NAMES else DEFAULT_LANGUAGE


def tr(key, *, language=None, **values):
    """Translate product chrome; all interpolation values remain untouched."""
    language = language or current_language()
    text = UI_TEXT.get(language, UI_TEXT[DEFAULT_LANGUAGE]).get(key, key)
    return text.format(**values) if values else text


def output_language_instruction(language):
    requirement = {
        "zh-TW": "Use natural Traditional Chinese (繁體中文), never Simplified Chinese.",
        "en": "Use clear English.",
    }[language]
    return (
        f"Required output language: {RESPONSE_LANGUAGES[language]}. {requirement} "
        "Apply this to all generated explanations, labels, suggestions, lessons, "
        "quizzes, review and interactive lab text, regardless of source language. "
        "Keep canonical enum values and stable IDs unchanged. Preserve mathematical "
        "symbols, variable names and helpful established English technical terms. "
        "Quoted or extracted source text must remain in its original language; "
        "never present a translated passage as the original source."
    )

