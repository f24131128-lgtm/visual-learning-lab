# DAY 28 CHECKPOINT — AI-SIMULATED RED TEAM

2026-10-12，Asia/Taipei。工作位置 D:\Projects\visual-learning-lab。
最終狀態：`AI_SIMULATED_RED_TEAM_DONE`。真人 Study A/B 尚未開始；
human PREP仍 `PREP_ONLY_REVIEW_PENDING`。不要重新啟動已完成的 regression。

已恢復 AI01–AI05 保存的九張截图與 operations.json；沒有重做 AI01–AI03。
AI01/02 控制成功；AI03 offline CTA 失敗；AI04 查證頁面 PARTIAL；
AI05 upload 成功、generation completion NOT TESTED。沒有真人資料。

已修兩項 UX：Source 概念 ownership→真實 controls；offline prepared / Own PDF
事前區分與 disabled AI 入口。沒有新 renderer、inverse、dependency 或 schema。

新 focused：7/7 PASS，13.106s。保存初始 2 failures（button gate）及第二次
2 errors（test accessor），已修。原 frozen files 及 baseline screenshots hashes
在 test 中核對成功。新 browser：Source→controls→A 3→2.90→Source→重開仍
2.90；原 source fact 3，原 PDF 可見，API/upload attempts=0。

最後一次完整 suite 已完成，一次且僅一次：
`python -X utf8 -B -m unittest discover -s tests -v`
log：`docs/day28-ai-red-team/full-regression.log`。
**500/500 PASS，303.017s，0 failures/errors/skips**。
組成：既有493（Day27 489＋PREP4）＋Day28新7。Focused最終7/7；
full suite包含同一7項，不能當成額外7種獨立產品行為。
勿重跑已完成 PREP 493 或 Day27 benchmark。

正式 app 命令：`python -m streamlit run app.py`。
新 offline lane 命令：
`python -X utf8 -B -m streamlit run tests/manual_day28_red_team.py --server.address 127.0.0.1 --server.port 8532 --server.headless true --browser.gatherUsageStats false`。
舊 preview PID40888 已核對並停止；新離線 lane PID16828 使用同一8532。

真人 PREP仍 `PREP_ONLY_REVIEW_PENDING`、human participants=0；未更改 frozen
protocol／rubric／入口，未觸碰 HUMAN_DATA_TEMPLATE.csv。修復後 production
hash 與歷史 seal 不同屬明示 UX 變更；不能重封或覆蓋歷史 baseline。

尚未測：真人學習成效、完整自有 PDF AI 分析、cross-domain browser 泛化。
本次恢復沒有新的付費 OpenAI API；前 Session AI05 曾提交正式分析但無最終
回應／帳務證據，不能宣稱前 Session 的整段 request count=0。

未 commit/push/checkout/reset，未開始 Day29。完整詳情與截圖：
[AI_SIMULATED_EVIDENCE.md](day28/AI_SIMULATED_EVIDENCE.md)、
[DAY28_EVIDENCE.md](DAY28_EVIDENCE.md)。

Git仍有未提交的修改／新增；詳見
[git-status-final.txt](day28-ai-red-team/git-status-final.txt)。新增 Day28 frozen
PREP檔在工作開始時已是 untracked，未刪除或重新封存。Production 修改5個
tracked檔：app.py、interactive_lab.py、i18n.py、workspace/ui.py、reuse ledger；
新增control_navigation與offline lane/tests/docs/evidence。無新依賴。
工作完成資料 hashes見[completion-integrity.json](day28-ai-red-team/completion-integrity.json)。
