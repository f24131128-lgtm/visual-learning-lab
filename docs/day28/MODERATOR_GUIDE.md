# Day28 主持人手冊（尚未開放測試）

PREP_ONLY_REVIEW_PENDING。現在只審閱，不能用預覽操作記錄冒充參與者。先取得人類 reviewer 對問題、答案、rubric、分派、accommodation 的批准；在單獨 approval record 填匿名 reviewer role、approved_at 與 freeze-manifest hash。沒有批准就不創建 raw participant files。

1. 審查 PRETEST_CHECKPOINT.md、文件 hashes、0 API 本機預檢與產品指纹。不同版本不得混合。桌機固定 1440×1000、瀏覽器版本于第一次參與前記錄，所有人保持相同設置；自己的語言／無障碍調整須事前記錄為 accommodation。
2. 準備英文閱讀能力足夠、首次 VLL 的 3–5 位，只用代碼。不給預期答案，不以題目前測教概念。允許拒绝／退出；不記錄姓名／聯络资訊／其他識別资料，不錄影錄音。
3. 人類批准後，首次使用前開 fresh browser session 的 `tests/manual_day28.py` 空首頁，勿點示例、Learn/Source/Explore/Practice。告知它是事先準備的示例，但不指示位置。準備示例標簽固定保留；現在只供審核，不開始 P01。批准後使用同一封存入口，不改正式 app 或 test version。
4. 只念固定 Study A 任務；用本機 stopwatch，t0 從首頁和任務就绪起算。最大 8 分鐘，90 秒完全阻塞才 rescue。標記五個累計時間、完整 friction 與 intervention，不收 keystrokes。
5. 停止操作計時後先念中性理解題，保留去識別回答，再逐字問五 ratings／三 open questions；不得解釋 Source/Twin/Explore 或替學員總結。
6. Study B 按 TASK_ORDER_ASSIGNMENTS.json。每題 5 分鐘；兩題間 2 分鐘、收回前題答案、不給反饋。VLL 使用重置過的準備材料，從 Learn 開始；PDF 打開同一份八頁 excerpt。不要為學員預調題目參數。第二題前關闭另一條件窗口。
7. 每題收原始回答、time/status、兩個 ratings 和證據使用；獨立人類 scorer 按固定 rubric 評分、保留理由。審稿人不同意见記在獨立字段，不更改 raw text。Codex 只能汇整人類已確認的分數。
8. 若 app 災難失敗，中止全系列、保存 failure/version，修復再另起 series；不能在 P01–P05 內静默修 UI。普通犹豫先計頻率，不立刻改產品。

## 觀察表怎麼填

`participant-template.json` 是沒有數據的單人模板；`HUMAN_DATA_TEMPLATE.csv` 只有表頭。全部未见／未問／未完成值 null／CSV 空白，真實 0 秒與 score=0 才填 0。複制到另存的本機 raw 目錄（不覆蓋模板，不入公開證據／不傳模型）。JSON 允許全部干預及有序摩擦；CSV 做三行／人（A、B-A、B-B），複杂 notes 參照 JSON，勿把研究 A/B 混成總分。

friction categories：`homepage_unclear`, `source_not_found`, `explorable_concept_not_found`, `linked_representation_unclear`, `change_unclear`, `source_baseline_confused`, `source_return_failed`, `interface_text_unclear`, `generation_loading_failure`, `browser_layout`, `other`。

每項填 sequence、elapsed_s、category、observed_action（只觀測）、participant_quote（可空）、blocking、related_intervention、resolved。介入填 elapsed_s、trigger（blocked_90s/app_failure）、exact_words、action、outcome。分清解釋是觀察／參與者原話／主持人判斷，不從 agent 自動化推測人類行為。

## 後續邊界

本次不創建 DAY28_EVIDENCE.md 或 DAY28_CHECKPOINT.md 的完成報告，也不收數據或出圖。未來全系列結束保留 raw、freeze baseline、每人行，再做描述摘要。完成時間中位數僅對 completed cases 報 n；所有 timeout/withdrawal/failure 另外顯示，不填假完成值。rating medians/ranges 保留每題 missing denominator。

TOP TWO usability candidates 僅满足 ≥2 位重複、或 1 位阻斷核心路徑；不修一人偏好。最多兩項小修，baseline 與 confirmation retest 分開，重複參與者／任務熟悉效應明示。禁止統計增益、學習有效性或普遍偏好宣稱。不開始 Day29，不 commit/push。

