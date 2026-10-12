# Study A v1 — 首次使用（審核待核準）

目的：第一次使用者能否自行找到教材、探索、觀察並回到來源；不是學習成效分數。招募 3–5 位未用過 VLL 的學生／合理學習者。只使用 P01–P05，非敏感可選欄位為廣泛學科、主題熟悉度 low/medium/high。主持人確認參與意願後才記錄；本次 prep 不招募也不收資料。

## 固定產品與準備素材

以 PRETEST_CHECKPOINT.md 的 commit、Git tree、78 檔正式程式指紋和研究入口檔案 hashes 為版本。Study A 從實際 app.py 的空首頁開始；不從 Source 或預先編譯 Explore 開始。`tests/manual_day28.py` 在頁尾附加明示的「試用準備好的示例」按鈕，載入未編輯的 Day27 POST_FIX SHM analysis/Atlas，經目前正式 normalizers 驗證後，進入 Learn、無預選焦點、Lab 預設值。

這個研究入口沒有加入正式首頁；它是必要的研究 accommodation。首次使用結論僅涵蓋此準備示例路徑及現有四個正式視圖，不包含自行上傳、等待、AI 編譯成功率或正式版尚不存在的 demo 入口發現率。保留首頁原本 PDF／貼文控制；若誤走該路，記錄死路與阻擋訊息，不算 API 生成測試。

素材：Day27 SHM（人工 POST_FIX A-axis PASS）。`.day27-local/subsets/harmonic.pdf` 為原 PDF 第 3–10 頁；預覽頁 1–8 對應原 PDF 3–10、印刷頁 23-2–23-9。正常 Source Atlas 只覆蓋預覽頁 1–3；振幅／週期／相位證據在預覽頁 1、7、8，可由既有 Source Lens 核對，7、8 不偽造框或新增語意定位。正式 Lab 是振幅／週期／相位滑桿，沒有直接拖曳把手。不要宣稱完整 Day26 direct-Twin Golden Path。

Day26 拋體 raw scene v2.2 被目前 v2.4 契約拒絕，原 PDF 也未留在 `.day26-local`；不遷移、不重生、不弱化驗證。SHM 準備入口不載入已知與實際 Lab 控制不一致的 planner reason；不開放新的 planner/compiler/explanation requests。正確的 analysis、formal 圖、Lab 與來源皆由正式 runtime 處理。

## 任務與固定邊界

逐字任務見 FROZEN_TASKS.md。開始計時 t0：首頁完成顯示且主持人已念完任務；首次示例載入、導航與猶豫均計入。總操作上限 480 秒。可提早自稱完成／退出；結束後停止操作計時再詢問固定中性理解題。不要求 think-aloud，以免額外訓練；自然說話可以逐字去識別記錄。

只有連續 90 秒完全無進展，或應用程式本身故障，才可介入。最多一次有路線資訊的救援；之後再阻塞 90 秒或達 480 秒即停止。中性程序救援：「你可以再看一下目前畫面上的選項，選擇你覺得符合任務的。」若仍完全阻塞，可在同一次救援指出一個下一步；必須逐字記錄，並認定為不獨立。任何一次介入均排除 FULL；重複介入／未完成核心任務為 FAIL。技術故障也是介入，不忽略；災難性阻塞中止整系列。

## 指標的操作定義

所有時間為從 t0 起算的秒數，不是階段相減；未達成填 null／CSV 留白，不填 0。

| 指標 | 觀察到才記錄 |
|---|---|
| first_source_inspection_s | 檢視真正 PDF 頁／原文，並指出一個與運動有關的公式、圖或敘述；摘要不算。 |
| representation_discovery_s | 自行打開／指出可改動的 Lab 控制，表明想試一項變數；只切視圖不算。 |
| first_state_change_s | 一個合法滑桿變更成功提交，值和至少一個曲線／數值反應可見；點擊未改值不算。 |
| supporting_source_return_s | 改動後回到相關原頁／原文並指出它支持哪個概念；返回無關頁不算。 |
| completion_time_s | 僅 completed 填完成操作的時間；未完成留 null。另以 stopping_time_s 記 timed_out/withdrew/app_failure 的停止時間，不把停止時間當成功完成時間。 |

另外記錄 noticing source/exploration、returned_support、noticed_result、source_unchanged_understood、changed_state_understood（true/false/null）、全部介入、按時間順序的摩擦、錯點／死路。單次猶豫是觀察，不自動是 bug。核心順序為 source→representation→change→notice→source；若自行先探索，記真實順序，FULL 仍需之後完成一次全鏈。

## 預先固定成功規則

FULL：480 秒內，無介入，獨立完成首頁→來源／脈絡→有用表示→合法改動→觀察結果→回支持來源，並能說明改了什麼、結果如何變、原 PDF／原文沒被改動。

PARTIAL：完成有用且成功的互動，但需一次介入；或缺少獨立來源返回／無法清楚說明來源與探索差異。尚未成功改動不算 PARTIAL。

FAIL：界限內沒有成功核心互動、超過一次介入、核心任務完全阻塞；退出／app failure 保留 FAIL 與原因，不從分母移除。沒有同意參與者不建立結果。

結果由人類主持人按 FROZEN_SCORING.md 判斷，Codex 不從瀏覽器動作推測理解。獨立詢問理解之後再問五評分／三開放題，避免提示原 PDF 未改的答案。

## 版本與後續

P01 開始即凍結產品、示例、任務、rubric 與分派。不得修到 P05 中途；災難阻塞先停止，記錄舊版本所有嘗試，修復後用新 study version 重新系列，不能混合。完整人類基線後才統計；最多兩項小修，每項至少兩人重複或一人阻斷核心路徑。確認重測獨立保存。

