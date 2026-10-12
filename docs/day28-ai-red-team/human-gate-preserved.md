# Day 28 PREP ONLY — 等待人類審核

2026-10-12（Asia/Taipei）。狀態 `PREP_ONLY_REVIEW_PENDING`，human approval=false，參與者=0，收集資料=0，模型／上傳請求=0。這是準備完成紀錄，Day28 人類研究尚未開始也未完成。不得用本機預檢代替人類可用性／理解證據。不 commit/push，不開啟 Day29。

## 復原結果

工作目錄限定 `D:\Projects\visual-learning-lab`。開始時 `git status --short` 為空。分支 `day17-learning-scene-wip`；目前 HEAD `5a6ec3c8ab6e70892b2d6a299a7ef315e90cf40d`（feat: validate day27 real-material generalization）；Git tree `7feeb7fe933c352ca9dd08df11d412f776e1efac`。歷史 Day27 核准文件的 HEAD 477de492 是當時尚未提交的版本，不能誤寫成現在 HEAD。

已讀 README、PRODUCT_VISION、DAY26_EVIDENCE、DAY27_EVIDENCE、DAY27_CHECKPOINT、UI_REDESIGN_CHECKPOINT，以及 Day27 human-approved-a-axis/completion/validation/final regression。採用較新的人工核准紀錄；較早文件仍寫 pending／480/489，保留歷史、不覆寫。

| Day27 已有證據 | 確認結果 |
|---|---|
| 凍結 baseline A | PASS 4 / PARTIAL 4 / FAIL 2，10 個分母保留。 |
| 人工核准 POST_FIX A | PASS 5 / PARTIAL 5 / FAIL 0；SHM 為明確新人工 PASS。 |
| 最終核准 full regression | 489/489，0 failures/errors/skips，242.890 秒；歷史 480/489 保留。 |
| 正式程式完整性 | 與 Day27 `live-production-seal.json` 的 78 個檔案 SHA-256 逐檔相符；Candidate C／renderer／正式首頁／requirements 均未改。 |

## 產品與研究入口指紋

正式 78 檔 SHA-256 map 的指紋：`1b7021801c03e0dbe9f7fe02d18f08ffb836292dcff779949c0cd1bd338bd8db`。

演算法：SHA-256(each file exact bytes)，path→hash map 用 UTF-8 JSON、sort_keys=true、ensure_ascii=false、separators=(',', ':') 序列化，再 SHA-256。與 Day27 演算法相同。Git tree 僅識別已提交內容；研究入口／本次文件尚未提交，其 exact bytes 另封存，不能只用 commit 代替研究版本。

`freeze-manifest.json` 同時封存題目、rubric、P01–P05 分派、全部 Day28 文件／預檢／研究入口檔案和 tracked worktree 指紋。`prepared-inputs.json` 封存原 PDF subset、未編輯 main 與 Atlas response 的 hashes；它不包含 credentials／request bodies，也不公開 local response bodies。manifest 自己不自我包含。人工 approval 需記錄 manifest 本身的 SHA-256，而非修改問題檔案來標示批准。

預檢成功後執行一次封存；之後驗證命令 `python -X utf8 -B tests/day28_freeze.py --verify`。任何不同都須在 P01 前重新審查／另封新版，不能靜默覆蓋。

## 選材與離線檢查

Day26 拋體不是可直接使用的當前素材：`.day26-local/response-3.json` scene_version=2.2，被當前 v2.4 normalize_world 拒絕 `incompatible declaration`，且該目錄未保存原 PDF。正確 scene 的相容性檢查為離線、0 生成；未遷移／修改 declaration／弱化 validator。

選擇 Day27 POST_FIX SHM：MIT OpenCourseWare / Peter Dourmashkin，Chapter 23: Simple Harmonic Motion。原 PDF SHA-256 `e950d874692071a2329d78ba0e952756e9fb1289c019e5e670a1a8171429b611`；八頁 subset SHA-256 `f3e563a5e3796cba4a3edc83dbce40ae0c0f07f5ac0122869c2845805e07c8d1`，1,622,242 bytes。原 PDF 3–10→預覽 1–8，印刷 23-2–23-9。使用本機既有 subset，不重新下載／生成。source pixels/text 保持原貌。

[原教材頁](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter23/)；[MIT OCW 條款](https://ocw.mit.edu/pages/privacy-and-terms-of-use/)；[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。2026-10-12 查核 primary publisher。僅非商業研究預覽；截選頁面未改內容，來源截圖沿用該授權、應保留署名，沒有 MIT 背書。研究題目／介面是另加內容。未加入第三方程式或依賴；既有 PyMuPDF 部署授權問題仍留在既有 ledger。

已抽取並視覺核對預覽頁 7、8：式 23.2.25、amplitude definition、Figure 23.4；頁 1 的式 23.1.1–23.1.4 亦核對。Poppler 產生原頁 PNG，字型 Symbol 出現環境 warning；可見頁面公式／圖與印刷頁標籤均正常。不是 OCR 或自行重畫。題目答案僅是待人工批准的推導。

目前 normalizers 接受原 main 的 1 個 Lab、6 個 lesson steps 和原 Atlas。正式 UI 的中文首頁／Source／Explore／Practice 均检查。研究入口从空 app.py 首页附加一次准备示例按鈕；载入后进入 Learn，无预选 focus、值归默认，所有 production widgets／renderers 不变。这是 study accommodation，不是已发布的首页功能。

AppTest（自動化，非人類）證明空首頁有 PDF 與 pasted-text 控制；載入示例後 Source→Explore→Practice→Source 可渲染；振幅 3→1.5 合法提交、曲線縮半、原 source facts／PDF bytes 不變，值跨視圖保留；拒絕異動 inputs 時不清空既有學習狀態。整個有效路徑 API attempts=0/uploads=0；未錄 keystrokes 或 participant response。

Codex in-app browser 的獨立工程 smoke：空首頁→準備示例→Learn→Source 真 PDF→Explore→展開參數→振幅 3→2.9→Practice→Source；看得到 A/T/φ、immutable source values 和假設探索標示。這是 agent 操作，不計人類時間、成功率、理解或偏好。窄版 viewport，非固定 1440×1000 參與者裝置驗收；保留一張 controls 截圖。AppTest 與 browser 分別是工程證據，不推論學員行為。

## 限制需一併批准

- 當前 SHM Lab 是滑桿／曲線，沒有直接拖曳 inverse；不能宣稱 Day26 完整 direct-Twin path。
- Atlas 只有預覽 1–3 頁。頁 1 的通用 sinusoidal formula region 沒有 catalog semantic ID；如選此區，只是來源檢視，不假造 link。振幅／相位細節 7、8 需既有 Source Lens；題目振幅／週期基本定義在頁 1 已足夠。研究操作不要求任意錯誤 source identity 成功。
- 未載入錯述 k/m 可調控制的 planner reason。表示規劃／spatial build／Explain 等新 AI 動作在這個準備 lane 被阻擋；誤點記 dead end。這不是正式 live compile 研究，也沒有默默修 planner。
- 同一參與者先做 A 才能保持 A 的首次使用；B 已接觸 SHM，記錄 prior exploration/help。固定題序 A→B，條件順序交替；n=3/5 有 2:1/3:2 不平衡。不消除 carryover／題目難度差異。
- 中文 UI、英文原文與既有英文生成內容；只能招募能閱讀該材料的人。外推性有限。

## 檢查與檔案

初次 focused：4 tests，1 個 test-only SessionState accessor error；其他核心互動已成功。修正研究測試欄位 accessor，未改正式程式。最終 focused：4/4，9.230 秒；完整 relevant suite 一次：493/493，255.037 秒，0 failures/errors（既有 489＋新 4）。完整 logs 保留於 pretest/。正式程式與歷史 tracked evidence 未改；沒有新的人類結果檔。

本次建立：PARTICIPANT_INSTRUCTIONS、MODERATOR_GUIDE、STUDY_A_PROTOCOL、STUDY_B_PROTOCOL、FROZEN_TASKS、FROZEN_SCORING、participant-template.json、HUMAN_DATA_TEMPLATE.csv、PRETEST_CHECKPOINT；加 TASK_ORDER_ASSIGNMENTS、ENTRY_PATH_RECOMMENDATION、prepared-inputs、freeze-manifest、pretest 工程紀錄；tests/day28_prepared、manual_day28、day28_freeze、test_day28_preparation。完整逐檔清單與 exact hashes 見 manifest。

沒有新增 dependency，也沒有新增 parser、renderer、learning interaction；復用正式 normalizers、Lab、Source Lens／Atlas、Workspace、AppTest 與原 PDF，故不新增開源子系統／不改既有 reuse ledger。沒有 Day28 完成報告／圖表／人類結果。

正式 app 精確命令：

```powershell
python -m streamlit run app.py
```

本機審核 prepared lane（只預覽，不收集資料）：

```powershell
python -X utf8 -B -m streamlit run tests/manual_day28.py --server.address 127.0.0.1 --server.port 8532 --server.headless true --browser.gatherUsageStats false
```

本環境 sandbox 的 python Windows Store alias 無法啟動；實際檢查用現有 `C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe`，經審核在本機執行，不安裝新 runtime。Python 的 real location 與 bare-mode Streamlit warnings 留在 logs；沒有把環境 warning 當 human failure。

**STOP：請人類批准兩研究的 exact questions、預期答案、rubric、P01–P05 分派與研究入口限制。未批准前不招募／收集／評分／畫人類結果，不 commit/push。**
